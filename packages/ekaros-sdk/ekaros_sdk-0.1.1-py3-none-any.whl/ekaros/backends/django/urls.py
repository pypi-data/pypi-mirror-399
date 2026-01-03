from django.urls import path
from ._views import v1_set_dynamic_route, v1_create_ab_experiment, v1_create_journey

urlpatterns = [
    path("v1/sdk/set_route/", v1_set_dynamic_route, name="sdk_set_route_v1"),
    path("v1/sdk/create_abtest/", v1_create_ab_experiment, name="sdk_create_abtest_v1"),
    path("v1/sdk/create_journey/", v1_create_journey, name="sdk_create_journey_v1"),
]