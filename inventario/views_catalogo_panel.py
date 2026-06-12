from .models import Producto, Subcategoria


def build_catalogo_cards(catalogos_qs):
    cards = []
    for catalogo in catalogos_qs:
        root_categories_count = Subcategoria.objects.filter(
            id_cat_fk=catalogo,
            subcategoria_padre__isnull=True,
        ).count()
        nested_subcats_count = Subcategoria.objects.filter(
            id_cat_fk=catalogo,
            subcategoria_padre__isnull=False,
        ).count()
        products_count = Producto.objects.filter(id_cat_fk=catalogo).count()
        cards.append(
            {
                'id': catalogo.id_cat,
                'codigo': (catalogo.codigo_macro or '').strip(),
                'nombre': catalogo.nombre_catalogo,
                'descripcion': catalogo.descripcion,
                'ubicacion': catalogo.id_ubicacion_fk.nombre if catalogo.id_ubicacion_fk else '',
                'ubicacion_id': catalogo.id_ubicacion_fk_id,
                'codigo_bloqueado': bool((catalogo.codigo_macro or '').strip()),
                'total_productos': products_count,
                'categorias_count': root_categories_count,
                'subcategorias_count': nested_subcats_count,
                'can_delete': products_count == 0,
                'delete_reason': '' if products_count == 0 else 'No se puede eliminar porque tiene productos asociados.',
            }
        )
    return cards


def _build_tree_nodes(subcats):
    nodes = {}
    roots = []
    for sc in subcats:
        nodes[sc.id_subcat] = {
            'id': sc.id_subcat,
            'codigo': (sc.codigo_clasificacion or '').strip(),
            'nombre': sc.nombre_subcategoria,
            'ruta': sc.ruta_completa,
            'padre_id': sc.subcategoria_padre_id,
            'children': [],
            'children_count': 0,
            'branch_products_count': 0,
            'can_delete': True,
            'delete_reason': '',
        }

    for sc in subcats:
        node = nodes[sc.id_subcat]
        padre_id = sc.subcategoria_padre_id
        if padre_id and padre_id in nodes:
            nodes[padre_id]['children'].append(node)
        else:
            roots.append(node)

    def _collect(node):
        descendant_ids = [node['id']]
        for child in node['children']:
            descendant_ids.extend(_collect(child))
        node['children_count'] = len(node['children'])
        node['branch_products_count'] = (
            Producto.objects
            .filter(subcategorias__id_subcat__in=descendant_ids)
            .distinct()
            .count()
        )
        node['can_delete'] = node['branch_products_count'] == 0
        if not node['can_delete']:
            node['delete_reason'] = 'No se puede eliminar porque tiene productos asociados.'
        return descendant_ids

    for root in roots:
        _collect(root)

    def _sort(node_list):
        node_list.sort(key=lambda item: item['nombre'].lower())
        for item in node_list:
            _sort(item['children'])

    _sort(roots)
    return roots


def build_catalogo_tree(catalogo, selected_subcat=None):
    subcats_qs = Subcategoria.objects.filter(id_cat_fk=catalogo).select_related('id_cat_fk', 'subcategoria_padre')
    roots = _build_tree_nodes(list(subcats_qs))
    if not selected_subcat:
        return roots

    # Cuando se entra en un nodo, mostramos sus hijas directas como nivel actual.
    for root in roots:
        if root['id'] == selected_subcat.id_subcat:
            return root['children']

        stack = list(root['children'])
        while stack:
            node = stack.pop(0)
            if node['id'] == selected_subcat.id_subcat:
                return node['children']
            stack.extend(node['children'])

    return []
