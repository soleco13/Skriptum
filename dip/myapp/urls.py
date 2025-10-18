from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, ProcessViewSet, TaskViewSet, UserViewSet, BpmnDiagramViewSet, DocumentAccessViewSet, BpmnAccessViewSet, RoleViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet)
router.register(r'processes', ProcessViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'users', UserViewSet)
router.register(r'bpmn-diagrams', BpmnDiagramViewSet)
router.register(r'document-access', DocumentAccessViewSet)
router.register(r'bpmn-access', BpmnAccessViewSet)
router.register(r'roles', RoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]