# populate_db.py

import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

# Inicializa o Faker para gerar dados em português do Brasil
fake = Faker('pt_BR')

# --- CONFIGURAÇÕES ---
DB_NAME = "gestao_projetos.db"
NUM_USUARIOS = 50
NUM_PROJETOS = 20
NUM_TAREFAS = 500
NUM_EQUIPES = 10
# ---------------------

def get_connection():
    """Função auxiliar para conectar ao banco de dados."""
    return sqlite3.connect(DB_NAME)

def populate_data():
    """Função principal que gera e insere todos os dados."""
    
    print("Iniciando a população do banco de dados...")
    
    conn = get_connection()
    cursor = conn.cursor()

    # --- ETAPA 1: Gerar e Inserir Usuários ---
    print(f"Gerando {NUM_USUARIOS} usuários...")
    usuarios = []
    for i in range(NUM_USUARIOS):
        nome_completo = fake.name()
        primeiro_nome = nome_completo.split(' ')[0].lower().replace('.', '')
        login_unico = f"{primeiro_nome}{i}"
        
        usuario = (
            nome_completo, fake.cpf(), fake.email(), fake.job(),
            login_unico, 'senha123', random.choice(['administrador', 'gerente', 'colaborador'])
        )
        usuarios.append(usuario)
    
    cursor.executemany("INSERT INTO usuarios (nome_completo, cpf, email, cargo, login, senha, perfil) VALUES (?, ?, ?, ?, ?, ?, ?)", usuarios)

    # --- ETAPA 2: Gerar e Inserir Projetos ---
    print(f"Gerando {NUM_PROJETOS} projetos...")
    cursor.execute("SELECT id FROM usuarios WHERE perfil = 'gerente' OR perfil = 'administrador'")
    gerente_ids = [row[0] for row in cursor.fetchall()]
    projetos = []
    for _ in range(NUM_PROJETOS):
        data_inicio = fake.date_time_between(start_date='-2y', end_date='-1y')
        data_fim = data_inicio + timedelta(days=random.randint(60, 365))
        projeto = (
            'Projeto ' + fake.bs().title(), fake.paragraph(nb_sentences=3),
            data_inicio.strftime('%Y-%m-%d'), data_fim.strftime('%Y-%m-%d'),
            random.choice(['Planejado', 'Em Andamento', 'Concluído', 'Cancelado']),
            random.choice(gerente_ids) if gerente_ids else None
        )
        projetos.append(projeto)
    cursor.executemany("INSERT INTO projetos (nome, descricao, data_inicio, data_termino_prevista, status, gerente_id) VALUES (?, ?, ?, ?, ?, ?)", projetos)

    # --- ETAPA 3: Gerar e Inserir Tarefas ---
    print(f"Gerando {NUM_TAREFAS} tarefas...")
    cursor.execute("SELECT id FROM usuarios")
    todos_usuario_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM projetos")
    todos_projeto_ids = [row[0] for row in cursor.fetchall()]
    tarefas = []
    for _ in range(NUM_TAREFAS):
        data_inicio_dt = fake.date_time_between(start_date='-1y', end_date='now')
        duracao_total = timedelta(days=random.randint(5, 30))
        data_fim_prevista_dt = data_inicio_dt + duracao_total
        
        status = random.choice(['Pendente', 'Em Andamento', 'Concluída', 'Cancelada'])
        data_conclusao = None
        
        if status == 'Concluída':
            dias_para_concluir = timedelta(days=random.randint(1, duracao_total.days))
            data_conclusao_dt = data_inicio_dt + dias_para_concluir
            data_conclusao = data_conclusao_dt.strftime('%Y-%m-%d')

        tarefa = (
            fake.sentence(nb_words=4).replace('.', ''), fake.paragraph(nb_sentences=2),
            data_inicio_dt.strftime('%Y-%m-%d'), data_fim_prevista_dt.strftime('%Y-%m-%d'),
            status, random.choice(['Baixa', 'Média', 'Alta']),
            random.choice(todos_usuario_ids), random.choice(todos_projeto_ids),
            data_conclusao
        )
        tarefas.append(tarefa)
    
    cursor.executemany("""
        INSERT INTO tarefas (titulo, descricao, data_inicio, data_termino_prevista, status, prioridade, responsavel_id, projeto_id, data_conclusao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tarefas)

    # --- ETAPA 4: Gerar e Inserir Equipes e Associações ---
    print(f"Gerando {NUM_EQUIPES} equipes e associações...")
    equipes = []
    for _ in range(NUM_EQUIPES):
        equipes.append((f"Equipe {fake.company_suffix()}", fake.catch_phrase()))
    cursor.executemany("INSERT INTO equipes (nome, descricao) VALUES (?, ?)", equipes)
    
    cursor.execute("SELECT id FROM equipes")
    todos_equipe_ids = [row[0] for row in cursor.fetchall()]
    associacoes = list(set([(random.choice(todos_equipe_ids), user_id) for user_id in todos_usuario_ids for _ in range(random.randint(1, 2))]))
    cursor.executemany("INSERT INTO equipe_usuario (equipe_id, usuario_id) VALUES (?, ?)", associacoes)

    conn.commit()
    conn.close()
    print("\nBanco de dados populado com sucesso!")

if __name__ == "__main__":
    populate_data()