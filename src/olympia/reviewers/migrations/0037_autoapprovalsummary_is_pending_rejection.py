# Generated by Django 4.2.15 on 2024-08-22 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviewers', '0036_alter_needshumanreview_reason_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='autoapprovalsummary',
            name='is_pending_rejection',
            field=models.BooleanField(default=False, help_text='Is pending rejection'),
        ),
    ]
