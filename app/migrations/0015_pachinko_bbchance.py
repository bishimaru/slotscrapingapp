# Generated by Django 3.2.15 on 2022-09-28 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_pachinko_game_1k'),
    ]

    operations = [
        migrations.AddField(
            model_name='pachinko',
            name='bbchance',
            field=models.CharField(max_length=10, null=True, verbose_name='当たり確率'),
        ),
    ]
