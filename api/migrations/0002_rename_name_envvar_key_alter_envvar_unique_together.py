# Generated by Django 4.2.11 on 2024-06-02 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='envvar',
            old_name='name',
            new_name='key',
        ),
        migrations.AlterUniqueTogether(
            name='envvar',
            unique_together={('key', 'environment')},
        ),
    ]