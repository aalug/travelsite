# Generated by Django 4.1.1 on 2022-10-04 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_userprofile_info_font_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageToStaff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('content', models.TextField()),
            ],
        ),
    ]
