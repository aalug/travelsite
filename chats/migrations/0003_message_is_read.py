# Generated by Django 4.1.1 on 2022-10-09 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0002_rename_data_created_chatroom_date_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
