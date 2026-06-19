import math
import pandas as pd

def calcular_descuento_cantidad(D, Co, holding_value, is_percentage, discount_table):
    try:
        if D <= 0:
            return {"error": "La demanda anual (D) debe ser un número positivo."}
        if Co <= 0:
            return {"error": "El costo por ordenar (Co) debe ser un número positivo."}
        if holding_value <= 0:
            return {"error": "El costo o tasa de almacenamiento debe ser un número positivo."}

        if not discount_table or len(discount_table) == 0:
            return {"error": "La tabla de descuentos no puede estar vacía."}

        table = []
        for idx, row in enumerate(discount_table):
            try:
                min_qty = float(row.get('min_qty', 0))
                price   = float(row.get('price', 0))
                if min_qty < 0:
                    return {"error": f"La cantidad mínima en la fila {idx + 1} no puede ser negativa."}
                if price <= 0:
                    return {"error": f"El precio unitario en la fila {idx + 1} debe ser positivo."}
                table.append({'min_qty': min_qty, 'price': price})
            except (ValueError, TypeError):
                return {"error": f"Datos no numéricos o inválidos en la fila {idx + 1} de la tabla de descuentos."}

        table = sorted(table, key=lambda x: x['min_qty'])

        for i in range(len(table) - 1):
            if table[i]['min_qty'] == table[i+1]['min_qty']:
                return {"error": f"Hay cantidades mínimas duplicadas ({table[i]['min_qty']})."}
            if table[i]['price'] <= table[i+1]['price']:
                return {"error": f"El precio debe disminuir a medida que aumenta la cantidad. Nivel {i+1} ({table[i]['price']}) tiene un precio menor o igual al Nivel {i+2} ({table[i+1]['price']})."}

        for i in range(len(table)):
            if i < len(table) - 1:
                table[i]['max_qty'] = table[i+1]['min_qty'] - 1
            else:
                table[i]['max_qty'] = float('inf')

        filas_comparacion = []
        best_cost      = float('inf')
        best_level_idx = -1
        best_q         = 0
        best_price     = 0
        best_desglose  = {}

        for idx, level in enumerate(table):
            price = level['price']
            min_q = level['min_qty']
            max_q = level['max_qty']

            Ch_level = holding_value * price if is_percentage else holding_value

            if Ch_level <= 0:
                return {"error": f"El costo de almacenamiento calculado en el nivel {idx+1} es cero o negativo."}

            Q_teorico = math.sqrt((2 * D * Co) / Ch_level)

            status     = "CLE Válido"
            Q_ajustado = Q_teorico

            if Q_teorico < min_q:
                Q_ajustado = min_q
                status     = "Ajustado (Límite Inferior)"
            elif Q_teorico > max_q:
                Q_ajustado = max_q
                status     = "Ajustado (Límite Superior)"

            Q_final = max(min_q, round(Q_ajustado))

            if Q_final == min_q and Q_teorico < min_q:
                status = "Ajustado (Límite Inferior)"
            elif Q_final == max_q and Q_teorico > max_q:
                status = "Ajustado (Límite Superior)"
            else:
                status = "CLE Válido"

            material_cost = D * price
            ordering_cost = (D / Q_final) * Co
            holding_cost  = (Q_final / 2) * Ch_level
            total_cost    = material_cost + ordering_cost + holding_cost

            filas_comparacion.append({
                "Nivel":           idx + 1,
                "Rango":           f"{int(min_q):,} a {f'{int(max_q):,}' if max_q != float('inf') else 'o más'}",
                "Precio ($)":      price,
                "Q* Teórico":      round(Q_teorico, 2),
                "Q Real":          int(Q_final),
                "Costo Material":  material_cost,
                "Costo Ordenar":   ordering_cost,
                "Costo Almacenar": holding_cost,
                "Costo Total":     total_cost,
                "Estado / Ajuste": status
            })

            if total_cost < best_cost:
                best_cost      = total_cost
                best_level_idx = idx + 1
                best_q         = int(Q_final)
                best_price     = price
                best_desglose  = {
                    "material_cost": material_cost,
                    "ordering_cost": ordering_cost,
                    "holding_cost":  holding_cost
                }

        df_comparativo = pd.DataFrame(filas_comparacion)

        return {
            "Q_optimo":           best_q,
            "nivel_optimo":       best_level_idx,
            "precio_optimo":      best_price,
            "costo_total_minimo": best_cost,
            "desglose":           best_desglose,
            "tabla_comparativa":  df_comparativo,
            "error":              None
        }

    except ZeroDivisionError:
        return {"error": "Error de división por cero detectado. Verifique que los valores ingresados sean correctos."}
    except Exception as e:
        return {"error": f"Error inesperado en el cálculo del modelo de descuentos: {str(e)}"}
