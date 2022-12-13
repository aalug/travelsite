# Generated by Django 4.1.1 on 2022-12-12 01:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0007_alter_post_categories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postcategory',
            name='slug',
            field=models.SlugField(help_text='format: letters, numbers, underscores or hyphens', max_length=150, null=True, unique=True, verbose_name='category safe URL'),
        ),
    ]