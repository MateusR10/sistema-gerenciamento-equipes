import streamlit as st
from datetime import datetime
from streamlit_sortables import sort_items

from database.db import inicializar_banco
from database import tarefas_repo as repo

# configuração básica da página (título na aba, ícone, layout ocupando a tela toda)
st.set_page_config(page_title="Sistema de Gerenciamento de Equipes", page_icon="🗂️", layout="wide")

# cria as tabelas no banco caso ainda não existam (não faz nada se já existirem)
inicializar_banco()

# ordem das colunas do kanban — é essa lista que dita a ordem em que elas aparecem na tela
FASES = ["A Fazer", "Em Andamento", "Em Revisão", "Concluído"]


def carregar_css(caminho):
    """Lê um arquivo .css do disco e devolve o conteúdo como texto."""
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return arquivo.read()


# aplica o css geral da página (fonte, etc.) — precisa do <style> porque é injetado via markdown
st.markdown(f"<style>{carregar_css('estilo/geral.css')}</style>", unsafe_allow_html=True)

# esse aqui não vai por <style>: o componente sort_items espera receber o css puro
CSS_KANBAN = carregar_css("estilo/kanban.css")


def tempo_decorrido(inicio_str):
    """Quanto tempo já passou desde que a tarefa entrou na fase atual (usado em 'Em Andamento')."""
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
    """Transforma um timedelta (ex: tempo total de execução) em texto tipo '2h 15min'."""
    minutos_totais = int(delta.total_seconds() // 60)
    h, m = divmod(minutos_totais, 60)
    return f"{h}h {m}min" if h else f"{m}min"


st.title("🗂️ Quadro de Atividades")

# ---- formulário de cadastro de nova atividade ----
# fica dentro de um expander pra não ocupar espaço da tela o tempo todo
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
                # cria a tarefa já na fase "A Fazer" (isso é feito dentro de criar_tarefa)
                repo.criar_tarefa(titulo.strip(), descricao.strip() or None, responsavel.strip())
                st.rerun()

st.divider()

# ---- monta os dados do quadro a partir do banco ----
tarefas = repo.listar_tarefas()
tarefas_por_id = {t["id"]: t for t in tarefas}

# o componente de arrastar trabalha com texto simples, então cada card vira uma
# string (título + responsável + tempo). guardamos um mapa rótulo -> id pra
# depois saber qual tarefa foi movida quando o usuário arrastar um card.
containers = []
rotulo_para_id = {}

for fase in FASES:
    tarefas_da_fase = [t for t in tarefas if t["fase_atual"] == fase]
    rotulos = []

    for t in tarefas_da_fase:
        linhas = [f"#{t['id']} · {t['titulo']}", f"👤 {t['responsavel']}"]

        # só mostra o cronômetro rodando quando a tarefa está em execução
        if fase == "Em Andamento":
            duracao = tempo_decorrido(t["inicio_fase_atual"])
            if duracao:
                linhas.append(f"⏱ {duracao}")
        # e o tempo total gasto quando ela já foi concluída
        elif fase == "Concluído":
            total = repo.tempo_total_execucao(t["id"])
            if total:
                linhas.append(f"✅ {formatar_intervalo(total)}")

        rotulo = "\n".join(linhas)
        rotulos.append(rotulo)
        rotulo_para_id[rotulo] = t["id"]

    containers.append({"header": f"{fase} ({len(tarefas_da_fase)})", "items": rotulos})

# ---- renderiza o quadro arrastável ----
# cada elemento de "resultado" reflete o estado atual da tela DEPOIS do usuário
# soltar o card em algum lugar — é comparando isso com o banco que descobrimos
# se algo mudou de coluna.
resultado = sort_items(
    containers,
    multi_containers=True,
    direction="horizontal",
    custom_style=CSS_KANBAN,
    key="quadro_kanban",
)

# ---- detecta se algum card mudou de fase e grava no banco ----
houve_mudanca = False
for indice, grupo in enumerate(resultado):
    fase_nova = FASES[indice]
    for rotulo in grupo["items"]:
        id_tarefa = rotulo_para_id.get(rotulo)
        if id_tarefa and tarefas_por_id[id_tarefa]["fase_atual"] != fase_nova:
            repo.mover_fase(id_tarefa, fase_nova)
            houve_mudanca = True

# se algo mudou, recarrega a página pra buscar o estado atualizado do banco
# (sem isso, o quadro podia mostrar um tempo/coluna desatualizado por um instante)
if houve_mudanca:
    st.rerun()