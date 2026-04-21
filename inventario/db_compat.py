from functools import lru_cache

from django.db import connection


USUARIO_OPTIONAL_COLUMNS = {
    'id_tipo_doc_fk': 'id_tipo_doc_fk',
    'verificacion_sena_estado': 'verificacion_sena_estado',
    'verificacion_sena_imagen': 'verificacion_sena_imagen',
    'verificacion_sena_documento': 'verificacion_sena_documento',
    'verificacion_sena_observacion': 'verificacion_sena_observacion',
    'verificacion_sena_solicitada_en': 'verificacion_sena_solicitada_en',
    'verificacion_sena_validada_en': 'verificacion_sena_validada_en',
}


@lru_cache(maxsize=8)
def _table_columns(table_name):
    try:
        with connection.cursor() as cursor:
            description = connection.introspection.get_table_description(cursor, table_name)
    except Exception:
        return set()

    columns = set()
    for column in description:
        columns.add(getattr(column, 'name', column[0]))
    return columns


def table_has_columns(table_name, required_columns):
    columns = _table_columns(table_name)
    if not columns:
        return False
    return set(required_columns).issubset(columns)


def usuario_missing_optional_fields(usuario_model):
    table_name = usuario_model._meta.db_table
    columns = _table_columns(table_name)
    if not columns:
        return []

    missing = []
    for field_name, column_name in USUARIO_OPTIONAL_COLUMNS.items():
        if column_name not in columns:
            missing.append(field_name)
    return missing


def usuario_supports_tipo_doc(usuario_model):
    return table_has_columns(usuario_model._meta.db_table, ['id_tipo_doc_fk']) and table_has_columns('tipo_doc', ['id_tipo_doc', 'codigo'])


def usuario_supports_verificacion_sena(usuario_model):
    required = [
        'verificacion_sena_estado',
        'verificacion_sena_imagen',
        'verificacion_sena_documento',
        'verificacion_sena_observacion',
        'verificacion_sena_solicitada_en',
        'verificacion_sena_validada_en',
    ]
    return table_has_columns(usuario_model._meta.db_table, required)


def get_safe_usuario_value(usuario, attr_name, default=None):
    usuario_real = getattr(usuario, '_wrapped', None)
    if usuario_real is not None and usuario_real is not usuario:
        usuario = usuario_real

    if attr_name in usuario.__dict__:
        return usuario.__dict__.get(attr_name, default)

    attname = None
    try:
        attname = usuario._meta.get_field(attr_name).attname
    except Exception:
        attname = None

    if attname and attname in usuario.__dict__:
        return usuario.__dict__.get(attname, default)
    return default


def get_usuario_model_from_instance(usuario):
    usuario_real = getattr(usuario, '_wrapped', None)
    if usuario_real is not None and usuario_real is not usuario:
        usuario = usuario_real
    return getattr(usuario, '_meta', None).model if getattr(usuario, '_meta', None) else None