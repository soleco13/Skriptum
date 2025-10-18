from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone

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

    class Meta:
        db_table = 'documents'  # Указываем существующее имя таблицы

    def __str__(self):
        return self.name


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