from django.urls.resolvers import URLPattern, URLResolver
from django.urls import path, clear_url_caches, get_resolver
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    Set,
    Sequence,
)
import time
import uuid
import socket
import atexit
import threading
from django.conf import settings
import requests
from ...constants import HEARTBEAT_INTERVAL, SERVER_HEARTBEAT_END_POINT, SERVER_REGISTRATION_END_POINT, SERVER_DEREGISTRATION_END_POINT, SERVER_SDK_INIT_END_POINT, SERVER_SDK_KEY_VALIDATION_END_POINT, CLIENT_SDK_TOKEN_CREATE_END_POINT, REGISTER_SERVER_VIEWS_END_POINT, API_TIMEOUT, DISCERANCE_DOMAIN, GET_ALL_JOURNIES
from ...utils.types import CapturedNode, RouteSpec
from ...utils.exceptions import SDKValidationException, JourneyException
from ...sse_client import SSEClient
from ...polling_client import PollingClient

class DjangoBackend:
    """
    Runtime-modifiable Django URL registry.

    Features:
      * Decorator-based view/function registration (`register`)
      * Capture an existing urlpatterns tree (preserves namespaces)
      * Dynamically assign or override routes at runtime
      * Keeps original module / namespace structure intact
    """
    
    _instance_registry: dict[str, 'DjangoBackend'] = {}

    def __init__(self, sdk_key: Optional[str] = None, instance_name: str = 'default') -> None:
        self._sdk_key: str = sdk_key or getattr(settings, 'DISCERANCE_SDK_KEY', '')
        self._instance_name: str = instance_name
        self.license_information: dict = self._sdk_init(sdk_key=self._sdk_key)
        self.project_id: str = self.license_information['project_id']
        self.project_name: str = self.license_information['project_name']
        self._enable_realtime: bool = True
        
        # Generate unique server ID
        self._server_id = str(uuid.uuid4())
        self._server_hostname = socket.gethostname()
        
        # Registered view callables keyed by logical name (e.g. "app_name:view_name" or "view_name")
        self._registered_views: Dict[str, Callable[..., Any]] = dict()

        # Dynamic routes keyed by url_pattern (string), value is (view_name, route_name)
        self._routes: Dict[str, RouteSpec] = dict()

        # Captured base patterns stored as a tree of CapturedItem
        self._base_patterns: List[CapturedNode] = list()
        
        # Baseline URLs that are not meant to be edited
        self._baseline_urls: Set[str] = set()
        
        # Optional map to track namespaces to resolvers (for future use)
        self._namespace_map: Dict[str, URLResolver] = dict()                
        
        #Register this Instance
        DjangoBackend._instance_registry[instance_name] = self
        
        # RegisteredView Sync
        self._registered_views_sync_status: bool = False
        
        # Journey Sync
        self._journeys_sync_status: bool = False
        
        # Real-time Sync components
        self._sse_client: Optional[SSEClient] = None
        self._polling_client: Optional[PollingClient] = None
        self._sync_lock = threading.Lock()
        
        # Register server and start real-time sync
        self._register_server()
        self._start_realtime_sync()
        
        self._enable_heartbeat = True
        self._start_heartbeat()
        
        # Register cleanup on exit
        atexit.register(self._cleanup)
    
    def _register_server(self):
        """Register this server instance with Ekaros"""
        # TODO: Add heartbeat mechanism
        try:
            response = requests.post(
                SERVER_REGISTRATION_END_POINT,
                headers={
                    'X-DISCERANCE-SERVER-SDK-KEY': self._sdk_key,
                    'X-DISCERANCE-PROJECT-ID': self.project_id,
                    'Content-Type': 'application/json'
                },
                json={
                    'server_id': self._server_id,
                    'hostname': self._server_hostname,
                    'router_instance': self._instance_name,
                },
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('status') != 1:
                print(f"Server registration failed: {result.get('message')}")
        
        except Exception as e:
            print(f"Failed to register server: {e}")
    
    def _deregister_server(self):
        """Deregister this server instance from Ekaros"""
        try:
            response = requests.post(
                SERVER_DEREGISTRATION_END_POINT,
                headers={
                    'X-DISCERANCE-SERVER-SDK-KEY': self._sdk_key,
                    'X-DISCERANCE-PROJECT-ID': self.project_id,
                    'Content-Type': 'application/json'
                },
                json={
                    'server_id': self._server_id,
                },
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
        
        except Exception as e:
            print(f"Failed to deregister server: {e}")
    
    def _start_realtime_sync(self):
        """Start SSE stream with polling fallback"""
        # SSE Client (primary)
        self._sse_client = SSEClient(
            sdk_key=self._sdk_key,
            project_id=self.project_id,
            server_id=self._server_id,
            on_journey_update=self._handle_journey_update,
            on_error=self._handle_sync_error
        )
        self._sse_client.start()
        
        # Polling Client (fallback)
        self._polling_client = PollingClient(
            sdk_key=self._sdk_key,
            project_id=self.project_id,
            on_journey_update=self._handle_journey_update,
            on_error=self._handle_sync_error
        )
        self._polling_client.start()
    
    def _handle_journey_update(self, journey_data: Dict[str, Any]):
        """Handle incoming journey update from SSE or polling"""
        from ...experiment import EkarosExperiment
        with self._sync_lock:
            try:
                action = journey_data.get('action')
                
                if action == 'delete':
                    journey_name: str = journey_data.get('journey_name', '')
                    if not journey_name:
                        print("Warning: Journey deletion event missing journey_name")
                        return
                    
                    print(f"Deleting journey: {journey_name}")
                    success = EkarosExperiment.remove_journey(journey_name)
                    
                    if success:
                        print(f"Journey '{journey_name}' deleted successfully")
                    else:
                        print(f"Journey '{journey_name}' not found or already deleted")
                else:
                    # Handle journey creation/update
                    EkarosExperiment.create_journey(
                        journey_name=journey_data.get('journey_name', ''),
                        router_instance=journey_data.get('router', ''),
                        steps=journey_data.get('steps', [])
                    )            
            except Exception as e:
                print(f"Error handling journey update: {e}")
    
    def _handle_sync_error(self, error: Exception):
        """Handle sync errors"""
        print(f"Sync error: {error}")
    
    def _cleanup(self):
        """Cleanup on shutdown"""
        if self._sse_client:
            self._sse_client.stop()
        if self._polling_client:
            self._polling_client.stop()
        if self._enable_realtime:
            self._deregister_server()
            
    def _send_heartbeat(self):
        """Sends a heartbeat signal to the Ekaros server."""
        try:
            response = requests.post(
                SERVER_HEARTBEAT_END_POINT,
                headers={
                    'X-DISCERANCE-SERVER-SDK-KEY': self._sdk_key,
                    'X-DISCERANCE-PROJECT-ID': self.project_id, # Required by Go Controller
                    'Content-Type': 'application/json'
                },
                json={
                    'server_id': self._server_id,
                },
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            # Optional: Print success
            # print(f"Heartbeat sent successfully for server ID: {self._server_id}")

        except Exception as e:
            print(f"Failed to send heartbeat: {e}")

    def _heartbeat_task(self):
        """Periodic task to send heartbeats."""
        # Send heartbeats slightly more frequently than the server's stale timeout (2 minutes)
        # Let's choose 60 seconds (1 minute) based on the Go cleanup task (5 mins, checks for 2 mins stale)
        
        while self._enable_heartbeat:
            self._send_heartbeat()
            time.sleep(HEARTBEAT_INTERVAL)

    def _start_heartbeat(self):
        """Starts the heartbeat thread."""
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_task, daemon=True)
        self._heartbeat_thread.start()
            
    @classmethod
    def get_instance(cls, name: str = 'default') -> 'DjangoBackend':
        """Get a registered router instance by name"""
        
        if name not in cls._instance_registry:
            raise ValueError(
                f"No DjangoBackend instance named '{name}' found. "
                f"Make sure you've instantiated it in your urls.py"
            )
        return cls._instance_registry[name]
    
    
    def validate_license(self):
        """Validate the Ekaros SDK API KEY"""
        try:
            response = requests.post(SERVER_SDK_KEY_VALIDATION_END_POINT, headers={'X-DISCERANCE-SERVER-SDK-KEY': self._sdk_key})
            response.raise_for_status()
            try:
                if not response.json()['validity']:
                    raise SDKValidationException(message="Invalid SDK Key")
            except requests.exceptions.JSONDecodeError:
                raise SDKValidationException(message="JSON decode error while validating SDK")
        except Exception as e:
            # Log the Error
            raise  SDKValidationException(message="Error occurred while validating SDK")
        
    def _sdk_init(self, sdk_key: str) -> Dict[str, Any]:
        """Initialize the SDK"""
        try:
            response = requests.post(SERVER_SDK_INIT_END_POINT, headers={'X-DISCERANCE-SERVER-SDK-KEY': sdk_key})
            response.raise_for_status()
            try:
                return response.json()['response']
            except requests.exceptions.JSONDecodeError:
                raise SDKValidationException(message="JSON decode error while validating SDK")
        except Exception as e:
            # Log the Exception
            raise SDKValidationException(message="Error occurred while validating SDK")
        
    def _get_filtered_registered_view_names(self):
        """
        Filter out the admin and ekaros internal API endpoits
        from being registered on Ekaros
        """
        view_names = list(self._registered_views.keys())
        filtered_view_names = list()
        for view_name in view_names:
            view_components = view_name.split(":")
            if len(view_components) != 2:
                continue
            namespace, _ = view_components
            if namespace in ("admin", "ekaros"):
                continue
            else:
                filtered_view_names.append(view_name)
        return filtered_view_names

    def _sync_journeys(self):
        """
            Sync Journeys on Start Up
        """
        from ...experiment import EkarosExperiment
        
        if self._journeys_sync_status:
            return
        
        try:
            get_all_journey_url = GET_ALL_JOURNIES.format(domain=DISCERANCE_DOMAIN)
            headers = {
                'X-DISCERANCE-SERVER-SDK-KEY': self._sdk_key
            }
            response = requests.get(get_all_journey_url, headers=headers)
            response.raise_for_status()
            journeys_response = response.json()
            if journeys_response["status"] != 1:
                raise JourneyException(message="unable to get journeys from ekaros")
            for journey in journeys_response["journey_details"]:
                EkarosExperiment.create_journey(
                    journey_name=journey["journey_name"], 
                    router_instance=journey["router"], 
                    steps=journey["steps"]
                )
            self._journeys_sync_status = True
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return
        except Exception as e:
            # Log Exception
            return
    
    def _sync_registered_views(self):
        """
        Sync all registered views with the Ekaros.
        Sends view names to the server for registration
        """

        if self._registered_views_sync_status:
            return
        
        if not self._registered_views:
            self._registered_views_sync_status = True
            return
        
        view_names = self._get_filtered_registered_view_names()
        
        try:
            response = requests.post(
                REGISTER_SERVER_VIEWS_END_POINT,
                headers={
                    'X-DISCERANCE-SERVER-SDK-KEY': self._sdk_key,
                    'Content-Type': 'application/json'
                },
                json={'view_names': view_names},
                timeout=API_TIMEOUT
            )
            response.raise_for_status()        
            self._registered_views_sync_status = True
            # Optional: Log success
            
        except requests.exceptions.Timeout:
            self._registered_views_sync_status = True
            
        except requests.exceptions.RequestException as e:
            self._registered_views_sync_status = True
            
        except Exception as e:
            # Catch any other unexpected errors
            self._registered_views_sync_status = True
    
    def _register_callable(self, view_name: str, view: Callable[..., Any]) -> Callable[..., Any]:
        """
        Register a callable under a logical name and return the callable (for decorator usage).
        """
        self._registered_views[view_name] = view
        return view

    def register(self, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator: @Ekaros.register("app_name:view_name")
        """
                
        def decorator(view):
            self._register_callable(view_name=name, view=view)
            return view
        return decorator

    def load_url_patterns(
        self,
        patterns: Sequence[Union[URLPattern, URLResolver, Tuple[str, Callable[..., Any]]]],
        namespace: Optional[str] = None
    ) -> List[CapturedNode]:
        """
        Recursively capture URLPattern / URLResolver tree while preserving namespaces.
        """
        
        captured: List[CapturedNode] = []
        for item in patterns:
            # Handle manual (url, view) tuples
            if isinstance(item, tuple) and len(item) == 2 and callable(item[1]):
                url, view = item
                pattern = path(url, view)
                captured.append(pattern)
            elif isinstance(item, URLResolver):
                ns = f"{namespace}:{item.namespace}" if namespace and item.namespace else (item.namespace or namespace)
                children = self.load_url_patterns(item.url_patterns, ns)
                captured.append({
                    "resolver": item,
                    "namespace": ns,
                    "children": children,
                })
                if item.namespace:
                    self._namespace_map[item.namespace] = item
            elif isinstance(item, URLPattern):
                full_name = f"{namespace}:{item.name}" if namespace and item.name else (item.name or None)
                if full_name and getattr(item, "callback", None):
                    self._registered_views[full_name] = item.callback
                captured.append(item)
            else:
                continue
        self._base_patterns = captured
        self._extract_all_urls(captured)
        return captured
    
    
    def _extract_all_urls(
        self,
        patterns: List[CapturedNode],
        namespace: Optional[str] = None
    ) -> None:
        """
        Recursively extract all literal URL paths from captured URL tree.
        Populates self._baseline_urls with normalized route strings.
        """
        for item in patterns:
            if isinstance(item, URLPattern):
                # Normalize pattern (remove ^, $, and leading '/')
                pattern_str = str(item.pattern).lstrip('^/').rstrip('$')
                if namespace:
                    full_path = f"{namespace}/{pattern_str}"
                else:
                    full_path = pattern_str
                self._baseline_urls.add(full_path)

            elif isinstance(item, dict) and "children" in item:
                child_ns = item.get("namespace") or namespace
                self._extract_all_urls(item["children"], child_ns)
                
    
    def validate_route(self, url_pattern: str) -> None:
        """
        Validate the route before modification
        
        Raises:
            1. PermissionError: When the baseline route is trying to be modified
        """
        
        if url_pattern in getattr(self, "_baseline_urls", set()):
            raise PermissionError(
                f"Cannot override existing baseline route: '{url_pattern}'"
            )

    def set_route(self, url_pattern: str, view_name: str, name=None):
        """
        Set a new route in the URL Tree
        Usage: Ekaros.set_route("ab_apis/new_dynamic/", "new_dynamic_view")
        """
        
        self.validate_license()
        normalized_url_pattern = url_pattern.lstrip('/')
        self.validate_route(url_pattern=normalized_url_pattern)
        
        if view_name not in self._registered_views:
            raise ValueError(f"View '{view_name}' not registered.")
        
        self._routes[normalized_url_pattern] = (view_name, name)
        self.refresh_urlpatterns()

    def remove_route(self, url_pattern: str):
        """
        Remove a URL Pattern from the URL Tree
        """
        
        self.validate_license()
        normalized_url_pattern = url_pattern.lstrip('/')
        self.validate_route(url_pattern=normalized_url_pattern)
        self._routes.pop(normalized_url_pattern, None)
        self.refresh_urlpatterns()
    
    def _build_patterns_tree(self, captured: List[CapturedNode]) -> List[Union[URLPattern, URLResolver]]:
        """
        Recursively rebuild URLPattern / URLResolver tree,
        adding dynamic routes at root level.
        """
        updated = []
        for item in captured:
            if isinstance(item, str):
                continue            
            if isinstance(item, URLPattern):
                updated.append(item)
            else:  # URLResolver tuple: (resolver, ns, children)
                resolver = item["resolver"]
                children = item["children"]
                # Recurse into children
                resolver.url_patterns = self._build_patterns_tree(children) # type: ignore
                updated.append(resolver)        
        return updated
    
    def get_urlpatterns(self) -> List[Union[URLPattern, URLResolver]]:
        """
        Return urlpatterns with preserved module/namespace tree + dynamic routes
        """
        
        base_patterns = self._build_patterns_tree(self._base_patterns)
        # Add dynamic routes at root level
        dynamic_patterns = []
        for url, (view_name, name) in self._routes.items():
            view = self._registered_views[view_name]
            if hasattr(view, "as_view"):
                view = view.as_view() # type: ignore
            dynamic_patterns.append(path(url, view, name=name)) # type: ignore
        # Put dynamic routes first so they take precedence
        self._sync_registered_views()
        self._sync_journeys()
        return dynamic_patterns + base_patterns
        
        
    def refresh_urlpatterns(self):
        """
        Rebuild Django URL cache and update app URLs dynamically
        """
        clear_url_caches()
        resolver = get_resolver(None)
        resolver.url_patterns = self.get_urlpatterns() # type: ignore
        resolver._populate()
    
    def get_registered_views(self):
        return self._registered_views
    
    def get_routes(self):
        return self._routes
    
    def create_client_token(
        self,
        custom_parameters: Optional[Dict[str, Any]] = None,
        timeout: int = 86400
    ) -> str:
        """
        Create a client SDK JWT token for frontend use.
        
        This method generates a temporary JWT token that can be safely used by
        frontend clients to communicate with api.ekaros.com. The server SDK key
        is never exposed to the client.
        
        Args:
            custom_parameters: Optional dictionary of custom parameters to include in the JWT.
                            These parameters will be embedded in the token and accessible
                            when the client makes requests to Ekaros APIs.
            timeout: Request timeout in seconds (default: 86400)
        
        Returns:
            Dictionary containing:
                - status: int (1 = success, 0 = failure, -1 = missing header)
                - status_description: str (human-readable status message)
                - jwt_token: str (the generated JWT token, if successful)
        
        Raises:
            SDKValidationException: If the request fails or returns an error
            requests.RequestException: If the HTTP request fails
        
        """        
        if not self._sdk_key:
            raise SDKValidationException(
                message="SDK key not configured. Cannot create client token."
            )
        
        headers = {
            'X-DISCERANCE-SERVER-SDK-KEY': self._sdk_key,
            'X-DISCERANCE-CLIENT-TOKEN-TIMEOUT': str(timeout),
            'Content-Type': 'application/json'
        }
        
        # Add custom parameters header if provided
        if custom_parameters:
            try:
                import json
                headers['X-DISCERANCE-CUSTOM-PARAMETERS'] = json.dumps(custom_parameters)
            except (TypeError, ValueError) as e:
                raise SDKValidationException(
                    message=f"Custom parameters must be JSON serializable: {e}"
                )
        
        try:
            response = requests.post(
                CLIENT_SDK_TOKEN_CREATE_END_POINT,
                headers=headers,
            )
            response.raise_for_status()
            
            try:
                data = response.json()
                                
                if 'status' not in data:
                    raise SDKValidationException(
                        message="Invalid response format from Ekaros API"
                    )
                
                if data['status'] != 1:
                    raise SDKValidationException(
                        message=f"Client token creation failed: {data.get('status_description', 'Unknown error')}"
                    )
                
                return data['jwt_token']
                
            except requests.exceptions.JSONDecodeError:
                raise SDKValidationException(
                    message="JSON decode error while creating client token"
                )
        
        except requests.RequestException as e:
            raise SDKValidationException(
                message=f"Error occurred while creating client token: {str(e)}"
            )