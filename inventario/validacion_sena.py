import re
import unicodedata

from PIL import Image, ImageOps


def normalizar_texto(texto):
    texto = (texto or '').strip().upper()
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def _tokens_nombre_usuario(usuario):
    nombre_completo = normalizar_texto(f'{usuario.nombre or ""} {usuario.apellido or ""}')
    return [token for token in nombre_completo.split(' ') if len(token) > 2]


def _extraer_texto_ocr(image):
    try:
        import pytesseract
    except Exception:
        return '', 'El OCR automático no está disponible en este servidor.'

    try:
        return pytesseract.image_to_string(image, lang='spa+eng'), ''
    except Exception:
        try:
            return pytesseract.image_to_string(image), ''
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
    text_has_sena = 'SENA' in texto_normalizado or 'SERVICIO NACIONAL DE APRENDIZAJE' in texto_normalizado
    return text_has_sena and green_ratio >= 0.04


def intentar_validacion_automatica(archivo, usuario):
    if not archivo:
        return {
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
        return {
            'ok': False,
            'message': 'No pudimos procesar la imagen enviada. Intenta con una foto más clara.',
            'error_code': 'invalid_image',
        }

    texto_ocr, ocr_error = _extraer_texto_ocr(image)
    texto_normalizado = normalizar_texto(texto_ocr)
    documento_usuario = re.sub(r'\D+', '', usuario.cc or '')
    texto_digitos = re.sub(r'\D+', '', texto_ocr or '')
    tokens_nombre = _tokens_nombre_usuario(usuario)
    coincidencias_nombre = sum(1 for token in tokens_nombre if token in texto_normalizado)
    min_coincidencias = len(tokens_nombre)
    if len(tokens_nombre) >= 3:
        min_coincidencias = len(tokens_nombre) - 1

    nombre_ok = bool(tokens_nombre) and coincidencias_nombre >= min_coincidencias
    documento_ok = bool(documento_usuario) and documento_usuario in texto_digitos
    logo_ok = _detectar_logo_sena(image, texto_normalizado)

    reasons = []
    if ocr_error:
        reasons.append(ocr_error)
    if not nombre_ok:
        reasons.append('El nombre del carnet no coincide claramente con tu cuenta.')
    if not documento_ok:
        reasons.append('El número de documento no coincide con tu cuenta.')
    if not logo_ok:
        reasons.append('No pudimos confirmar el logo del SENA en la foto.')

    if ocr_error or not (nombre_ok and documento_ok and logo_ok):
        return {
            'ok': False,
            'message': 'No se pudo validar tu carnet de forma automática. Puedes solicitar validación manual si lo necesitas.',
            'error_code': 'ocr_failed' if ocr_error else 'mismatch',
            'details': reasons,
            'texto_ocr': texto_ocr,
        }

    return {
        'ok': True,
        'message': 'Tu carnet SENA fue validado correctamente.',
        'details': ['Logo SENA detectado.', 'Nombre y documento coinciden con tu cuenta.'],
        'texto_ocr': texto_ocr,
    }