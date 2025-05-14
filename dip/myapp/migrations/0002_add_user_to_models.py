# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),  # Зависимость от миграции auth.User
        ('myapp', '0001_initial'),  # Зависимость от предыдущей миграции
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='documents',
                to='auth.user',
                default=1  # Устанавливаем значение по умолчанию для существующих записей
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='process',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='processes',
                to='auth.user',
                default=1  # Устанавливаем значение по умолчанию для существующих записей
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='tasks',
                to='auth.user',
                default=1  # Устанавливаем значение по умолчанию для существующих записей
            ),
            preserve_default=False,
        ),
    ]