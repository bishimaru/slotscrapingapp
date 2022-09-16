from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from .models import *
import datetime
from django.db.models import Sum, Avg, aggregates



# class IndexView(TemplateView):
#     template_name = 'index.html'

class StoreNameView(ListView):
    model = PachiSlotStore
    template_name = 'index.html'
    context_object_name = "stores"

    def get_queryset(self):
        return PachiSlotStore.objects.all()

class DateView(ListView):
    model = BusinessDay
    template_name = 'date.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_name = self.request.GET.get('sn')
        dates = BusinessDay.objects.filter(
            store_name_id=store_name).distinct().order_by('-date')
        context['store_name'] = PachiSlotStore.objects.get(pk=store_name).name
        context['dates'] = dates

        return context

class SlotNameView(ListView):
    model = Slot
    template_name = 'slot_name_list.html'
    context_object_name = 'name_cnt'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_name = self.request.GET.get('sn')
        date = self.request.GET.get('date')
       
        nm = Slot.objects.filter(
            date=date,).distinct().values('name')
        name_cnt = {}
        avarage = []
        name_pay = []

        for n in nm:
            cnt = Slot.objects.filter(
                date=date, name=n['name']).values('name').count()
            name_cnt[n['name']] = cnt
        n_c = sorted(name_cnt.items(), key=lambda x: x[1], reverse=True)
        for n in n_c:

            ava = Slot.objects.filter(date=date, name=n[0]).aggregate(Avg('count'))
            ava = int(ava['count__avg'])
            avarage.append(ava)

            py = Slot.objects.filter(
                date=date, name=n[0]).aggregate(Sum('payout'))
            py = int(py['payout__sum'])
            name_pay.append(py)

        context.update({
            'name_cnt': n_c,
            'store_name': store_name,
            'date': date,
            'avg': avarage,
            'py': name_pay
        })
        return context

class DetailView(ListView):
    model = Slot
    template_name = 'detail.html'

    def queryset(self):
        store_name = self.request.GET.get('sn')
        day = self.request.GET.get('date')
        name = self.request.GET.get('name')
        dates = Slot.objects.filter(date=day, name=name)
        return dates

    def get_context_data(self):
        context = super().get_context_data()
        store_name = self.request.GET.get('sn')
        date = self.request.GET.get('date')
        name = self.request.GET.get('name')

        totalpay = Slot.objects.filter(date=date, name=name).aggregate(Sum('payout'))
        totalpay = totalpay['payout__sum']

        avgpay = Slot.objects.filter(date=date, name=name).aggregate(Avg('payout'))
        avgpay = (int)(avgpay['payout__avg'])

        avgcount = Slot.objects.filter(date=date, name=name).aggregate(Avg('count'))
        avgcount = (int)(avgcount['count__avg'])

        context['tp'] = totalpay
        context['ap'] = avgpay
        context['ac'] = avgcount
        return context
