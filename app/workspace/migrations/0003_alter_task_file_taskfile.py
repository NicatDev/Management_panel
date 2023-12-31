# Generated by Django 4.1.3 on 2023-03-09 09:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0002_alter_status_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='task_files', verbose_name='file'),
        ),
        migrations.CreateModel(
            name='TaskFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated date')),
                ('file', models.FileField(upload_to='files/task/', verbose_name='file')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='workspace.task')),
            ],
            options={
                'verbose_name': 'Task File',
                'verbose_name_plural': 'Task Files',
            },
        ),
    ]
