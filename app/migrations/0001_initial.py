# Generated by Django 3.2.15 on 2022-09-06 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='PachiSlotStore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='店舗名')),
                ('memo', models.CharField(blank=True, max_length=100, null=True, verbose_name='メモ')),
            ],
            options={
                'verbose_name_plural': '店舗',
            },
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='機種名')),
                ('number', models.IntegerField(verbose_name='台番号')),
                ('bigbonus', models.IntegerField(verbose_name='BB')),
                ('regularbonus', models.IntegerField(verbose_name='RB')),
                ('count', models.IntegerField(verbose_name='総回転数')),
                ('bbchance', models.CharField(max_length=10, verbose_name='BB確率')),
                ('rbchance', models.CharField(max_length=10, verbose_name='RB確率')),
                ('lastgames', models.IntegerField(verbose_name='宵越し')),
                ('payout', models.IntegerField(verbose_name='差枚数')),
                ('memo', models.CharField(blank=True, max_length=100, null=True, verbose_name='メモ')),
                ('date', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='app.businessday')),
            ],
        ),
        migrations.AddField(
            model_name='businessday',
            name='store_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='app.pachislotstore'),
        ),
    ]
