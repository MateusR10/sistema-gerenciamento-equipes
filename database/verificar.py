import sqlite3

conexao = sqlite3.connect("gerenciamento.db")
tabelas = conexao.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(tabelas)
conexao.close()