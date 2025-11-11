from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now

from .models import PatientSubmission, ESTADOS
from .forms import QRForm, FilterForm


def qr_form(request):
    if request.method == "POST":
        form = QRForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, "patients/qr_done.html", {})
    else:
        form = QRForm()
    return render(request, "patients/qr_form.html", {"form": form})


# ---------- PANEL (con filtros, paginación y export) ----------
@login_required
def panel(request):
    # filtros por querystring
    form = FilterForm(request.GET or None)
    qs = PatientSubmission.objects.all().order_by("-fecha_cx", "-timestamp")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q)
                | Q(dni__icontains=q)
                | Q(cobertura__icontains=q)
                | Q(medico__icontains=q)
            )
        for f in ["cobertura", "medico", "estado", "sector"]:
            v = form.cleaned_data.get(f)
            if v:
                qs = qs.filter(**{f"{f}__icontains": v})

        d = form.cleaned_data.get("desde")
        h = form.cleaned_data.get("hasta")
        if d:
            qs = qs.filter(fecha_cx__gte=d)
        if h:
            qs = qs.filter(fecha_cx__lte=h)
    else:
        # por defecto: últimos 30 días
        d = now().date() - timedelta(days=30)
        qs = qs.filter(fecha_cx__gte=d)

    # paginación simple (50 por página)
    try:
        page = int(request.GET.get("page", 1))
    except:
        page = 1
    PAGE_SIZE = 50
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    total = qs.count()
    submissions = list(qs[start:end])
    has_prev = page > 1
    has_next = end < total

    estados = [e[0] for e in ESTADOS]
    ctx = {
        "submissions": submissions,
        "form": form,
        "estados": estados,
        "page": page,
        "has_prev": has_prev,
        "has_next": has_next,
        "total": total,
        "page_size": PAGE_SIZE,
    }
    return render(request, "patients/panel.html", ctx)


# ---------- Drawer “carpetita por paciente” ----------
@login_required
def patient_drawer(request, pk):
    s = get_object_or_404(PatientSubmission, pk=pk)
    return render(request, "patients/_patient_drawer.html", {"s": s})


# ---------- Export CSV (sobre filtros actuales) ----------
@login_required
def export_csv(request):
    form = FilterForm(request.GET or None)
    qs = PatientSubmission.objects.all().order_by("-fecha_cx", "-timestamp")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q)
                | Q(dni__icontains=q)
                | Q(cobertura__icontains=q)
                | Q(medico__icontains=q)
            )
        for f in ["cobertura", "medico", "estado", "sector"]:
            v = form.cleaned_data.get(f)
            if v:
                qs = qs.filter(**{f"{f}__icontains": v})
        d = form.cleaned_data.get("desde")
        h = form.cleaned_data.get("hasta")
        if d:
            qs = qs.filter(fecha_cx__gte=d)
        if h:
            qs = qs.filter(fecha_cx__lte=h)

    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="autorizaciones.csv"'
    resp.write("ID;Nombre;DNI;Cobertura;Medico;Sector;FechaCx;Estado\n")
    for s in qs[:20000]:
        row = [
            s.id,
            (s.nombre or "").replace(";", ","),
            s.dni or "",
            (s.cobertura or "").replace(";", ","),
            (s.medico or "").replace(";", ","),
            getattr(s, "sector", "") or "",
            s.fecha_cx.strftime("%d/%m/%Y") if s.fecha_cx else "",
            s.estado or "",
        ]
        resp.write(";".join(map(str, row)) + "\n")
    return resp


# ---------- Calendario y día (como ya tenías) ----------
@login_required
def calendar_view(request):
    today = date.today()
    y = int(request.GET.get("y", today.year))
    m = int(request.GET.get("m", today.month))

    first = date(y, m, 1)
    # mes siguiente (limite superior) y mes previo (para navegación)
    next_first = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
    prev_first = (first - timedelta(days=1)).replace(day=1)

    # cantidad de días del mes
    _, ndays = monthrange(y, m)
    days = [date(y, m, d) for d in range(1, ndays + 1)]

    # conteos por día
    qs = (
        PatientSubmission.objects
        .filter(fecha_cx__gte=first, fecha_cx__lt=next_first)
        .values("fecha_cx")
        .annotate(c=Count("id"))
    )
    counts = {row["fecha_cx"]: row["c"] for row in qs}

    # matriz de semanas (7 columnas)
    start_wd = first.weekday()  # lunes=0 ... domingo=6
    weeks, week = [], [None] * start_wd
    for d in days:
        week.append(d)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        week += [None] * (7 - len(week))
        weeks.append(week)

    ctx = {
        "weeks": weeks,
        "y": y, "m": m,
        "month_name": first.strftime("%B").capitalize(),
        "prev_y": prev_first.year, "prev_m": prev_first.month,
        "next_y": next_first.year, "next_m": next_first.month,
        "counts": counts,
    }
    return render(request, "patients/calendar.html", ctx)


@login_required
def api_day(request, iso):
    # vista del detalle del día (clic en una celda)
    try:
        y, m, d = [int(x) for x in iso.split("-")]
        the_date = date(y, m, d)
    except Exception:
        the_date = None

    rows = (
        PatientSubmission.objects.filter(fecha_cx=the_date).order_by("sector", "medico", "nombre")
        if the_date else []
    )
    return render(request, "patients/day.html", {"rows": rows, "iso": iso})

# ---------- Estadísticas mínima (dejamos hook para Chart.js) ----------
@login_required
def stats_view(request):
    qs = PatientSubmission.objects.all()
    by_estado = dict(qs.values_list("estado").annotate(c=Count("id")))
    by_sector = dict(qs.values_list("sector").annotate(c=Count("id")))
    return render(request, "patients/stats.html", {
        "by_estado": by_estado,
        "by_sector": by_sector,
    })
