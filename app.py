import streamlit as st
from datetime import datetime
from streamlit_sortables import sort_items

from database.db import inicializar_banco
from database import tarefas_repo as repo

st.set_page_config(page_title="Sistema de Gerenciamento de Equipes", page_icon="🗂️", layout="wide")

inicializar_banco()

FASES = ["A Fazer", "Em Andamento", "Em Revisão", "Concluído"]

CUSTOM_CSS = """
.sortable-component {
    display: flex;
    gap: 14px;
    overflow-x: auto;
    padding-bottom: 10px;
}
.sortable-container {
    background: #F1F2F6;
    border-radius: 12px;
    padding: 10px;
    min-width: 240px;
    flex: 0 0 240px;
}
.sortable-container-header {
    font-weight: 600;
    font-size: 0.9rem;
    color: #374151;
    padding: 6px 4px 12px 4px;
    margin-bottom: 6px;
    border-bottom: 2px solid rgba(0,0,0,0.08);
}
.sortable-item {
    background: #ff8f;
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 8px;
    font-size: 0.83rem;
    line-height: 1.5;
    white-space: pre-line;
    box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    border-left: 4px solid #94A3B8;
    cursor: grab;
}
.sortable-container:nth-child(2) .sortable-item { border-left-color: #F59E0B; }
.sortable-container:nth-child(3) .sortable-item { border-left-color: #8B5CF6; }
.sortable-container:nth-child(4) .sortable-item { border-left-color: #10B981; }
"""

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
</style>
""", unsafe_allow_html=True)


def tempo_decorrido(inicio_str):
    if not inicio_str:
        return None
    inicio = datetime.strptime(inicio_str, "%Y-%m-%d %H:%M:%S")
    segundos = int((datetime.now() - inicio).total_seconds())
    h, resto = divmod(segundos, 3600)
    m = resto // 60
    if h:
        return f"{h}h {m}min"
    if m:
        return f"{m}min"
    return "agora mesmo"


def formatar_intervalo(delta):
    minutos_totais = int(delta.total_seconds() // 60)
    h, m = divmod(minutos_totais, 60)
    return f"{h}h {m}min" if h else f"{m}min"


st.title("🗂️ Quadro de Atividades")

with st.expander("➕ Nova atividade"):
    with st.form("form_nova_tarefa", clear_on_submit=True):
        col1, col2 = st.columns(2)
        titulo = col1.text_input("Título")
        responsavel = col2.text_input("Responsável")
        descricao = st.text_area("Descrição", height=70)
        enviar = st.form_submit_button("Cadastrar")

        if enviar:
            if not titulo.strip() or not responsavel.strip():
                st.warning("Preencha ao menos o título e o responsável.")
            else:
                repo.criar_tarefa(titulo.strip(), descricao.strip() or None, responsavel.strip())
                st.rerun()

st.divider()

tarefas = repo.listar_tarefas()
tarefas_por_id = {t["id"]: t for t in tarefas}

containers = []
rotulo_para_id = {}

for fase in FASES:
    tarefas_da_fase = [t for t in tarefas if t["fase_atual"] == fase]
    rotulos = []

    for t in tarefas_da_fase:
        linhas = [f"#{t['id']} · {t['titulo']}", f"👤 {t['responsavel']}"]

        if fase == "Em Andamento":
            duracao = tempo_decorrido(t["inicio_fase_atual"])
            if duracao:
                linhas.append(f"⏱ {duracao}")
        elif fase == "Concluído":
            total = repo.tempo_total_execucao(t["id"])
            if total:
                linhas.append(f"✅ {formatar_intervalo(total)}")

        rotulo = "\n".join(linhas)
        rotulos.append(rotulo)
        rotulo_para_id[rotulo] = t["id"]

    containers.append({"header": f"{fase} ({len(tarefas_da_fase)})", "items": rotulos})

resultado = sort_items(
    containers,
    multi_containers=True,
    direction="horizontal",
    custom_style=CUSTOM_CSS,
    key="quadro_kanban",
)

houve_mudanca = False
for indice, grupo in enumerate(resultado):
    fase_nova = FASES[indice]
    for rotulo in grupo["items"]:
        id_tarefa = rotulo_para_id.get(rotulo)
        if id_tarefa and tarefas_por_id[id_tarefa]["fase_atual"] != fase_nova:
            repo.mover_fase(id_tarefa, fase_nova)
            houve_mudanca = True

if houve_mudanca:
    st.rerun()