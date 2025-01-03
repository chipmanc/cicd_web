# Generated by Django 4.2.11 on 2024-09-28 22:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_stage_pipeline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stage',
            name='pipeline',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='stages', to='api.pipeline'),
        ),
        migrations.AlterField(
            model_name='task',
            name='stage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='api.stage'),
        ),
        migrations.AlterUniqueTogether(
            name='stage',
            unique_together={('name', 'project')},
        ),
    ]
