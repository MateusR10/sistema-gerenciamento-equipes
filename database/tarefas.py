from datetime import datetime
from db import conectar

FASES = ["A Fazer", "Em Andamento", "Em Revisão", "Concluído"]


def listar_tarefas(id_responsavel=None):
    """
    Lista tarefas do banco.
    Se id_responsavel for None, retorna todas as tarefas (visão do ADM).
    Se for informado, retorna só as tarefas daquele responsável (visão do participante).
    """
    conexao = conectar()
    if id_responsavel is None:
        cursor = conexao.execute(
            """
            SELECT tarefas.id, tarefas.titulo, tarefas.descricao, tarefas.fase_atual,
                   tarefas.prazo, tarefas.id_responsavel, usuarios.nome
            FROM tarefas
            JOIN usuarios ON usuarios.id = tarefas.id_responsavel
            ORDER BY tarefas.data_criacao DESC
            """
        )
    else:
        cursor = conexao.execute(
            """
            SELECT tarefas.id, tarefas.titulo, tarefas.descricao, tarefas.fase_atual,
                   tarefas.prazo, tarefas.id_responsavel, usuarios.nome
            FROM tarefas
            JOIN usuarios ON usuarios.id = tarefas.id_responsavel
            WHERE tarefas.id_responsavel = ?
            ORDER BY tarefas.data_criacao DESC
            """,
            (id_responsavel,),
        )
    tarefas = cursor.fetchall()
    conexao.close()
    return tarefas


def listar_usuarios():
    """Lista todos os usuários (usado pelo ADM para atribuir tarefas)."""
    conexao = conectar()
    cursor = conexao.execute("SELECT id, nome, tipo FROM usuarios ORDER BY nome")
    usuarios = cursor.fetchall()
    conexao.close()
    return usuarios


def criar_tarefa(titulo, descricao, id_responsavel, prazo=None):
    conexao = conectar()
    agora = datetime.now().isoformat(timespec="seconds")
    cursor = conexao.execute(
        """
        INSERT INTO tarefas (titulo, descricao, id_responsavel, fase_atual, data_criacao, prazo)
        VALUES (?, ?, ?, 'A Fazer', ?, ?)
        """,
        (titulo, descricao, id_responsavel, agora, prazo),
    )
    id_tarefa = cursor.lastrowid
    conexao.execute(
        "INSERT INTO historico_fases (id_tarefa, fase, data_inicio) VALUES (?, 'A Fazer', ?)",
        (id_tarefa, agora),
    )
    conexao.commit()
    conexao.close()
    return id_tarefa


def mover_tarefa(id_tarefa, nova_fase):
    """Move uma tarefa para outra fase e registra o histórico de tempo por fase."""
    if nova_fase not in FASES:
        raise ValueError(f"Fase inválida: {nova_fase}")

    conexao = conectar()
    agora = datetime.now().isoformat(timespec="seconds")

    # Fecha o registro de histórico da fase anterior (se existir e ainda estiver aberto)
    conexao.execute(
        """
        UPDATE historico_fases
        SET data_fim = ?
        WHERE id_tarefa = ? AND data_fim IS NULL
        """,
        (agora, id_tarefa),
    )

    # Abre um novo registro de histórico para a nova fase
    conexao.execute(
        "INSERT INTO historico_fases (id_tarefa, fase, data_inicio) VALUES (?, ?, ?)",
        (id_tarefa, nova_fase, agora),
    )

    # Atualiza a fase atual da tarefa
    conexao.execute(
        "UPDATE tarefas SET fase_atual = ? WHERE id = ?",
        (nova_fase, id_tarefa),
    )

    conexao.commit()
    conexao.close()


def buscar_fase(id_tarefa):
    """Retorna a fase atual de uma tarefa específica."""
    conexao = conectar()
    cursor = conexao.execute("SELECT fase_atual FROM tarefas WHERE id = ?", (id_tarefa,))
    linha = cursor.fetchone()
    conexao.close()
    return linha[0] if linha else None


def excluir_tarefa(id_tarefa):
    conexao = conectar()
    conexao.execute("DELETE FROM historico_fases WHERE id_tarefa = ?", (id_tarefa,))
    conexao.execute("DELETE FROM tarefas WHERE id = ?", (id_tarefa,))
    conexao.commit()
    conexao.close()