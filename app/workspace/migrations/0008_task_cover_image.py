# Generated by Django 4.1.3 on 2023-04-03 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0007_alter_action_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='task_cover_images', verbose_name='cover image'),
        ),
    ]