from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    position = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)  # URL к аватару
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль пользователя при создании нового пользователя"""
    if created:
        UserProfile.objects.create(user=instance)

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
    
    class Meta:
        verbose_name = 'BPMN диаграмма'
        verbose_name_plural = 'BPMN диаграммы'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name