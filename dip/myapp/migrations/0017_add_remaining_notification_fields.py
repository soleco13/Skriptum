# Generated manually to add remaining fields to notification table

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0016_add_link_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='myapp.document', verbose_name='Связанный документ'),
        ),
        migrations.AddField(
            model_name='notification',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='myapp.task', verbose_name='Связанная задача'),
        ),
        migrations.AddField(
            model_name='notification',
            name='process',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='myapp.process', verbose_name='Связанный процесс'),
        ),
    ]
