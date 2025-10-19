# Generated manually to fix missing fields in notification table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0014_add_notification_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='link',
            field=models.URLField(blank=True, null=True, verbose_name='Ссылка'),
        ),
        migrations.AddField(
            model_name='notification',
            name='document',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='notifications', to='myapp.document', verbose_name='Связанный документ'),
        ),
        migrations.AddField(
            model_name='notification',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='notifications', to='myapp.task', verbose_name='Связанная задача'),
        ),
        migrations.AddField(
            model_name='notification',
            name='process',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='notifications', to='myapp.process', verbose_name='Связанный процесс'),
        ),
    ]
