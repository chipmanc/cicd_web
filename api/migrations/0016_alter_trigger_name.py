# Generated by Django 4.2.11 on 2024-11-03 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_remove_scmpoll_repo_remove_scmwebhook_repo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trigger',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]