import sqlite3
import os

# Caminho do arquivo do banco (vai ser criado na mesma pasta deste script)
CAMINHO_BANCO = os.path.join(os.path.dirname(__file__), "gerenciamento.db")

# Caminho do schema.sql
CAMINHO_SCHEMA = os.path.join(os.path.dirname(__file__), "schema.sql")

def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao

def inicializar_banco():
    conexao = conectar()
    with open(CAMINHO_SCHEMA, "r", encoding="utf-8") as arquivo:
        script_sql = arquivo.read()
    conexao.executescript(script_sql)
    conexao.commit()
    conexao.close()
    print(f"Banco inicializando em: {CAMINHO_BANCO}")

if __name__ == "__main__":
    inicializar_banco()