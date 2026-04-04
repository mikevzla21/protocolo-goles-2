import streamlit as st

# 1. Configuración de página e Interfaz (ESTÉTICA ORIGINAL)
st.set_page_config(page_title="Analizador Miguel", layout="wide", page_icon="⚽")

st.markdown("""
    <style>
    @media (max-width: 640px) {
        .stButton>button { width: 100% !important; height: 3.5em !important; font-size: 18px !important; border-radius: 12px !important; margin-bottom: 10px; }
    }
    .boton-rojo>div>button { background-color: #e74c3c !important; color: white !important; font-weight: bold !important; border: 2px solid #c0392b !important; }
    .alerta-cuota { background-color: #ff9800; color: white; padding: 12px; border-radius: 8px; font-weight: bold; text-align: center; margin-bottom: 20px; border: 2px solid #e67e22; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR LÓGICO MAESTRO ---
def motor_logico_maestro(l_total):
    matriz = {
        2.61: (84.0, 57.0, "A"), 2.71: (86.0, 59.0, "B"), 3.54: (93.0, 71.0, "C/K"),
        2.72: (85.0, 61.0, "D"), 2.81: (87.0, 63.0, "E"), 2.14: (77.0, 50.0, "F"),
        2.57: (83.0, 56.0, "G"), 3.46: (93.0, 70.0, "H"), 3.70: (94.0, 74.0, "I"),
        2.15: (71.0, 43.0, "J"), 2.64: (84.0, 59.0, "L"), 1.81: (65.0, 30.0, "M"),
        3.69: (92.0, 71.0, "N"), 2.78: (77.0, 52.0, "Ñ"), 2.33: (72.0, 41.0, "O"),
        3.40: (89.0, 65.0, "P"), 3.96: (94.0, 76.0, "Q"), 3.48: (91.0, 68.0, "R"),
        3.29: (87.0, 62.0, "S"), 3.81: (93.0, 74.0, "T"), 2.40: (72.0, 46.0, "U"),
        3.75: (89.0, 72.0, "V"), 3.71: (94.0, 74.0, "W"), 1.45: (52.0, 17.0, "X"),
        2.89: (88.0, 62.0, "Y"), 3.11: (89.0, 64.0, "Z"),
        3.30: (91.0, 66.0, "A2"), 2.68: (85.0, 58.0, "B2"), 3.90: (95.0, 77.0, "D2"),
        3.32: (91.0, 66.0, "E2"), 3.74: (94.0, 74.0, "F2"), 2.13: (76.0, 26.0, "G2"),
        4.08: (96.0, 80.0, "H2"), 4.00: (95.0, 78.0, "I2"), 2.37: (81.0, 54.0, "L2"),
        2.47: (82.0, 54.0, "M2"), 2.70: (85.0, 60.0, "N2"), 2.36: (80.0, 53.0, "Ñ2"),
        1.19: (50.0, 19.0, "O2"), 2.04: (67.0, 38.0, "P2"), 1.55: (59.0, 32.0, "Q2"),
        2.78: (86.0, 62.0, "R2"), 2.02: (66.0, 37.0, "S2"), 2.31: (78.0, 51.0, "T2"),
        2.09: (69.0, 40.0, "U2"), 2.15: (71.0, 43.0, "V2"), 2.61: (84.0, 58.0, "W2"),
        2.27: (76.0, 49.0, "X2"), 1.81: (65.0, 30.0, "Y2")
    }
    ref = min(matriz.keys(), key=lambda x: abs(x - l_total))
    o15_f, o25_f, letra = matriz[ref]
    return max(1, o15_f), max(1, o25_f), l_total, letra

st.write("### ⚽ ANALIZADOR MIGUEL")

if 'analisis_realizado' not in st.session_state:
    st.session_state.analisis_realizado = False
    st.session_state.resultados = {}

def limpiar_pantalla():
    st.session_state.analisis_realizado = False
    st.session_state.resultados = {}

# --- PARÁMETROS DE ENTRADA ---
with st.sidebar:
    st.header("⚙️ Parámetros de entrada")
    tipo_p = st.selectbox("Tipo de Partido", ["Liga", "Torneo", "Campo Neutral / Amistoso"])
    es_liga = (tipo_p == "Liga")
    jornada_val = st.number_input("Jornada", min_value=1, value=7, disabled=not es_liga)
    
    st.markdown("---")
    st.markdown("### 📊 Datos Local")
    l_a = st.number_input("Anotados Local", value=1.50, key="la_input")
    l_c = st.number_input("Concedidos Local", value=1.00, key="lc_input")
    puesto_l = st.number_input("Puesto tabla local", value=1, min_value=1, key="pl_input", disabled=not es_liga)
    baja_l = st.checkbox("¿Baja sensible Local? (Estrella lesionada)", key="bl")
    sup_l = st.checkbox("¿Suplentes local >=3?", key="sl")

    st.markdown("---")
    st.markdown("### 📊 Datos Visitante")
    v_a = st.number_input("Anotados Visitante", value=1.50, key="va_input")
    v_c = st.number_input("Concedidos Visitante", value=1.00, key="vc_input")
    puesto_v = st.number_input("Puesto tabla visitante", value=15, min_value=1, key="pv_input", disabled=not es_liga)
    baja_v = st.checkbox("¿Baja sensible Visitante? (Estrella lesionada)", key="bv")
    sup_v = st.checkbox("¿Suplentes visita >=3?", key="sv")

# --- PROCESAMIENTO ---
if st.button("EJECUTAR ANÁLISIS", key="main_exec"):
    l_loc_calc = ((l_a + v_c)/2) * (1 - (0.1 if baja_l else 0) - (0.1 if sup_l else 0))
    l_vis_calc = ((v_a + l_c)/2) * (1 - (0.1 if baja_v else 0) - (0.1 if sup_v else 0))
    
    if es_liga and jornada_val >= 6:
        l_loc_calc *= 1.15
        if abs(puesto_l - puesto_v) >= 10:
            if puesto_l < puesto_v: l_loc_calc *= 1.05; l_vis_calc *= 0.85
            else: l_loc_calc *= 0.85; l_vis_calc *= 1.10
    
    o15, o25, lt, letra = motor_logico_maestro(l_loc_calc + l_vis_calc)
    st.session_state.analisis_realizado = True
    st.session_state.resultados = {"o15": o15, "o25": o25, "lt": lt, "letra": letra, "ll": l_loc_calc, "lv": l_vis_calc, "la": l_a, "va": v_a, "lc_l": l_c, "lc_v": v_c}

# --- RESULTADOS ---
if st.session_state.analisis_realizado:
    res = st.session_state.resultados
    p_val = round(res["o25"])
    pico = round(res['lt'])
    
    f_msg, f_col, f_tipo, bloqueado = "SIN PATRÓN CLARO", "#4a4a4a", "VACIO", True
    
    if p_val in [57, 58, 59, 65, 72, 73]: 
        f_msg, f_col, f_tipo, bloqueado = "VALUE SÓLIDO: 1.5 GOLES", "#00ff00", "1.5", False
    elif 61 <= p_val <= 64: 
        f_msg, f_col, f_tipo, bloqueado = "VALUE SÓLIDO: 2.5 GOLES", "#00ff00", "2.5", False
    elif p_val in [70, 71, 74]: 
        f_msg, f_col, f_tipo, bloqueado = "VALUE 1.5 RIESGOSO", "#e74c3c", "RIESGO_15", False
    elif p_val == 60: 
        f_msg, f_col, f_tipo, bloqueado = "VALUE 2.5 RIESGOSO", "#e74c3c", "RIESGO_25", False

    if f_tipo in ["1.5", "2.5"]:
        st.markdown(f'<div class="alerta-cuota">⚠️ VALUE {f_tipo} DETECTADO: Comprobar cuotas Local/Visita y Over 1.5 PARA CORROBORAR SOLIDEZ DEL VEREDICTO</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        prob_loc = (res["ll"] / (res["lt"] + 0.001)) * 100
        prob_vis = (res["lv"] / (res["lt"] + 0.001)) * 100
        fav = "Local" if prob_loc > prob_vis else "Visitante"
        st.markdown(f"| Mercado | Probabilidad |\n| :--- | :--- |\n| Over 1.5 | **{res['o15']:.1f}%** |\n| Over 2.5 | **{res['o25']:.1f}%** |\n| Victoria Local | {prob_loc:.1f}% |\n| Victoria Visitante | {prob_vis:.1f}% |")
        
        est = f"Doble Oportunidad {fav}"
        if f_tipo == "1.5" or f_tipo == "RIESGO_15": est += " y Over 1.5"
        elif f_tipo == "2.5" or f_tipo == "RIESGO_25": est += " y Over 2.5"
        
        st.markdown(f"""<div style="background-color:#4a4a4a; padding:12px; border-radius:8px; color:white; text-align:center;">
            <span style="font-size:0.8em;">ESTRATEGIA SUGERIDA:</span><br><b>{est.upper()}</b>
        </div>""", unsafe_allow_html=True)

    with c2:
        defensas = "OVER SÓLIDO" if (res["lc_l"] > 1.2 and res["lc_v"] > 1.2) else "EQUILIBRADO"
        st.markdown("### 🎯 Patrón visual clave")
        st.markdown(f"* Anotados combinados: **{(res['la'] + res['va']):.1f}**")
        st.markdown(f"* Ambas defensas permeables = **{defensas}**")
        st.markdown(f"* Desbalance/Equilibrio → **{pico} goles pico probable.**")
        st.markdown(f'''<div style="border-left:5px solid {f_col}; background-color:#1e1e1e; padding:15px; font-weight:bold; color:white; border-radius:0 8px 8px 0;">FILTRO: {f_msg}</div>''', unsafe_allow_html=True)
        st.write(f"**λ Total:** {res['lt']:.2f} | **Letra:** {res['letra']}")

    # --- ANALIZADOR DE CUOTAS Y SINCRO ---
    st.markdown("---")
    with st.expander("📊 ANALIZADOR DE CUOTAS Y SINCRO", expanded=True):
        pico_2 = (pico == 2)
        if bloqueado and not pico_2:
            st.warning("🚫 ANALIZADOR DESHABILITADO: El filtro no marca un patrón claro.")
        else:
            cq1, cq2, cq3 = st.columns(3)
            c_l = cq1.number_input("Cuota Victoria Local", 1.0, 10.0, 1.85, disabled=pico_2, key="key_c_loc")
            c_v = cq2.number_input("Cuota Victoria Visitante", 1.0, 10.0, 3.50, disabled=pico_2, key="key_c_vis")
            c_o15 = cq3.number_input("Cuota Over 1.5 Goles", 1.0, 5.0, 1.20, key="key_c_o15")

            if st.button("ANALIZAR SINCRO", key="key_btn_sincro"):
                if f_tipo == "2.5":
                    if c_o15 <= 1.22:
                        st.success("✅ SINCRO ÉXITO: Flujo validado para Over 2.5.")
                        if es_liga:
                            st.success("**RECOMENDACIÓN: Over 2.5 combinado con over de córners 'X-3'**")
                        else:
                            st.success("**RECOMENDACIÓN: Over 2.5 sin combinar con over de córners**")
                    elif 1.23 <= c_o15 <= 1.33:
                        st.error("🚨 CONFLICTO: Cuota alta para Over 2.5.")
                        if es_liga: st.success("**Recomendación: Under 3.5 goles combinado con over de córners 'X+3'**")
                        else: st.success("**Recomendación: Under 3.5 goles sin combinar con córners**")

                elif f_tipo in ["RIESGO_15", "RIESGO_25", "1.5"] or pico_2:
                    if c_o15 <= 1.22:
                        st.error("🚨 Recomendación: No operar 1.5 goles. Riesgo latente por recompensa no compensable")
                    elif 1.23 <= c_o15 <= 1.33:
                        if es_liga: st.success("**Recomendación: Under 3.5 goles combinado con over de córners 'X+3'**")
                        else: st.success("**Recomendación: Under 3.5 goles sin combinar con córners**")

    st.button("LIMPIAR ANÁLISIS", on_click=limpiar_pantalla, type="primary", key="btn_limpiar")
