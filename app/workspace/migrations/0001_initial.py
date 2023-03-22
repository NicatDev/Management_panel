# Generated by Django 4.1.3 on 2023-02-27 08:30

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import workspace.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountThrough',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated date')),
                ('type', models.IntegerField(choices=[(1, 'Admin'), (2, 'Member'), (3, 'Client')], default=1)),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workspace', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Account Through',
                'verbose_name_plural': 'Account Through',
            },
        ),
        migrations.CreateModel(
            name='Deadline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated date')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deadlines', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Deadline',
                'verbose_name_plural': 'Deadlines',
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated date')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='name')),
                ('order', models.IntegerField(default=0, verbose_name='order')),
                ('level', models.CharField(choices=[('base', 'Base Level'), ('neutral', 'Neutral Level'), ('work_on', 'Working on it'), ('final', 'Final level'), ('deleted', 'Deleted')], default='neutral', max_length=10, verbose_name='Səviyyə')),
                ('extra', models.JSONField(blank=True, null=True, verbose_name='extra')),
                ('next_step', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='previous_steps', to='workspace.status', verbose_name='Next step')),
                ('type', models.ForeignKey(limit_choices_to={'app_label': 'workspace', 'model__in': ['task']}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contenttypes.contenttype', verbose_name='Statusun Tipi')),
            ],
            options={
                'verbose_name': 'Status',
                'verbose_name_plural': 'Statuses',
                'ordering': ('order',),
            },
            bases=(models.Model, workspace.mixins.JSONFieldModelMixin),
        ),
        migrations.CreateModel(
            name='WorkSpace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated date')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True, verbose_name='slug')),
                ('account', models.ManyToManyField(related_name='workspaces', through='workspace.AccountThrough', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'WorkSpace',
                'verbose_name_plural': 'WorkSpaces',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated date')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('text', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='sharing text')),
                ('file', models.FileField(blank=True, null=True, upload_to='files/task/<built-in function id>', verbose_name='file')),
                ('sharing_type', models.IntegerField(choices=[(1, 'Image'), (2, 'Video'), (3, 'other')], default=1, verbose_name='sharing type')),
                ('deadline', models.DateTimeField(blank=True, null=True, verbose_name='deadline')),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True, verbose_name='slug')),
                ('assignee', models.ManyToManyField(blank=True, related_name='assigned_tasks', through='workspace.Deadline', to=settings.AUTH_USER_MODEL, verbose_name='assignee')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_tasks', to=settings.AUTH_USER_MODEL, verbose_name='client')),
                ('sharing_platform', models.ManyToManyField(blank=True, related_name='used_in_tasks', to='account.socialplatform', verbose_name='sharing platform')),
                ('status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='tasks', to='workspace.status', verbose_name='Status')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='workspace.workspace')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
            },
            bases=(models.Model, workspace.mixins.StatusNotifyEventFinder),
        ),
        migrations.AddField(
            model_name='deadline',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='deadlines', to='workspace.status'),
        ),
        migrations.AddField(
            model_name='deadline',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deadlines', to='workspace.task'),
        ),
        migrations.AddField(
            model_name='accountthrough',
            name='workspace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accounts', to='workspace.workspace'),
        ),
    ]
