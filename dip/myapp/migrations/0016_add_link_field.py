# Generated manually to add link field to notification table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0015_add_missing_notification_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='link',
            field=models.URLField(blank=True, null=True, verbose_name='Ссылка'),
        ),
    ]
