from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_document_created_alter_document_content_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', CKEditor5Field(blank=True, config_name='default', null=True)),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('version_name', models.CharField(blank=True, max_length=100, null=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='myapp.document')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='document_history', to='auth.user')),
            ],
            options={
                'verbose_name': 'История документа',
                'verbose_name_plural': 'История документов',
                'ordering': ['-created_at'],
            },
        ),
    ]