# Generated by Django 4.2.11 on 2024-12-14 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_alter_trigger_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='git',
            options={'verbose_name_plural': 'Git'},
        ),
        migrations.AddField(
            model_name='git',
            name='ref',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
