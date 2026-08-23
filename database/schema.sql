CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email  TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('ADM', 'PARTICIPANTE'))
);

CREATE TABLE IF NOT EXISTS tarefas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    id_responsavel INTEGER NOT NULL,
    fase_atual TEXT NOT NULL DEFAULT 'A Fazer'
    CHECK (fase_atual IN ('A Fazer', 'Em Andamento', 'Em Revisão', 'Concluído')),
    data_criacao TEXT NOT NULL,
    prazo TEXT,
    FOREIGN KEY (id_responsavel) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS historico_fases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tarefa INTEGER NOT NULL,
    fase TEXT NOT NULL,
    data_inicio TEXT NOT NULL,
    data_fim TEXT,
    FOREIGN KEY (id_tarefa) REFERENCES tarefas(id)
);