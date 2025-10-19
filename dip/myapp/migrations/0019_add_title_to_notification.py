# Generated manually to add title field to notification table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0018_add_process_id_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(max_length=255, default='Уведомление', verbose_name='Заголовок'),
        ),
    ]
