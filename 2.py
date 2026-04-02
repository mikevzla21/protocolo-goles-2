import streamlit as st
import math

# 1. Configuración de página (Modo Wide para que se adapte mejor)
st.set_page_config(page_title="Analizador Miguel", layout="wide", page_icon="⚽")

# 2. Estilo CSS para que en el celular los botones sean grandes y fáciles de tocar
st.markdown("""
    <style>
    /* Optimización para móviles */
    @media (max-width: 640px) {
        .stButton>button {
            width: 100% !important;
            height: 3.5em !important;
            font-size: 18px !important;
            border-radius: 12px !important;
            margin-bottom: 10px;
        }
        .stNumberInput, .stSelectbox {
            margin-bottom: 15px;
        }
    }
    /* Estilo general de los botones */
    .stButton>button {
        transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR LÓGICO MAESTRO (MATRIZ A-Z) ---
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
    # Encontrar el lambda más cercano
    lambda_ref = min(matriz.keys(), key=lambda x: abs(x - l_total))
    o15_f, o25_f, letra = matriz[lambda_ref]
    return max(1, o15_f), max(1, o25_f), l_total, letra

st.write("### ⚽ ANALIZADOR DE GOLES MIGUEL")

# Inicialización de estado
if 'analisis_realizado' not in st.session_state:
    st.session_state.analisis_realizado = False
    st.session_state.resultados = {}

def limpiar_pantalla():
    st.session_state.analisis_realizado = False
    st.session_state.resultados = {}

# --- ENTRADA DE DATOS (SIDEBAR PARA MÓVIL) ---
with st.sidebar:
    st.header("⚙️ Parámetros de entrada")
    tipo_p = st.selectbox("Tipo de Partido", ["Liga", "Torneo", "Campo Neutral / Amistoso"])
    
    label_loc_a, label_loc_c = "", ""
    label_vis_a, label_vis_c = "", ""
    deshabilitar_puestos = False
    jornada_val = 1
    
    if tipo_p == "Liga":
        jornada_val = st.number_input("Jornada", min_value=1, value=7)
        if jornada_val >= 6:
            label_loc_a, label_loc_c = "en casa (Local)", "en casa (Local)"
            label_vis_a, label_vis_c = "fuera de casa (Visitante)", "fuera de casa (Visitante)"
        else:
            label_loc_a, label_loc_c = "generales (Local)", "generales (Local)"
            label_vis_a, label_vis_c = "generales (Visitante)", "generales (Visitante)"
            
    elif tipo_p == "Torneo":
        deshabilitar_puestos = True
        st.write("¿Ronda <= 5?")
        ronda_inicial = st.radio("Selecciona:", ["Si", "No"], horizontal=True)
        if ronda_inicial == "Si":
            label_loc_a, label_loc_c = "generales", "generales"
            label_vis_a, label_vis_c = "generales", "generales"
        else:
            label_loc_a, label_loc_c = "en casa (Local)", "en casa (Local)"
            label_vis_a, label_vis_c = "fuera de casa (Visitante)", "fuera de casa (Visitante)"
    else:
        deshabilitar_puestos = True
        label_loc_a, label_loc_c = "generales (Local)", "generales (Local)"
        label_vis_a, label_vis_c = "generales (Visitante)", "generales (Visitante)"

    st.markdown("---")
    st.subheader("📊 Datos Local")
    l_a = st.number_input(f"Anotados {label_loc_a}", value=1.50, key="input_l_a")
    l_c = st.number_input(f"Concedidos {label_loc_c}", value=1.00, key="input_l_c")
    puesto_l = st.number_input("Puesto tabla local", value=1, min_value=1, disabled=deshabilitar_puestos)
    baja_l = st.checkbox("¿Baja sensible (Estrella equipo)?", key="bl")
    suplente_l = st.checkbox("¿Suplentes local >=3?", key="sl")

    st.markdown("---")
    st.subheader("📊 Datos Visitante")
    v_a = st.number_input(f"Anotados {label_vis_a}", value=1.50, key="input_v_a")
    v_c = st.number_input(f"Concedidos {label_vis_c}", value=1.00, key="input_v_c")
    puesto_v = st.number_input("Puesto tabla visitante", value=15, min_value=1, disabled=deshabilitar_puestos)
    baja_v = st.checkbox("¿Baja sensible (Estrella equipo)? ", key="bv") # Espacio extra para key única
    suplente_v = st.checkbox("¿Suplentes visita >=3?", key="sv") 

# --- LÓGICA DE CÁLCULO ---
if st.button("EJECUTAR ANÁLISIS"):
    # Promedios cruzados (Dividido entre 2 para convergencia)
    l_loc_calc = (l_a + v_c) / 2
    l_vis_calc = (v_a + l_c) / 2
    
    # Ajustes por bajas o suplentes (-10% cada uno)
    adj_l = 1.0 - (0.10 if baja_l else 0) - (0.10 if suplente_l else 0)
    adj_v = 1.0 - (0.10 if baja_v else 0) - (0.10 if suplente_v else 0)
    l_loc_calc *= adj_l
    l_vis_calc *= adj_v

    # Ajuste por Choque de Fuerzas (Puestos)
    if not deshabilitar_puestos:
        l_loc_calc *= 1.15 # Bono base local
        if jornada_val >= 6 and abs(puesto_l - puesto_v) >= 10:
            if puesto_l < puesto_v:
                l_loc_calc *= 1.05; l_vis_calc *= 0.85 # Favorito local
            else:
                l_loc_calc *= 0.85; l_vis_calc *= 1.10 # Favorito visita

    # Obtener resultados de matriz
    o15, o25, l_total, letra_id = motor_logico_maestro(l_loc_calc + l_vis_calc)
    
    st.session_state.analisis_realizado = True
    st.session_state.resultados = {
        "letra": letra_id, "lambda": l_total, "o15": o15, "o25": o25,
        "l_loc": l_loc_calc, "l_vis": l_vis_calc
    }

# --- MOSTRAR RESULTADOS (ADAPTADO A MÓVIL) ---
if st.session_state.analisis_realizado:
    res = st.session_state.resultados
    p_val = round(res["o25"])
    
    v_msg, v_col, es_r, es_s = "VALUE DESCONOCIDO", "#f39c12", False, False
    val_o = ""

    # Filtros de Valor según tu protocolo
    if 57 <= p_val <= 59 or p_val == 65 or 72 <= p_val <= 73: 
        v_msg, v_col, val_o, es_s = "VALUE SÓLIDO: 1.5 GOLES", "#00ff00", "OVER 1.5", True
    elif 61 <= p_val <= 64: 
        v_msg, v_col, val_o, es_s = "VALUE SÓLIDO: 2.5 GOLES", "#00ff00", "OVER 2.5", True
    elif p_val in [70, 71]: 
        v_msg, v_col, es_r = "VALUE RIESGOSO 1.5 (RANGO 70/71)", "#e74c3c", True
    elif p_val == 60:
        v_msg, v_col, es_r = "VALUE RIESGOSO 2.5 (RANGO 60)", "#e74c3c", True
    elif p_val == 74:
        v_msg, v_col, es_r = "VALUE RIESGOSO (RANGO 74)", "#e74c3c", True

    prob_loc = (res["l_loc"] / (res["lambda"] + 0.001)) * 100
    prob_vis = (res["l_vis"] / (res["lambda"] + 0.001)) * 100
    equipo_f = "Local" if prob_loc > prob_vis else "Visitante"
    
    # Estrategia sugerida
    if res["lambda"] <= 1.99: est, nota = f"D.O {equipo_f} y Under 4.5", "(λ conservadora)"
    elif es_r: est, nota = f"Doble Oportunidad {equipo_f}", f"({v_msg})"
    elif val_o != "": est, nota = f"D.O {equipo_f} y {val_o}", f"({val_o} directo viable)"
    else: est, nota = f"Doble Oportunidad {equipo_f}", "(Sin patrón claro)"

    # Layout de resultados (Se apila en móviles automáticamente)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"| Mercado | Probabilidad |\n| :--- | :--- |\n| Over 1.5 | {res['o15']:.1f}% |\n| Over 2.5 | {res['o25']:.1f}% |\n| Victoria Local | {prob_loc:.1f}% |\n| Victoria Visitante | {prob_vis:.1f}% |")
        st.markdown(f"""<div style="background-color:#4a4a4a; padding:12px; border-radius:8px; color:white; text-align:center;">
            <span style="font-size:0.8em;">ESTRATEGIA SUGERIDA:</span><br>
            <span style="font-size:1.1em; font-weight:bold;">{est.upper()}</span><br>
            <span style="font-size:0.8em; font-style:italic;">{nota}</span>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div style="border-left:5px solid {v_col}; background-color:#1e1e1e; padding:15px; font-weight:bold; color:white; border-radius:0 8px 8px 0;">FILTRO: {v_msg}</div>''', unsafe_allow_html=True)
        st.write(f"**λ Total:** {res['lambda']:.2f} | **Letra:** {res['letra']}")

    st.markdown("---")
    # Sección de Cuotas para el análisis final
    with st.expander("📊 ¿ANALIZAR CON CUOTAS?", expanded=True):
        col_q1, col_q2 = st.columns(2)
        cuo_l = col_q1.number_input("Cuota Local", value=1.0, step=0.01, key="ql")
        cuo_v = col_q2.number_input("Cuota Visitante", value=1.0, step=0.01, key="qv")
        
        if st.button("VEREDICTO RIGUROSO"):
            fav = "Local" if cuo_l < cuo_v else "Visitante"
            c_min = min(cuo_l, cuo_v)
            if c_min < 1.10: st.warning(f"🚨 **SUPER FAVORITO:** {fav}.")
            elif 1.10 <= c_min <= 1.50: st.info(f"🏆 **Favoritismo Absoluto:** {fav}.")
            elif 1.51 <= c_min <= 1.85: st.info(f"⚖️ **Favoritismo Moderado:** {fav}.")
            else: st.info(f"⚔️ **Parejo.**")
            
            if es_s: st.success(f"🎯 **SINCRO:** Filtro Sólido respalda la apuesta.")
            elif es_r: st.error(f"📉 **DIVERGENCIA:** El filtro marca riesgo.")
            else: st.warning(f"⚠️ **SINCRO INCIERTO.**")

    st.button("LIMPIAR ANÁLISIS", on_click=limpiar_pantalla, type="primary")
