from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, TemplateView
from .models import StockItem, StockUploadLog
from .forms import StockUploadForm
from .services import process_upload
from .report import generate_stock_report

class StockManagerMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_stock_manager or u.is_procurement_officer or u.is_staff

class StockDashboardView(StockManagerMixin, TemplateView):
    template_name = 'stock/dashboard.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        items = list(StockItem.objects.all())
        ctx['total']         = len(items)
        ctx['out_of_stock']  = sum(1 for i in items if i.action=='OUT OF STOCK')
        ctx['reorder_now']   = sum(1 for i in items if i.action=='REORDER NOW')
        ctx['reorder_soon']  = sum(1 for i in items if i.action=='REORDER SOON')
        ctx['overstocked']   = sum(1 for i in items if i.action=='OVERSTOCKED')
        ctx['well_stocked']  = sum(1 for i in items if i.action=='WELL STOCKED')
        urgent = [i for i in items if i.action in ('OUT OF STOCK','REORDER NOW','REORDER SOON')]
        ctx['urgent_items']  = sorted(urgent,key=lambda x:(0 if x.action=='OUT OF STOCK' else 1 if x.action=='REORDER NOW' else 2))[:15]
        ctx['overstocked_items'] = [i for i in items if i.action=='OVERSTOCKED'][:10]
        ctx['last_upload']   = StockUploadLog.objects.first()
        return ctx

class StockListView(StockManagerMixin, ListView):
    model = StockItem
    template_name = 'stock/list.html'
    context_object_name = 'items'
    paginate_by = 50
    def get_queryset(self):
        qs=StockItem.objects.all()
        self.q=self.request.GET.get('q','')
        self.action_f=self.request.GET.get('action','')
        self.cat_f=self.request.GET.get('category','')
        if self.q: qs=qs.filter(Q(qb_code__icontains=self.q)|Q(description__icontains=self.q))
        if self.cat_f: qs=qs.filter(category__icontains=self.cat_f)
        return qs
    def get_context_data(self,**kwargs):
        ctx=super().get_context_data(**kwargs)
        ctx['q']=self.q; ctx['action_f']=self.action_f; ctx['cat_f']=self.cat_f
        if self.action_f: ctx['items']=[i for i in ctx['items'] if i.action==self.action_f]
        ctx['categories']=list(StockItem.objects.exclude(category='').values_list('category',flat=True).distinct().order_by('category'))
        ctx['action_choices']=[('','All'),('OUT OF STOCK','Out of Stock'),('REORDER NOW','Reorder Now'),('REORDER SOON','Reorder Soon'),('OVERSTOCKED','Overstocked'),('WELL STOCKED','Well Stocked'),('NO USAGE DATA','No Data')]
        return ctx

class StockUploadView(StockManagerMixin, TemplateView):
    template_name='stock/upload.html'
    def get_context_data(self,**kwargs):
        ctx=super().get_context_data(**kwargs)
        ctx['form']=StockUploadForm()
        ctx['logs']=StockUploadLog.objects.all()[:10]
        return ctx
    def post(self,request,*args,**kwargs):
        form=StockUploadForm(request.POST,request.FILES)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))
        f=request.FILES['file']
        try:
            log,created,updated,skipped=process_upload(f,f.name,request.user)
            messages.success(request,f'Import complete — {created} created, {updated} updated, {skipped} skipped.')
        except Exception as e:
            messages.error(request,f'Import failed: {e}')
        return redirect(reverse('stock:list'))

class StockAnalysisView(StockManagerMixin, TemplateView):
    template_name='stock/analysis.html'
    def get_context_data(self,**kwargs):
        ctx=super().get_context_data(**kwargs)
        items=list(StockItem.objects.all())
        MONTHS=['Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May']
        monthly=[round(sum(float(getattr(i,f'usage_{m.lower()}')) for i in items),2) for m in MONTHS]
        ctx['months']=MONTHS; ctx['monthly_totals']=monthly; ctx['items']=items
        ctx['top_usage']=sorted([i for i in items if i.monthly_moving_average>0],key=lambda x:x.monthly_moving_average,reverse=True)[:10]
        ctx['overstocked']=[i for i in items if i.action=='OVERSTOCKED']
        action_counts={}
        for i in items: action_counts[i.action]=action_counts.get(i.action,0)+1
        ctx['action_counts']=action_counts
        return ctx

@login_required
def download_report(request):
    u=request.user
    if not (u.is_stock_manager or u.is_procurement_officer or u.is_staff): raise PermissionDenied
    from django.utils import timezone
    items=list(StockItem.objects.all())
    buf=generate_stock_report(items)
    fn=f"Stock_Analysis_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
    resp=HttpResponse(buf.getvalue(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition']=f'attachment; filename="{fn}"'
    return resp
