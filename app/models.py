from django.db import models

# Create your models here.

class PachiSlotStore(models.Model):
    class Meta:
          verbose_name_plural = '店舗'

    name = models.CharField(max_length=100, verbose_name='店舗名')
    memo = models.CharField(max_length=100, verbose_name='メモ', blank=True, null=True)

    def __str__(self):
          return self.name

class BusinessDay(models.Model):
    class Meta:
          verbose_name_plural = '営業日'
    date = models.DateField()
    store_name = models.ForeignKey(PachiSlotStore, on_delete=models.DO_NOTHING)
    total_pay = models.IntegerField(verbose_name='総差枚数', null=True)
    total_pay_pachinko = models.IntegerField(verbose_name='総出玉数', null=True)


#     def __str__(self):
#         return self.date

class SlotTitle(models.Model):
      class Meta:
          verbose_name_plural = '機種名'
      date = models.ForeignKey(BusinessDay, on_delete=models.DO_NOTHING, related_name="slot_title")
      name = models.CharField(max_length=100, verbose_name='機種名')
      numbers = models.IntegerField(verbose_name='台数', null=True)
      memo = models.CharField(max_length=100, verbose_name='メモ', blank=True, null=True)

      def __str__(self):
        return self.name

class Slot(models.Model):
    class Meta:
          verbose_name_plural = '台データ'
    name = models.CharField(max_length=100, verbose_name='機種名')
    date = models.ForeignKey(BusinessDay, on_delete=models.DO_NOTHING)
    number = models.IntegerField(verbose_name='台番号')
    bigbonus = models.IntegerField(verbose_name='BB')
    regularbonus = models.IntegerField(verbose_name='RB')
    count = models.IntegerField(verbose_name='総回転数')
    bbchance = models.CharField(max_length=10, verbose_name='BB確率', null=True)
    rbchance = models.CharField(max_length=10, verbose_name='RB確率', null=True)
    lastgames = models.IntegerField(verbose_name='宵越し', null=True)
    payout = models.IntegerField(verbose_name='差枚数')
    memo = models.CharField(max_length=100, verbose_name='メモ', blank=True, null=True)

    def __str__(self):
        return self.name

class Pachinko(models.Model):
      class Meta:
          verbose_name_plural = 'パチンコ'
      name = models.CharField(max_length=100, verbose_name='機種名')
      date = models.ForeignKey(BusinessDay, on_delete=models.DO_NOTHING)
      number = models.IntegerField(verbose_name='台番号')
      bonus = models.IntegerField(verbose_name='当たり')
      bbchance = models.CharField(max_length=10, verbose_name='当たり確率', null=True)
      count = models.IntegerField(verbose_name='総回転数')
      lastgames = models.IntegerField(verbose_name='宵越し', null=True)
      payout = models.IntegerField(verbose_name='差枚数')
      game_1k = models.FloatField(verbose_name='1kあたり目安', null=True)
      memo = models.CharField(max_length=100, verbose_name='メモ', blank=True, null=True)

      def __str__(self):
        return self.name
