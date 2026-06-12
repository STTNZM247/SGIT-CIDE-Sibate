import json
import secrets

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.utils import timezone

from .forms import CatalogoForm, CategoriaWizardForm
from .models import Catalogo, Subcategoria


def _user_role(request):
    if not request.user.is_authenticated:
        return None
    if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False):
        return 'admin'

    rol = (getattr(getattr(request.user, 'id_rol_fk', None), 'nombre_rol', '') or '').strip().lower()
    if rol in {'admin', 'administrador'}:
        return 'admin'
    if rol in {'almacenista', 'almacen'}:
        return 'almacenista'
    if rol in {'', 'usuario', 'aprendiz', 'instructor'}:
        return 'usuario'
    return rol


def _is_admin(request):
    return _user_role(request) == 'admin'


def _normalize_code(value):
    return (value or '').strip().upper()


def _normalize_name(value):
    return ' '.join((value or '').strip().split())


def _generate_code(length=5):
    return str(secrets.randbelow(10 ** length)).zfill(length)


def _macro_code_exists(code, exclude_id=None):
    qs = Catalogo.objects.filter(codigo_macro__iexact=code)
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()


def _categoria_code_exists(macro_id, code, exclude_id=None):
    qs = Subcategoria.objects.filter(
        id_cat_fk_id=macro_id,
        subcategoria_padre__isnull=True,
        codigo_clasificacion__iexact=code,
    )
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()


def _subcategoria_code_exists(categoria_id, code, exclude_id=None):
    qs = Subcategoria.objects.filter(
        subcategoria_padre_id=categoria_id,
        codigo_clasificacion__iexact=code,
    )
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()


def _codigo_disponible(nivel, codigo, macro_id=None, categoria_id=None):
    code = _normalize_code(codigo)
    if not code:
        return False
    if nivel == 'macro':
        return not _macro_code_exists(code)
    if nivel == 'categoria':
        if not macro_id:
            return False
        return not _categoria_code_exists(int(macro_id), code)
    if nivel == 'subcategoria':
        if not categoria_id:
            return False
        return not _subcategoria_code_exists(int(categoria_id), code)
    return False


def _generar_codigo_unico(nivel, macro_id=None, categoria_id=None, length=5):
    for _ in range(200):
        codigo = _generate_code(length)
        if _codigo_disponible(nivel, codigo, macro_id=macro_id, categoria_id=categoria_id):
            return codigo
    return None


@login_required
def wizard_crear_macro(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Metodo no permitido.'}, status=405)
    if not _is_admin(request):
        return JsonResponse({'ok': False, 'error': 'Solo admin.'}, status=403)

    form = CatalogoForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'error': 'Datos invalidos.', 'errors': form.errors}, status=400)

    codigo_macro = _normalize_code(form.cleaned_data.get('codigo_macro'))
    if codigo_macro and _macro_code_exists(codigo_macro):
        return JsonResponse({'ok': False, 'error': 'Código ya registrado.'}, status=400)

    macro = form.save(commit=False)
    macro.codigo_macro = codigo_macro
    macro.fch_registro = timezone.now()
    macro.fch_ult_act = timezone.now()
    macro.save()

    return JsonResponse(
        {
            'ok': True,
            'macro': {
                'id': macro.id_cat,
                'codigo': macro.codigo_macro or '',
                'nombre': macro.nombre_catalogo or '',
            },
        }
    )


@login_required
def wizard_crear_categoria(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Metodo no permitido.'}, status=405)
    if not _is_admin(request):
        return JsonResponse({'ok': False, 'error': 'Solo admin.'}, status=403)

    macro_id = request.POST.get('macro_id')
    if not macro_id:
        return JsonResponse({'ok': False, 'error': 'Falta macro_id.'}, status=400)

    form = CategoriaWizardForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'error': 'Datos invalidos.', 'errors': form.errors}, status=400)

    try:
        macro = Catalogo.objects.get(pk=int(macro_id))
    except (Catalogo.DoesNotExist, ValueError):
        return JsonResponse({'ok': False, 'error': 'Macro no encontrada.'}, status=404)

    codigo_categoria = _normalize_code(form.cleaned_data['codigo_categoria'])
    if codigo_categoria and _categoria_code_exists(macro.id_cat, codigo_categoria):
        return JsonResponse({'ok': False, 'error': 'Código ya registrado.'}, status=400)

    categoria = Subcategoria.objects.create(
        id_cat_fk=macro,
        subcategoria_padre=None,
        codigo_clasificacion=codigo_categoria,
        nombre_subcategoria=_normalize_name(form.cleaned_data['nombre_categoria']),
        descripcion=(form.cleaned_data.get('descripcion_categoria') or '').strip(),
        fch_registro=timezone.now(),
        fch_ult_act=timezone.now(),
    )

    return JsonResponse(
        {
            'ok': True,
            'categoria': {
                'id': categoria.id_subcat,
                'codigo': categoria.codigo_clasificacion or '',
                'nombre': categoria.nombre_subcategoria,
            },
        }
    )


@login_required
def wizard_crear_subcategorias(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Metodo no permitido.'}, status=405)
    if not _is_admin(request):
        return JsonResponse({'ok': False, 'error': 'Solo admin.'}, status=403)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'ok': False, 'error': 'JSON invalido.'}, status=400)

    categoria_id = payload.get('categoria_id')
    items = payload.get('subcategorias') or []

    if not categoria_id:
        return JsonResponse({'ok': False, 'error': 'Falta categoria_id.'}, status=400)
    if not isinstance(items, list) or not items:
        return JsonResponse({'ok': False, 'error': 'Debes enviar al menos una subcategoria.'}, status=400)

    try:
        categoria = Subcategoria.objects.select_related('id_cat_fk').get(pk=int(categoria_id), subcategoria_padre__isnull=True)
    except (Subcategoria.DoesNotExist, ValueError):
        return JsonResponse({'ok': False, 'error': 'Categoria no encontrada.'}, status=404)

    codigos_vistos = set()
    duplicados_codigo = []
    for raw in items:
        codigo = (raw.get('codigo') or '').strip()
        nombre = _normalize_name(raw.get('nombre'))
        if not codigo or not nombre:
            continue
        llave_codigo = codigo.upper()
        if llave_codigo in codigos_vistos:
            duplicados_codigo.append(codigo)
        codigos_vistos.add(llave_codigo)

    if duplicados_codigo:
        return JsonResponse(
            {
                'ok': False,
                'error': 'Hay códigos repetidos dentro del formulario.',
                'details': {
                    'codigos_repetidos': sorted(set(duplicados_codigo)),
                },
            },
            status=400,
        )

    existentes = []
    for raw in items:
        codigo = (raw.get('codigo') or '').strip()
        nombre = _normalize_name(raw.get('nombre'))
        if not codigo or not nombre:
            continue
        codigo_norm = _normalize_code(codigo)
        if _subcategoria_code_exists(categoria.id_subcat, codigo_norm):
            existentes.append(f'{codigo} / {nombre}')

    if existentes:
        return JsonResponse(
            {
                'ok': False,
                'error': 'Código ya registrado.',
                'details': {'existentes': existentes},
            },
            status=400,
        )

    created = []
    try:
        with transaction.atomic():
            for raw in items:
                codigo = (raw.get('codigo') or '').strip()
                nombre = _normalize_name(raw.get('nombre'))
                descripcion = (raw.get('descripcion') or '').strip()
                if not codigo or not nombre:
                    continue

                codigo_norm = _normalize_code(codigo)
                if _subcategoria_code_exists(categoria.id_subcat, codigo_norm):
                    raise IntegrityError('codigo duplicado')

                subcat = Subcategoria.objects.create(
                    id_cat_fk=categoria.id_cat_fk,
                    subcategoria_padre=categoria,
                    codigo_clasificacion=codigo_norm,
                    nombre_subcategoria=nombre,
                    descripcion=descripcion,
                    fch_registro=timezone.now(),
                    fch_ult_act=timezone.now(),
                )
                created.append(
                    {
                        'id': subcat.id_subcat,
                        'codigo': subcat.codigo_clasificacion or '',
                        'nombre': subcat.nombre_subcategoria,
                        'descripcion': subcat.descripcion or '',
                    }
                )
    except IntegrityError:
        return JsonResponse(
            {
                'ok': False,
                'error': 'No se pudo guardar porque el código de subcategoría ya existe en esa rama.',
            },
            status=400,
        )

    if not created:
        return JsonResponse({'ok': False, 'error': 'No se pudo crear ninguna subcategoria valida.'}, status=400)

    return JsonResponse({'ok': True, 'subcategorias': created})


@login_required
def wizard_codigo_api(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Metodo no permitido.'}, status=405)
    if not _is_admin(request):
        return JsonResponse({'ok': False, 'error': 'Solo admin.'}, status=403)

    nivel = _normalize_code(request.POST.get('nivel') or '').lower()
    modo = _normalize_code(request.POST.get('modo') or 'validar').lower()
    codigo = _normalize_code(request.POST.get('codigo'))
    macro_id = request.POST.get('macro_id') or None
    categoria_id = request.POST.get('categoria_id') or None

    if modo == 'generar':
        if nivel == 'categoria' and not macro_id:
            return JsonResponse({'ok': False, 'error': 'Primero crea la macro categoría.'}, status=400)
        if nivel == 'subcategoria' and not categoria_id:
            return JsonResponse({'ok': False, 'error': 'Primero crea la categoría.'}, status=400)
        generado = _generar_codigo_unico(nivel, macro_id=macro_id, categoria_id=categoria_id)
        if not generado:
            return JsonResponse({'ok': False, 'error': 'No fue posible generar un código disponible.'}, status=400)
        return JsonResponse({'ok': True, 'disponible': True, 'codigo': generado})

    if not nivel or not codigo:
        return JsonResponse({'ok': False, 'error': 'Faltan datos para validar el código.'}, status=400)

    if nivel == 'categoria' and not macro_id:
        return JsonResponse({'ok': False, 'error': 'Primero crea la macro categoría.'}, status=400)
    if nivel == 'subcategoria' and not categoria_id:
        return JsonResponse({'ok': False, 'error': 'Primero crea la categoría.'}, status=400)

    disponible = _codigo_disponible(nivel, codigo, macro_id=macro_id, categoria_id=categoria_id)
    return JsonResponse(
        {
            'ok': True,
            'disponible': disponible,
            'mensaje': 'Código disponible.' if disponible else 'Código ya registrado.',
        }
    )
