# Generated by Django 4.2.1 on 2023-05-22 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_rename_user_tguser'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tguser',
            old_name='user_name',
            new_name='user_username',
        ),
        migrations.RemoveField(
            model_name='tguser',
            name='user_number',
        ),
        migrations.AddField(
            model_name='tguser',
            name='user_first_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='tguser',
            name='user_last_name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]