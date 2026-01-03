import threading
import time
import requests
from typing import Callable, Optional, Dict, Any
from .constants import JOURNEY_POLLING_END_POINT, POLLING_INTERVAL, API_TIMEOUT

class PollingClient:
    """
    Polling fallback for journey updates when SSE is unavailable.
    Uses last_sync_timestamp to fetch only new updates.
    """
    
    def __init__(
        self,
        sdk_key: str,
        project_id: str,
        on_journey_update: Callable[[Dict[str, Any]], None],
        interval: int = POLLING_INTERVAL,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        self._sdk_key = sdk_key
        self._project_id = project_id
        self._on_journey_update = on_journey_update
        self._interval = interval
        self._on_error = on_error
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_sync_timestamp: Optional[str] = None
    
    def start(self):
        """Start polling in a background thread"""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop polling"""
        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
    
    def _poll_loop(self):
        """Main polling loop"""
        while self._running:
            try:
                self._poll_updates()
            except Exception as e:
                if self._on_error:
                    self._on_error(e)
            
            # Wait for next interval or stop signal
            self._stop_event.wait(self._interval)
    
    def _poll_updates(self):
        """Fetch journey updates from server"""
        headers = {
            'X-EKAROS-SERVER-SDK-KEY': self._sdk_key,
            'X-EKAROS-PROJECT-ID': self._project_id,
        }
        
        params = {}
        if self._last_sync_timestamp:
            params['since'] = self._last_sync_timestamp
        
        try:
            response = requests.get(
                JOURNEY_POLLING_END_POINT,
                headers=headers,
                params=params,
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 1:
                updates = data.get('updates', [])
                
                for update in updates:
                    self._on_journey_update(update)
                
                # Update timestamp for next poll
                if 'last_sync_timestamp' in data:
                    self._last_sync_timestamp = data['last_sync_timestamp']
        
        except requests.RequestException as e:
            if self._on_error:
                self._on_error(e)