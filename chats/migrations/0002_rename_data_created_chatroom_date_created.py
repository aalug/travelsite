# Generated by Django 4.1.1 on 2022-10-09 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatroom',
            old_name='data_created',
            new_name='date_created',
        ),
    ]
