from db import conectar

def buscar_usuario_por_email(email):
    """"
    Procura um usuário no banco pelo e-mail.
    Retorna os dados do usuário se encontrar, ou Nome se não existir.
    """
    conexao = conectar()
    cursor = conexao.execute(
        "SELECT id, nome, email, senha, tipo FROM usuarios WHERE email = ?",
        (email,)
    )

    usuario = cursor.fetchone()
    conexao.close()
    return usuario

def verificar_login(email, senha):
    """
    Confere se existe um usuário com esse email E essa senha.
    Retorna os dados do usuário se o login for válido, ou None se não for.
    """
    usuario = buscar_usuario_por_email(email)
    if usuario is None:
        return None

    senha_do_banco = usuario[3] # posição 3 = coluna "senha"
    if senha_do_banco == senha:
        return usuario
    else:
        return None