from django.contrib.auth.models import User
from myapp.models import Role

# Получаем всех пользователей
users = User.objects.all()
print('Пользователи в системе:')
for user in users:
    print(f'- {user.username} (ID: {user.id})')

# Получаем роль администратора
admin_role = Role.objects.filter(name='admin').first()
print(f'\nРоль администратора: {admin_role}')

# Назначаем роль администратора первому пользователю
if users and admin_role:
    first_user = users[0]
    first_user.profile.role = admin_role
    first_user.profile.save()
    print(f'\nРоль администратора назначена пользователю {first_user.username}')
    print(f'Разрешения пользователя: {first_user.profile.role.get_permissions()}')
else:
    print('Не удалось назначить роль администратора')
