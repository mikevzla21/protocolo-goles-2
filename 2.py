import streamlit as st
import requests
from datetime import datetime
import pytz
import json
import os
import telebot

# --- CONFIGURACIÓN DE SEGURIDAD Y TELEGRAM ---
try:
    MI_KEY_PRIVADA = st.secrets["MI_KEY_PRIVADA"]
    TOKEN_TELEGRAM = st.secrets["TOKEN_TELEGRAM"]
    CHAT_ID_CANAL = st.secrets["CHAT_ID_CANAL"]
except:
    MI_KEY_PRIVADA = "7a7a86dd262319eb7c938354c20c7215"
    TOKEN_TELEGRAM = "8331811774:AAEuXEMABQE_uH4DZEovQXaiP6uG_3bqrgM"
    CHAT_ID_CANAL = "-1003959034940"

bot_telegram = telebot.TeleBot(TOKEN_TELEGRAM)

# 1. Configuración de página e Interfaz
st.set_page_config(page_title="Analizador Miguel", layout="wide", page_icon="⚽")

if 'memoria_ligas' not in st.session_state:
    st.session_state.memoria_ligas = {}

# --- BLOQUE DE MEMORIA ACTUALIZADO (CON PERSISTENCIA DE LIGAS) ---
def cargar_memoria_bot():
    if os.path.exists("memoria_bot.json"):
        try:
            with open("memoria_bot.json", "r") as f:
                data = json.load(f)
                if "memoria_ligas" in data:
                    for liga, nivel in data["memoria_ligas"].items():
                        st.session_state.memoria_ligas[liga] = nivel
                return data
        except: pass
    return {
        "ultimo_lote": 0, 
        "fecha_actual": "", 
        "enviados": [], 
        "acertados": 0, 
        "fallados": 0,
        "patrones_fallidos": {},
        "memoria_ligas": {} 
    }

def guardar_memoria_bot(datos):
    datos["memoria_ligas"] = st.session_state.memoria_ligas
    with open("memoria_bot.json", "w") as f:
        json.dump(datos, f)

memoria_temp = cargar_memoria_bot()

# CSS Original
st.markdown("""
    <style>
    @media (max-width: 640px) {
        .stButton>button { width: 100% !important; height: 3.5em !important; font-size: 18px !important; border-radius: 12px !important; margin-bottom: 10px; }
    }
    .boton-rojo>div>button { background-color: #e74c3c !important; color: white !important; font-weight: bold !important; border: 2px solid #c0392b !important; }
    .alerta-cuota { background-color: #ff9800; color: white; padding: 12px; border-radius: 8px; font-weight: bold; text-align: center; margin-bottom: 20px; border: 2px solid #e67e22; font-size: 1.1em; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1e1e1e; border-radius: 5px 5px 0 0; color: white; padding: 10px 20px; }
    .stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] { border-bottom: 4px solid #00ff00 !important; background-color: #2e2e2e !important; }
    .stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] { border-bottom: 4px solid #ff0000 !important; background-color: #2e2e2e !important; }
    </style>
    """, unsafe_allow_html=True)

NIVELES_CONFIG = {
    "🟢 Profesional (1ra)": "🟢",
    "🟡 Ascenso (2da/3ra)": "🟡",
    "🟠 Ligas Menores (4ta+)": "🟠",
    "🔵 Copas / Torneos": "🔵",
    "⚪ Especial (Fem/Amat/U23)": "⚪"
}

def asignar_color_nivel(liga_nombre, pais_nombre, equipo_h, equipo_a):
    if liga_nombre in st.session_state.memoria_ligas:
        return st.session_state.memoria_ligas[liga_nombre]
    nombre_full = (liga_nombre + " " + pais_nombre).lower()
    equipos_full = (equipo_h + " " + equipo_a).lower()
    KEYWORDS_FEM = ["women", "femenino", "femenil", "nwsl", "wsl", "liga f", "première ligue", "shebelieves", "gold cup", "w champions cup"]
    if any(x in nombre_full or x in equipos_full for x in KEYWORDS_FEM + ["u17", "u19", "u20", "u21", "u22", "u23", "amateur", "reserve", "youth", "ncaa"]):
        return "⚪"
    elite_keywords = ["premier league", "bundesliga", "serie a", "laliga", "la liga", "ligue 1", "super lig", "trendyol süper lig", "eredivisie", "futve", "liga mx", "dimayor", "primera a", "liga profesional", "brasileiro serie a", "carioca", "paulista", "liga 1", "liga pro", "liga portugal", "betclic", "saudi pro league", "pro league", "jupiler", "ekstraklasa", "parva liga", "superliga româniei", "liga i"]
    if any(x in nombre_full for x in elite_keywords) and not any(y in nombre_full for y in ["second", "2. division", "segunda", "division b"]):
        return "🟢"
    ascenso_keywords = ["championship", "2. bundesliga", "serie b", "laliga 2", "la liga 2", "hypermotion", "league one", "segunda"]
    if any(x in nombre_full for x in ascenso_keywords):
        return "🟡"
    if any(x in nombre_full for x in ["cup", "trophy", "copa", "fa cup", "pokal", "libertadores", "sudamericana", "champions league", "playoffs"]):
        return "🔵"
    return "🟠"

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

def buscar_partidos_fecha(fecha_obj, zona_horaria):
    f_str = fecha_obj.strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-apisports-key': MI_KEY_PRIVADA}
    params = {"date": f_str}
    PAISES_TOP = ["Spain", "England", "Germany", "Italy", "France", "Netherlands", "Brazil", "Argentina", "Mexico", "USA", "Portugal", "Venezuela", "Colombia", "Saudi Arabia", "Belgium", "Bulgaria", "Poland", "Romania", "Turkey"]

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            eventos = data.get('response', [])
            lista_final = []
            tz_local = pytz.timezone(zona_horaria)
            for ev in eventos:
                liga_nombre = ev.get('league', {}).get('name', 'Desconocida')
                pais_nombre = ev.get('league', {}).get('country', 'Internacional')
                h = ev.get('teams', {}).get('home', {}).get('name', 'Local')
                a = ev.get('teams', {}).get('away', {}).get('name', 'Visita')
                nivel_actual = asignar_color_nivel(liga_nombre, pais_nombre, h, a)
                if nivel_actual in ["🟢", "🟡", "🔵", "⚪"] or pais_nombre in PAISES_TOP:
                    status_short = ev.get('fixture', {}).get('status', {}).get('short')
                    if status_short in ['FT', 'AET', 'PEN']: continue
                    ts = ev.get('fixture', {}).get('timestamp', 0)
                    hora_str = datetime.fromtimestamp(ts, pytz.utc).astimezone(tz_local).strftime("%H:%M")
                    desc = ev.get('fixture', {}).get('status', {}).get('long', 'Disponible')
                    lista_final.append({
                        "id": ev.get('fixture', {}).get('id'), 
                        "live": (status_short in ['1H', 'HT', '2H', 'ET', 'P']), 
                        "ts": ts, "liga": liga_nombre,
                        "pais": pais_nombre, "h": h, "a": a, "desc": desc, "hora": hora_str,
                        "color": nivel_actual
                    })
            lista_final.sort(key=lambda x: (not x['live'], x['color'] != "🟢", x['ts']))
            return lista_final
        return []
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return []

def enviar_lote_automatico(partidos_detectados, tz_ref):
    memoria = cargar_memoria_bot()
    ahora = datetime.now(pytz.timezone(tz_ref))
    fecha_hoy = ahora.strftime("%Y-%m-%d")
    if memoria["fecha_actual"] != fecha_hoy:
        memoria["ultimo_lote"] = 0
        memoria["fecha_actual"] = fecha_hoy
        memoria["enviados"] = []
    memoria["ultimo_lote"] += 1
    partidos_para_enviar = [p for p in partidos_detectados if p['id'] not in memoria["enviados"]]
    if not partidos_para_enviar:
        return
    mensaje = f"📦 *{memoria['ultimo_lote']}er Lote de Escaneo*\n📅 {ahora.strftime('%d/%m/%Y %H:%M')}\n----------------------------------\n\n"
    for p in partidos_para_enviar[:12]:
        mensaje += f"⚽ *{p['h']} vs {p['a']}*\n🏆 {p['liga']} ({p['color']})\n⏰ Hora: {p['hora']}\n\n"
        memoria["enviados"].append(p['id'])
    mensaje += "----------------------------------\n"
    mensaje += f"📊 Acertados: {memoria['acertados']} | Fallados: {memoria['fallados']}"
    try:
        bot_telegram.send_message(CHAT_ID_CANAL, mensaje, parse_mode="Markdown")
        guardar_memoria_bot(memoria)
    except Exception as e: pass

# --- FUNCIÓN DE INTEGRACIÓN PARA GITHUB ---
def ejecutar_analisis_automatico():
    """Función que une API + Filtros + Telegram"""
    tz_defecto = "America/Caracas"
    hoy = datetime.now(pytz.timezone(tz_defecto))
    partidos = buscar_partidos_fecha(hoy, tz_defecto)
    if partidos:
        enviar_lote_automatico(partidos, tz_defecto)

# --- INTERFAZ ---
st.write("### ⚽ ANALIZADOR MIGUEL")

if 'analisis_realizado' not in st.session_state:
    st.session_state.analisis_realizado = False
    st.session_state.resultados = {}

def limpiar_pantalla():
    st.session_state.analisis_realizado = False
    st.session_state.resultados = {}

tab_calc, tab_api = st.tabs(["📊 Calculadora Manual", "🚀 Escáner 24/7"])

with st.sidebar:
    st.header("⚙️ Parámetros de entrada")
    tipo_p = st.selectbox("Tipo de Partido", ["Liga", "Torneo", "Campo Neutral / Amistoso"])
    cat_aprendizaje = st.selectbox("Nivel de Fútbol", list(NIVELES_CONFIG.keys()))
    es_liga = (tipo_p == "Liga")
    jornada_val = st.number_input("Jornada", min_value=1, value=7, disabled=not es_liga)
    st.markdown("---")
    st.markdown("### 📊 Datos Local")
    l_a = st.number_input("Anotados Local", value=1.50, key="la_")
    l_c = st.number_input("Concedidos Local", value=1.00, key="lc_")
    puesto_l = st.number_input("Puesto tabla local", value=1, min_value=1, key="pl_", disabled=not es_liga)
    baja_l = st.checkbox("¿Baja sensible Local?", key="bl_")
    sup_l = st.checkbox("¿Suplentes local >=3?", key="sl_")
    st.markdown("---")
    st.markdown("### 📊 Datos Visitante")
    v_a = st.number_input("Anotados Visitante", value=1.50, key="va_")
    v_c = st.number_input("Concedidos Visitante", value=1.00, key="vc_")
    puesto_v = st.number_input("Puesto tabla visitante", value=15, min_value=1, key="pv_", disabled=not es_liga)
    baja_v = st.checkbox("¿Baja sensible Visitante?", key="bv_")
    sup_v = st.checkbox("¿Suplentes visita >=3?", key="sv_")

with tab_calc:
    if st.button("EJECUTAR ANÁLISIS", key="btn_ejec"):
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

    if st.session_state.analisis_realizado:
        res = st.session_state.resultados
        p_val, pico = round(res["o25"]), round(res['lt'])
        f_msg, f_col, f_tipo, bloqueado = "SIN PATRÓN CLARO", "#4a4a4a", "VACIO", True
        if p_val in [57, 58, 59, 65, 72, 73]: f_msg, f_col, f_tipo, bloqueado = "VALUE SÓLIDO: 1.5 GOLES", "#00ff00", "1.5", False
        elif 61 <= p_val <= 64: f_msg, f_col, f_tipo, bloqueado = "VALUE SÓLIDO: 2.5 GOLES", "#00ff00", "2.5", False
        elif p_val in [70, 71, 74]: f_msg, f_col, f_tipo, bloqueado = "VALUE 1.5 RIESGOSO", "#e74c3c", "RIESGO_15", False
        elif p_val == 60: f_msg, f_col, f_tipo, bloqueado = "VALUE 2.5 RIESGOSO", "#e74c3c", "RIESGO_25", False
        
        if f_tipo in ["1.5", "2.5"]: st.markdown(f'<div class="alerta-cuota">⚠️ VALUE {f_tipo} DETECTADO: Comprobar cuotas Local/Visita y Over 1.5 PARA CORROBORAR SOLIDEZ DEL VEREDICTO</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            p_l, p_v = (res["ll"]/(res["lt"]+0.001))*100, (res["lv"]/(res["lt"]+0.001))*100
            fav = "Local" if p_l > p_v else "Visitante"
            st.markdown(f"| Mercado | Probabilidad |\n| :--- | :--- |\n| Over 1.5 | **{res['o15']:.1f}%** |\n| Over 2.5 | **{res['o25']:.1f}%** |\n| Victoria Local | {p_l:.1f}% |\n| Victoria Visitante | {p_v:.1f}% |")
            est = f"Doble Oportunidad {fav}"
            if "1.5" in f_tipo: est += " y Over 1.5"
            elif "2.5" in f_tipo: est += " y Over 2.5"
            st.markdown(f"""<div style="background-color:#4a4a4a; padding:12px; border-radius:8px; color:white; text-align:center;"><span style="font-size:0.8em;">ESTRATEGIA SUGERIDA:</span><br><b>{est.upper()}</b></div>""", unsafe_allow_html=True)
        with c2:
            sum_a, sum_c = res['la'] + res['va'], res['lc_l'] + res['lc_v']
            rel = sum_a / (sum_c if sum_c > 0 else 0.1)
            if rel < 1.5: txt_ac, rec_ac, defensas = f"**{sum_a:.1f}/{sum_c:.1f}** - Relación = **{rel:.2f}** (Inercia baja)", "**Under 2.5/3.5 goles**", "INERCIA BAJA"
            elif rel < 2.0: txt_ac, rec_ac, defensas = f"**{sum_a:.1f}/{sum_c:.1f}** - Relación = **{rel:.2f}** (Equilibrio)", "**Over 1.5 / Under 3.5 goles**", "EQUILIBRADO"
            else: txt_ac, rec_ac, defensas = f"**{sum_a:.1f}/{sum_c:.1f}** - Relación = **{rel:.2f}** (Saturación)", "**Over 2.5 goles**", "OVER SÓLIDO"
            
            st.markdown("### 🎯 Patrón visual clave")
            st.markdown(f"* Anotados combinados: **{sum_a:.1f}**")
            st.markdown(f"* Concedidos combinados: **{sum_c:.1f}**")
            st.markdown(f"* Relación A/C: {txt_ac}")
            st.markdown(f"* Recomendación táctica: {rec_ac}")
            st.markdown(f"* Ambas defensas permeables = **{defensas}**")
            st.markdown(f'''<div style="border-left:5px solid {f_col}; background-color:#1e1e1e; padding:15px; font-weight:bold; color:white; border-radius:0 8px 8px 0;">FILTRO: {f_msg}</div>''', unsafe_allow_html=True)
            st.write(f"**λ Total:** {res['lt']:.2f} | **Letra:** {res['letra']}")
        
        st.markdown("---")
        with st.expander("📊 ANALIZADOR DE CUOTAS Y SINCRO", expanded=True):
            if bloqueado and pico != 2: st.warning("🚫 Filtro sin patrón claro para análisis de cuotas.")
            else:
                cq1, cq2, cq3 = st.columns(3)
                c_o15 = cq3.number_input("Cuota Over 1.5 Goles", 1.0, 5.0, 1.20, key="qc_o15")
                if st.button("ANALIZAR SINCRO", key="btn_sinc"):
                    if rel >= 2.0 and f_tipo == "2.5" and c_o15 <= 1.22: st.success("✅ SINCRO ÉXITO: Over 2.5 combinado con over de córners 'X-3'")
                    else: st.info("Evaluar mercado manual. Cuota o Inercia fuera de rango óptimo.")
        st.button("LIMPIAR ANÁLISIS", on_click=limpiar_pantalla, type="primary", key="btn_clr")

with tab_api:
    c_api1, c_api2 = st.columns(2)
    with c_api1: f_input = st.date_input("Selecciona fecha", datetime.now(), key="f_input")
    with c_api2:
        lista_tz = pytz.all_timezones
        try: idx_vza = lista_tz.index("America/Caracas")
        except: idx_vza = 0
        tz_input = st.selectbox("🕒 País Referencia (Hora)", lista_tz, index=idx_vza)
        
    if st.button("🚀 INICIAR ESCANEO DE JORNADA", key="btn_scan"):
        with st.spinner(f"Escaneando jornada ({tz_input})..."):
            st.session_state.lista_partidos = buscar_partidos_fecha(f_input, tz_input)

    if 'lista_partidos' in st.session_state and st.session_state.lista_partidos:
        if st.button("🌙 ENVIAR LOTE AL CANAL (MODO CENTINELA)"):
            enviar_lote_automatico(st.session_state.lista_partidos, tz_input)

        with st.expander("🛠️ AJUSTE DINÁMICO DE CATEGORÍA"):
            ligas_presentes = sorted(list(set([p['liga'] for p in st.session_state.lista_partidos])))
            ca1, ca2, ca3 = st.columns([2,1,1])
            l_sel = ca1.selectbox("Selecciona Liga a corregir", ligas_presentes)
            n_sel = ca2.selectbox("Nuevo Nivel", list(NIVELES_CONFIG.values()))
            if ca3.button("GUARDAR CAMBIO"):
                st.session_state.memoria_ligas[l_sel] = n_sel
                mem_actual = cargar_memoria_bot()
                guardar_memoria_bot(mem_actual)
                st.success(f"Ajuste para {l_sel} guardado permanentemente.")
                st.rerun()

        st.markdown("---")
        st.markdown("### 🔍 FILTRADO POR NIVEL MAESTRO")
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            nivel_busqueda = st.selectbox("AJUSTE ESCANEO NIVEL DE FÚTBOL", list(NIVELES_CONFIG.keys()), key="sel_nivel_esp")
        with col_f2:
            btn_esp = st.button("🎯 INICIAR ESCANEO ESPECÍFICO")

        if btn_esp:
            color_objetivo = NIVELES_CONFIG[nivel_busqueda]
            filtrados = [p for p in st.session_state.lista_partidos if p['color'] == color_objetivo]
            st.success(f"Encontrados {len(filtrados)} partidos de nivel {nivel_busqueda}.")
            for p in filtrados:
                txt = f"{p['color']} | 🕒 {p['hora']} | {'🔴 **EN VIVO:** ' if p['live'] else ''}{p['h']} vs {p['a']} | {p['pais']} - {p['liga']} ({p['desc']})"
                st.write(txt)
        else:
            st.success(f"Encontrados {len(st.session_state.lista_partidos)} partidos.")
            for p in st.session_state.lista_partidos:
                txt = f"{p['color']} | 🕒 {p['hora']} | {'🔴 **EN VIVO:** ' if p['live'] else ''}{p['h']} vs {p['a']} | {p['pais']} - {p['liga']} ({p['desc']})"
                st.write(txt)

st.markdown("---")
with st.expander("🤖 ESTADO DEL BOT CENTINELA"):
    mem = cargar_memoria_bot()
    st.write(f"Lote actual: {mem['ultimo_lote']}")
    st.write(f"ID Canal: `{CHAT_ID_CANAL}`")
    if st.button("LIMPIAR MEMORIA (RESET)"):
        guardar_memoria_bot({"ultimo_lote": 0, "fecha_actual": "", "enviados": [], "acertados": 0, "fallados": 0, "patrones_fallidos": {}, "memoria_ligas": {}})
        st.session_state.memoria_ligas = {}
        st.rerun()

# --- BLOQUE DE EJECUCIÓN AUTOMÁTICA (ORDEN DEL SERVIDOR) ---
if __name__ == "__main__":
    # Si detecta que está en un entorno de GitHub Actions o similar
    if os.getenv("GITHUB_ACTIONS") == "true":
        ejecutar_analisis_automatico()
