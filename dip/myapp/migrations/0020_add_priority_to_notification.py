# Generated manually to add priority field to notification table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_add_title_to_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='priority',
            field=models.CharField(choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий')], default='medium', max_length=10, verbose_name='Приоритет'),
        ),
    ]
