import streamlit as st
import sys
import os
from streamlit_sortables import sort_items

sys.path.append(os.path.join(os.path.dirname(__file__), "database"))

from usuarios import verificar_login
from tarefas import FASES, listar_tarefas, listar_usuarios, criar_tarefa, mover_tarefa, excluir_tarefa

st.set_page_config(page_title="Sistema de Gerenciamento de Equipes", layout="wide")
st.title("Sistema de Gerenciamento de Equipes")

# Se ainda não existe "usuario_logado" na memória da sessão, criamos com valor None
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None


def tela_login():
    st.subheader("Login")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        usuario = verificar_login(email, senha)
        if usuario is None:
            st.error("E-mail ou senha inválidos.")
        else:
            st.session_state.usuario_logado = usuario
            st.rerun()


def tela_principal():
    usuario = st.session_state.usuario_logado
    nome = usuario[1]
    tipo = usuario[4]

    col_boas_vindas, col_sair = st.columns([5, 1])
    with col_boas_vindas:
        st.success(f"Bem-vindo, {nome}! (Perfil: {tipo})")
    with col_sair:
        if st.button("Sair"):
            st.session_state.usuario_logado = None
            st.rerun()

    if tipo == "ADM":
        tela_adm(usuario)
    else:
        tela_participante(usuario)


def _formulario_nova_tarefa(usuario, permitir_escolher_responsavel):
    """Formulário de criação de tarefa. ADM escolhe o responsável; participante cria pra si mesmo."""
    with st.expander("➕ Nova tarefa", expanded=False):
        titulo = st.text_input("Título da tarefa", key="novo_titulo")
        descricao = st.text_area("Descrição", key="nova_descricao")

        if permitir_escolher_responsavel:
            usuarios = listar_usuarios()
            opcoes = {f"{u[1]} ({u[2]})": u[0] for u in usuarios}
            responsavel_label = st.selectbox("Responsável", list(opcoes.keys()), key="novo_responsavel")
            id_responsavel = opcoes[responsavel_label]
        else:
            id_responsavel = usuario[0]

        prazo = st.date_input("Prazo", value=None, key="novo_prazo")

        if st.button("Criar tarefa", key="botao_criar_tarefa"):
            if not titulo:
                st.warning("Informe um título para a tarefa.")
            else:
                criar_tarefa(
                    titulo=titulo,
                    descricao=descricao,
                    id_responsavel=id_responsavel,
                    prazo=prazo.isoformat() if prazo else None,
                )
                st.success("Tarefa criada!")
                st.rerun()


def _quadro_kanban(tarefas, mostrar_responsavel, chave):
    """Desenha o quadro Kanban com colunas arrastáveis (drag-and-drop)."""
    if not tarefas:
        st.info("Nenhuma tarefa por aqui ainda.")
        return

    # Mapeia o texto exibido em cada cartão de volta pro id da tarefa e pra fase original
    texto_para_id = {}
    fase_original_por_id = {}
    itens_por_fase = {fase: [] for fase in FASES}

    for tarefa in tarefas:
        id_tarefa, titulo, descricao, fase_atual, prazo, id_responsavel, nome_responsavel = tarefa
        texto = f"#{id_tarefa} · {titulo}"
        if mostrar_responsavel:
            texto += f" ({nome_responsavel})"
        texto_para_id[texto] = id_tarefa
        fase_original_por_id[id_tarefa] = fase_atual
        itens_por_fase[fase_atual].append(texto)

    containers = [{"header": fase, "items": itens_por_fase[fase]} for fase in FASES]

    estilo = """
    .sortable-component.vertical {
        gap: 1rem;
        align-items: flex-start;
    }
    .sortable-container {
        background-color: rgba(151, 166, 195, 0.10) !important;
        border-radius: 0.5rem;
    }
    .sortable-container-header {
        font-weight: 600;
        padding: 0.5rem 0.75rem !important;
        background-color: rgba(151, 166, 195, 0.25) !important;
        border-radius: 0.5rem 0.5rem 0 0;
    }
    .sortable-container-body {
        min-height: 120px;
        padding: 0.5rem !important;
    }
    .sortable-item {
        background-color: #ffffff !important;
        color: #262730 !important;
        border: 1px solid rgba(151, 166, 195, 0.35);
        border-radius: 0.4rem;
        padding: 0.5rem 0.75rem !important;
        margin-bottom: 0.5rem;
        cursor: grab;
    }
    """

    resultado = sort_items(
        containers,
        multi_containers=True,
        direction="vertical",
        custom_style=estilo,
        key=chave,
    )

    # Compara o resultado do arrasta-e-solta com o estado salvo no banco
    # e persiste qualquer mudança de fase detectada.
    houve_mudanca = False
    for container in resultado:
        nova_fase = container["header"]
        for texto in container["items"]:
            id_tarefa = texto_para_id.get(texto)
            if id_tarefa is None:
                continue
            if fase_original_por_id[id_tarefa] != nova_fase:
                mover_tarefa(id_tarefa, nova_fase)
                houve_mudanca = True

    if houve_mudanca:
        st.rerun()


def tela_adm(usuario):
    st.subheader("Painel do ADM")
    _formulario_nova_tarefa(usuario, permitir_escolher_responsavel=True)

    st.divider()
    st.markdown("### Quadro Kanban (todas as tarefas)")
    st.caption("Arraste os cartões entre as colunas para mudar a fase.")
    tarefas = listar_tarefas()  # None = todas
    _quadro_kanban(tarefas, mostrar_responsavel=True, chave="kanban_adm")


def tela_participante(usuario):
    st.subheader("Minhas tarefas")
    _formulario_nova_tarefa(usuario, permitir_escolher_responsavel=False)

    st.divider()
    st.caption("Arraste os cartões entre as colunas para mudar a fase.")
    id_usuario = usuario[0]
    tarefas = listar_tarefas(id_responsavel=id_usuario)
    _quadro_kanban(tarefas, mostrar_responsavel=False, chave="kanban_participante")


# Decide qual tela mostrar, dependendo se tem alguém logado ou não
if st.session_state.usuario_logado is None:
    tela_login()
else:
    tela_principal()