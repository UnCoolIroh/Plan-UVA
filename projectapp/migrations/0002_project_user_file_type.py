# Generated by Django 4.2.16 on 2024-10-21 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project_user',
            name='file_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]