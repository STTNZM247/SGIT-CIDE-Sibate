import base64
import re
import unicodedata

from django.core.files.base import ContentFile

from PIL import Image, ImageOps


def cargar_captura_desde_data_url(data_url):
    data_url = (data_url or '').strip()
    if not data_url or ';base64,' not in data_url:
        return None

    header, encoded = data_url.split(';base64,', 1)
    extension = 'png'
    if '/' in header:
        extension = header.split('/')[-1] or 'png'

    try:
        binary = base64.b64decode(encoded)
    except Exception:
        return None

    return ContentFile(binary, name=f'captura-carnet.{extension}')


def normalizar_texto(texto):
    texto = (texto or '').strip().upper()
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def _tokens_nombre_usuario(usuario):
    nombre_completo = normalizar_texto(f'{usuario.nombre or ""} {usuario.apellido or ""}')
    return [token for token in nombre_completo.split(' ') if len(token) > 2]


def _recortar_carnet_sobre_fondo_oscuro(image):
    """Intenta recortar automáticamente el carnet blanco cuando el fondo es oscuro.

    Si no encuentra un rectángulo razonable, retorna la imagen original.
    """
    try:
        gray = ImageOps.grayscale(image)
        # El carnet suele ser la zona más clara de la foto.
        mask = gray.point(lambda px: 255 if px >= 165 else 0)
        bbox = mask.getbbox()
        if not bbox:
            return image, False

        left, top, right, bottom = bbox
        width = max(1, right - left)
        height = max(1, bottom - top)
        img_w, img_h = image.size

        area_ratio = (width * height) / max(1, img_w * img_h)
        ratio = width / max(1, height)

        # Filtro para evitar recortes absurdos.
        # Carnet vertical aproximado: ~0.65 (ancho/alto). Damos tolerancia amplia.
        if area_ratio < 0.08 or ratio < 0.38 or ratio > 1.05:
            return image, False

        pad_x = int(width * 0.04)
        pad_y = int(height * 0.04)
        left = max(0, left - pad_x)
        top = max(0, top - pad_y)
        right = min(img_w, right + pad_x)
        bottom = min(img_h, bottom + pad_y)

        recorte = image.crop((left, top, right, bottom))
        return recorte, True
    except Exception:
        return image, False


def _variantes_para_ocr(image):
    variantes = [image]
    try:
        gray = ImageOps.grayscale(image)
        contrast = ImageOps.autocontrast(gray)
        variantes.append(contrast.convert('RGB'))

        # Escalado para OCR en texto pequeño.
        upscale = contrast.resize(
            (max(1, contrast.width * 2), max(1, contrast.height * 2)),
            resample=Image.Resampling.LANCZOS,
        )
        variantes.append(upscale.convert('RGB'))
    except Exception:
        pass
    return variantes


def _documento_con_etiqueta_en_texto(texto_normalizado, documento_usuario):
    if not documento_usuario:
        return False

    doc_flexible = r'\D*'.join(documento_usuario)
    etiquetas = [
        r'T\.?\s*[I1]\.?',
        r'TARJETA\s+DE\s+IDENTIDAD',
        r'C\.?\s*[C0]\.?',
        r'CEDULA',
        r'CEDULA\s+DE\s+CIUDADANIA',
    ]

    for etiqueta in etiquetas:
        patron = rf'(?:{etiqueta})\s*[:#\-\.]?\s*{doc_flexible}\b'
        if re.search(patron, texto_normalizado):
            return True

        patron_cercano_1 = rf'(?:{etiqueta}).{{0,24}}{doc_flexible}\b'
        patron_cercano_2 = rf'{doc_flexible}\b.{{0,24}}(?:{etiqueta})'
        if re.search(patron_cercano_1, texto_normalizado) or re.search(patron_cercano_2, texto_normalizado):
            return True

    # Fallback: si el OCR leyó el documento exacto, lo aceptamos para no bloquear por ruido.
    if re.search(rf'\b{doc_flexible}\b', texto_normalizado):
        return True

    return False


def _extraer_texto_ocr(image):
    try:
        import pytesseract
    except Exception:
        return '', 'El OCR automático no está disponible en este servidor.'

    try:
        return pytesseract.image_to_string(image, lang='spa+eng', config='--oem 3 --psm 6'), ''
    except Exception:
        try:
            return pytesseract.image_to_string(image, config='--oem 3 --psm 6'), ''
        except Exception:
            return '', 'No se pudo leer el texto del carnet en esta imagen.'


def _detectar_logo_sena(image, texto_normalizado):
    rgb = image.convert('RGB')
    width, height = rgb.size
    crop = rgb.crop((0, 0, max(1, int(width * 0.42)), max(1, int(height * 0.35))))
    total = max(1, crop.size[0] * crop.size[1])
    verdes = 0

    for r, g, b in crop.getdata():
        if g > 85 and g > r + 18 and g > b + 18:
            verdes += 1

    green_ratio = verdes / total
    text_has_sena = (
        'SENA' in texto_normalizado
        or 'SERVICIO NACIONAL DE APRENDIZAJE' in texto_normalizado
        or 'APRENDIZ' in texto_normalizado
    )

    # Umbral más tolerante para foto real de carnet donde el logo ocupa poca área.
    return green_ratio >= 0.018 or (text_has_sena and green_ratio >= 0.012)


def cargar_imagen_validacion(archivo, *, require_vertical=True):
    if not archivo:
        return None, {
            'ok': False,
            'message': 'Debes cargar una foto del carnet SENA para intentar la validación automática.',
            'error_code': 'missing_file',
        }

    try:
        image = Image.open(archivo)
        image = ImageOps.exif_transpose(image)
        image.load()
        archivo.seek(0)
    except Exception:
        return None, {
            'ok': False,
            'message': 'No pudimos procesar la imagen enviada. Intenta con una foto más clara.',
            'error_code': 'invalid_image',
        }

    width, height = image.size
    if require_vertical and width > height:
        image = image.rotate(90, expand=True)

    return image, None


def _evaluar_validacion_por_imagen(image, usuario):
    texto_ocr_total = ''
    ocr_error = ''

    recorte, recortado = _recortar_carnet_sobre_fondo_oscuro(image)
    for variante in _variantes_para_ocr(recorte):
        texto_tmp, error_tmp = _extraer_texto_ocr(variante)
        if texto_tmp:
            if texto_tmp not in texto_ocr_total:
                texto_ocr_total = f'{texto_ocr_total}\n{texto_tmp}'.strip()
        elif error_tmp and not ocr_error:
            ocr_error = error_tmp

    texto_normalizado = normalizar_texto(texto_ocr_total)
    documento_usuario = re.sub(r'\D+', '', usuario.cc or '')
    tokens_nombre = _tokens_nombre_usuario(usuario)

    coincidencias_nombre = sum(1 for token in tokens_nombre if token in texto_normalizado)
    min_coincidencias = len(tokens_nombre)
    if len(tokens_nombre) >= 3:
        min_coincidencias = len(tokens_nombre) - 1

    nombre_ok = bool(tokens_nombre) and coincidencias_nombre >= min_coincidencias
    documento_ok = _documento_con_etiqueta_en_texto(texto_normalizado, documento_usuario)
    logo_ok = _detectar_logo_sena(recorte if recortado else image, texto_normalizado)

    reasons = []
    if ocr_error:
        reasons.append(ocr_error)
    if not nombre_ok:
        reasons.append('El nombre del carnet no coincide claramente con tu cuenta (se compara en mayúsculas, sin importar tildes).')
    if not documento_ok:
        reasons.append('No encontramos tu documento (TI/CC) en el texto del carnet.')
    if not logo_ok:
        reasons.append('No pudimos confirmar el logo del SENA en la foto.')
    if not recortado:
        reasons.append('Tip: usa un fondo negro liso para que el sistema recorte mejor el carnet automáticamente.')

    score = int(bool(nombre_ok)) + int(bool(documento_ok)) + int(bool(logo_ok))
    if ocr_error:
        score -= 1

    return {
        'ok': not ocr_error and nombre_ok and documento_ok and logo_ok,
        'message': 'Tu carnet SENA fue validado correctamente.' if (not ocr_error and nombre_ok and documento_ok and logo_ok) else 'No se pudo validar tu carnet de forma automática. Puedes solicitar validación manual si lo necesitas.',
        'error_code': None if (not ocr_error and nombre_ok and documento_ok and logo_ok) else ('ocr_failed' if ocr_error else 'mismatch'),
        'details': ['Logo SENA detectado.', 'Nombre y documento coinciden con tu cuenta.'] if (not ocr_error and nombre_ok and documento_ok and logo_ok) else reasons,
        'texto_ocr': texto_ocr_total,
        'score': score,
    }


def intentar_validacion_automatica(archivo, usuario):
    image, image_error = cargar_imagen_validacion(archivo, require_vertical=True)
    if image_error:
        return image_error

    variantes = [image, image.rotate(90, expand=True), image.rotate(270, expand=True)]
    mejor_intento = None

    for img in variantes:
        resultado = _evaluar_validacion_por_imagen(img, usuario)
        if resultado['ok']:
            resultado.pop('score', None)
            return resultado

        if not mejor_intento or resultado['score'] > mejor_intento['score']:
            mejor_intento = resultado

    if mejor_intento:
        mejor_intento.pop('score', None)
        return mejor_intento

    return {
        'ok': False,
        'message': 'No se pudo validar tu carnet de forma automática. Puedes solicitar validación manual si lo necesitas.',
        'error_code': 'ocr_failed',
        'details': ['No se pudo analizar la imagen del carnet.'],
        'texto_ocr': '',
    }