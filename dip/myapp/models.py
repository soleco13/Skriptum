from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

# Create your models here.

class Role(models.Model):
    """
    Модель ролей пользователей в системе
    """
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Руководитель'),
        ('secretary', 'Секретарь'),
        ('employee', 'Сотрудник'),
        ('viewer', 'Наблюдатель'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True, verbose_name='Название роли')
    display_name = models.CharField(max_length=100, verbose_name='Отображаемое название')
    description = models.TextField(blank=True, verbose_name='Описание роли')
    color = models.CharField(max_length=7, default='#6c757d', verbose_name='Цвет роли (HEX)')
    icon = models.CharField(max_length=50, default='fas fa-user', verbose_name='Иконка роли')
    
    # Разрешения
    can_create_documents = models.BooleanField(default=False, verbose_name='Может создавать документы')
    can_edit_documents = models.BooleanField(default=False, verbose_name='Может редактировать документы')
    can_delete_documents = models.BooleanField(default=False, verbose_name='Может удалять документы')
    can_share_documents = models.BooleanField(default=False, verbose_name='Может делиться документами')
    
    can_create_processes = models.BooleanField(default=False, verbose_name='Может создавать процессы')
    can_edit_processes = models.BooleanField(default=False, verbose_name='Может редактировать процессы')
    can_delete_processes = models.BooleanField(default=False, verbose_name='Может удалять процессы')
    can_manage_processes = models.BooleanField(default=False, verbose_name='Может управлять процессами')
    
    can_create_tasks = models.BooleanField(default=False, verbose_name='Может создавать задачи')
    can_edit_tasks = models.BooleanField(default=False, verbose_name='Может редактировать задачи')
    can_delete_tasks = models.BooleanField(default=False, verbose_name='Может удалять задачи')
    can_assign_tasks = models.BooleanField(default=False, verbose_name='Может назначать задачи')
    
    can_manage_users = models.BooleanField(default=False, verbose_name='Может управлять пользователями')
    can_view_analytics = models.BooleanField(default=False, verbose_name='Может просматривать аналитику')
    can_manage_roles = models.BooleanField(default=False, verbose_name='Может управлять ролями')
    
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['display_name']
    
    def __str__(self):
        return self.display_name
    
    def get_permissions(self):
        """
        Возвращает список всех разрешений роли
        """
        permissions = []
        if self.can_create_documents:
            permissions.append('create_documents')
        if self.can_edit_documents:
            permissions.append('edit_documents')
        if self.can_delete_documents:
            permissions.append('delete_documents')
        if self.can_share_documents:
            permissions.append('share_documents')
        if self.can_create_processes:
            permissions.append('create_processes')
        if self.can_edit_processes:
            permissions.append('edit_processes')
        if self.can_delete_processes:
            permissions.append('delete_processes')
        if self.can_manage_processes:
            permissions.append('manage_processes')
        if self.can_create_tasks:
            permissions.append('create_tasks')
        if self.can_edit_tasks:
            permissions.append('edit_tasks')
        if self.can_delete_tasks:
            permissions.append('delete_tasks')
        if self.can_assign_tasks:
            permissions.append('assign_tasks')
        if self.can_manage_users:
            permissions.append('manage_users')
        if self.can_view_analytics:
            permissions.append('view_analytics')
        if self.can_manage_roles:
            permissions.append('manage_roles')
        return permissions

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    position = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # Поле для загрузки файлов
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users', verbose_name='Роль')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP последнего входа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания профиля')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления профиля')
    
    def __str__(self):
        return self.user.username
    
    def has_permission(self, permission):
        """
        Проверяет, есть ли у пользователя определенное разрешение
        """
        if not self.role or not self.role.is_active:
            return False
        
        role_permissions = self.role.get_permissions()
        return permission in role_permissions
    
    def has_any_permission(self, permissions):
        """
        Проверяет, есть ли у пользователя хотя бы одно из разрешений
        """
        if not self.role or not self.role.is_active:
            return False
        
        role_permissions = self.role.get_permissions()
        return any(permission in role_permissions for permission in permissions)
    
    def get_role_display(self):
        """
        Возвращает отображаемое название роли
        """
        return self.role.display_name if self.role else 'Без роли'
    
    def get_role_color(self):
        """
        Возвращает цвет роли
        """
        return self.role.color if self.role else '#6c757d'
    
    def get_role_icon(self):
        """
        Возвращает иконку роли
        """
        return self.role.icon if self.role else 'fas fa-user'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль пользователя при создании нового пользователя"""
    if created:
        # Получаем роль по умолчанию (сотрудник)
        default_role = Role.objects.filter(name='employee').first()
        UserProfile.objects.create(user=instance, role=default_role)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль пользователя при сохранении пользователя"""
    instance.profile.save()

class Document(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    created = models.DateField()
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    file_type = models.CharField(max_length=10, null=True, blank=True)  # doc, docx, pdf
    content = CKEditor5Field(null=True, blank=True, config_name='default')  # Для хранения форматированного текста с возможностью загрузки файлов
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    
    # Поля для подписи и печати
    signature = models.TextField(null=True, blank=True, verbose_name='Подпись (base64)')
    signature_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата подписи')
    signed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='signed_documents', verbose_name='Подписант')
    
    digital_stamp = models.TextField(null=True, blank=True, verbose_name='Электронная печать (base64)')
    stamp_data = models.JSONField(null=True, blank=True, verbose_name='Данные печати')
    stamp_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата проставления печати')
    stamped_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stamped_documents', verbose_name='Кто проставил печать')

    def __str__(self):
        return self.name
    
    def is_signed(self):
        """Проверяет, подписан ли документ"""
        return self.signature is not None and self.signature.strip() != ''
    
    def is_stamped(self):
        """Проверяет, проставлена ли печать на документе"""
        return self.digital_stamp is not None and self.digital_stamp.strip() != ''
    
    def is_approved(self):
        """Проверяет, утвержден ли документ (подписан или проставлена печать)"""
        return self.is_signed() or self.is_stamped()
    
    def get_signature_info(self):
        """Возвращает информацию о подписи"""
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"=== Проверка подписи для документа {self.id} ===")
        logger.error(f"self.signature существует: {self.signature is not None}")
        logger.error(f"self.signature не пустое: {bool(self.signature and self.signature.strip())}")
        logger.error(f"is_signed() возвращает: {self.is_signed()}")
        
        if self.is_signed():
            logger.error(f"=== Получение информации о подписи для документа {self.id} ===")
            logger.error(f"Длина данных подписи: {len(self.signature) if self.signature else 0}")
            logger.error(f"Начало данных подписи: {self.signature[:100] if self.signature else 'None'}")
            
            result = {
                'signed_by': self.signed_by.get_full_name() if self.signed_by else 'Неизвестно',
                'signature_date': self.signature_date,
                'signature': self.signature,  # Добавляем base64 данные подписи
                'has_signature': True
            }
            logger.error(f"=== Длина возвращаемой подписи: {len(result.get('signature', '')) if result.get('signature') else 0} ===")
            return result
        logger.error(f"=== Документ {self.id} НЕ подписан ===")
        return {'has_signature': False}
    
    def get_stamp_info(self):
        """Возвращает информацию о печати"""
        if self.is_stamped():
            return {
                'stamped_by': self.stamped_by.get_full_name() if self.stamped_by else 'Неизвестно',
                'stamp_date': self.stamp_date,
                'stamp_data': self.stamp_data,
                'stamp': self.digital_stamp,  # Добавляем base64 данные печати
                'has_stamp': True
            }
        return {'has_stamp': False}


class DocumentHistory(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='history')
    content = CKEditor5Field(null=True, blank=True, config_name='default')  # Копия содержимого документа
    created_at = models.DateTimeField(default=timezone.now)  # Дата и время создания версии
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_history')
    version_name = models.CharField(max_length=100, blank=True, null=True)  # Опциональное название версии
    
    class Meta:
        ordering = ['-created_at']  # Сортировка по убыванию даты создания
        verbose_name = 'История документа'
        verbose_name_plural = 'История документов'
    
    def __str__(self):
        return f'Версия {self.document.name} от {self.created_at.strftime("%d.%m.%Y %H:%M")}'


class DocumentAccess(models.Model):
    ACCESS_LEVELS = (
        ('read', 'Чтение'),
        ('write', 'Редактирование'),
        ('admin', 'Администратор'),
    )
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='access_permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_access')
    access_level = models.CharField(max_length=10, choices=ACCESS_LEVELS, default='read')
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_access')
    granted_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('document', 'user')  # Один пользователь может иметь только один уровень доступа к документу
        verbose_name = 'Доступ к документу'
        verbose_name_plural = 'Доступы к документам'
    
    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.document.name} ({self.get_access_level_display()})'


class BpmnAccess(models.Model):
    ACCESS_LEVELS = (
        ('view', 'Просмотр'),
        ('edit', 'Редактирование'),
        ('admin', 'Администратор'),
    )
    
    diagram = models.ForeignKey('BpmnDiagram', on_delete=models.CASCADE, related_name='access_permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bpmn_access')
    access_level = models.CharField(max_length=10, choices=ACCESS_LEVELS, default='view')
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_bpmn_access')
    granted_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('diagram', 'user')  # Один пользователь может иметь только один уровень доступа к диаграмме
        verbose_name = 'Доступ к BPMN диаграмме'
        verbose_name_plural = 'Доступы к BPMN диаграммам'
    
    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.diagram.name} ({self.get_access_level_display()})'


class Process(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20)
    progress = models.IntegerField()
    participants = models.IntegerField()
    deadline = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processes')

    class Meta:
        db_table = 'processes'  # Указываем существующее имя таблицы

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    deadline = models.DateField()
    assignee = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    class Meta:
        db_table = 'tasks'  # Указываем существующее имя таблицы

    def __str__(self):
        return self.title

class BpmnDiagram(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    xml = models.TextField()  # Хранение BPMN XML
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bpmn_diagrams')
    process = models.ForeignKey('Process', on_delete=models.CASCADE, related_name='bpmn_diagrams', blank=True, null=True)
    
    class Meta:
        verbose_name = 'BPMN диаграмма'
        verbose_name_plural = 'BPMN диаграммы'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class Notification(models.Model):
    """
    Модель уведомлений для пользователей системы
    """
    NOTIFICATION_TYPES = [
        ('info', 'Информационное'),
        ('warning', 'Предупреждение'),
        ('task', 'Задача'),
        ('document', 'Документ'),
        ('process', 'Процесс'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='Пользователь')
    title = models.CharField(max_length=255, default='Уведомление', verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info', verbose_name='Тип уведомления')
    priority = models.CharField(max_length=10, choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий')], default='medium', verbose_name='Приоритет')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    is_archived = models.BooleanField(default=False, verbose_name='Архивировано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    link = models.URLField(blank=True, null=True, verbose_name='Ссылка')
    
    # Дополнительные поля для связи с объектами
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name='Связанный документ')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name='Связанная задача')
    process = models.ForeignKey(Process, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name='Связанный процесс')
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.message[:50]}...'
    
    def mark_as_read(self):
        """Помечает уведомление как прочитанное"""
        self.is_read = True
        self.save(update_fields=['is_read'])
    
    def get_icon(self):
        """Возвращает иконку для типа уведомления"""
        icons = {
            'info': 'fas fa-info-circle',
            'warning': 'fas fa-exclamation-triangle',
            'task': 'fas fa-tasks',
            'document': 'fas fa-file-alt',
            'process': 'fas fa-cogs',
        }
        return icons.get(self.type, 'fas fa-bell')
    
    def get_color(self):
        """Возвращает цвет для типа уведомления"""
        colors = {
            'info': 'text-info',
            'warning': 'text-warning',
            'task': 'text-primary',
            'document': 'text-success',
            'process': 'text-secondary',
        }
        return colors.get(self.type, 'text-muted')


# Сигналы для автоматического создания уведомлений
def create_notification(user=None, user_id=None, message=None, notification_type='info', link=None, document=None, task=None, process=None, title=None, document_id=None, task_id=None, process_id=None):
    """
    Создает уведомление для пользователя
    """
    try:
        # Получаем пользователя по ID, если передан user_id
        if user_id and not user:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.error(f"Пользователь с ID {user_id} не найден")
                return None
        
        if not user:
            logger.error("Не указан пользователь для уведомления")
            return None
        
        # Генерируем заголовок на основе типа уведомления, если не указан
        if not title:
            if notification_type == 'document':
                title = 'Документ'
            elif notification_type == 'task':
                title = 'Задача'
            elif notification_type == 'process':
                title = 'Процесс'
            elif notification_type == 'warning':
                title = 'Предупреждение'
            else:
                title = 'Уведомление'
        
        # Получаем объекты по ID, если переданы ID
        if document_id and not document:
            try:
                document = Document.objects.get(id=document_id)
            except Document.DoesNotExist:
                logger.warning(f"Документ с ID {document_id} не найден")
                document = None
        
        if task_id and not task:
            try:
                task = Task.objects.get(id=task_id)
            except Task.DoesNotExist:
                logger.warning(f"Задача с ID {task_id} не найдена")
                task = None
        
        if process_id and not process:
            try:
                process = Process.objects.get(id=process_id)
            except Process.DoesNotExist:
                logger.warning(f"Процесс с ID {process_id} не найден")
                process = None
        
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=notification_type,
            link=link,
            document=document,
            task=task,
            process=process
        )
        
        # Отправляем real-time уведомление через WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'notifications_{user.id}',
                {
                    'type': 'notification_message',
                    'notification': {
                        'id': notification.id,
                        'message': notification.message,
                        'type': notification.type,
                        'is_read': notification.is_read,
                        'created_at': notification.created_at.isoformat(),
                        'link': notification.link,
                        'icon': notification.get_icon(),
                        'color': notification.get_color(),
                    }
                }
            )
        
        logger.info(f"Создано уведомление для пользователя {user.username}: {message}")
        return notification
    except Exception as e:
        logger.error(f"Ошибка при создании уведомления: {e}")
        return None


@receiver(post_save, sender=Document)
def document_notification(sender, instance, created, **kwargs):
    """Создает уведомления при создании/обновлении документа"""
    try:
        if created:
            # Уведомление для создателя документа
            message = f"Документ '{instance.name}' создан"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='document',
                link=f"/documents/{instance.id}/edit",
                document=instance
            )
            
            # Уведомления для пользователей с доступом к документу
            access_users = User.objects.filter(
                document_access__document=instance
            ).exclude(id=instance.user.id).distinct()
            
            for user in access_users:
                message = f"Вам предоставлен доступ к документу '{instance.name}'"
                create_notification(
                    user=user,
                    message=message,
                    notification_type='document',
                    link=f"/documents/{instance.id}/edit",
                    document=instance
                )
        else:
            # Уведомление об обновлении документа
            message = f"Документ '{instance.name}' обновлен"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='document',
                link=f"/documents/{instance.id}/edit",
                document=instance
            )
            
            # Уведомления для пользователей с доступом к документу
            access_users = User.objects.filter(
                document_access__document=instance
            ).exclude(id=instance.user.id).distinct()
            
            for user in access_users:
                message = f"Документ '{instance.name}' был обновлен"
                create_notification(
                    user=user,
                    message=message,
                    notification_type='document',
                    link=f"/documents/{instance.id}/edit",
                    document=instance
                )
    except Exception as e:
        logger.error(f"Ошибка при создании уведомления для документа: {e}")


@receiver(post_save, sender=Task)
def task_notification(sender, instance, created, **kwargs):
    """Создает уведомления при создании/обновлении задачи"""
    try:
        if created:
            # Уведомление для создателя задачи
            message = f"Задача '{instance.title}' создана"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='task',
                link=f"/tasks/{instance.id}/edit",
                task=instance
            )
            
            # Уведомление для исполнителя задачи (если указан)
            if instance.assignee:
                try:
                    assignee_user = User.objects.get(username=instance.assignee)
                    if assignee_user != instance.user:
                        message = f"Вам назначена задача '{instance.title}'"
                        create_notification(
                            user=assignee_user,
                            message=message,
                            notification_type='task',
                            link=f"/tasks/{instance.id}/edit",
                            task=instance
                        )
                except User.DoesNotExist:
                    logger.warning(f"Пользователь {instance.assignee} не найден для задачи {instance.id}")
        else:
            # Уведомление об обновлении задачи
            message = f"Задача '{instance.title}' обновлена"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='task',
                link=f"/tasks/{instance.id}/edit",
                task=instance
            )
            
            # Уведомление для исполнителя задачи
            if instance.assignee:
                try:
                    assignee_user = User.objects.get(username=instance.assignee)
                    if assignee_user != instance.user:
                        message = f"Задача '{instance.title}' была обновлена"
                        create_notification(
                            user=assignee_user,
                            message=message,
                            notification_type='task',
                            link=f"/tasks/{instance.id}/edit",
                            task=instance
                        )
                except User.DoesNotExist:
                    logger.warning(f"Пользователь {instance.assignee} не найден для задачи {instance.id}")
    except Exception as e:
        logger.error(f"Ошибка при создании уведомления для задачи: {e}")


@receiver(post_save, sender=Process)
def process_notification(sender, instance, created, **kwargs):
    """Создает уведомления при создании/обновлении процесса"""
    try:
        if created:
            # Уведомление для создателя процесса
            message = f"Процесс '{instance.name}' создан"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='process',
                link=f"/processes/{instance.id}/edit",
                process=instance
            )
        else:
            # Уведомление об обновлении процесса
            message = f"Процесс '{instance.name}' обновлен"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='process',
                link=f"/processes/{instance.id}/edit",
                process=instance
            )
    except Exception as e:
        logger.error(f"Ошибка при создании уведомления для процесса: {e}")


@receiver(post_save, sender=BpmnDiagram)
def bpmn_diagram_notification(sender, instance, created, **kwargs):
    """Создает уведомления при создании/обновлении BPMN диаграммы"""
    try:
        if created:
            message = f"BPMN диаграмма '{instance.name}' создана"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='process',
                link=f"/processes/{instance.process.id}/edit" if instance.process else f"/bpmn/{instance.id}/edit",
                process=instance.process
            )
        else:
            message = f"BPMN диаграмма '{instance.name}' обновлена"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='process',
                link=f"/processes/{instance.process.id}/edit" if instance.process else f"/bpmn/{instance.id}/edit",
                process=instance.process
            )
    except Exception as e:
        logger.error(f"Ошибка при создании уведомления для BPMN диаграммы: {e}")


@receiver(post_save, sender=DocumentAccess)
def document_access_notification(sender, instance, created, **kwargs):
    """Создает уведомления при выдаче доступа к документу"""
    try:
        if created:
            # Уведомление для пользователя, которому выдан доступ
            message = f"Вам предоставлен доступ к документу '{instance.document.name}' ({instance.get_access_level_display()})"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='document',
                link=f"/documents/{instance.document.id}/edit",
                document=instance.document
            )
            
            # Уведомление для владельца документа о том, что доступ выдан
            if instance.document.user != instance.user:
                message = f"Пользователю {instance.user.get_full_name() or instance.user.username} предоставлен доступ к документу '{instance.document.name}' ({instance.get_access_level_display()})"
                create_notification(
                    user=instance.document.user,
                    message=message,
                    notification_type='info',
                    link=f"/documents/{instance.document.id}/edit",
                    document=instance.document
                )
        else:
            # Уведомление об изменении уровня доступа
            message = f"Уровень доступа к документу '{instance.document.name}' изменен на {instance.get_access_level_display()}"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='info',
                link=f"/documents/{instance.document.id}/edit",
                document=instance.document
            )
    except Exception as e:
        logger.error(f"Ошибка при создании уведомления для доступа к документу: {e}")


@receiver(post_save, sender=BpmnAccess)
def bpmn_access_notification(sender, instance, created, **kwargs):
    """Создает уведомления при выдаче доступа к BPMN диаграмме"""
    try:
        if created:
            # Уведомление для пользователя, которому выдан доступ
            message = f"Вам предоставлен доступ к BPMN диаграмме '{instance.diagram.name}' ({instance.get_access_level_display()})"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='process',
                link=f"/bpmn/{instance.diagram.id}/edit",
                process=instance.diagram.process
            )
            
            # Уведомление для владельца диаграммы о том, что доступ выдан
            if instance.diagram.user != instance.user:
                message = f"Пользователю {instance.user.get_full_name() or instance.user.username} предоставлен доступ к BPMN диаграмме '{instance.diagram.name}' ({instance.get_access_level_display()})"
                create_notification(
                    user=instance.diagram.user,
                    message=message,
                    notification_type='info',
                    link=f"/bpmn/{instance.diagram.id}/edit",
                    process=instance.diagram.process
                )
        else:
            # Уведомление об изменении уровня доступа
            message = f"Уровень доступа к BPMN диаграмме '{instance.diagram.name}' изменен на {instance.get_access_level_display()}"
            create_notification(
                user=instance.user,
                message=message,
                notification_type='info',
                link=f"/bpmn/{instance.diagram.id}/edit",
                process=instance.diagram.process
            )
    except Exception as e:
        logger.error(f"Ошибка при создании уведомления для доступа к BPMN диаграмме: {e}")


@receiver(pre_delete, sender=DocumentAccess)
def document_access_removed_notification(sender, instance, **kwargs):
    """Создает уведомления при удалении доступа к документу"""
    try:
        # Сохраняем данные до удаления объекта
        user_id = instance.user.id
        user_name = instance.user.get_full_name() or instance.user.username
        document_id = instance.document.id
        document_name = instance.document.name
        document_owner_id = instance.document.user.id
        
        # Уведомление для пользователя, у которого отозван доступ
        message = f"Доступ к документу '{document_name}' отозван"
        create_notification(
            user_id=user_id,
            message=message,
            notification_type='warning',
            link=f"/documents/{document_id}/edit"
            # Не передаем document_id, чтобы избежать ссылки на удаляемый объект
        )
        
        # Уведомление для владельца документа о том, что доступ отозван
        if document_owner_id != user_id:
            message = f"Доступ пользователя {user_name} к документу '{document_name}' отозван"
            create_notification(
                user_id=document_owner_id,
                message=message,
                notification_type='info',
                link=f"/documents/{document_id}/edit"
                # Не передаем document_id, чтобы избежать ссылки на удаляемый объект
            )
    except Exception as e:
        logger.error(f"Ошибка при создании уведомления об отзыве доступа к документу: {e}")


@receiver(pre_delete, sender=BpmnAccess)
def bpmn_access_removed_notification(sender, instance, **kwargs):
    """Создает уведомления при удалении доступа к BPMN диаграмме"""
    try:
        # Сохраняем данные до удаления объекта
        user_id = instance.user.id
        user_name = instance.user.get_full_name() or instance.user.username
        process_id = instance.diagram.process.id
        process_name = instance.diagram.name
        process_owner_id = instance.diagram.user.id
        
        # Уведомление для пользователя, у которого отозван доступ
        message = f"Доступ к BPMN диаграмме '{process_name}' отозван"
        create_notification(
            user_id=user_id,
            message=message,
            notification_type='warning',
            link=f"/processes/{process_id}/edit"
            # Не передаем process_id, чтобы избежать ссылки на удаляемый объект
        )
        
        # Уведомление для владельца диаграммы о том, что доступ отозван
        if process_owner_id != user_id:
            message = f"Доступ пользователя {user_name} к BPMN диаграмме '{process_name}' отозван"
            create_notification(
                user_id=process_owner_id,
                message=message,
                notification_type='info',
                link=f"/processes/{process_id}/edit"
                # Не передаем process_id, чтобы избежать ссылки на удаляемый объект
            )
    except Exception as e:
        logger.error(f"Ошибка при создании уведомления об отзыве доступа к BPMN диаграмме: {e}")