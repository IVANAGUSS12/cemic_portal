import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Patient, Attachment

@login_required
def panel_index(request):
    return render(request, 'panel/index.html', {})

def qr_index(request):
    return render(request, 'qr/index.html', {})

def qr_gracias(request):
    return render(request, 'qr/gracias.html', {})

def patient_to_dict(p):
    return {
        "id": p.id,
        "nombre": p.nombre,
        "dni": p.dni or "",
        "email": p.email or "",
        "telefono": p.telefono or "",
        "cobertura": p.cobertura or "",
        "medico": p.medico or "",
        "observaciones": p.observaciones or "",
        "estado": p.estado or "Pendiente",
        "sector": p.sector_code,
        "sector__code": p.sector_code,
        "fecha_cx": p.fecha_cx.isoformat() if p.fecha_cx else "",
        "created_at": p.created_at.isoformat(),
    }

def attachment_to_dict(a):
    return {
        "id": a.id,
        "kind": a.kind,
        "url": a.url,
        "name": a.file.name.rsplit('/',1)[-1],
        "created_at": a.created_at.isoformat(),
    }

@csrf_exempt
@require_http_methods(["GET","POST"])
def patients_api(request):
    if request.method == "GET":
        qs = Patient.objects.all().order_by('-created_at')

        cobertura = request.GET.get('cobertura') or ""
        estado    = request.GET.get('estado') or ""
        medico    = request.GET.get('medico') or ""
        sector_code = request.GET.get('sector__code') or request.GET.get('sector') or ""

        if cobertura: qs = qs.filter(cobertura=cobertura)
        if estado:    qs = qs.filter(estado=estado)
        if medico:    qs = qs.filter(medico=medico)
        if sector_code: qs = qs.filter(sector_code=sector_code)

        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        return JsonResponse({
            "count": paginator.count,
            "results": [patient_to_dict(p) for p in page_obj.object_list]
        })

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("JSON inválido")

    required = ["nombre","dni","email","telefono","cobertura","medico","sector_code"]
    if any(not data.get(k) for k in required):
        return HttpResponseBadRequest("Faltan campos obligatorios")

    p = Patient.objects.create(
        nombre=data.get("nombre",""),
        dni=data.get("dni",""),
        email=data.get("email",""),
        telefono=data.get("telefono",""),
        cobertura=data.get("cobertura",""),
        medico=data.get("medico",""),
        observaciones=data.get("observaciones",""),
        sector_code=data.get("sector_code") or "trauma",
        fecha_cx=data.get("fecha_cx") or None,
    )
    return JsonResponse(patient_to_dict(p), status=201)

@csrf_exempt
@require_http_methods(["GET","PATCH"])
def patient_detail_api(request, pk:int):
    p = get_object_or_404(Patient, pk=pk)
    if request.method == "GET":
        data = patient_to_dict(p)
        data["attachments"] = [attachment_to_dict(a) for a in p.attachments.all().order_by('-created_at')]
        return JsonResponse(data)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("JSON inválido")

    estado = data.get("estado") or data.get("status")
    fecha  = data.get("fecha_cx") or data.get("fecha_cirugia")

    if estado: p.estado = estado
    if fecha in ("", None):
        p.fecha_cx = None
    elif isinstance(fecha, str):
        try:
            from datetime import date
            y,m,d = map(int, fecha.split("-"))
            p.fecha_cx = date(y,m,d)
        except Exception:
            pass
    p.save()
    return JsonResponse(patient_to_dict(p))

@csrf_exempt
@require_http_methods(["POST"])
def attachments_api(request):
    if request.content_type is None or "multipart/form-data" not in request.content_type:
        return HttpResponseBadRequest("Se espera multipart/form-data")
    patient_id = request.POST.get("patient")
    kind = (request.POST.get("kind") or "otro").lower()
    file = request.FILES.get("file")
    if not patient_id or not file:
        return HttpResponseBadRequest("Faltan campos")
    p = get_object_or_404(Patient, pk=patient_id)
    a = Attachment.objects.create(patient=p, kind=kind, file=file)
    return JsonResponse(attachment_to_dict(a), status=201)
