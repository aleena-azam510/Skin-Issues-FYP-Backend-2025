# Generated by Django 5.1.5 on 2025-07-06 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0011_skincondition_page_prevention_summary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='skincondition_page',
            name='prevention_image',
        ),
        migrations.AddField(
            model_name='skincondition_page',
            name='prevention_card_image',
            field=models.ImageField(blank=True, null=True, upload_to='skin_conditions/card_images/prevention/'),
        ),
    ]
