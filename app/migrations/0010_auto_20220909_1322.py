# Generated by Django 3.2.15 on 2022-09-09 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_slot_lastgames'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slot',
            name='bbchance',
            field=models.CharField(max_length=10, null=True, verbose_name='BB確率'),
        ),
        migrations.AlterField(
            model_name='slot',
            name='rbchance',
            field=models.CharField(max_length=10, null=True, verbose_name='RB確率'),
        ),
    ]
