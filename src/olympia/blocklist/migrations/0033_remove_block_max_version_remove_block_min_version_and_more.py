# Generated by Django 4.2.16 on 2024-09-20 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blocklist', '0032_alter_blocklistsubmission_reason_url_null_true'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='block',
            name='max_version',
        ),
        migrations.RemoveField(
            model_name='block',
            name='min_version',
        ),
        migrations.RemoveField(
            model_name='blocklistsubmission',
            name='max_version',
        ),
        migrations.RemoveField(
            model_name='blocklistsubmission',
            name='min_version',
        ),
        migrations.AddField(
            model_name='blockversion',
            name='hard',
            field=models.BooleanField(default=True),
        ),
    ]
