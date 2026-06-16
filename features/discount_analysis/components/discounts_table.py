import streamlit as st
import pandas as pd

DEFAULT_DISCOUNTS = {
    "Cantidad Mínima": pd.Series(dtype='float64'),
    "Precio Unitario": pd.Series(dtype='float64')
}

def init_discount_table():
    if "discount_df" not in st.session_state:
        st.session_state.discount_df = pd.DataFrame(DEFAULT_DISCOUNTS)

def validate_discount_df(df):
    if df.empty:
        return False, "La tabla no puede estar vacía."
    if df.isnull().values.any():
        return False, "Por favor complete todas las celdas de la tabla."
    try:
        min_q = df["Cantidad Mínima"].astype(float).tolist()
        prices = df["Precio Unitario"].astype(float).tolist()
    except Exception:
        return False, "Todos los valores en la tabla deben ser números."
        
    sorted_pairs = sorted(zip(min_q, prices), key=lambda x: x[0])
    
    for q, p in sorted_pairs:
        if q < 0:
            return False, "Las cantidades mínimas no pueden ser negativas."
        if p <= 0:
            return False, "Los precios deben ser mayores a cero."
            
    for i in range(len(sorted_pairs) - 1):
        if sorted_pairs[i][0] == sorted_pairs[i+1][0]:
            return False, f"Cantidad mínima duplicada en {sorted_pairs[i][0]:,.0f}."
        if sorted_pairs[i][1] <= sorted_pairs[i+1][1]:
            return False, f"Los precios deben ser decrecientes. El precio unitario de {sorted_pairs[i+1][0]:,.0f} ({sorted_pairs[i+1][1]:.2f}) debe ser menor que el de {sorted_pairs[i][0]:,.0f} ({sorted_pairs[i][1]:.2f})."
            
    return True, ""

def on_discount_table_change():
    editor_state = st.session_state.discount_table_editor
    updated_df = st.session_state.discount_df.copy()

    for idx, changes in editor_state.get("edited_rows", {}).items():
        for col, val in changes.items():
            updated_df.at[idx, col] = val

    for row in editor_state.get("added_rows", []):
        new_row = {col: row.get(col, None) for col in updated_df.columns}
        updated_df = pd.concat([updated_df, pd.DataFrame([new_row])], ignore_index=True)

    deleted = editor_state.get("deleted_rows", [])
    if deleted:
        updated_df = updated_df.drop(index=deleted).reset_index(drop=True)

    st.session_state.discount_df = updated_df

def render_discounts_table():
    init_discount_table()
    
    st.markdown('<div style="margin-top:15px; margin-bottom:5px; font-weight:600; color:#e5e7eb; font-size:14px;">Tabla de Rangos de Descuento</div>', unsafe_allow_html=True)
    st.caption("Nota: Agregue o modifique filas para definir los niveles de descuento. Asegúrese de que las cantidades mínimas sean crecientes y los precios decrecientes.")
    
    st.data_editor(
        st.session_state.discount_df,
        key="discount_table_editor",
        on_change=on_discount_table_change,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cantidad Mínima": st.column_config.NumberColumn(
                label="Cantidad Mínima",
                min_value=0,
                step=1,
                format="%d",
                required=True
            ),
            "Precio Unitario": st.column_config.NumberColumn(
                label="Precio Unitario",
                min_value=0.01,
                step=0.01,
                format="$%.2f",
                required=True
            )
        }
    )
    
    valid, message = validate_discount_df(st.session_state.discount_df)
    if not valid:
        if st.session_state.discount_df.empty:
            st.info("💡 La tabla de descuentos está vacía. Ingrese al menos un rango (ej: Cantidad Mínima 0 y su Precio Unitario) para comenzar.")
        else:
            st.warning(f"⚠️ {message}")
    else:
        st.success("✓ Tabla de descuentos configurada correctamente.")
        
    return valid, message