from django.urls import path

from .consumers import ScalarizationConsumer

ws_urlpatterns = [
    path('ws/scalarizations/', ScalarizationConsumer.as_asgi())
]
