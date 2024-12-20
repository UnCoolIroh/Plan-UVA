# Generated by Django 4.2.16 on 2024-11-27 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectapp', '0012_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='weight',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
