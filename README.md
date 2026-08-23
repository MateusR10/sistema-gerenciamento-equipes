# Sistema de Gerenciamento de Equipes

Projeto de RAD (Rapid Application Development) para acompanhar o rendimento da equipe usando um quadro Kanban com controle de tempo por fase.

## Como rodar o projeto (primeira vez)

1. Clonar o repositório e entrar na pasta
2. Criar o ambiente virtual: entrem no terminal e digite:
```bash
   python -m venv venv
```
3. Ativar o ambiente virtual:
   - Windows (PowerShell): `venv\Scripts\activate`
   
4. Instalar as dependências: entrem no terminal e digite:
```bash
   pip install streamlit pandas
```
ou
```bash
pip install -r requeriments.txt
```
5. Criar o banco de dados local: entrar no terminal e digitar:
```bash
   python database/db.py
```

Isso vai gerar o arquivo `database/gerenciamento.db` (não é enviado ao Git, porque cada um tem que gerar o seu ao rodar o comando acima).

## Estrutura do projeto

sistema-gerenciamento-equipes/
├── database/
│ ├── schema.sql -> definição das tabelas (fonte da verdade)
│ ├── db.py -> conecta e inicializa o banco
│ └── verificar.py -> script auxiliar pra checar as tabelas criadas
├── app.py -> ponto de entrada do Streamlit
├── requirements.txt
├── .gitignore
└── README.md


## Andamento

- [x] Aula 1: estrutura do projeto, modelo de dados (usuarios, tarefas, historico_fases), banco criado e testado
- [ ] Aula 2: tela de login (perfis ADM / Participante)
- [ ] Aula 3: CRUD de tarefas + quadro Kanban
- [ ] Aula 4: registro automático de tempo por fase
- [ ] Aula 5: métricas, gráfico e exportação de relatório