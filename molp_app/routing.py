from django.urls import path

from .consumers import ScalarizationConsumer, UserScalarizationConsumer

ws_urlpatterns = [
    path('ws/scalarizations/', ScalarizationConsumer.as_asgi()),
    path('ws/user_scalarizations/', UserScalarizationConsumer.as_asgi())
]
