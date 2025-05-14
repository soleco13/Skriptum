from rest_framework import viewsets, filters, status, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import Document, Process, Task, UserProfile, DocumentHistory, BpmnDiagram
from .serializers import DocumentSerializer, ProcessSerializer, TaskSerializer, UserSerializer, UserProfileSerializer, UserCreateSerializer, DocumentHistorySerializer, BpmnDiagramSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()  # Добавляем базовый queryset
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type', 'status']
    search_fields = ['name']
    
    def get_queryset(self):
        # Возвращаем только документы текущего пользователя
        return Document.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        """Получение содержимого документа для редактирования"""
        document = self.get_object()
        return Response({
            'id': document.id,
            'name': document.name,
            'content': document.content,
            'file': document.file.url if document.file else None,
            'file_type': document.file_type
        })
    
    @action(detail=True, methods=['put', 'patch'])
    def update_content(self, request, pk=None):
        """Обновление содержимого документа с поддержкой CKEditor и сохранением истории"""
        document = self.get_object()
        old_content = document.content
        document.content = request.data.get('content', document.content)
        
        # Создаем запись в истории только если содержимое изменилось
        if old_content != document.content:
            # Сохраняем версию документа в историю
            DocumentHistory.objects.create(
                document=document,
                content=old_content,  # Сохраняем предыдущую версию
                user=request.user,
                version_name=request.data.get('version_name', f'Версия от {document.name}')
            )
        
        document.save()
        return Response({
            'id': document.id,
            'name': document.name,
            'content': document.content
        })
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Получение истории изменений документа"""
        document = self.get_object()
        history = DocumentHistory.objects.filter(document=document)
        serializer = DocumentHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='restore/(?P<history_id>[^/.]+)')
    def restore_version(self, request, pk=None, history_id=None):
        """Восстановление документа из истории"""
        document = self.get_object()
        
        try:
            # Получаем запись истории
            history_item = DocumentHistory.objects.get(id=history_id, document=document)
            
            # Сохраняем текущую версию в историю перед восстановлением
            DocumentHistory.objects.create(
                document=document,
                content=document.content,
                user=request.user,
                version_name=f'Автосохранение перед восстановлением версии от {history_item.created_at.strftime("%d.%m.%Y %H:%M")}'
            )
            
            # Восстанавливаем содержимое из истории
            document.content = history_item.content
            document.save()
            
            return Response({
                'id': document.id,
                'name': document.name,
                'content': document.content,
                'message': f'Документ восстановлен из версии от {history_item.created_at.strftime("%d.%m.%Y %H:%M")}'
            })
        except DocumentHistory.DoesNotExist:
            return Response({'error': 'Версия не найдена'}, status=status.HTTP_404_NOT_FOUND)

class BpmnDiagramViewSet(viewsets.ModelViewSet):
    queryset = BpmnDiagram.objects.all()
    serializer_class = BpmnDiagramSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        # Возвращаем только диаграммы текущего пользователя
        return BpmnDiagram.objects.filter(user=self.request.user)
    
class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()  # Добавляем базовый queryset
    serializer_class = ProcessSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Возвращаем только процессы текущего пользователя
        return Process.objects.filter(user=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()  # Добавляем базовый queryset
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Возвращаем только задачи текущего пользователя
        return Task.objects.filter(user=self.request.user)

def get_data(request):
    # Пример данных, которые можно вернуть
    data = {"message": "Hello, World!"}
    return JsonResponse(data)


class UserViewSet(viewsets.ModelViewSet):
    """
    API для работы с пользователями
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Получение данных текущего пользователя
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """
        Обновление данных текущего пользователя
        """
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Обновление профиля текущего пользователя
        """
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
