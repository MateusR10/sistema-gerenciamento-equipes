from datetime import datetime
from database.db import conectar

FORMATO_DATA = "%Y-%m-%d %H:%M:%S"


def get_ou_criar_usuario(nome):
    # ainda não temos cadastro/login de usuários, então por enquanto
    # criamos o usuário na hora se ele não existir. trocar isso quando
    # a tela de usuários existir.
    nome = nome.strip()
    conexao = conectar()
    try:
        linha = conexao.execute("SELECT id FROM usuarios WHERE nome = ?", (nome,)).fetchone()
        if linha:
            return linha[0]

        email = f"{nome.lower().replace(' ', '.')}@temp.local"
        cursor = conexao.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, "temporaria", "PARTICIPANTE"),
        )
        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()


def criar_tarefa(titulo, descricao, responsavel_nome, prazo=None):
    id_responsavel = get_ou_criar_usuario(responsavel_nome)
    agora = datetime.now().strftime(FORMATO_DATA)

    conexao = conectar()
    try:
        cursor = conexao.execute(
            """INSERT INTO tarefas (titulo, descricao, id_responsavel, fase_atual, data_criacao, prazo)
               VALUES (?, ?, ?, 'A Fazer', ?, ?)""",
            (titulo, descricao, id_responsavel, agora, prazo),
        )
        id_tarefa = cursor.lastrowid
        conexao.execute(
            "INSERT INTO historico_fases (id_tarefa, fase, data_inicio, data_fim) VALUES (?, 'A Fazer', ?, NULL)",
            (id_tarefa, agora),
        )
        conexao.commit()
        return id_tarefa
    finally:
        conexao.close()


def listar_tarefas():
    conexao = conectar()
    try:
        linhas = conexao.execute(
            """
            SELECT t.id, t.titulo, t.fase_atual, u.nome,
                   (SELECT h.data_inicio FROM historico_fases h
                    WHERE h.id_tarefa = t.id AND h.fase = t.fase_atual AND h.data_fim IS NULL
                    ORDER BY h.id DESC LIMIT 1)
            FROM tarefas t
            JOIN usuarios u ON u.id = t.id_responsavel
            ORDER BY t.id
            """
        ).fetchall()
        return [
            {"id": l[0], "titulo": l[1], "fase_atual": l[2], "responsavel": l[3], "inicio_fase_atual": l[4]}
            for l in linhas
        ]
    finally:
        conexao.close()


def mover_fase(id_tarefa, nova_fase):
    agora = datetime.now().strftime(FORMATO_DATA)
    conexao = conectar()
    try:
        conexao.execute(
            "UPDATE historico_fases SET data_fim = ? WHERE id_tarefa = ? AND data_fim IS NULL",
            (agora, id_tarefa),
        )
        conexao.execute(
            "INSERT INTO historico_fases (id_tarefa, fase, data_inicio, data_fim) VALUES (?, ?, ?, NULL)",
            (id_tarefa, nova_fase, agora),
        )
        conexao.execute("UPDATE tarefas SET fase_atual = ? WHERE id = ?", (nova_fase, id_tarefa))
        conexao.commit()
    finally:
        conexao.close()


def tempo_total_execucao(id_tarefa):
    """Do momento em que entrou em 'Em Andamento' até entrar em 'Concluído'.
    Retorna None se a tarefa ainda não passou por esse ciclo completo."""
    conexao = conectar()
    try:
        inicio = conexao.execute(
            "SELECT data_inicio FROM historico_fases WHERE id_tarefa = ? AND fase = 'Em Andamento' ORDER BY id ASC LIMIT 1",
            (id_tarefa,),
        ).fetchone()
        fim = conexao.execute(
            "SELECT data_inicio FROM historico_fases WHERE id_tarefa = ? AND fase = 'Concluído' ORDER BY id DESC LIMIT 1",
            (id_tarefa,),
        ).fetchone()
        if not inicio or not fim:
            return None
        return datetime.strptime(fim[0], FORMATO_DATA) - datetime.strptime(inicio[0], FORMATO_DATA)
    finally:
        conexao.close()