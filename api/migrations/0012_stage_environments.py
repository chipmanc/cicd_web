# Generated by Django 4.2.11 on 2024-09-29 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_remove_stage_pipeline_pipeline_stages'),
    ]

    operations = [
        migrations.AddField(
            model_name='stage',
            name='environments',
            field=models.ManyToManyField(to='api.environment'),
        ),
    ]
