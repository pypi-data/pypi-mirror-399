import random
from typing import List, Tuple, Dict, Any
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .core import Ekaros
import json
from .utils.types import ExperimentType

class EkarosExperiment:
    """
    Ekaros Experiment Class helps in creating experiments on the APIs
    
    Supported Experiments:
        1. A/B Experiment: Specify the registered views you want to use and the distribution for the A/B test.
        2. Journey: Specify a Journey and with the help of HTTP Headers, serve the Users the Views you want to.
    """

    _ab_experiments: Dict[str, Dict[str, Any]] = {}
    _journeys: Dict[str, Dict[str, Dict[int, str]]] = {}

    @classmethod
    def create_abtest(
        cls,
        url_pattern: str,
        options: List[Tuple[str, int]],
        name: str = '',
        router_instance: str = "default",
    ):
        """
        Create an A/B test route that randomly assigns traffic based on percentages.

        Args:
            url_pattern (str): The base path for the experiment.
            options (List[Tuple[str, int]]): List of (view_name, percentage) tuples.
            name (str): Optional name for the test route.
            router_instance (str): Which Ekaros instance to use.
            
        raises:
            ValueError: If the percentages do not add up to 100
            ValueError: If the specified view/function is not registered
            ValueError: If the Ekaros is not initialized
        """
        
        ekaros = Ekaros.get_instance(router_instance)
        ekaros.validate_license()
        
        url_pattern = url_pattern.lstrip("/")
        ekaros.validate_route(url_pattern=url_pattern)

        total = sum(p for _, p in options)
        if total != 100:
            raise ValueError("Percentages must add up to 100")

        cls._ab_experiments[url_pattern] = {
            "name": name,
            "options": options,
            "router": router_instance,
        }

        @csrf_exempt
        @ekaros.track()
        def _ab_experiment_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            rand = random.uniform(0, 100)
            cumulative = 0
            selected_view_name = None
            for view_name, pct in options:
                cumulative += pct
                if rand <= cumulative:
                    selected_view_name = view_name
                    break

            if not selected_view_name:
                selected_view_name = options[-1][0]  # fallback

            if selected_view_name not in ekaros.get_registered_views():
                raise ValueError(f"View '{selected_view_name}' not registered in router.")

            request._ekaros_registered_view = selected_view_name # type: ignore
            request._ekaros_experiment_type = ExperimentType.ABTEST.value # type: ignore
            request._ekaros_router = router_instance # type: ignore
            request._diserance_abtest_name = name # type: ignore
            view = ekaros.get_registered_views()[selected_view_name]
            if hasattr(view, "as_view"):
                view = view.as_view() # type: ignore
            
            return view(request, *args, **kwargs)

        # Register this A/B test as a dynamic route
        ekaros.get_routes()[url_pattern] = (f"__experiment__{url_pattern}", name)
        ekaros.get_registered_views()[f"__experiment__{url_pattern}"] = _ab_experiment_view
        ekaros.refresh_urlpatterns()
        
    @classmethod
    def create_journey(
        cls,
        journey_name: str,
        steps: List[Dict[str, Any]],
        router_instance: str = "default",
    ):
        """
        Create a multi-step journey where each step has its own URL and bucket → view mapping.

        steps: [
            {
                "url": "...",
                "journey_views": [
                    [1, "view1"],
                    [2, "view2"]
                ]
            },
            ...
        ]
        """
        print(f"[INFO] creation journey with name: {journey_name}")
        ekaros = Ekaros.get_instance(router_instance)
        ekaros.validate_license()

        if journey_name in cls._journeys:
            raise ValueError(f"Journey '{journey_name}' already exists")

        cls._journeys[journey_name] = {}

        for step in steps:
            url_pattern = step["url"].lstrip("/")
            journey_views = step["journey_views"]

            ekaros.validate_route(url_pattern=url_pattern)

            bucket_map = {}
            for bucket_num, view_name in journey_views:
                if not isinstance(bucket_num, int) or bucket_num < 1:
                    raise ValueError(f"Invalid bucket number: {bucket_num}")

                if view_name not in ekaros.get_registered_views():
                    raise ValueError(f"View '{view_name}' not registered")

                bucket_map[bucket_num] = view_name

            if journey_name not in cls._journeys:
                cls._journeys[journey_name] = {}

            cls._journeys[journey_name][url_pattern] = bucket_map 


            @csrf_exempt
            @ekaros.track()
            def _journey_step_view(request, *args, _url=url_pattern, **kwargs):
                # 1️⃣ Resolve journey name
                journey = request.headers.get(
                    "X-EKAROS-JOURNEY-NAME",
                    journey_name,  # fallback to bound journey
                )

                if journey not in cls._journeys:
                    return HttpResponse(
                        f"Invalid journey '{journey}'",
                        status=400
                    )

                if _url not in cls._journeys[journey]:
                    return HttpResponse(
                        f"Journey '{journey}' does not define step '{_url}'",
                        status=400
                    )

                # 2️⃣ Resolve bucket
                try:
                    bucket = int(request.headers.get("X-EKAROS-JOURNEY-PATH", "1"))
                except ValueError:
                    bucket = 1
                
                raw_custom_params = request.headers.get("X-EKAROS-CUSTOM-PARAM", "{}")

                try:
                    custom_param = json.loads(raw_custom_params)
                except json.JSONDecodeError:
                    custom_param = {}

                step_map = cls._journeys[journey][_url]
                selected_view = step_map.get(bucket, step_map[1])

                # 3️⃣ Attach metadata
                request._ekaros_registered_view = selected_view
                request._ekaros_experiment_type = ExperimentType.JOURNEY.value
                request._ekaros_journey_name = journey
                request._ekaros_journey_path = bucket
                request._ekaros_router = router_instance
                request._ekaros_custom_param = custom_param

                view = ekaros.get_registered_views()[selected_view]
                if hasattr(view, "as_view"):
                    view = view.as_view() #type: ignore

                return view(request, *args, **kwargs)


            dynamic_view_name = f"__journey__{journey_name}__{url_pattern}"
            ekaros.get_routes()[url_pattern] = (dynamic_view_name, journey_name)
            ekaros.get_registered_views()[dynamic_view_name] = _journey_step_view

        ekaros.refresh_urlpatterns()


    @classmethod
    def list_ab_experiments(cls) -> Dict[str, Dict[str, Any]]:
        """Return all active A/B tests"""
        
        return cls._ab_experiments

    @classmethod
    def remove_ab_experiment(cls, url_pattern: str):
        """Remove a previously registered A/B test"""
        
        url_pattern = url_pattern.lstrip("/")
        
        if url_pattern not in cls._ab_experiments:
            return False

        exp = cls._ab_experiments.pop(url_pattern)
        ekaros = Ekaros.get_instance(exp["router"])
        ekaros.validate_route(url_pattern=url_pattern)
        
        ekaros.remove_route(url_pattern)
        return True

    @classmethod
    def remove_journey(cls, journey_name: str) -> bool:
        """
        Remove a journey and all its associated routes.
        
        Args:
            journey_name: The name of the journey to remove
            
        Returns:
            bool: True if journey was removed, False if journey didn't exist
        """
        
        if journey_name not in cls._journeys:
            print(f"Journey '{journey_name}' not found")
            return False

        journey_steps = cls._journeys.pop(journey_name)
        
        # Extract URL patterns from journey data
        # Format: {'journey/details/': {1: 'view1', 2: 'view2'}, 'journey/start/': {...}}
        url_patterns = journey_steps.keys()
        router_instance = "default"
        
        try:
            ekaros = Ekaros.get_instance(router_instance)
            
            # Remove all routes associated with this journey
            for url_pattern in url_patterns:
                still_used = any(
                    url_pattern in journeys
                    for journeys in cls._journeys.values()
                )

                if not still_used:
                    ekaros.get_routes().pop(url_pattern, None)
                    
            # Remove journey from the registry
            del cls._journeys[journey_name]
            
            # Refresh URL patterns to apply changes
            ekaros.refresh_urlpatterns()
            
            print(f"Journey '{journey_name}' removed successfully")
            return True
            
        except ValueError as e:
            print(f"Error removing journey '{journey_name}': Router instance not found")
            # Clean up journey data even if router is not available
            del cls._journeys[journey_name]
            return False
            
        except Exception as e:
            print(f"Error removing journey '{journey_name}': {e}")
            # Clean up journey data even on error
            del cls._journeys[journey_name]
            return False