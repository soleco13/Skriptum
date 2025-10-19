# Generated manually to add is_archived field to notification table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_add_priority_to_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='is_archived',
            field=models.BooleanField(default=False, verbose_name='Архивировано'),
        ),
    ]
