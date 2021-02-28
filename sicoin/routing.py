from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing
from sicoin.incident import routing as incident_routing

application = ProtocolTypeRouter({
    'websocket':
        URLRouter(
            chat.routing.websocket_urlpatterns + incident_routing.websocket_urlpatterns
        )
})
