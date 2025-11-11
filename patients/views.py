from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.utils.timezone import now
from datetime import date, timedelta
from .models import PatientSubmission, ESTADOS
from .forms import QRForm, FilterForm

class LoginViewCustom(LoginView):
    template_name = "auth/login.html"

def logout_view(request):
    logout(request); return redirect('login')

def qr_form(request):
    if request.method=="POST":
        form=QRForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request,"patients/qr_done.html",{})
    else:
        form=QRForm()
    return render(request,"patients/qr_form.html",{"form":form})

@login_required
def panel(request):
    form=FilterForm(request.GET or None)
    qs=PatientSubmission.objects.all().order_by('-fecha_cx','-timestamp')
    if form.is_valid():
        q=form.cleaned_data.get("q")
        if q:
            qs=qs.filter(Q(nombre__icontains=q)|Q(dni__icontains=q)|Q(cobertura__icontains=q)|Q(medico__icontains=q))
        for f in ["cobertura","medico","estado","sector"]:
            v=form.cleaned_data.get(f)
            if v: qs=qs.filter(**{f"{f}__icontains":v})
        d=form.cleaned_data.get("desde"); h=form.cleaned_data.get("hasta")
        if d: qs=qs.filter(fecha_cx__gte=d)
        if h: qs=qs.filter(fecha_cx__lte=h)
    estados=[e[0] for e in ESTADOS]
    return render(request,"patients/panel.html",{"rows":qs[:50],"form":form,"estados":estados})

@login_required
def calendar_view(request):
    return render(request,"patients/calendar.html",{})

@login_required
def api_day(request, iso):
    try:
        y,m,d=[int(x) for x in iso.split("-")]; the_date=date(y,m,d)
    except:
        return render(request,"patients/day.html",{"rows":[],"iso":iso})
    rows=PatientSubmission.objects.filter(fecha_cx=the_date).order_by('sector','medico','nombre')
    return render(request,"patients/day.html",{"rows":rows,"iso":iso})

@login_required
def stats_view(request):
    qs=PatientSubmission.objects.all()
    q=request.GET.get("q","").strip()
    if q: qs=qs.filter(Q(nombre__icontains=q)|Q(dni__icontains=q)|Q(cobertura__icontains=q)|Q(medico__icontains=q))
    for key in ["cobertura","medico","estado","sector"]:
        v=request.GET.get(key,"").strip()
        if v: qs=qs.filter(**{f"{key}__icontains":v})
    by_estado=dict(qs.values_list('estado').annotate(c=Count('id')))
    by_cob=dict(qs.values_list('cobertura').annotate(c=Count('id'))[:15])
    by_med=dict(qs.values_list('medico').annotate(c=Count('id'))[:15])
    return render(request,"patients/stats.html",{"by_estado":by_estado,"by_cob":by_cob,"by_med":by_med})
