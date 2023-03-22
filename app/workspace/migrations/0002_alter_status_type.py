# Generated by Django 4.1.3 on 2023-02-28 07:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('workspace', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='type',
            field=models.ForeignKey(limit_choices_to={'app_label__in': ['workspace', 'account'], 'model__in': ['task', 'instagram']}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contenttypes.contenttype', verbose_name='Statusun Tipi'),
        ),
    ]
