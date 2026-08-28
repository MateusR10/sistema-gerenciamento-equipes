import streamlit as st
import sys
import os

# Adiciona a pasta "database" na lista de lugares onde o Python procura módulos
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))

from usuarios import verificar_login

st.title("Sistema de Gerenciamento de Equipes")

st.subheader("Login")

email = st.text_input("E-mail")
senha = st.text_input("Senha", type="password")

if st.button("Entrar"):
    usuario = verificar_login(email, senha)
    if usuario is None:
        st.error("E-mail ou senha inválidos.")
    else:
        st.success(f"Bem-vindo, {usuario[1]}!")