# Generated manually to add process_id field to notification table

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_add_remaining_notification_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='process',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='myapp.process', verbose_name='Связанный процесс'),
        ),
    ]
