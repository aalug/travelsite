# Generated by Django 4.1.1 on 2022-10-04 18:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_messagetostaff_options_responsetouser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responsetouser',
            name='original_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.messagetostaff'),
        ),
        migrations.AlterField(
            model_name='responsetouser',
            name='staff_member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]