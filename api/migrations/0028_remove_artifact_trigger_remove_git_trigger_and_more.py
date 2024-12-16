# Generated by Django 4.2.11 on 2024-12-15 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('api', '0027_remove_trigger_stage_stage_trigger'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artifact',
            name='trigger',
        ),
        migrations.RemoveField(
            model_name='git',
            name='trigger',
        ),
        migrations.RemoveField(
            model_name='stage',
            name='trigger',
        ),
        migrations.AddField(
            model_name='stage',
            name='content_type',
            field=models.ForeignKey(default=24, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stage',
            name='object_id',
            field=models.PositiveIntegerField(default='1'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Trigger',
        ),
    ]