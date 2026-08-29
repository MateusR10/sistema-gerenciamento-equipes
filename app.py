import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "database"))

from usuarios import verificar_login

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

            st.success(f"Bem-vindo, {nome}! (Perfil: {tipo})")

            if tipo == "ADM":
                 tela_adm()
            else:
                 tela_participante()

            if st.button("Sair"):
                 st.session_state.usuario_logado = None
                 st.rerun()

def tela_adm():
     st.subheader("Painel do ADM")
     st.write("Aqui, mais pra frente, o ADM vai ver todas as tarefas de todos os participantes.")

def tela_participante():
     st.subheader("Minhas tarefas")
     st.write("Aqui, mais pra frente, o participante vai ver apenas as próprias tarefas.")

# Decide qual tela mostrar, dependendo se tem alguém logado ou não
if st.session_state.usuario_logado is None:
     tela_login()
else:
     tela_principal()