
from pathlib import Path
import json
import math
import html
from collections import Counter, defaultdict

import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap, Draw
from streamlit_folium import st_folium

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
STATE_FILE = DATA_DIR / "task_state.json"

st.set_page_config(
    page_title="LIS-ACCESS Decision Support Tool",
    page_icon="♿",
    layout="wide",
)

# ---------- UI ----------
st.markdown("""
<style>
.block-container {padding-top: 3rem; padding-bottom: 2rem;}
.main-title {
    font-size: 2.6rem;
    font-weight: 800;
    line-height: 1.2;
    margin-top: .4rem;
    margin-bottom: .3rem;
    color: #1f2937;
}
.sub-title {
    color:#66706b;
    font-size: 1.05rem;
    margin-bottom:.8rem;
}
.small-note {color:#737b77; font-size:.88rem;}
div[data-testid="stMetric"] {
    border:1px solid #d9dfdd;
    border-radius:12px;
    padding:10px 12px;
    background:#fafbfa;
}
.task-card {
    border:1px solid #dfe4e1;
    border-radius:10px;
    padding:10px 12px;
    margin-bottom:8px;
}
.job-card {
    border:1px solid #dfe4e1;
    border-radius:14px;
    padding:16px;
    min-height:175px;
    background:#ffffff;
}
.job-icon {font-size:2rem; margin-bottom:.35rem;}
.job-title {font-size:1.05rem; font-weight:700; margin-bottom:.3rem;}
.job-desc {font-size:.9rem; color:#69716d; line-height:1.35;}
.legend-row {display:flex;gap:18px;align-items:center;flex-wrap:wrap;margin:.25rem 0 .8rem 0;}
.legend-item {display:flex;gap:7px;align-items:center;font-size:.88rem;color:#4d5551;}
.legend-dot {width:12px;height:12px;border-radius:50%;display:inline-block;}
</style>
""", unsafe_allow_html=True)

T = {
"PT": {
    "title":"LIS-ACCESS — Ferramenta de Apoio à Decisão",

    "home":"Início",
    "home_intro":"Jobs to be done",
    "home_desc":"Escolha a aba correspondente para executar a análise pretendida.",
    "job_map_title":"Explorar problemas de acessibilidade",
    "job_map_desc":"Visualizar obstáculos, serviços essenciais e POIs; usar pontos, clusters, heatmap e polígonos personalizados.",
    "job_prox_title":"Analisar proximidade",
    "job_prox_desc":"Selecionar hospitais, escolas ou estações, escolher um ou vários equipamentos e definir livremente o raio de análise.",
    "job_plan_title":"Planear intervenções",
    "job_plan_desc":"Associar intervenção e entidade responsável, bloquear tarefas e preparar critérios independentes de custo, tempo e complexidade.",
    "job_monitor_title":"Monitorizar execução",
    "job_monitor_desc":"Acompanhar tarefas atribuídas, checkpoints, estados de execução e resolução por serviço e território.",
    "show_map":"Mostrar mapa",
    "map_styles":"No controlo de camadas do mapa pode alternar entre OpenStreetMap, mapa claro e satélite.",
    "legend_obstacles":"Obstáculos",
    "legend_hospital":"Hospitais",
    "legend_school":"Escolas",
    "legend_station":"Estações",
    "legend_pois":"POIs",
    "subtitle":"MVP Lisboa: obstáculos StreetCo, serviços essenciais, POIs, análise espacial, planeamento e monitorização.",
    "language":"Idioma",
    "demo_profile":"Perfil de demonstração",
    "admin":"CML / Administrador",
    "service_user":"Serviço responsável",
    "responsible_service":"Serviço",
    "filters":"Filtros",
    "uit":"Unidade de Intervenção Territorial",
    "all_uit":"Todas",
    "parish":"Freguesia",
    "street":"Rua",
    "obstacle_type":"Tipo de obstáculo",
    "all_f":"Todas",
    "all_m":"Todos",
    "view":"Visualização",
    "points":"Pontos",
    "clusters":"Clusters",
    "heatmap":"Heatmap",
    "layers":"Camadas",
    "show_services":"Serviços essenciais",
    "show_pois":"Pontos de Interesse",
    "map_analysis":"Mapa e análise",
    "proximity":"Proximidade",
    "planning":"Planeamento",
    "monitoring":"Monitorização",
    "obstacles":"Obstáculos",
    "streets":"Ruas mapeadas",
    "types":"Tipos de obstáculos",
    "mapped_pois":"Pontos de Interesse",
    "map":"Mapa interativo",
    "polygon_help":"Use o botão de desenho no canto superior esquerdo do mapa para desenhar um polígono e analisar apenas essa área.",
    "polygon_analysis":"Análise da área desenhada",
    "inside_polygon":"Obstáculos no polígono",
    "predominant":"Obstáculo predominante",
    "clear_polygon":"Limpar análise do polígono",
    "no_polygon":"Ainda não foi desenhado nenhum polígono.",
    "service_analysis":"Análise de proximidade a serviços essenciais",
    "service_type":"Tipo de serviço",
    "select_services":"Selecionar equipamentos",
    "radius":"Raio personalizado (m)",
    "only_radius":"Mostrar apenas obstáculos dentro do raio",
    "within_radius":"Obstáculos dentro do raio",
    "distance_note":"Neste MVP o buffer usa distância em linha reta. Distância pedonal pela rede é uma evolução posterior.",
    "radius_table_title":"Obstáculos dentro do raio selecionado",
    "reference_service":"Serviço de referência",
    "distance_to_service":"Distância ao serviço (m)",
    "photo":"Fotografia",
    "export_radius":"Exportar obstáculos dentro do raio (CSV)",
    "poi_section":"Pontos de interesse StreetNav",
    "poi_type":"Tipo de POI",
    "accessibility":"Acessibilidade",
    "condition":"Estado",
    "task_management":"Atribuição e bloqueio de tarefas",
    "intervention":"Intervenção necessária",
    "entity":"Entidade responsável",
    "lock":"Bloquear tarefa para esta entidade",
    "apply":"Aplicar",
    "assignment_note":"No MVP, o bloqueio é uma simulação funcional de permissões. Autenticação institucional real deve ser implementada numa fase posterior.",
    "unassigned":"Não atribuída",
    "locked":"Bloqueada",
    "open":"Aberta",
    "selected_obstacle":"Obstáculo selecionado",
    "choose_obstacle":"Escolher obstáculo",
    "cost":"Custo estimado (€)",
    "time":"Tempo estimado (horas)",
    "complexity":"Complexidade",
    "status":"Estado",
    "not_started":"Por iniciar",
    "in_progress":"Em execução",
    "checkpoint":"Checkpoint",
    "resolved":"Resolvido",
    "save_task":"Guardar tarefa",
    "priority":"Priorização",
    "priority_note":"Os critérios estão preparados, mas a priorização só é calculada quando existirem valores de custo, tempo e complexidade.",
    "available_data":"Tarefas com dados de priorização",
    "no_priority":"Ainda não existem dados suficientes para calcular uma priorização.",
    "progress":"Progresso",
    "global_summary":"Resumo global",
    "assigned":"Atribuídos",
    "resolved_count":"Resolvidos",
    "resolution_rate":"Taxa de resolução",
    "by_entity":"Por entidade responsável",
    "by_parish":"Por freguesia",
    "results":"Resultados",
    "download":"Exportar resultados filtrados (CSV)",
    "photo":"Fotografia",
    "streetnav_pois":"Pontos de Interesse",
    "service":"Serviço essencial",
    "hospital":"Hospital",
    "school":"Escola",
    "station":"Estação",
    "bench":"Banco",
    "parking":"Estacionamento",
    "water_source":"Fonte de água",
    "toilets":"Instalação sanitária",
    "task_access_denied":"Esta tarefa está bloqueada por outra entidade. Neste perfil não pode ser alterada.",
},
"EN": {
    "title":"LIS-ACCESS — Decision Support Tool",

    "home":"Home",
    "home_intro":"Jobs to be done",
    "home_desc":"Choose the relevant tab to carry out the required analysis.",
    "job_map_title":"Explore accessibility problems",
    "job_map_desc":"View obstacles, essential services and POIs; use points, clusters, heatmap and custom polygons.",
    "job_prox_title":"Analyse proximity",
    "job_prox_desc":"Select hospitals, schools or stations, choose one or several facilities and freely define the analysis radius.",
    "job_plan_title":"Plan interventions",
    "job_plan_desc":"Assign interventions and responsible entities, lock tasks and prepare independent cost, time and complexity criteria.",
    "job_monitor_title":"Monitor execution",
    "job_monitor_desc":"Track assigned tasks, checkpoints, execution status and resolution by service and territory.",
    "show_map":"Show map",
    "map_styles":"Use the map layer control to switch between OpenStreetMap, light map and satellite.",
    "legend_obstacles":"Obstacles",
    "legend_hospital":"Hospitals",
    "legend_school":"Schools",
    "legend_station":"Stations",
    "legend_pois":"POIs",
    "subtitle":"Lisbon MVP: StreetCo obstacles, essential services, POIs, spatial analysis, planning and monitoring.",
    "language":"Language",
    "demo_profile":"Demo profile",
    "admin":"CML / Administrator",
    "service_user":"Responsible service",
    "responsible_service":"Service",
    "filters":"Filters",
    "uit":"Intervention Territorial Unit",
    "all_uit":"All",
    "parish":"Parish",
    "street":"Street",
    "obstacle_type":"Obstacle type",
    "all_f":"All",
    "all_m":"All",
    "view":"View",
    "points":"Points",
    "clusters":"Clusters",
    "heatmap":"Heatmap",
    "layers":"Layers",
    "show_services":"Essential services",
    "show_pois":"Points of Interest",
    "map_analysis":"Map & analysis",
    "proximity":"Proximity",
    "planning":"Planning",
    "monitoring":"Monitoring",
    "obstacles":"Obstacles",
    "streets":"Mapped streets",
    "types":"Obstacle types",
    "mapped_pois":"Points of Interest",
    "map":"Interactive map",
    "polygon_help":"Use the drawing button in the upper-left corner of the map to draw a polygon and analyse only that area.",
    "polygon_analysis":"Drawn-area analysis",
    "inside_polygon":"Obstacles inside polygon",
    "predominant":"Predominant obstacle",
    "clear_polygon":"Clear polygon analysis",
    "no_polygon":"No polygon has been drawn yet.",
    "service_analysis":"Proximity analysis around essential services",
    "service_type":"Service type",
    "select_services":"Select facilities",
    "radius":"Custom radius (m)",
    "only_radius":"Show only obstacles inside radius",
    "within_radius":"Obstacles inside radius",
    "distance_note":"This MVP uses straight-line buffers. Walking-network distance is a later enhancement.",
    "radius_table_title":"Obstacles inside selected radius",
    "reference_service":"Reference service",
    "distance_to_service":"Distance to service (m)",
    "photo":"Photo",
    "export_radius":"Export obstacles inside radius (CSV)",
    "poi_section":"StreetNav points of interest",
    "poi_type":"POI type",
    "accessibility":"Accessibility",
    "condition":"Condition",
    "task_management":"Task assignment and locking",
    "intervention":"Required intervention",
    "entity":"Responsible entity",
    "lock":"Lock task to this entity",
    "apply":"Apply",
    "assignment_note":"In the MVP, locking is a functional permissions simulation. Institutional authentication should be added later.",
    "unassigned":"Unassigned",
    "locked":"Locked",
    "open":"Open",
    "selected_obstacle":"Selected obstacle",
    "choose_obstacle":"Choose obstacle",
    "cost":"Estimated cost (€)",
    "time":"Estimated time (hours)",
    "complexity":"Complexity",
    "status":"Status",
    "not_started":"Not started",
    "in_progress":"In progress",
    "checkpoint":"Checkpoint",
    "resolved":"Resolved",
    "save_task":"Save task",
    "priority":"Prioritisation",
    "priority_note":"The criteria are prepared, but prioritisation is only calculated when cost, time and complexity values exist.",
    "available_data":"Tasks with prioritisation data",
    "no_priority":"There is not enough data to calculate prioritisation yet.",
    "progress":"Progress",
    "global_summary":"Global summary",
    "assigned":"Assigned",
    "resolved_count":"Resolved",
    "resolution_rate":"Resolution rate",
    "by_entity":"By responsible entity",
    "by_parish":"By parish",
    "results":"Results",
    "download":"Export filtered results (CSV)",
    "photo":"Photo",
    "streetnav_pois":"Points of Interest",
    "service":"Essential service",
    "hospital":"Hospital",
    "school":"School",
    "station":"Station",
    "bench":"Bench",
    "parking":"Parking",
    "water_source":"Water source",
    "toilets":"Toilets",
    "task_access_denied":"This task is locked by another entity. It cannot be changed under this profile.",
}
}

# ---------- Helpers ----------
def safe(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return html.escape(str(v))

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

def point_in_polygon(lat, lon, polygon_coords):
    # polygon_coords GeoJSON order: [lon, lat]
    x, y = lon, lat
    inside = False
    pts = polygon_coords
    j = len(pts)-1
    for i in range(len(pts)):
        xi, yi = pts[i][0], pts[i][1]
        xj, yj = pts[j][0], pts[j][1]
        intersect = ((yi > y) != (yj > y)) and (
            x < (xj-xi) * (y-yi) / ((yj-yi) if (yj-yi) != 0 else 1e-12) + xi
        )
        if intersect:
            inside = not inside
        j = i
    return inside

def default_intervention(obstacle_pt):
    x = (obstacle_pt or "").strip().lower()
    rules = [
        (["pavimento degradado","buraco","calçada desnivelada"], "Reparação / manutenção do pavimento"),
        (["passeio estreito"], "Avaliar alargamento ou desobstrução do passeio"),
        (["ausência de passeio"], "Criar percurso pedonal / passeio acessível"),
        (["ressalto do passeio"], "Correção de desnível / rebaixamento"),
        (["inclinação transversal"], "Correção da inclinação transversal"),
        (["escadas"], "Avaliar solução de acessibilidade alternativa"),
        (["poste"], "Avaliar relocalização ou adequação do elemento"),
        (["árvore","ramo","sebe","plantas"], "Poda, manutenção ou desobstrução"),
        (["esplanada","andaime","elemento de construção"], "Desobstrução / regularização da ocupação"),
    ]
    for keys, value in rules:
        if any(k in x for k in keys):
            return value
    return "Avaliação técnica necessária"


def div_icon(symbol, bg, title=""):
    return folium.DivIcon(
        icon_size=(34,34),
        icon_anchor=(17,17),
        html=f"""
        <div title="{html.escape(str(title))}" style="
            width:32px;height:32px;border-radius:50%;
            background:{bg};border:2px solid white;
            box-shadow:0 1px 6px rgba(0,0,0,.35);
            display:flex;align-items:center;justify-content:center;
            font-size:18px;line-height:1;">
            {symbol}
        </div>"""
    )

def service_style(service_type):
    t = str(service_type or "").lower()
    if "hospital" in t:
        return "🏥", "#d9534f"
    if "escola" in t or "school" in t:
        return "🏫", "#2f80ed"
    if "metro" in t or "station" in t or "estação" in t:
        return "🚉", "#7a4fb3"
    return "📍", "#5f6f69"

def poi_style(poi_type):
    t = str(poi_type or "").lower()
    if "bench" in t or "banco" in t:
        return "🪑", "#2e8b57"
    if "parking" in t or "estacion" in t:
        return "🅿️", "#2457d6"
    if "water" in t or "água" in t or "agua" in t:
        return "💧", "#17a2b8"
    if "toilet" in t or "sanitária" in t or "sanitaria" in t:
        return "🚻", "#7b5aa6"
    return "📍", "#65746e"

def add_base_layers(m):
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="© OpenStreetMap contributors",
        name="OpenStreetMap",
        overlay=False, control=True, show=True
    ).add_to(m)
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr="© OpenStreetMap contributors © CARTO",
        name="Mapa claro / Light map",
        overlay=False, control=True, show=False
    ).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri",
        name="Satélite / Satellite",
        overlay=False, control=True, show=False
    ).add_to(m)

@st.cache_data
def load_geojsons():
    with open(DATA_DIR/"obstacles_lisbon_final.geojson", encoding="utf-8") as f:
        obsj = json.load(f)
    with open(DATA_DIR/"essential_services_lisbon.geojson", encoding="utf-8") as f:
        servj = json.load(f)
    with open(DATA_DIR/"streetco_pois_normalized.geojson", encoding="utf-8") as f:
        poij = json.load(f)

    obs_rows = []
    for ft in obsj["features"]:
        p = dict(ft.get("properties") or {})
        lon, lat = ft["geometry"]["coordinates"][:2]
        p["longitude"] = float(lon)
        p["latitude"] = float(lat)
        p["obstacle_id"] = str(p.get("id") or p.get("fid"))
        p["street_name"] = p.get("osm_name")
        p["type_pt"] = p.get("type_label_pt")
        p["type_en"] = p.get("type_label_en")
        obs_rows.append(p)

    serv_rows = []
    for ft in servj["features"]:
        p = dict(ft.get("properties") or {})
        lon, lat = ft["geometry"]["coordinates"][:2]
        p["longitude"] = float(lon)
        p["latitude"] = float(lat)
        p["service_id"] = str(p.get("full_id") or p.get("osm_id") or p.get("fid"))
        p["service_name"] = p.get("name") or p.get("name:pt") or p.get("name:en") or "Sem nome"
        serv_rows.append(p)

    poi_rows = []
    for ft in poij["features"]:
        p = dict(ft.get("properties") or {})
        lon, lat = ft["geometry"]["coordinates"][:2]
        p["longitude"] = float(lon)
        p["latitude"] = float(lat)
        poi_rows.append(p)

    return pd.DataFrame(obs_rows), pd.DataFrame(serv_rows), pd.DataFrame(poi_rows)

def load_task_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_task_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

obs, services, pois = load_geojsons()
if "task_state" not in st.session_state:
    st.session_state.task_state = load_task_state()

# ---------- Language and permissions ----------
lang = st.sidebar.selectbox("Idioma / Language", ["PT","EN"], index=0)
tr = T[lang]
profile = st.sidebar.selectbox(tr["demo_profile"], [tr["admin"], tr["service_user"]])

known_entities = sorted({
    v.get("entity","") for v in st.session_state.task_state.values()
    if v.get("entity")
})
current_entity = None
if profile == tr["service_user"]:
    current_entity = st.sidebar.selectbox(
        tr["responsible_service"],
        known_entities if known_entities else ["—"]
    )

st.markdown(f'<div class="main-title">{tr["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{tr["subtitle"]}</div>', unsafe_allow_html=True)

# ---------- Shared filters ----------
filtered = obs.copy()
with st.sidebar:
    st.header(tr["filters"])

    uits = sorted(filtered["uit"].dropna().astype(str).unique())
    selected_uit = st.selectbox(tr["uit"], [tr["all_uit"]] + uits)
    if selected_uit != tr["all_uit"]:
        filtered = filtered[filtered["uit"].astype(str) == selected_uit]

    parishes = sorted(filtered["freguesia"].dropna().astype(str).unique())
    parish = st.selectbox(tr["parish"], [tr["all_f"]] + parishes)
    if parish != tr["all_f"]:
        filtered = filtered[filtered["freguesia"].astype(str) == parish]

    streets = sorted(filtered["street_name"].dropna().astype(str).unique())
    street = st.selectbox(tr["street"], [tr["all_f"]] + streets)
    if street != tr["all_f"]:
        filtered = filtered[filtered["street_name"].astype(str) == street]

    type_col = "type_pt" if lang == "PT" else "type_en"
    obs_types = sorted(filtered[type_col].dropna().astype(str).unique())
    obstacle_type = st.selectbox(tr["obstacle_type"], [tr["all_m"]] + obs_types)
    if obstacle_type != tr["all_m"]:
        filtered = filtered[filtered[type_col].astype(str) == obstacle_type]

    view_mode = st.radio(tr["view"], [tr["points"], tr["clusters"], tr["heatmap"]], horizontal=True)

    st.subheader(tr["layers"])
    show_services = st.checkbox(tr["show_services"], value=False)
    show_pois = st.checkbox(tr["show_pois"], value=False)

tabs = st.tabs([tr["home"], tr["map_analysis"], tr["proximity"], tr["planning"], tr["monitoring"]])

with tabs[0]:
    st.subheader(tr["home_intro"])
    st.caption(tr["home_desc"])
    jc1,jc2,jc3,jc4 = st.columns(4)
    jobs = [
        (jc1, "🗺️", tr["job_map_title"], tr["job_map_desc"]),
        (jc2, "📍", tr["job_prox_title"], tr["job_prox_desc"]),
        (jc3, "🛠️", tr["job_plan_title"], tr["job_plan_desc"]),
        (jc4, "📊", tr["job_monitor_title"], tr["job_monitor_desc"]),
    ]
    for col, ico, title, desc in jobs:
        with col:
            st.markdown(
                f'<div class="job-card"><div class="job-icon">{ico}</div>'
                f'<div class="job-title">{title}</div>'
                f'<div class="job-desc">{desc}</div></div>',
                unsafe_allow_html=True
            )
    st.divider()
    h1,h2,h3,h4 = st.columns(4)
    h1.metric(tr["obstacles"], len(obs))
    h2.metric(tr["streets"], obs["street_name"].nunique())
    h3.metric(tr["types"], obs["type_pt"].nunique())
    h4.metric(tr["mapped_pois"], len(pois))


# ---------- TAB 1 MAP + POLYGON ----------
with tabs[1]:
    k1,k2,k3,k4 = st.columns(4)
    k1.metric(tr["obstacles"], len(filtered))
    k2.metric(tr["streets"], filtered["street_name"].nunique())
    k3.metric(tr["types"], filtered[type_col].nunique())
    k4.metric(tr["mapped_pois"], len(pois))

    st.subheader(tr["map"])
    st.markdown(
        f"""<div class="legend-row">
        <div class="legend-item"><span class="legend-dot" style="background:#f28e2b"></span>{tr["legend_obstacles"]}</div>
        <div class="legend-item"><span class="legend-dot" style="background:#d9534f"></span>{tr["legend_hospital"]}</div>
        <div class="legend-item"><span class="legend-dot" style="background:#2f80ed"></span>{tr["legend_school"]}</div>
        <div class="legend-item"><span class="legend-dot" style="background:#7a4fb3"></span>{tr["legend_station"]}</div>
        <div class="legend-item"><span class="legend-dot" style="background:#2e8b57"></span>{tr["legend_pois"]}</div>
        </div>""",
        unsafe_allow_html=True
    )
    st.caption(tr["polygon_help"])
    st.caption(tr["map_styles"])

    m = folium.Map(location=[38.725, -9.155], zoom_start=12, tiles=None, control_scale=True)
    add_base_layers(m)

    if view_mode == tr["heatmap"]:
        HeatMap(filtered[["latitude","longitude"]].dropna().values.tolist(),
                radius=18, blur=16, min_opacity=.25).add_to(m)
    elif view_mode == tr["clusters"]:
        cluster = MarkerCluster(name=tr["obstacles"]).add_to(m)
        for _, r in filtered.dropna(subset=["latitude","longitude"]).iterrows():
            folium.CircleMarker(
                [r["latitude"], r["longitude"]], radius=4, weight=1,
                fill=True, fill_opacity=.85,
                tooltip=safe(r.get(type_col)),
                popup=folium.Popup(
                    f"<b>{safe(r.get(type_col))}</b><br>{safe(r.get('street_name'))}<br>{safe(r.get('freguesia'))}",
                    max_width=360
                )
            ).add_to(cluster)
    else:
        for _, r in filtered.dropna(subset=["latitude","longitude"]).iterrows():
            task = st.session_state.task_state.get(str(r["obstacle_id"]), {})
            photo = r.get("photo")
            photo_html = (
                f"<br>{safe(tr['photo'])}: <a href='{html.escape(str(photo))}' target='_blank'>abrir</a>"
                if photo else ""
            )
            popup = f"""
            <b>{safe(r.get(type_col))}</b><br>
            {safe(tr["street"])}: {safe(r.get("street_name"))}<br>
            {safe(tr["parish"])}: {safe(r.get("freguesia"))}<br>
            {safe(tr["intervention"])}: {safe(task.get("intervention") or default_intervention(r.get("type_pt")))}<br>
            {safe(tr["entity"])}: {safe(task.get("entity") or tr["unassigned"])}<br>
            {safe(tr["status"])}: {safe(task.get("status") or tr["not_started"])}
            {photo_html}
            """
            folium.CircleMarker(
                [r["latitude"], r["longitude"]], radius=4, weight=1,
                fill=True, fill_opacity=.82,
                tooltip=safe(r.get(type_col)),
                popup=folium.Popup(popup, max_width=380)
            ).add_to(m)

    if show_services:
        fg = folium.FeatureGroup(name=tr["show_services"])
        for _, s in services.iterrows():
            label = safe(s.get("service_name"))
            stype = safe(s.get("service_type"))
            symbol, bg = service_style(s.get("service_type"))
            folium.Marker(
                [s["latitude"],s["longitude"]],
                icon=div_icon(symbol, bg, f"{stype}: {label}"),
                tooltip=f"{stype}: {label}",
                popup=folium.Popup(f"<b>{label}</b><br>{stype}", max_width=300)
            ).add_to(fg)
        fg.add_to(m)

    if show_pois:
        fg = folium.FeatureGroup(name=tr["streetnav_pois"])
        for _, p in pois.iterrows():
            ptype = p.get("poi_type_pt") if lang == "PT" else p.get("poi_type_en")
            photo = p.get("photo")
            popup = (
                f"<b>{safe(ptype)}</b><br>"
                f"{safe(tr['condition'])}: {safe(p.get('condition'))}<br>"
                f"{safe(tr['accessibility'])}: {safe(p.get('accessibility'))}<br>"
                f"{safe(tr['photo'])}: "
                + (f"<a href='{html.escape(str(photo))}' target='_blank'>abrir</a>" if photo else "—")
            )
            symbol, bg = poi_style(ptype)
            folium.Marker(
                [p["latitude"],p["longitude"]],
                icon=div_icon(symbol, bg, ptype),
                tooltip=safe(ptype),
                popup=folium.Popup(popup,max_width=320)
            ).add_to(fg)
        fg.add_to(m)

    Draw(
        export=False,
        draw_options={
            "polyline": False,
            "rectangle": True,
            "circle": False,
            "circlemarker": False,
            "marker": False,
            "polygon": True,
        },
        edit_options={"edit": True, "remove": True},
    ).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    show_map_panel = st.toggle(tr["show_map"], value=True, key="show_main_map")
    if show_map_panel:
        map_state = st_folium(
            m, height=650, use_container_width=True,
            returned_objects=["all_drawings","last_active_drawing"]
        )
    else:
        map_state = {}

    drawings = (map_state or {}).get("all_drawings") or []
    polygon = None
    if drawings:
        # use the latest polygon/rectangle
        for d in reversed(drawings):
            geom = d.get("geometry", {})
            if geom.get("type") == "Polygon":
                polygon = geom.get("coordinates", [[]])[0]
                break

    if polygon:
        inside_mask = filtered.apply(
            lambda r: point_in_polygon(float(r["latitude"]), float(r["longitude"]), polygon),
            axis=1
        )
        poly_df = filtered[inside_mask].copy()
        st.subheader(tr["polygon_analysis"])
        c1,c2,c3 = st.columns(3)
        c1.metric(tr["inside_polygon"], len(poly_df))
        pred = "—"
        if not poly_df.empty:
            vc = poly_df[type_col].dropna().value_counts()
            pred = vc.index[0] if len(vc) else "—"
        c2.metric(tr["predominant"], pred)
        c3.metric(tr["types"], poly_df[type_col].nunique())
        if not poly_df.empty:
            summary = poly_df[type_col].value_counts().rename_axis(tr["obstacle_type"]).reset_index(name="n")
            st.dataframe(summary, use_container_width=True, hide_index=True)
    else:
        st.info(tr["no_polygon"])

# ---------- TAB 2 PROXIMITY ----------
with tabs[2]:
    st.subheader(tr["service_analysis"])
    svc_types = sorted(services["service_type"].dropna().astype(str).unique())
    selected_type = st.selectbox(tr["service_type"], svc_types)
    svc_subset = services[services["service_type"].astype(str) == selected_type].copy()
    svc_names = sorted(svc_subset["service_name"].dropna().astype(str).unique())
    selected_names = st.multiselect(tr["select_services"], svc_names, default=svc_names[:1] if svc_names else [])
    radius = st.number_input(tr["radius"], min_value=25, max_value=10000, value=500, step=25)

    selected_services = svc_subset[svc_subset["service_name"].astype(str).isin(selected_names)].copy()
    prox_df = filtered.copy()
    if not selected_services.empty:
        def nearest_service_info(r):
            distances = [
                (
                    haversine_m(
                        float(r["latitude"]), float(r["longitude"]),
                        float(s["latitude"]), float(s["longitude"])
                    ),
                    str(s["service_name"])
                )
                for _, s in selected_services.iterrows()
            ]
            return min(distances, key=lambda x: x[0])

        nearest_info = prox_df.apply(nearest_service_info, axis=1)
        prox_df["distance_to_selected_service_m"] = nearest_info.apply(lambda x: x[0])
        prox_df["reference_service"] = nearest_info.apply(lambda x: x[1])
        within = prox_df[prox_df["distance_to_selected_service_m"] <= radius].copy()
    else:
        within = prox_df.iloc[0:0].copy()
        within["reference_service"] = pd.Series(dtype="object")

    c1,c2,c3 = st.columns(3)
    c1.metric(tr["within_radius"], len(within))
    c2.metric(tr["types"], within[type_col].nunique())
    pred = within[type_col].value_counts().index[0] if len(within) and len(within[type_col].dropna()) else "—"
    c3.metric(tr["predominant"], pred)
    st.caption(tr["distance_note"])

    only_radius = st.toggle(tr["only_radius"], value=True)
    map_df = within if only_radius else filtered

    pm = folium.Map(location=[38.725,-9.155], zoom_start=12, tiles=None)
    add_base_layers(pm)
    for _, s in selected_services.iterrows():
        symbol, bg = service_style(s.get("service_type"))
        folium.Marker(
            [s["latitude"],s["longitude"]],
            icon=div_icon(symbol, bg, s["service_name"]),
            tooltip=safe(s["service_name"]),
            popup=f"<b>{safe(s['service_name'])}</b><br>{safe(selected_type)}"
        ).add_to(pm)
        folium.Circle(
            [s["latitude"],s["longitude"]],
            radius=float(radius), weight=2, fill=True, fill_opacity=.08
        ).add_to(pm)

    for _, r in map_df.iterrows():
        folium.CircleMarker(
            [r["latitude"],r["longitude"]], radius=4, color="#a85f00", weight=1,
            fill=True, fill_color="#f28e2b", fill_opacity=.88,
            tooltip=safe(r.get(type_col)),
            popup=folium.Popup(
                f"<b>{safe(r.get(type_col))}</b><br>{safe(r.get('street_name'))}",
                max_width=300
            )
        ).add_to(pm)

    folium.LayerControl(collapsed=False).add_to(pm)
    show_prox_map = st.toggle(tr["show_map"], value=True, key="show_prox_map")
    if show_prox_map:
        st_folium(pm, height=600, use_container_width=True)

    st.markdown(f"### {tr['radius_table_title']}")
    if within.empty:
        st.info("Sem obstáculos dentro do raio selecionado." if lang == "PT" else "No obstacles inside the selected radius.")
    else:
        radius_table = within.copy()
        radius_table["distance_to_selected_service_m"] = radius_table["distance_to_selected_service_m"].round(1)

        display_cols = [
            type_col,
            "street_name",
            "freguesia",
            "uit",
            "reference_service",
            "distance_to_selected_service_m",
            "latitude",
            "longitude",
            "photo",
            "obstacle_id",
        ]
        display_cols = [c for c in display_cols if c in radius_table.columns]

        rename_map = {
            type_col: tr["obstacle_type"],
            "street_name": tr["street"],
            "freguesia": tr["parish"],
            "uit": tr["uit"],
            "reference_service": tr["reference_service"],
            "distance_to_selected_service_m": tr["distance_to_service"],
            "latitude": "Latitude",
            "longitude": "Longitude",
            "photo": tr["photo"],
            "obstacle_id": "ID",
        }

        radius_display = radius_table[display_cols].rename(columns=rename_map)
        st.dataframe(
            radius_display.sort_values(tr["distance_to_service"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                tr["photo"]: st.column_config.LinkColumn(
                    tr["photo"],
                    display_text="Abrir" if lang == "PT" else "Open"
                )
            } if tr["photo"] in radius_display.columns else None
        )

        radius_csv = radius_display.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            tr["export_radius"],
            data=radius_csv,
            file_name="lis_access_obstaculos_dentro_raio.csv" if lang == "PT" else "lis_access_obstacles_within_radius.csv",
            mime="text/csv",
            key="download_radius_obstacles"
        )

    st.divider()
    st.subheader(tr["poi_section"])
    poi_type_col = "poi_type_pt" if lang == "PT" else "poi_type_en"
    poi_types = sorted(pois[poi_type_col].dropna().unique())
    chosen_poi_types = st.multiselect(tr["poi_type"], poi_types, default=poi_types)
    acc_opts = sorted(pois["accessibility"].dropna().unique())
    chosen_acc = st.multiselect(tr["accessibility"], acc_opts, default=acc_opts)
    poi_filtered = pois[pois[poi_type_col].isin(chosen_poi_types)].copy()
    if chosen_acc:
        poi_filtered = poi_filtered[
            poi_filtered["accessibility"].isin(chosen_acc) | poi_filtered["accessibility"].isna()
        ]
    st.dataframe(
        poi_filtered[[poi_type_col,"condition","accessibility","cleanliness","reported_at","photo"]],
        use_container_width=True, hide_index=True
    )

# ---------- TAB 3 PLANNING / TASK LOCK ----------
with tabs[3]:
    st.subheader(tr["task_management"])
    st.caption(tr["assignment_note"])

    task_df = filtered.copy()
    task_df["display"] = task_df.apply(
        lambda r: f"{r['obstacle_id'][:8]} · {safe(r.get(type_col))} · {safe(r.get('street_name'))}",
        axis=1
    )
    choices = task_df["display"].tolist()
    if not choices:
        st.warning("No results / Sem resultados")
    else:
        choice = st.selectbox(tr["choose_obstacle"], choices)
        row = task_df[task_df["display"] == choice].iloc[0]
        oid = str(row["obstacle_id"])
        existing = dict(st.session_state.task_state.get(oid, {}))

        owner = existing.get("entity")
        is_locked = bool(existing.get("locked"))
        can_edit = profile == tr["admin"] or (
            profile == tr["service_user"] and owner and current_entity == owner
        )
        if is_locked and profile == tr["service_user"] and current_entity != owner:
            can_edit = False
            st.error(tr["task_access_denied"])

        default_int = existing.get("intervention") or default_intervention(row.get("type_pt"))
        intervention = st.text_input(tr["intervention"], value=default_int, disabled=not can_edit)

        entity_options = [
            tr["unassigned"],
            "CML – serviço a definir",
            "Junta de Freguesia",
            "Direção Municipal de Mobilidade",
            "Direção Municipal de Ambiente / Estrutura Verde",
            "Operador / concessionário externo",
            "Outro"
        ]
        if owner and owner not in entity_options:
            entity_options.append(owner)
        entity_index = entity_options.index(owner) if owner in entity_options else 0
        entity = st.selectbox(tr["entity"], entity_options, index=entity_index, disabled=(profile != tr["admin"]))

        lock = st.checkbox(tr["lock"], value=is_locked, disabled=(profile != tr["admin"]))

        c1,c2,c3 = st.columns(3)
        cost_val = existing.get("cost")
        time_val = existing.get("time_hours")
        complexity_val = existing.get("complexity")

        cost = c1.number_input(tr["cost"], min_value=0.0, value=float(cost_val or 0), step=50.0, disabled=not can_edit)
        time_h = c2.number_input(tr["time"], min_value=0.0, value=float(time_val or 0), step=.5, disabled=not can_edit)
        complexity_options = ["—","1","2","3","4","5"]
        ci = complexity_options.index(str(complexity_val)) if str(complexity_val) in complexity_options else 0
        complexity = c3.selectbox(tr["complexity"], complexity_options, index=ci, disabled=not can_edit)

        statuses = [tr["not_started"], tr["in_progress"], tr["checkpoint"], tr["resolved"]]
        prev_status = existing.get("status")
        si = statuses.index(prev_status) if prev_status in statuses else 0
        status = st.selectbox(tr["status"], statuses, index=si, disabled=not can_edit)

        if st.button(tr["save_task"], type="primary", disabled=not can_edit):
            chosen_entity = None if entity == tr["unassigned"] else entity
            st.session_state.task_state[oid] = {
                "intervention": intervention,
                "entity": chosen_entity,
                "locked": bool(lock),
                "cost": cost if cost > 0 else None,
                "time_hours": time_h if time_h > 0 else None,
                "complexity": None if complexity == "—" else int(complexity),
                "status": status,
                "parish": row.get("freguesia"),
                "street": row.get("street_name"),
                "obstacle_type_pt": row.get("type_pt"),
                "obstacle_type_en": row.get("type_en"),
            }
            save_task_state(st.session_state.task_state)
            st.success("Guardado / Saved")

    st.divider()
    st.subheader(tr["priority"])
    st.caption(tr["priority_note"])

    pri_rows = []
    for oid, task in st.session_state.task_state.items():
        if task.get("cost") and task.get("time_hours") and task.get("complexity"):
            pri_rows.append({
                "obstacle_id": oid,
                tr["intervention"]: task.get("intervention"),
                tr["entity"]: task.get("entity"),
                tr["cost"]: task.get("cost"),
                tr["time"]: task.get("time_hours"),
                tr["complexity"]: task.get("complexity"),
                tr["status"]: task.get("status"),
            })
    if pri_rows:
        pri = pd.DataFrame(pri_rows)
        # lower cost, time, complexity = easier/quick-win. Kept separate, no composite score.
        sort_by = st.selectbox(
            tr["priority"],
            [tr["cost"], tr["time"], tr["complexity"]]
        )
        st.dataframe(pri.sort_values(sort_by), use_container_width=True, hide_index=True)
    else:
        st.info(tr["no_priority"])

# ---------- TAB 4 MONITORING ----------
with tabs[4]:
    st.subheader(tr["global_summary"])
    state = st.session_state.task_state
    total_tasks = len(state)
    assigned = sum(1 for v in state.values() if v.get("entity"))
    resolved = sum(1 for v in state.values() if v.get("status") == tr["resolved"] or v.get("status") == T["PT"]["resolved"] or v.get("status") == T["EN"]["resolved"])
    rate = (resolved / total_tasks * 100) if total_tasks else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric(tr["obstacles"], len(obs))
    c2.metric(tr["assigned"], assigned)
    c3.metric(tr["resolved_count"], resolved)
    c4.metric(tr["resolution_rate"], f"{rate:.1f}%")

    rows = []
    for oid, task in state.items():
        rows.append({
            "obstacle_id": oid,
            tr["obstacle_type"]: task.get("obstacle_type_pt") if lang=="PT" else task.get("obstacle_type_en"),
            tr["street"]: task.get("street"),
            tr["parish"]: task.get("parish"),
            tr["intervention"]: task.get("intervention"),
            tr["entity"]: task.get("entity"),
            tr["status"]: task.get("status"),
            tr["locked"]: task.get("locked"),
            tr["cost"]: task.get("cost"),
            tr["time"]: task.get("time_hours"),
            tr["complexity"]: task.get("complexity"),
        })
    monitor = pd.DataFrame(rows)

    if monitor.empty:
        st.info("Ainda não existem tarefas atribuídas / No tasks assigned yet.")
    else:
        st.dataframe(monitor, use_container_width=True, hide_index=True)

        st.subheader(tr["by_entity"])
        by_ent = (
            monitor.fillna({tr["entity"]: tr["unassigned"]})
            .groupby(tr["entity"], dropna=False)
            .agg(total=("obstacle_id","count"))
            .reset_index()
            .sort_values("total", ascending=False)
        )
        st.dataframe(by_ent, use_container_width=True, hide_index=True)

        st.subheader(tr["by_parish"])
        by_par = (
            monitor.fillna({tr["parish"]:"—"})
            .groupby(tr["parish"], dropna=False)
            .agg(total=("obstacle_id","count"))
            .reset_index()
            .sort_values("total", ascending=False)
        )
        st.dataframe(by_par, use_container_width=True, hide_index=True)

st.divider()
export_df = filtered.copy()
csv = export_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    tr["download"],
    data=csv,
    file_name="lis_access_filtered_obstacles.csv",
    mime="text/csv"
)
