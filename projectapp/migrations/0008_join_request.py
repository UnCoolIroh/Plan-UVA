# Generated by Django 4.2.16 on 2024-11-03 01:55

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('projectapp', '0007_document_project_group_project_group_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='JoinRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('approved', models.BooleanField(default=False)),
                ('rejected', models.BooleanField(default=False)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_requests', to='projectapp.project_group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projectapp.project_user')),
            ],
        ),
    ]
