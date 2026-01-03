from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .backend import DjangoBackend
from ...experiment import EkarosExperiment


@csrf_exempt
@require_POST
def v1_set_dynamic_route(request):
    # TODO: Authenticate this API. Make this Authentication strictly Django based. 
    # Let the superuser create a new user for this called ekaros_user and set a password.
    # Use this Auth to access this API.
    
    """
    Set or override a route dynamically at runtime.
    Expects JSON body:
    {
        "url": "test/",
        "view": "ab_apis:api1_v2",
        "name": "api1_v1_v2"
    }
    """
    try:
        body = json.loads(request.body)
        url = body.get("url")
        url = url.lstrip("/")

        view_name = body.get("view")
        name = body.get("name")
        router_name = body.get("router", "default")

        if not url or not view_name:
            return JsonResponse({"status": "error", "message": "Missing url or view"}, status=400)

        # Get the router instance
        try:
            ekaros = DjangoBackend.get_instance(router_name)
        except ValueError as e:
            return JsonResponse(
                {"status": "error", "message": str(e)}, 
                status=404
            )
            
        ekaros.set_route(url, view_name, name)
        
        return JsonResponse({"status": "ok", "url": url, "view": view_name, "name": name, "router": router_name}, status=200)
    
    except ValueError as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    except Exception as e:
        print(f"Exception Raised: {e}")
        return JsonResponse({"status": "error", "message": f"Error Occurred. Please check logs."}, status=400)


@csrf_exempt
@require_POST
def v1_create_ab_experiment(request):
    # TODO: Authenticate this API. Make this Authentication strictly Django based. 
    # Let the superuser create a new user for this called ekaros_user and set a password.
    # Use this Auth to access this API.
    
    """
    Create an A/B test dynamically at runtime.

    Expected JSON body:
    {
        "url": "abtest/",
        "options": [
            ["view_A", 60],
            ["view_B", 40]
        ],
        "name": "homepage_abtest",
        "router": "default"
    }
    """
    try:
        body = json.loads(request.body)
        url = body.get("url")
        url = url.lstrip("/")
        options = body.get("options")
        name = body.get("name")
        router_name = body.get("router", "default")

        # Validate inputs
        if not url or not options:
            return JsonResponse({"status": "error", "message": "Missing url or options"}, status=400)
        if not isinstance(options, list) or not all(isinstance(opt, (list, tuple)) and len(opt) == 2 for opt in options):
            return JsonResponse({"status": "error", "message": "Options must be list of [view_name, percentage]"}, status=400)

        # Validate router
        try:
            DjangoBackend.get_instance(router_name)
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=404)

        # Create experiment
        EkarosExperiment.create_abtest(url, options, name=name, router_instance=router_name)

        return JsonResponse({
            "status": "ok",
            "message": "A/B experiment created successfully",
            "url": url,
            "options": options,
            "name": name,
            "router": router_name
        }, status=200)

    except ValueError as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
    except Exception as e:
        print(f"Exception Raised: {e}")
        return JsonResponse({"status": "error", "message": "Error occurred. Please check logs."}, status=400)
    

@csrf_exempt
@require_POST
def v1_create_journey(request):
    """
    Create a Multi-Step Journey

    Expected JSON body:
    {
        "journey_name": "signup_journey",
        "router": "default",
        "steps": [
            {
                "url": "path/to/step/",
                "journey_views": [
                    [1, "view1"],
                    [2, "view2"]
                ]
            },
            ...
        ]
    }
    """
    try:
        body = json.loads(request.body)

        journey_name = body.get("journey_name")
        router_name = body.get("router", "default")
        steps = body.get("steps")

        # Validate basic fields
        if not journey_name:
            return JsonResponse({"status": "error", "message": "Missing 'journey_name'"}, status=400)

        if not steps or not isinstance(steps, list):
            return JsonResponse({"status": "error", "message": "Missing or invalid 'steps' list"}, status=400)

        # Validate router existence
        try:
            DjangoBackend.get_instance(router_name)
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=404)

        # Validate each step
        for step in steps:
            if "url" not in step or "journey_views" not in step:
                return JsonResponse(
                    {"status": "error", "message": "Each step must include 'url' and 'journey_views'"},
                    status=400,
                )

            if not isinstance(step["journey_views"], list):
                return JsonResponse(
                    {"status": "error", "message": "'journey_views' must be a list of [bucket, view]"},
                    status=400,
                )

            for pair in step["journey_views"]:
                if not (isinstance(pair, (list, tuple)) and len(pair) == 2):
                    return JsonResponse(
                        {"status": "error", 
                         "message": "Invalid journey_views format. Expected [bucket, view_name]"},
                        status=400,
                    )

        # Create the journey (multi-step)
        EkarosExperiment.create_journey(
            journey_name=journey_name,
            steps=steps,
            router_instance=router_name
        )

        return JsonResponse({
            "status": "ok",
            "message": "Journey created successfully",
            "journey_name": journey_name,
            "router": router_name,
            "steps": steps
        }, status=200)

    except ValueError as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

    except Exception as e:
        print(f"Exception Raised: {e}")
        return JsonResponse(
            {"status": "error", "message": "Error occurred. Please check logs."},
            status=400
        )
