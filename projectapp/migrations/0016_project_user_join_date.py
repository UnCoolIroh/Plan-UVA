# Generated by Django 4.2.16 on 2024-12-06 04:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('projectapp', '0015_document_file_alter_document_file_extension_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project_user',
            name='join_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
