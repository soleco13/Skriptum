"""
WebSocket URL routing для совместного редактирования BPMN диаграмм
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/bpmn/collaborate/(?P<diagram_id>\w+)/$', consumers.BpmnCollaborationConsumer.as_asgi()),
]
