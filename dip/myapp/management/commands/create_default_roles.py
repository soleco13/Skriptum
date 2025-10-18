from django.core.management.base import BaseCommand
from myapp.models import Role


class Command(BaseCommand):
    help = 'Создает роли по умолчанию в системе'

    def handle(self, *args, **options):
        roles_data = [
            {
                'name': 'admin',
                'display_name': 'Администратор',
                'description': 'Полный доступ ко всем функциям системы',
                'color': '#dc3545',
                'icon': 'fas fa-crown',
                'can_create_documents': True,
                'can_edit_documents': True,
                'can_delete_documents': True,
                'can_share_documents': True,
                'can_create_processes': True,
                'can_edit_processes': True,
                'can_delete_processes': True,
                'can_manage_processes': True,
                'can_create_tasks': True,
                'can_edit_tasks': True,
                'can_delete_tasks': True,
                'can_assign_tasks': True,
                'can_manage_users': True,
                'can_view_analytics': True,
                'can_manage_roles': True,
            },
            {
                'name': 'manager',
                'display_name': 'Руководитель',
                'description': 'Управление командой и процессами',
                'color': '#007bff',
                'icon': 'fas fa-user-tie',
                'can_create_documents': True,
                'can_edit_documents': True,
                'can_delete_documents': True,
                'can_share_documents': True,
                'can_create_processes': True,
                'can_edit_processes': True,
                'can_delete_processes': True,
                'can_manage_processes': True,
                'can_create_tasks': True,
                'can_edit_tasks': True,
                'can_delete_tasks': True,
                'can_assign_tasks': True,
                'can_manage_users': False,
                'can_view_analytics': True,
                'can_manage_roles': False,
            },
            {
                'name': 'secretary',
                'display_name': 'Секретарь',
                'description': 'Работа с документами и координация процессов',
                'color': '#28a745',
                'icon': 'fas fa-user-secret',
                'can_create_documents': True,
                'can_edit_documents': True,
                'can_delete_documents': False,
                'can_share_documents': True,
                'can_create_processes': True,
                'can_edit_processes': True,
                'can_delete_processes': False,
                'can_manage_processes': False,
                'can_create_tasks': True,
                'can_edit_tasks': True,
                'can_delete_tasks': False,
                'can_assign_tasks': True,
                'can_manage_users': False,
                'can_view_analytics': False,
                'can_manage_roles': False,
            },
            {
                'name': 'employee',
                'display_name': 'Сотрудник',
                'description': 'Базовая роль для выполнения задач',
                'color': '#6c757d',
                'icon': 'fas fa-user',
                'can_create_documents': True,
                'can_edit_documents': True,
                'can_delete_documents': False,
                'can_share_documents': False,
                'can_create_processes': False,
                'can_edit_processes': False,
                'can_delete_processes': False,
                'can_manage_processes': False,
                'can_create_tasks': True,
                'can_edit_tasks': True,
                'can_delete_tasks': False,
                'can_assign_tasks': False,
                'can_manage_users': False,
                'can_view_analytics': False,
                'can_manage_roles': False,
            },
            {
                'name': 'viewer',
                'display_name': 'Наблюдатель',
                'description': 'Только просмотр документов и процессов',
                'color': '#17a2b8',
                'icon': 'fas fa-eye',
                'can_create_documents': False,
                'can_edit_documents': False,
                'can_delete_documents': False,
                'can_share_documents': False,
                'can_create_processes': False,
                'can_edit_processes': False,
                'can_delete_processes': False,
                'can_manage_processes': False,
                'can_create_tasks': False,
                'can_edit_tasks': False,
                'can_delete_tasks': False,
                'can_assign_tasks': False,
                'can_manage_users': False,
                'can_view_analytics': False,
                'can_manage_roles': False,
            }
        ]

        created_count = 0
        updated_count = 0

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создана роль: {role.display_name}')
                )
            else:
                # Обновляем существующую роль
                for key, value in role_data.items():
                    if key != 'name':
                        setattr(role, key, value)
                role.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Обновлена роль: {role.display_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nСоздано ролей: {created_count}\n'
                f'Обновлено ролей: {updated_count}\n'
                f'Всего ролей в системе: {Role.objects.count()}'
            )
        )
