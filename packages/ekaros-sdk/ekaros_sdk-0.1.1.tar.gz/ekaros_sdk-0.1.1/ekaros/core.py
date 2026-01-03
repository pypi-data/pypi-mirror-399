from .utils.types import CapturedNode
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    Sequence,
)
from django.urls.resolvers import URLPattern, URLResolver
import time
import threading
from functools import wraps
from django.http import HttpRequest, HttpResponse
import threading
import tracemalloc
import random
from .constants import MEMORY_SAMPLING_RATE, EKAROS_EVENTS_ENDPOINT, REQUEST_TIMEOUT_SECONDS
import threading
import requests
import json
import base64
import logging
from typing import Dict, Any

class Ekaros:
    """
    Ekaros Python SDK
    
    Currently Supports:
        1. Django    
        
    Raises:
        1. ValueError: When the framework is not supported
        2. SDKValidationException: When the SDK API Key validation fails
    """
    _instance_registry: Dict[str, Callable[..., Any]] = {}
    
    def __init__(self, framework="django", instance_name: str = 'default', **opts):
        try:
            if framework == "django":
                from .backends.django.backend import DjangoBackend
                self.backend = DjangoBackend(instance_name=instance_name ,**opts)
            else:
                raise ValueError(f"Unknown framework '{framework}'")
        except Exception as e:
            raise e
        
        Ekaros._instance_registry[instance_name] = self # type: ignore
    
    @classmethod
    def get_instance(cls, name="default") -> 'Ekaros':
        if name not in cls._instance_registry:
            raise ValueError(f"Ekaros instance '{name}' not initialized.")
        return cls._instance_registry[name] # type: ignore

    
    def register(self, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator: @ekaros.register("app_name:view_name")
        """
        
        return self.backend.register(name=name)

    def track(self):
        """
        Decorator to track comprehensive API performance metrics:
        - Latency (ms)
        - Memory (request/response size + sampled allocation tracking)
        - Status code
        - Path & method
        - Errors
        - Experiment detection (A/B testing)
        - Headers (all request headers)
        - Request data (body/query params)
        - Response data (complete response content)
        
        Configuration:
        - Adjust Ekaros._MEMORY_SAMPLE_RATE to change how often detailed memory tracking occurs
        (0.05 = 5%, 0.10 = 10%, 1.0 = always)
        
        TODO: 
        Add metrics of which user's data is being sent. 
        Possibly through the API_KEY we provide the SDK to talk to our Backend.
        Add ServerID
        """
        def decorator(view_func):
        
            @wraps(view_func)
            def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
                start_time = time.time()
                start_time_epoch = int(time.time())
                request_size = len(request.body) if request.body else 0      
                should_track_memory = random.random() < MEMORY_SAMPLING_RATE
                memory_allocated_bytes = None
                peak_memory_bytes = None
                
                if should_track_memory:
                    try:
                        tracemalloc.start()
                        snapshot_before = tracemalloc.take_snapshot()
                    except Exception:
                        should_track_memory = False
                
                # Capture all headers
                request_headers = dict(request.headers)
                
                # Capture request body
                request_body = None
                try:
                    if request.body:
                        # Try to decode as UTF-8 string first
                        request_body = request.body.decode('utf-8')
                        # Optionally parse JSON if content-type is application/json
                        if request.content_type == 'application/json':
                            try:
                                request_body = json.loads(request_body)
                            except json.JSONDecodeError:
                                pass  # Keep as string if not valid JSON
                except UnicodeDecodeError:
                    # If binary data, encode as base64 for storage
                    request_body = base64.b64encode(request.body).decode('utf-8')
                
                # Capture query parameters
                query_params = dict(request.GET)
                
                # Capture POST data (for form submissions)
                post_data = dict(request.POST) if request.POST else None
                
                response = None
                error_message = None
                status_code = 500
                
                try:
                    response = view_func(request, *args, **kwargs)
                    status_code = response.status_code
                except Exception as e:
                    error_message = str(e)
                    status_code = 500
                    raise
                finally:
                    latency_ms = (time.time() - start_time) * 1000
                    response_size = 0                    
                    response_headers = {}
                    response_body = None
                    
                    if response:
                        # Capture response headers
                        response_headers = dict(response.items())
                        
                        # Capture response body
                        if hasattr(response, 'content'):
                            response_size = len(response.content)
                            try:
                                # Try to decode as UTF-8 string
                                response_body = response.content.decode('utf-8')
                                # Try to parse as JSON if applicable
                                content_type = response.get('Content-Type', '')
                                if 'application/json' in content_type:
                                    try:
                                        response_body = json.loads(response_body)
                                    except json.JSONDecodeError:
                                        pass  # Keep as string
                            except UnicodeDecodeError:
                                # If binary, encode as base64
                                response_body = base64.b64encode(response.content).decode('utf-8')
                        elif hasattr(response, 'streaming_content'):
                            response_size = -1
                            response_body = "<streaming_content>"
                    
                    if should_track_memory:
                        try:
                            snapshot_after = tracemalloc.take_snapshot()
                            stats = snapshot_after.compare_to(snapshot_before, 'lineno') # type: ignore
                            memory_allocated_bytes = sum(stat.size_diff for stat in stats)
                            peak_memory_bytes = tracemalloc.get_traced_memory()[1]
                            tracemalloc.stop()
                        except Exception:
                            pass
                    
                    
                    request_content_type = request.content_type or ''
                    response_content_type = ''
                    if response:
                        response_content_type = response.get('Content-Type', '')

                    payload_metrics = {
                        "start_time": start_time_epoch,
                        "path": request.path,
                        "method": request.method,
                        "latency_ms": round(latency_ms, 2),
                        "status_code": status_code,
                        "request_size_bytes": request_size,
                        "response_size_bytes": response_size,
                        "total_data_bytes": request_size + (response_size if response_size >= 0 else 0),
                        "error": error_message,                        
                        "request_headers": request_headers,
                        "request_body": request_body,
                        "query_params": query_params,
                        "post_data": post_data,
                        "response_headers": response_headers,
                        "response_body": response_body,
                        "request_content_type": request_content_type,
                        "response_content_type": response_content_type,
                    }
                    
                    if memory_allocated_bytes is not None:
                        payload_metrics["memory_allocated_bytes"] = memory_allocated_bytes
                        payload_metrics["peak_memory_bytes"] = peak_memory_bytes
                    
                    try:
                        experiment_type = getattr(request, '_ekaros_experiment_type', None)
                        
                        if experiment_type:
                            payload_metrics["experiment_type"] = experiment_type
                            payload_metrics["registered_view"] = getattr(request, '_ekaros_registered_view', None)
                            payload_metrics["router"] = getattr(request, '_ekaros_router', 'default')
                            
                            if experiment_type == 1:
                                payload_metrics["abtest_name"] = getattr(request, '_diserance_abtest_name', None)
                            elif experiment_type == 2:
                                payload_metrics["journey_name"] = getattr(request, '_ekaros_journey_name', None)
                                payload_metrics["journey_path"] = str(getattr(request, '_ekaros_journey_path', None))
                                payload_metrics["ekaros_custom_params"] = getattr(request, '_ekaros_custom_param', {})
                                                
                    except (ImportError, AttributeError, KeyError) as e:
                        # TODO: LOG THE ERROR
                        pass
                    
                    try:
                        self.send_metrics_async(payload=payload_metrics, sdk_key=self.get_sdk_key(), server_id=self.get_server_id())
                    except Exception:
                        pass
                
                return response # type: ignore
            
            return wrapper

        return decorator

    def set_route(self, url_pattern: str, view_name: str, name=None):
        """
        Set a new route in the URL Tree
        Usage: diserance.set_route("ab_apis/new_dynamic/", "new_dynamic_view")
        """
        
        return self.backend.set_route(url_pattern=url_pattern, view_name=view_name, name=name)

    def remove_route(self, url_pattern: str):
        """
        Remove a URL Pattern from the URL Tree
        """
        
        return self.backend.remove_route(url_pattern=url_pattern)

    def validate_license(self):
        """Validate the Ekaros SDK Initialization"""
        
        return self.backend.validate_license()

    def load_url_patterns(
        self,
        patterns: Sequence[Union[URLPattern, URLResolver, Tuple[str, Callable[..., Any]]]],
        namespace: Optional[str] = None
    ) -> List[CapturedNode]:
        """
        Recursively capture URLPattern / URLResolver tree while preserving namespaces.
        """
        
        return self.backend.load_url_patterns(patterns=patterns, namespace=namespace)
    
    def get_urlpatterns(self) -> List[Union[URLPattern, URLResolver]]:
        """
        Return urlpatterns with preserved module/namespace tree + dynamic routes
        """
        
        return self.backend.get_urlpatterns()

    def validate_route(self, url_pattern: str) -> None:
        """
        Validate the route before modification
        
        Raises:
            1. PermissionError: When the baseline route is trying to be modified
        """
        return self.backend.validate_route(url_pattern=url_pattern)
    
    def refresh_urlpatterns(self):
        """
        Rebuild Django URL cache and update app URLs dynamically
        """
        return self.backend.refresh_urlpatterns()
    
    def get_registered_views(self):
        """Get the list of registered views"""
        return self.backend._registered_views
    
    def get_routes(self):
        """Get the list of routes"""
        return self.backend._routes

    def get_sdk_key(self):
        """Get the sdk key"""
        return self.backend._sdk_key

    def get_server_id(self):
        """Get server id"""
        return self.backend._server_id

    def create_client_token(
        self,
        custom_parameters: Optional[Dict[str, Any]] = None,
        timeout: int = 86400
    ) -> str:
        return self.backend.create_client_token(custom_parameters=custom_parameters, timeout=timeout)

    def send_metrics_async(
        self,
        payload: Dict[str, Any],
        sdk_key: str = '',
        server_id: str = '',
    ):
        """
        Send backend metrics to Ekaros asynchronously.

        This function is intentionally fire-and-forget:
        - Runs in a daemon thread
        - Never blocks the request lifecycle
        - Swallows all exceptions (metrics must never break prod traffic)
        """

        if not sdk_key or not server_id:
            # Fail silently — metrics should never crash app
            return

        def _send():
            try:
                headers = {
                    "X-EKAROS-SERVER-SDK-KEY": sdk_key,
                    "X-EKAROS-SERVER-ID": server_id,
                    "Content-Type": "application/json",
                }

                response = requests.post(
                    EKAROS_EVENTS_ENDPOINT,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
                
                if response.status_code >= 400:
                    logging.debug(
                        "Ekaros metrics failed",
                        extra={
                            "status_code": response.status_code,
                            "response": response.text,
                        },
                    )

            except Exception as e:
                # Never raise — metrics must be invisible to the app
                logging.debug("Ekaros metrics exception", exc_info=e)

        threading.Thread(target=_send, daemon=True).start()


