# Generated by Django 5.2 on 2025-04-28 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance_app', '0020_insuranceproduct_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='petprofile',
            name='preference_dict',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
