# Generated by Django 5.0.3 on 2024-03-18 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neticapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=100, null=True),
        ),
    ]
