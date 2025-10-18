from rest_framework import viewsets, filters, status, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Document, Process, Task, UserProfile, DocumentHistory, BpmnDiagram, DocumentAccess, BpmnAccess, Role
from .serializers import DocumentSerializer, ProcessSerializer, TaskSerializer, UserSerializer, UserProfileSerializer, UserCreateSerializer, DocumentHistorySerializer, BpmnDiagramSerializer, UserSearchSerializer, DocumentAccessSerializer, BpmnAccessSerializer, RoleSerializer, RoleListSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()  # Добавляем базовый queryset
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type', 'status']
    search_fields = ['name']
    
    def get_queryset(self):
        # Возвращаем документы пользователя + документы, к которым есть доступ
        user = self.request.user
        
        # Документы, принадлежащие пользователю
        owned_documents = Q(user=user)
        
        # Документы, к которым предоставлен доступ
        shared_documents = Q(access_permissions__user=user)
        
        return Document.objects.filter(owned_documents | shared_documents).distinct()
    
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
        # Возвращаем диаграммы пользователя + диаграммы, к которым есть доступ
        user = self.request.user
        
        # Диаграммы, принадлежащие пользователю
        owned_diagrams = Q(user=user)
        
        # Диаграммы, к которым предоставлен доступ
        shared_diagrams = Q(access_permissions__user=user)
        
        return BpmnDiagram.objects.filter(owned_diagrams | shared_diagrams).distinct()
    
    def perform_create(self, serializer):
        # Устанавливаем пользователя при создании
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        # Сохраняем исходного владельца диаграммы при обновлении
        print(f"Обновление диаграммы. Данные: {self.request.data}")
        print(f"Метод запроса: {self.request.method}")
        
        # Получаем текущий объект диаграммы
        instance = self.get_object()
        original_owner = instance.user
        
        print(f"Исходный владелец диаграммы: {original_owner}")
        print(f"Текущий пользователь: {self.request.user}")
        
        # Сохраняем с исходным владельцем
        serializer.save(user=original_owner)
    
    @action(detail=False, methods=['get'], url_path='by-process/(?P<process_id>[^/.]+)')
    def by_process(self, request, process_id=None):
        """Получение диаграммы по ID процесса"""
        try:
            diagram = BpmnDiagram.objects.get(process_id=process_id)
            serializer = BpmnDiagramSerializer(diagram, context={'request': request})
            return Response(serializer.data)
        except BpmnDiagram.DoesNotExist:
            return Response({'error': 'Диаграмма для данного процесса не найдена'}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        print(f"UPDATE запрос к BPMN диаграмме. Данные: {request.data}")
        print(f"Метод: {request.method}")
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            print(f"Ошибка при обновлении BPMN диаграммы: {e}")
            raise
    
    def retrieve(self, request, pk=None):
        """
        Получение диаграммы. Если диаграмма с указанным ID не найдена,
        пытаемся найти диаграмму для процесса с указанным ID.
        """
        try:
            # Сначала пытаемся найти диаграмму по ID
            diagram = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(diagram)
            return Response(serializer.data)
        except BpmnDiagram.DoesNotExist:
            # Если диаграмма не найдена, пытаемся найти по process
            try:
                diagram = self.get_queryset().get(process=pk)
                serializer = self.get_serializer(diagram)
                return Response(serializer.data)
            except BpmnDiagram.DoesNotExist:
                # Если диаграмма для процесса не найдена, возвращаем 404
                return Response(
                    {'detail': 'BPMN диаграмма не найдена'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
    
class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()  # Добавляем базовый queryset
    serializer_class = ProcessSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Возвращаем процессы пользователя + процессы, к диаграммам которых есть доступ
        user = self.request.user
        
        # Процессы, принадлежащие пользователю
        owned_processes = Q(user=user)
        
        # Процессы, к диаграммам которых предоставлен доступ
        shared_processes = Q(bpmn_diagrams__access_permissions__user=user)
        
        return Process.objects.filter(owned_processes | shared_processes).distinct()

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
    
    @action(detail=False, methods=['get'])
    def profile_stats(self, request):
        """
        Получение статистики пользователя
        """
        user = request.user
        
        # Подсчитываем количество документов, задач и процессов
        documents_count = Document.objects.filter(user=user).count()
        tasks_count = Task.objects.filter(user=user).count()
        processes_count = Process.objects.filter(user=user).count()
        
        # Подсчитываем количество документов с доступом
        shared_documents_count = DocumentAccess.objects.filter(user=user).count()
        
        # Подсчитываем количество BPMN диаграмм с доступом
        shared_bpmn_count = BpmnAccess.objects.filter(user=user).count()
        
        return Response({
            'documents_count': documents_count,
            'tasks_count': tasks_count,
            'processes_count': processes_count,
            'shared_documents_count': shared_documents_count,
            'shared_bpmn_count': shared_bpmn_count,
            'total_documents': documents_count + shared_documents_count,
            'total_processes': processes_count + shared_bpmn_count
        })
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """
        Получение последней активности пользователя
        """
        user = request.user
        activities = []
        
        # Получаем последние документы
        recent_documents = Document.objects.filter(user=user).order_by('-created')[:5]
        for doc in recent_documents:
            activities.append({
                'type': 'document',
                'description': f'Создан документ "{doc.name}"',
                'time': doc.created.strftime('%d.%m.%Y'),
                'timestamp': doc.created.isoformat(),
                'icon': 'fas fa-file-alt',
                'color': '#3b82f6'
            })
        
        # Получаем последние задачи
        recent_tasks = Task.objects.filter(user=user).order_by('-id')[:5]
        for task in recent_tasks:
            activities.append({
                'type': 'task',
                'description': f'Создана задача "{task.title}"',
                'time': 'Сегодня',  # Можно добавить поле created_at в модель Task
                'timestamp': '2025-01-15T10:00:00Z',
                'icon': 'fas fa-tasks',
                'color': '#10b981'
            })
        
        # Получаем последние процессы
        recent_processes = Process.objects.filter(user=user).order_by('-id')[:5]
        for process in recent_processes:
            activities.append({
                'type': 'process',
                'description': f'Создан процесс "{process.name}"',
                'time': 'Вчера',  # Можно добавить поле created_at в модель Process
                'timestamp': '2025-01-14T15:30:00Z',
                'icon': 'fas fa-project-diagram',
                'color': '#f59e0b'
            })
        
        # Сортируем по времени (новые сначала)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response(activities[:10])  # Возвращаем только последние 10 активностей
    
    @action(detail=False, methods=['post'])
    def upload_avatar(self, request):
        """
        Загрузка аватара пользователя
        """
        if 'avatar' not in request.FILES:
            return Response({'error': 'Файл аватара не найден'}, status=status.HTTP_400_BAD_REQUEST)
        
        avatar_file = request.FILES['avatar']
        
        # Проверяем размер файла (максимум 5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return Response({'error': 'Размер файла не должен превышать 5MB'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем тип файла
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return Response({'error': 'Неподдерживаемый тип файла. Разрешены: JPEG, PNG, GIF, WebP'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Сохраняем файл
            profile = request.user.profile
            
            # Генерируем уникальное имя файла
            import uuid
            file_extension = avatar_file.name.split('.')[-1]
            unique_filename = f"avatar_{request.user.id}_{uuid.uuid4().hex}.{file_extension}"
            
            # Сохраняем файл в папку avatars
            avatar_path = f"avatars/{unique_filename}"
            
            # Создаем папку если её нет
            import os
            from django.conf import settings
            avatars_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
            os.makedirs(avatars_dir, exist_ok=True)
            
            # Сохраняем файл
            with open(os.path.join(avatars_dir, unique_filename), 'wb') as f:
                for chunk in avatar_file.chunks():
                    f.write(chunk)
            
            # Обновляем профиль
            profile.avatar = avatar_path
            profile.save()
            
            return Response({
                'success': True,
                'avatar_url': f"{settings.MEDIA_URL}{avatar_path}",
                'message': 'Аватар успешно загружен'
            })
            
        except Exception as e:
            return Response({'error': f'Ошибка при загрузке аватара: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Поиск пользователей по имени или email
        """
        query = request.query_params.get('q', '').strip()
        
        # Если запрос пустой, возвращаем 3 случайных пользователя
        if not query:
            users = User.objects.exclude(id=request.user.id).order_by('?')[:3]
            serializer = UserSearchSerializer(users, many=True)
            return Response(serializer.data)
        
        # Если запрос слишком короткий, тоже показываем случайных пользователей
        if len(query) < 2:
            users = User.objects.exclude(id=request.user.id).order_by('?')[:3]
            serializer = UserSearchSerializer(users, many=True)
            return Response(serializer.data)
        
        # Выполняем поиск
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=request.user.id)[:10]  # Исключаем текущего пользователя и ограничиваем до 10
        
        # Если поиск не дал результатов, показываем случайных пользователей
        if not users.exists():
            users = User.objects.exclude(id=request.user.id).order_by('?')[:3]
        
        serializer = UserSearchSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        """Назначение роли пользователю"""
        user_profile = request.user.profile
        
        if not user_profile.has_permission('manage_users'):
            return Response({'error': 'У вас нет прав для назначения ролей'}, status=status.HTTP_403_FORBIDDEN)
        
        target_user = self.get_object()
        role_id = request.data.get('role_id')
        
        if not role_id:
            return Response({'error': 'ID роли обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            role = Role.objects.get(id=role_id)
            target_user.profile.role = role
            target_user.profile.save()
            
            return Response({
                'message': f'Роль "{role.display_name}" назначена пользователю {target_user.username}',
                'user': {
                    'id': target_user.id,
                    'username': target_user.username,
                    'role': role.display_name
                }
            })
        except Role.DoesNotExist:
            return Response({'error': 'Роль не найдена'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_role(self, request, pk=None):
        """Снятие роли с пользователя"""
        user_profile = request.user.profile
        
        if not user_profile.has_permission('manage_users'):
            return Response({'error': 'У вас нет прав для снятия ролей'}, status=status.HTTP_403_FORBIDDEN)
        
        target_user = self.get_object()
        
        # Проверяем, что пользователь не пытается снять роль с себя
        if target_user == request.user:
            return Response({'error': 'Нельзя снять роль с самого себя'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_role = target_user.profile.role
        target_user.profile.role = None
        target_user.profile.save()
        
        return Response({
            'message': f'Роль "{old_role.display_name}" снята с пользователя {target_user.username}',
            'user': {
                'id': target_user.id,
                'username': target_user.username,
                'role': None
            }
        })


class DocumentAccessViewSet(viewsets.ModelViewSet):
    """
    API для управления доступом к документам
    """
    queryset = DocumentAccess.objects.all()
    serializer_class = DocumentAccessSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Возвращаем только доступы для документов, владельцем которых является текущий пользователь
        return DocumentAccess.objects.filter(document__user=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='document/(?P<document_id>[^/.]+)')
    def by_document(self, request, document_id=None):
        """
        Получение списка пользователей с доступом к конкретному документу
        """
        try:
            # Проверяем, что документ принадлежит текущему пользователю
            document = Document.objects.get(id=document_id, user=request.user)
            
            # Получаем все доступы к этому документу
            accesses = DocumentAccess.objects.filter(document=document)
            serializer = DocumentAccessSerializer(accesses, many=True)
            
            # Также добавляем информацию о владельце
            owner_info = {
                'id': 'owner',
                'user': document.user.id,
                'user_name': f"{document.user.first_name} {document.user.last_name}".strip() if document.user.first_name or document.user.last_name else document.user.username,
                'user_email': document.user.email,
                'access_level': 'owner',
                'access_level_display': 'Владелец',
                'granted_by': None,
                'granted_by_name': None,
                'granted_at': None,
                'granted_at_formatted': None,
            }
            
            return Response({
                'owner': owner_info,
                'shared_users': serializer.data
            })
            
        except Document.DoesNotExist:
            return Response({'error': 'Документ не найден или у вас нет прав доступа'}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        """
        Предоставление доступа к документу
        """
        document_id = request.data.get('document')
        user_id = request.data.get('user')
        
        try:
            # Проверяем, что документ принадлежит текущему пользователю
            document = Document.objects.get(id=document_id, user=request.user)
            
            # Проверяем, что пользователь существует и не является владельцем документа
            user = User.objects.get(id=user_id)
            if user == request.user:
                return Response({'error': 'Нельзя выдать доступ самому себе'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Проверяем, нет ли уже доступа у этого пользователя
            existing_access = DocumentAccess.objects.filter(document=document, user=user).first()
            if existing_access:
                return Response({'error': 'У пользователя уже есть доступ к этому документу'}, status=status.HTTP_400_BAD_REQUEST)
            
            return super().create(request, *args, **kwargs)
            
        except Document.DoesNotExist:
            return Response({'error': 'Документ не найден или у вас нет прав доступа'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        """
        Обновление уровня доступа
        """
        access = self.get_object()
        
        # Проверяем, что текущий пользователь является владельцем документа
        if access.document.user != request.user:
            return Response({'error': 'У вас нет прав для изменения доступа к этому документу'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Отзыв доступа к документу
        """
        access = self.get_object()
        
        # Проверяем, что текущий пользователь является владельцем документа
        if access.document.user != request.user:
            return Response({'error': 'У вас нет прав для отзыва доступа к этому документу'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)


class BpmnAccessViewSet(viewsets.ModelViewSet):
    """
    API для управления доступом к BPMN диаграммам
    """
    queryset = BpmnAccess.objects.all()
    serializer_class = BpmnAccessSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Возвращаем только доступы для диаграмм, владельцем которых является текущий пользователь
        # Если у пользователя нет диаграмм, возвращаем пустой queryset
        return BpmnAccess.objects.filter(diagram__user=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='diagram/(?P<diagram_id>[^/.]+)')
    def by_diagram(self, request, diagram_id=None):
        """
        Получение списка пользователей с доступом к конкретной BPMN диаграмме
        """
        try:
            # Проверяем, что диаграмма принадлежит текущему пользователю
            diagram = BpmnDiagram.objects.get(id=diagram_id, user=request.user)
            
            # Получаем все доступы к этой диаграмме
            accesses = BpmnAccess.objects.filter(diagram=diagram)
            serializer = BpmnAccessSerializer(accesses, many=True)
            
            # Также добавляем информацию о владельце
            owner_info = {
                'id': 'owner',
                'user': diagram.user.id,
                'user_name': f"{diagram.user.first_name} {diagram.user.last_name}".strip() if diagram.user.first_name or diagram.user.last_name else diagram.user.username,
                'user_email': diagram.user.email,
                'access_level': 'owner',
                'access_level_display': 'Владелец',
                'granted_by': None,
                'granted_by_name': None,
                'granted_at': None,
                'granted_at_formatted': None,
            }
            
            return Response({
                'owner': owner_info,
                'shared_users': serializer.data
            })
            
        except BpmnDiagram.DoesNotExist:
            return Response({'error': 'BPMN диаграмма не найдена или у вас нет прав доступа'}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        """
        Предоставление доступа к BPMN диаграмме
        """
        diagram_id = request.data.get('diagram')
        user_id = request.data.get('user')
        
        try:
            # Проверяем, что диаграмма принадлежит текущему пользователю
            diagram = BpmnDiagram.objects.get(id=diagram_id, user=request.user)
            
            # Проверяем, что пользователь существует и не является владельцем диаграммы
            user = User.objects.get(id=user_id)
            if user == request.user:
                return Response({'error': 'Нельзя выдать доступ самому себе'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Проверяем, нет ли уже доступа у этого пользователя
            existing_access = BpmnAccess.objects.filter(diagram=diagram, user=user).first()
            if existing_access:
                return Response({'error': 'У пользователя уже есть доступ к этой диаграмме'}, status=status.HTTP_400_BAD_REQUEST)
            
            return super().create(request, *args, **kwargs)
            
        except BpmnDiagram.DoesNotExist:
            return Response({'error': 'BPMN диаграмма не найдена или у вас нет прав доступа'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        """
        Обновление уровня доступа к BPMN диаграмме
        """
        access = self.get_object()
        
        # Проверяем, что текущий пользователь является владельцем диаграммы
        if access.diagram.user != request.user:
            return Response({'error': 'У вас нет прав для изменения доступа к этой диаграмме'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Отзыв доступа к BPMN диаграмме
        """
        access = self.get_object()
        
        # Проверяем, что текущий пользователь является владельцем диаграммы
        if access.diagram.user != request.user:
            return Response({'error': 'У вас нет прав для отзыва доступа к этой диаграмме'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления ролями пользователей
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['display_name', 'description']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RoleListSerializer
        return RoleSerializer
    
    def get_queryset(self):
        """
        Возвращает роли с проверкой прав доступа
        """
        user_profile = self.request.user.profile
        
        # Только пользователи с правом управления ролями могут видеть все роли
        if user_profile.has_permission('manage_roles'):
            return Role.objects.all()
        
        # Обычные пользователи видят только активные роли
        return Role.objects.filter(is_active=True)
    
    def create(self, request, *args, **kwargs):
        """
        Создание новой роли (только для пользователей с правом manage_roles)
        """
        user_profile = request.user.profile
        if not user_profile.has_permission('manage_roles'):
            return Response({'error': 'У вас нет прав для создания ролей'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Обновление роли (только для пользователей с правом manage_roles)
        """
        user_profile = request.user.profile
        if not user_profile.has_permission('manage_roles'):
            return Response({'error': 'У вас нет прав для редактирования ролей'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Удаление роли (только для пользователей с правом manage_roles)
        """
        user_profile = request.user.profile
        if not user_profile.has_permission('manage_roles'):
            return Response({'error': 'У вас нет прав для удаления ролей'}, status=status.HTTP_403_FORBIDDEN)
        
        role = self.get_object()
        
        # Проверяем, что роль не используется пользователями
        if role.users.exists():
            return Response({'error': 'Нельзя удалить роль, которая назначена пользователям'}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def available_roles(self, request):
        """
        Получение списка доступных ролей для назначения пользователям
        """
        user_profile = request.user.profile
        
        if not user_profile.has_permission('manage_users'):
            return Response({'error': 'У вас нет прав для просмотра ролей'}, status=status.HTTP_403_FORBIDDEN)
        
        roles = Role.objects.filter(is_active=True)
        serializer = RoleListSerializer(roles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        Получение списка пользователей с определенной ролью
        """
        user_profile = request.user.profile
        
        if not user_profile.has_permission('manage_users'):
            return Response({'error': 'У вас нет прав для просмотра пользователей'}, status=status.HTTP_403_FORBIDDEN)
        
        role = self.get_object()
        users = role.users.all()
        
        # Возвращаем только основную информацию о пользователях
        user_data = []
        for user_profile in users:
            user_data.append({
                'id': user_profile.user.id,
                'username': user_profile.user.username,
                'first_name': user_profile.user.first_name,
                'last_name': user_profile.user.last_name,
                'email': user_profile.user.email,
                'position': user_profile.position,
                'department': user_profile.department,
                'is_active': user_profile.is_active
            })
        
        return Response(user_data)
    
    @action(detail=True, methods=['post'])
    def assign_to_user(self, request, pk=None):
        """
        Назначение роли пользователю
        """
        user_profile = request.user.profile
        
        if not user_profile.has_permission('manage_users'):
            return Response({'error': 'У вас нет прав для назначения ролей'}, status=status.HTTP_403_FORBIDDEN)
        
        role = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'Не указан ID пользователя'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_user = User.objects.get(id=user_id)
            target_profile = target_user.profile
            
            # Проверяем, что пользователь не пытается изменить свою роль
            if target_user == request.user:
                return Response({'error': 'Нельзя изменить свою собственную роль'}, status=status.HTTP_400_BAD_REQUEST)
            
            target_profile.role = role
            target_profile.save()
            
            return Response({
                'message': f'Роль "{role.display_name}" успешно назначена пользователю {target_user.username}',
                'user': {
                    'id': target_user.id,
                    'username': target_user.username,
                    'role': role.display_name
                }
            })
            
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def permissions_list(self, request):
        """
        Получение списка всех доступных разрешений в системе
        """
        user_profile = request.user.profile
        
        if not user_profile.has_permission('manage_roles'):
            return Response({'error': 'У вас нет прав для просмотра разрешений'}, status=status.HTTP_403_FORBIDDEN)
        
        permissions = [
            {
                'name': 'create_documents',
                'display_name': 'Создание документов',
                'description': 'Возможность создавать новые документы',
                'category': 'documents'
            },
            {
                'name': 'edit_documents',
                'display_name': 'Редактирование документов',
                'description': 'Возможность редактировать существующие документы',
                'category': 'documents'
            },
            {
                'name': 'delete_documents',
                'display_name': 'Удаление документов',
                'description': 'Возможность удалять документы',
                'category': 'documents'
            },
            {
                'name': 'share_documents',
                'display_name': 'Обмен документами',
                'description': 'Возможность делиться документами с другими пользователями',
                'category': 'documents'
            },
            {
                'name': 'create_processes',
                'display_name': 'Создание процессов',
                'description': 'Возможность создавать новые процессы',
                'category': 'processes'
            },
            {
                'name': 'edit_processes',
                'display_name': 'Редактирование процессов',
                'description': 'Возможность редактировать существующие процессы',
                'category': 'processes'
            },
            {
                'name': 'delete_processes',
                'display_name': 'Удаление процессов',
                'description': 'Возможность удалять процессы',
                'category': 'processes'
            },
            {
                'name': 'manage_processes',
                'display_name': 'Управление процессами',
                'description': 'Возможность управлять всеми процессами в системе',
                'category': 'processes'
            },
            {
                'name': 'create_tasks',
                'display_name': 'Создание задач',
                'description': 'Возможность создавать новые задачи',
                'category': 'tasks'
            },
            {
                'name': 'edit_tasks',
                'display_name': 'Редактирование задач',
                'description': 'Возможность редактировать существующие задачи',
                'category': 'tasks'
            },
            {
                'name': 'delete_tasks',
                'display_name': 'Удаление задач',
                'description': 'Возможность удалять задачи',
                'category': 'tasks'
            },
            {
                'name': 'assign_tasks',
                'display_name': 'Назначение задач',
                'description': 'Возможность назначать задачи другим пользователям',
                'category': 'tasks'
            },
            {
                'name': 'manage_users',
                'display_name': 'Управление пользователями',
                'description': 'Возможность управлять пользователями системы',
                'category': 'system'
            },
            {
                'name': 'view_analytics',
                'display_name': 'Просмотр аналитики',
                'description': 'Возможность просматривать аналитику и отчеты',
                'category': 'system'
            },
            {
                'name': 'manage_roles',
                'display_name': 'Управление ролями',
                'description': 'Возможность управлять ролями и разрешениями',
                'category': 'system'
            }
        ]
        
        return Response(permissions)

    @action(detail=True, methods=['post'])
    def remove_user(self, request, pk=None):
        """Снятие роли с пользователя"""
        user_profile = request.user.profile
        
        if not user_profile.has_permission('manage_users'):
            return Response({'error': 'У вас нет прав для снятия ролей'}, status=status.HTTP_403_FORBIDDEN)
        
        role = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'Не указан ID пользователя'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_user = User.objects.get(id=user_id)
            target_profile = target_user.profile
            
            # Проверяем, что пользователь не пытается снять роль с себя
            if target_user == request.user:
                return Response({'error': 'Нельзя снять роль с самого себя'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Проверяем, что у пользователя действительно эта роль
            if target_profile.role != role:
                return Response({'error': 'У пользователя нет этой роли'}, status=status.HTTP_400_BAD_REQUEST)
            
            target_profile.role = None
            target_profile.save()
            
            return Response({
                'message': f'Роль "{role.display_name}" снята с пользователя {target_user.username}',
                'user': {
                    'id': target_user.id,
                    'username': target_user.username,
                    'role': None
                }
            })
            
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
