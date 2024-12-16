# Generated by Django 4.2.11 on 2024-10-05 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_stage_environments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='repo',
            name='branch',
        ),
        migrations.RemoveField(
            model_name='repo',
            name='project',
        ),
        migrations.RemoveField(
            model_name='repo',
            name='shallow_clone',
        ),
        migrations.RemoveField(
            model_name='repo',
            name='user',
        ),
        migrations.RemoveField(
            model_name='repo',
            name='webhook_secret',
        ),
        migrations.AlterField(
            model_name='repo',
            name='fetch',
            field=models.CharField(choices=[('poll', 'Poll'), ('webhook', 'Webhook')], default='poll', max_length=15),
        ),
        migrations.CreateModel(
            name='Trigger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('trigger_type', models.CharField(choices=[('artifact', 'Artifact'), ('git', 'Git'), ('manual', 'Manual'), ('secret', 'Secret')], max_length=25)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='triggers', to='api.project')),
            ],
        ),
        migrations.CreateModel(
            name='ScmWebhook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.repo')),
            ],
        ),
        migrations.CreateModel(
            name='ScmPoll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(default='master', max_length=255)),
                ('shallow_clone', models.BooleanField(default=False)),
                ('user', models.CharField(max_length=50)),
                ('webhook_secret', models.CharField(blank=True, max_length=255, null=True)),
                ('repo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.repo')),
            ],
        ),
        migrations.AddField(
            model_name='repo',
            name='trigger',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='repo', to='api.trigger'),
            preserve_default=False,
        ),
    ]