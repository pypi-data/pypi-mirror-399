from .Mesh import edges, calculate_square_vertices
from .Constants import Colors

#__all__ = ["_find_line_intersection", "rayCast", "collision"]

def _find_line_intersection(start_1, end_1, start_2, end_2):
    dx1, dy1 = end_1[0] - start_1[0], end_1[1] - start_1[1]
    dx2, dy2 = end_2[0] - start_2[0], end_2[1] - start_2[1]

    det = dx1 * dy2 - dy1 * dx2
    if det == 0:
        return None

    sx, sy = start_2[0] - start_1[0], start_2[1] - start_1[1]
    inv_det = 1 / det

    u = (sx * dy2 - sy * dx2) * inv_det
    v = (sx * dy1 - sy * dx1) * inv_det

    if 0 <= u <= 1 and 0 <= v <= 1:
        return round(start_1[0] + u * dx1), round(start_1[1] + u * dy1)
    return None

def _get_object_variables(obj, var):
    if isinstance(var, str):
        return {var: obj.variables.get(var)} if var in obj.variables else {}
    elif isinstance(var, list):
        return {v: obj.variables.get(v) for v in var if v in obj.variables}
    return {}

def _get_edges(obj, location=None, size=None, rotation=None):
    if obj.variables.get("_type") == "Object2D" and obj.mesh.vertices:
        return obj.mesh.edges
    location = obj.location if location is None else location
    size = obj.size if size is None else size
    size = size if isinstance(size, (list, tuple)) else (0, 0)
    rotation = obj.rotation if rotation is None else rotation
    return edges(calculate_square_vertices(location, size, rotation))

def _determine_collision_side(location, size, target_obj):
    if location[1] + size[1] - 5 <= target_obj.location[1]:
        return 'bottom'
    elif location[1] + 5 >= target_obj.location[1] + target_obj.size[1]:
        return 'top'
    elif location[0] + size[0] - 5 <= target_obj.location[0]:
        return 'right'
    elif location[0] + 5 >= target_obj.location[0] + target_obj.size[0]:
        return 'left'
    return 'center'

def rayCast(window, camera, start, end, objs, variables):
    _location_camera = camera.location if camera else window.camera.location
    _start = (start[0] + _location_camera[0], start[1] + _location_camera[1])
    _end = (end[0] + _location_camera[0], end[1] + _location_camera[1])

    objs = window.drawnObjects.getAllObjects() if objs is None else (
        [objs] if not isinstance(objs, (list, tuple)) else objs
    )

    def ray(obj, var):
        vars_found = _get_object_variables(obj, var)
        if var and not vars_found:
            return False

        for edge_start, edge_end in _get_edges(obj):
            li = _find_line_intersection(_start, _end, edge_start, edge_end)
            if li:
                return [obj, li, vars_found]
        return False

    return [ret for obj in objs if (ret := ray(obj, variables))]

def collision(window, camera, obj, objs, variables, draw=False, draw_color=Colors.Blue):
    render, cache_location, cache_size = obj.getTrueRenderLocationSize(window, camera)
    if not render:
        return False

    objs = window.drawnObjects.getAllObjects() if objs is None else (
        [objs] if isinstance(objs, (dict, set)) or not isinstance(objs, (list, tuple)) else objs
    )

    def _coll(_obj, var):
        vars_found = _get_object_variables(_obj, var)
        if var and not vars_found:
            return False

        _location, _size = (cache_location, cache_size) if obj.collisionBounds is None else obj.collisionBounds.getTrueLocationSize(cache_size, cache_location)

        edges_self = _get_edges(obj, _location, _size)
        edges_obj = _get_edges(_obj)

        if draw:
            for _edges in (*edges_self, *edges_obj):
                window.drawSimpleLine(_edges[0], _edges[1], draw_color)

        for edge_self_start, edge_self_end in edges_self:
            for edge_obj_start, edge_obj_end in edges_obj:
                li = _find_line_intersection(edge_self_start, edge_self_end, edge_obj_start, edge_obj_end)
                if li:
                    if draw:
                        window.drawSquare((li[0] - 5, li[1] - 5), (10, 10), 0, 0, draw_color)
                    collision_side = _determine_collision_side(_location, _size, _obj)
                    return [_obj, li, vars_found, collision_side, _location, _size]
        return False

    ret = None

    return [ret for _obj in objs if _obj != obj and (ret := _coll(_obj, variables))] or False
