# Generated by Django 3.2.15 on 2022-09-06 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pachislotstore',
            name='ttt',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='メmmm'),
        ),
    ]
