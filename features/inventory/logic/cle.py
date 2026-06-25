import math


def _as_number(value, field_name, allow_zero=False, required=True):
    if value is None:
        if required:
            return None, f"{field_name} es requerido."
        return None, None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None, f"{field_name} debe ser un valor numerico."

    if allow_zero:
        if number < 0:
            return None, f"{field_name} no puede ser negativo."
    elif number <= 0:
        return None, f"{field_name} debe ser mayor a cero."

    return number, None


def calcular_cle(
    demanda_anual,
    costo_ordenar,
    costo_almacenar,
    precio_unitario=None,
    dias_laborales=None,
    demanda_diaria=None,
    tiempo_entrega=None,
    inventario_seguridad=None,
):
    D, error = _as_number(demanda_anual, "La demanda anual")
    if error:
        return {"error": error}

    Co, error = _as_number(costo_ordenar, "El costo por ordenar")
    if error:
        return {"error": error}

    Ch, error = _as_number(costo_almacenar, "El costo por almacenar")
    if error:
        return {"error": error}

    Cu, error = _as_number(precio_unitario, "El precio unitario", required=False)
    if error:
        return {"error": error}

    work_days, error = _as_number(
        dias_laborales,
        "Los dias laborales por ano",
        required=False,
    )
    if error:
        return {"error": error}

    daily_demand, error = _as_number(
        demanda_diaria,
        "La demanda diaria",
        required=False,
    )
    if error:
        return {"error": error}

    lead_time, error = _as_number(
        tiempo_entrega,
        "El tiempo de entrega",
        allow_zero=True,
        required=False,
    )
    if error:
        return {"error": error}

    safety_stock, error = _as_number(
        inventario_seguridad,
        "El inventario de seguridad",
        allow_zero=True,
        required=False,
    )
    if error:
        return {"error": error}

    q_optima = math.sqrt((2 * D * Co) / Ch)
    safety_for_inventory = safety_stock if safety_stock is not None else 0

    inventario_maximo = q_optima + safety_for_inventory
    promedio_inventario = (q_optima / 2) + safety_for_inventory
    numero_ordenes = D / q_optima
    costo_anual_orden = numero_ordenes * Co
    costo_anual_almacenado_base = (q_optima / 2) * Ch
    costo_anual_almacenado = promedio_inventario * Ch
    costo_total_relevante = costo_anual_orden + costo_anual_almacenado_base
    costo_total_operativo = costo_anual_orden + costo_anual_almacenado
    costo_anual_compra = D * Cu if Cu is not None else None
    costo_total = costo_total_operativo

    if costo_anual_compra is not None:
        costo_total += costo_anual_compra

    reorder_values = [work_days, daily_demand, lead_time]
    opcionales_completos = all(value is not None for value in reorder_values)
    punto_reorden = None
    demanda_diaria_calculada = D / work_days if work_days else None
    advertencias = []

    if opcionales_completos:
        punto_reorden = (daily_demand * lead_time) + safety_for_inventory

        if demanda_diaria_calculada:
            diferencia = abs(daily_demand - demanda_diaria_calculada)
            tolerancia = demanda_diaria_calculada * 0.05
            if diferencia > tolerancia:
                advertencias.append(
                    "La demanda diaria ingresada difiere en mas de 5% de "
                    "la demanda anual dividida entre los dias laborales."
                )

    return {
        "error": None,
        "demanda_anual": D,
        "costo_ordenar": Co,
        "costo_almacenar": Ch,
        "precio_unitario": Cu,
        "incluye_costo_compra": Cu is not None,
        "dias_laborales": work_days,
        "demanda_diaria": daily_demand,
        "demanda_diaria_calculada": demanda_diaria_calculada,
        "tiempo_entrega": lead_time,
        "inventario_seguridad": safety_stock,
        "opcionales_completos": opcionales_completos,
        "punto_reorden": punto_reorden,
        "cantidad_optima": q_optima,
        "inventario_maximo": inventario_maximo,
        "promedio_inventario": promedio_inventario,
        "numero_ordenes": numero_ordenes,
        "costo_anual_almacenado_base": costo_anual_almacenado_base,
        "costo_anual_almacenado": costo_anual_almacenado,
        "costo_anual_orden": costo_anual_orden,
        "costo_total_relevante": costo_total_relevante,
        "costo_total_operativo": costo_total_operativo,
        "costo_anual_compra": costo_anual_compra,
        "costo_total": costo_total,
        "advertencias": advertencias,
    }
