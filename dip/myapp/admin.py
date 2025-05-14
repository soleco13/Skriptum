from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Document, Process, Task, UserProfile, DocumentHistory

# Регистрация моделей в админке
admin.site.register(Document)
admin.site.register(Process)
admin.site.register(Task)
admin.site.register(DocumentHistory)

# Определение встроенного представления для профиля пользователя
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'

# Определение нового класса UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Перерегистрация модели User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
