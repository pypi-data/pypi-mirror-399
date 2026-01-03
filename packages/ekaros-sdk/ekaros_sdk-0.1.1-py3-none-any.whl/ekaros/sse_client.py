import threading
import time
import json
import requests
from typing import Callable, Optional, Dict, Any
from .constants import SSE_TIMEOUT, SSE_STREAM_END_POINT, SSE_RECONNECT_DELAY, SSE_SSL_VERIFICATION

class SSEClient:
    """
    Server-Sent Events client for real-time journey updates.
    Automatically reconnects on connection loss.
    """
    
    def __init__(
        self, 
        sdk_key: str,
        project_id: str,
        server_id: str,
        on_journey_update: Callable[[Dict[str, Any]], None],
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        self._sdk_key = sdk_key
        self._project_id = project_id
        self._server_id = server_id
        self._on_journey_update = on_journey_update
        self._on_error = on_error
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._reconnect_attempts = 0
        self._max_reconnect_delay = 60  # Max 60 seconds between reconnects
        
    def start(self):
        """Start the SSE connection in a background thread"""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._reconnect_attempts = 0
        self._thread = threading.Thread(target=self._connect_and_listen, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the SSE connection"""
        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
    
    def _get_reconnect_delay(self) -> int:
        """Calculate exponential backoff delay"""
        delay = min(SSE_RECONNECT_DELAY * (2 ** self._reconnect_attempts), self._max_reconnect_delay)
        return delay
    
    def _connect_and_listen(self):
        """Main SSE connection loop with auto-reconnect"""
        while self._running:
            try:
                headers = {
                    'X-EKAROS-SERVER-SDK-KEY': self._sdk_key,
                    'X-EKAROS-PROJECT-ID': self._project_id,
                    'X-EKAROS-SERVER-ID': self._server_id,
                    'Accept': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                }
                
                # Use a session for connection pooling
                session = requests.Session()
                
                with session.get(
                    SSE_STREAM_END_POINT,
                    headers=headers,
                    stream=True,
                    timeout=(SSE_TIMEOUT, None),  # 30s connect timeout, no read timeout
                    verify=SSE_SSL_VERIFICATION,  # Verify SSL certificates
                ) as response:
                    
                    # Check if connection was successful
                    if response.status_code != 200:
                        raise requests.HTTPError(f"SSE connection failed with status {response.status_code}")
                    
                    response.raise_for_status()
                    
                    # Reset reconnect attempts on successful connection
                    self._reconnect_attempts = 0
                    
                    # Process SSE stream line by line
                    for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                        if not self._running:
                            break
                        
                        if line:
                            self._process_sse_line(line)
            
            except requests.exceptions.ConnectionError as e:
                if self._on_error:
                    self._on_error(e)
                
                if not self._running:
                    break
                
                self._reconnect_attempts += 1
                delay = self._get_reconnect_delay()
                print(f"SSE connection lost. Reconnecting in {delay}s... (attempt {self._reconnect_attempts})")
                self._stop_event.wait(delay)
            
            except requests.exceptions.ChunkedEncodingError as e:
                # Connection ended prematurely - this is common with SSE
                if self._on_error:
                    self._on_error(e)
                
                if not self._running:
                    break
                
                self._reconnect_attempts += 1
                delay = self._get_reconnect_delay()
                print(f"SSE stream interrupted. Reconnecting in {delay}s...")
                self._stop_event.wait(delay)
            
            except requests.exceptions.Timeout as e:
                if self._on_error:
                    self._on_error(e)
                
                if not self._running:
                    break
                
                self._reconnect_attempts += 1
                delay = self._get_reconnect_delay()
                print(f"SSE connection timeout. Reconnecting in {delay}s...")
                self._stop_event.wait(delay)
            
            except requests.RequestException as e:
                if self._on_error:
                    self._on_error(e)
                
                if not self._running:
                    break
                
                self._reconnect_attempts += 1
                delay = self._get_reconnect_delay()
                print(f"SSE request error: {e}. Reconnecting in {delay}s...")
                self._stop_event.wait(delay)
            
            except Exception as e:
                if self._on_error:
                    self._on_error(e)
                
                if not self._running:
                    break
                
                self._reconnect_attempts += 1
                delay = self._get_reconnect_delay()
                print(f"SSE unexpected error: {e}. Reconnecting in {delay}s...")
                self._stop_event.wait(delay)
    
    def _process_sse_line(self, line: str):
        """Parse SSE message and trigger callback"""
        if line.startswith('data:'):
            data_str = line[5:]  # Remove 'data: ' prefix
            
            if not data_str.strip():
                return
            if data_str.strip() == '[HEARTBEAT]':
                # Server heartbeat - connection is alive
                return        
            try:
                data = json.loads(data_str)                
                event_type = data.get('event_type')
                if event_type == 'journey_created':
                    print(f"Received journey creation event: {data.get('journey_name')}")
                    self._on_journey_update(data)
                elif event_type == 'journey_updated':
                    self._on_journey_update(data)
                elif event_type == 'journey_deleted':
                    journey_name = data.get('journey_name')
                    if journey_name:
                        self._on_journey_update({
                            'action': 'delete',
                            'journey_name': journey_name
                        })
                        print(f"Received journey deletion event: {journey_name}")
                    else:
                        print(f"Warning: journey_deleted event missing journey_name")
            except json.JSONDecodeError as e:
                # Ignore malformed JSON
                print(f"Failed to parse SSE data: {e}")
                pass
            except Exception as e:
                print(f"Error processing SSE message: {e}")
                pass