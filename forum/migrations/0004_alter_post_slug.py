# Generated by Django 4.1.1 on 2022-12-07 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_alter_author_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(blank=True, max_length=430, null=True, unique=True),
        ),
    ]
