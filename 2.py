import streamlit as st
import math

st.set_page_config(page_title="Analizador Miguel V2", layout="wide")

def motor_logico_maestro(l_tu, l_ri, t_a, r_a, t_c, r_c):
    """
    Motor V2.4 Blindado: Prioridad a Patrones Maestros y Filtros de Realidad.
    """
    l_total = round(l_tu + l_ri, 2)
    
    # 1. BASE DE DATOS DE PATRONES MAESTROS (MIGUEL)
    patrones = {
        2.0: (71.0, 43.0), 2.1: (86.0, 59.0), 2.2: (77.0, 50.0), 2.3: (93.0, 71.0),
        2.5: (93.0, 72.0), 2.6: (85.0, 61.0), 2.7: (94.0, 74.0), 3.0: (87.0, 62.0),
        3.1: (88.0, 64.0), 3.2: (87.0, 63.0), 3.6: (92.0, 71.0), 4.0: (87.0, 62.0),
        4.6: (89.0, 72.0), 4.7: (93.0, 74.0)
    }

    # Verificación de Patrón Maestro (Salida inmediata si coincide)
    for l_ref, values in patrones.items():
        if abs(l_total - l_ref) <= 0.05:
            return values[0], values[1], l_total, True

    # 2. CÁLCULO DINÁMICO (Respaldo si no hay patrón)
    p0 = math.exp(-l_total)
    p1 = l_total * math.exp(-l_total)
    p2 = (math.pow(l_total, 2) / 2) * math.exp(-l_total)
    
    o15_f = (1 - (p0 + p1)) * 100
    o25_f = (1 - (p0 + p1 + p2)) * 100

    # 3. FILTRO DE REALIDAD (MIGUEL PROTOCOL)
    ataque_total = t_a + r_a
    # Si los ataques no llegan a 2.6, capamos el Over para evitar trampas de defensas malas
    if ataque_total < 2.6:
        o25_f = min(o25_f, 45.0)
        o15_f = min(o15_f, 70.0)
        
    # Si las defensas son exageradas (>2.8) pero el ataque es bajo, Poisson miente
    if (t_c > 2.8 or r_c > 2.8) and ataque_total < 2.8:
        o15_f -= 15.0
        o25_f -= 20.0

    return max(10, o15_f), max(5, o25_f), l_total, False

st.write("### ⚽ ANALIZADOR DE GOLES MIGUEL")

with st.sidebar:
    st.header("⚙️ Parámetros")
    t_a = st.number_input("Tus Goles Anotados", value=1.60)
    t_c = st.number_input("Tus Goles Concedidos", value=1.50)
    st.markdown("---")
    r_a = st.number_input("Rival Goles Anotados", value=1.50)
    r_c = st.number_input("Rival Goles Concedidos", value=1.60)
    m_l = st.number_input("Media Goles Liga", value=1.30)

if st.button("EJECUTAR ANÁLISIS"):
    # Lambdas puros
    l_tu = (t_a * r_c) / m_l
    l_ri = (r_a * t_c) / m_l
    
    # Aplicar Motor V2.4
    o15, o25, l_total, es_maestro = motor_logico_maestro(l_tu, l_ri, t_a, r_a, t_c, r_c)
    
    # Ambos Marcan (Basado en equilibrio)
    p_tu_0 = math.exp(-max(l_tu, 0.001))
    p_ri_0 = math.exp(-max(l_ri, 0.001))
    btts = ((1 - p_tu_0) * (1 - p_ri_0) * 100) + (5.0 if abs(l_tu - l_ri) < 0.5 else -5.0)
    
    # Under deducido matemáticamente
    u35 = 100 - (o25 * 0.75)
    u45 = 100 - (o25 * 0.35)

    # --- LÓGICA DE VEREDICTO DE PRECISIÓN (MIGUEL PROTOCOL) ---
    p_val = round(o25)
    veredicto = "VALUE DESCONOCIDO"
    color = "#f39c12" # Naranja por defecto

    if 57 <= p_val <= 59:
        veredicto, color = "VALUE SÓLIDO: 1.5 GOLES", "#00ff00"
    elif 60 <= p_val <= 64:
        veredicto, color = "VALUE SÓLIDO: 2.5 GOLES", "#00ff00"
    elif p_val == 65:
        veredicto, color = "VALUE SÓLIDO: 1.5 GOLES", "#00ff00"
    elif 70 <= p_val <= 74:
        veredicto, color = "VALUE SÓLIDO: 1.5 GOLES", "#00ff00"
    elif p_val >= 75:
        # Modificación integrada: Búnker para asegurar el 1.5
        veredicto, color = "BÚNKER: OVER 1.5 (SEGURIDAD MÁXIMA)", "#00d4ff"

    # Información de cabecera
    if es_maestro:
        st.success(f"✅ PATRÓN MAESTRO DETECTADO: λ ≈ {l_total:.2f}")
    else:
        st.info(f"Fuerza de Ataque: Tú ({l_tu:.2f}) vs Rival ({l_ri:.2f}) | Total: {l_total:.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📝 Cuadro de Probabilidades")
        st.markdown(f"""
| Mercado | Probabilidad |
| :--- | :--- |
| **Ambos Marcan (BTTS)** | **{max(min(btts, 98.0), 10.0):.1f}%** |
| Over 1.5 | {o15:.1f}% |
| Over 2.5 | {o25:.1f}% |
| Under 3.5 | {u35:.1f}% |
| Under 4.5 | {u45:.1f}% |
| Victoria Tú | {((l_tu) / (l_total + 0.001)) * 100:.1f}% |
""")

    with col2:
        st.markdown("#### 🎯 Patrón Visual Clave")
        st.write(f"* **Anotados combinados:** {t_a + r_a:.2f}")
        st.write(f"* **Pico probable:** {l_total:.2f} goles.")
        
        diferencia = abs(l_tu - l_ri)
        diagnostico = "EQUILIBRADO (Impulsa el Over)" if diferencia <= 0.5 else "DESBALANCEADO (Frena el Over)"
        st.write(f"* **Distribución:** {diagnostico}")
        
        st.write("")
        # Recuadro de Veredicto con tu estética original
        st.markdown(f'<div style="border-left:5px solid {color}; background-color:#1e1e1e; padding:15px; font-weight:bold; color:white;">FILTRO: {veredicto}</div>', unsafe_allow_html=True)
        
        if (t_a + r_a) < 2.6:
            st.warning("⚠️ ALERTA: Ataque insuficiente para confiar en Overs.")