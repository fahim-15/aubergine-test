# Generated by Django 2.0 on 2020-02-07 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_mgmt', '0002_gallerymaster_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallerymaster',
            name='thumbnail_url',
        ),
        migrations.AddField(
            model_name='gallerymaster',
            name='thumbnail_key',
            field=models.TextField(blank=True, null=True),
        ),
    ]
