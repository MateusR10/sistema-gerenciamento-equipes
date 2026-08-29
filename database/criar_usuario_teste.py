from db import conectar

conexao = conectar()

# Verifica se o participante de teste já existe, pra não duplicar
existente = conexao.execute(
    "SELECT id FROM usuarios WHERE email = ?", ("participante@teste.com",)
) .fetchone()

if existente is None:
    conexao.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        ("João Participante", "participante@teste.com", "123456", "PARTICIPANTE")
    )
    conexao.commit()
    print("Participante de teste criado!")
else:
    print("Participante de teste já existia, nada foi criado.")

conexao.close()