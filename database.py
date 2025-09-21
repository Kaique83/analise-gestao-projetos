# database.py
# Gerencia todas as interações com o banco de dados SQLite.

import sqlite3

class Database:
    """
    Classe para gerenciar a conexão e as operações no banco de dados.
    """
    def __init__(self, db_name="gestao_projetos.db"):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            # Tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_completo TEXT NOT NULL,
                    cpf TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    cargo TEXT NOT NULL,
                    login TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL,
                    perfil TEXT NOT NULL
                )
            ''')
            
            # Tabela de projetos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projetos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    data_inicio TEXT NOT NULL,
                    data_termino_prevista TEXT NOT NULL,
                    status TEXT NOT NULL,
                    gerente_id INTEGER,
                    FOREIGN KEY (gerente_id) REFERENCES usuarios (id) ON DELETE SET NULL
                )
            ''')
            
            # Tabela de Sprints
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    data_inicio TEXT,
                    data_fim TEXT,
                    status TEXT DEFAULT 'Planejado', -- Planejado, Ativo, Concluído
                    projeto_id INTEGER NOT NULL,
                    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
                )
            ''')

            # Tabela de tarefas com a nova coluna 'sprint_id'
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tarefas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descricao TEXT,
                    data_inicio TEXT NOT NULL,
                    data_termino_prevista TEXT NOT NULL,
                    status TEXT NOT NULL,
                    prioridade TEXT DEFAULT 'Média',
                    responsavel_id INTEGER,
                    projeto_id INTEGER,
                    sprint_id INTEGER, 
                    FOREIGN KEY (responsavel_id) REFERENCES usuarios (id) ON DELETE SET NULL,
                    FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE,
                    FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE SET NULL
                )
            ''')

            # Tabela de equipes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS equipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    descricao TEXT
                )
            ''')

            # Tabela de dependências entre tarefas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tarefa_dependencias (
                    tarefa_id INTEGER NOT NULL,
                    depende_de_id INTEGER NOT NULL,
                    PRIMARY KEY (tarefa_id, depende_de_id),
                    FOREIGN KEY (tarefa_id) REFERENCES tarefas(id) ON DELETE CASCADE,
                    FOREIGN KEY (depende_de_id) REFERENCES tarefas(id) ON DELETE CASCADE
                )
            ''')

            # Tabela de associação projeto-usuário
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projeto_usuario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    projeto_id INTEGER NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                    UNIQUE(projeto_id, usuario_id)
                )
            ''')

            # Tabela de associação equipe-usuário
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS equipe_usuario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    equipe_id INTEGER NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    FOREIGN KEY (equipe_id) REFERENCES equipes (id) ON DELETE CASCADE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                    UNIQUE(equipe_id, usuario_id)
                )
            ''')
            
            # Adiciona a coluna 'sprint_id' à tabela 'tarefas' se ela não existir
            try:
                cursor.execute("ALTER TABLE tarefas ADD COLUMN sprint_id INTEGER REFERENCES sprints(id) ON DELETE SET NULL")
                conn.commit()
            except sqlite3.OperationalError:
                pass # A coluna já existe
            
            # Insere o usuário 'admin' padrão
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE login = 'admin'")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO usuarios (nome_completo, cpf, email, cargo, login, senha, perfil)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', ('Administrador', '000.000.000-00', 'admin@empresa.com', 
                      'Administrador', 'admin', 'admin123', 'administrador'))
            
            conn.commit()
            
    # --- NOVO MÉTODO PARA O DASHBOARD DE SPRINT ---
    def get_sprint_ativo_por_projeto(self, projeto_id):
        """
        Busca o sprint que está atualmente com o status 'Ativo' para um projeto.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sprints WHERE projeto_id = ? AND status = 'Ativo' LIMIT 1", (projeto_id,))
            return cursor.fetchone()

    # --- MÉTODO ATUALIZADO PARA SPRINTS ---
    def criar_sprint(self, dados_sprint):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sprints (nome, data_inicio, data_fim, projeto_id) VALUES (?, ?, ?, ?)", dados_sprint)
            conn.commit()
            return cursor.lastrowid

    def get_sprints_por_projeto(self, projeto_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sprints WHERE projeto_id = ? ORDER BY data_inicio DESC", (projeto_id,))
            return cursor.fetchall()
            
    def get_tarefas_sem_sprint(self, projeto_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, titulo FROM tarefas WHERE projeto_id = ? AND sprint_id IS NULL", (projeto_id,))
            return cursor.fetchall()

    def get_tarefas_do_sprint(self, sprint_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, titulo FROM tarefas WHERE sprint_id = ?", (sprint_id,))
            return cursor.fetchall()
            
    def adicionar_tarefa_ao_sprint(self, tarefa_id, sprint_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tarefas SET sprint_id = ? WHERE id = ?", (sprint_id, tarefa_id))
            conn.commit()

    def remover_tarefa_do_sprint(self, tarefa_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tarefas SET sprint_id = NULL WHERE id = ?", (tarefa_id,))
            conn.commit()
            
    def get_sprint_por_id(self, sprint_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sprints WHERE id = ?", (sprint_id,))
            return cursor.fetchone()

    # --- NOVO MÉTODO ---
    def atualizar_status_sprint(self, sprint_id, novo_status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE sprints SET status = ? WHERE id = ?", (novo_status, sprint_id))
            conn.commit()
    def get_all_usuarios(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios ORDER BY nome_completo")
            return cursor.fetchall()
            
    def get_usuario(self, usuario_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
            return cursor.fetchone()
    
    def get_usuario_by_login(self, login):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE login = ?", (login,))
            return cursor.fetchone()
    
    def insert_usuario(self, usuario_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (nome_completo, cpf, email, cargo, login, senha, perfil)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', usuario_data)
            conn.commit()
            return cursor.lastrowid
    
    def update_usuario(self, usuario_id, usuario_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE usuarios 
                SET nome_completo=?, cpf=?, email=?, cargo=?, login=?, senha=?, perfil=?
                WHERE id=?
            ''', (*usuario_data, usuario_id))
            conn.commit()
    
    def delete_usuario(self, usuario_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id=?", (usuario_id,))
            conn.commit()
    
    def get_all_projetos(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.nome, p.descricao, p.data_inicio, p.data_termino_prevista, p.status, 
                       IFNULL(u.nome_completo, 'N/A') as gerente_nome
                FROM projetos p 
                LEFT JOIN usuarios u ON p.gerente_id = u.id
                ORDER BY p.nome
            ''')
            return cursor.fetchall()
    
    def get_projeto(self, projeto_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, u.nome_completo 
                FROM projetos p 
                LEFT JOIN usuarios u ON p.gerente_id = u.id
                WHERE p.id = ?
            ''', (projeto_id,))
            return cursor.fetchone()
    
    def insert_projeto(self, projeto_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO projetos (nome, descricao, data_inicio, data_termino_prevista, status, gerente_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', projeto_data)
            conn.commit()
            return cursor.lastrowid
    
    def update_projeto(self, projeto_id, projeto_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE projetos 
                SET nome=?, descricao=?, data_inicio=?, data_termino_prevista=?, status=?, gerente_id=?
                WHERE id=?
            ''', (*projeto_data, projeto_id))
            conn.commit()
    
    def delete_projeto(self, projeto_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projetos WHERE id=?", (projeto_id,))
            conn.commit()

    def get_all_equipes(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM equipes ORDER BY nome")
            return cursor.fetchall()
    
    def get_equipe(self, equipe_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM equipes WHERE id = ?", (equipe_id,))
            return cursor.fetchone()
    
    def insert_equipe(self, equipe_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO equipes (nome, descricao) VALUES (?, ?)", equipe_data)
            conn.commit()
            return cursor.lastrowid
    
    def update_equipe(self, equipe_id, equipe_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE equipes SET nome=?, descricao=? WHERE id=?", (*equipe_data, equipe_id))
            conn.commit()
    
    def delete_equipe(self, equipe_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM equipes WHERE id=?", (equipe_id,))
            conn.commit()
            
    def get_tarefas_por_projeto(self, projeto_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.id, t.titulo, t.prioridade, t.status, 
                       IFNULL(u.nome_completo, 'N/A') as responsavel_nome
                FROM tarefas t 
                LEFT JOIN usuarios u ON t.responsavel_id = u.id
                WHERE t.projeto_id = ?
                ORDER BY t.titulo
            ''', (projeto_id,))
            return cursor.fetchall()
    
    def get_tarefa(self, tarefa_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tarefas WHERE id = ?", (tarefa_id,))
            return cursor.fetchone()
    
    def insert_tarefa(self, tarefa_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tarefas (titulo, descricao, data_inicio, data_termino_prevista, 
                                     status, prioridade, responsavel_id, projeto_id, sprint_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
            ''', tarefa_data)
            conn.commit()
            return cursor.lastrowid
    
    def update_tarefa(self, tarefa_id, tarefa_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tarefas 
                SET titulo=?, descricao=?, data_inicio=?, data_termino_prevista=?, 
                    status=?, prioridade=?, responsavel_id=?, projeto_id=?
                WHERE id=?
            ''', (*tarefa_data, tarefa_id))
            conn.commit()
            
    def delete_tarefa(self, tarefa_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tarefas WHERE id=?", (tarefa_id,))
            conn.commit()
    
    def get_usuarios_para_combo(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome_completo FROM usuarios ORDER BY nome_completo")
            return cursor.fetchall()
    
    def get_projetos_para_combo(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM projetos ORDER BY nome")
            return cursor.fetchall()
    
    def get_gerentes_para_combo(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome_completo FROM usuarios 
                WHERE perfil = 'gerente' OR perfil = 'administrador' 
                ORDER BY nome_completo
            """)
            return cursor.fetchall()

    def get_usuarios_do_projeto(self, projeto_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.nome_completo FROM usuarios u
                JOIN projeto_usuario pu ON u.id = pu.usuario_id
                WHERE pu.projeto_id = ? ORDER BY u.nome_completo
            ''', (projeto_id,))
            return cursor.fetchall()

    def get_usuarios_fora_do_projeto(self, projeto_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, nome_completo FROM usuarios
                WHERE id NOT IN (SELECT usuario_id FROM projeto_usuario WHERE projeto_id = ?) 
                ORDER BY nome_completo
            ''', (projeto_id,))
            return cursor.fetchall()

    def add_usuario_ao_projeto(self, projeto_id, usuario_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO projeto_usuario (projeto_id, usuario_id) VALUES (?, ?)",
                           (projeto_id, usuario_id))
            conn.commit()

    def remove_usuario_do_projeto(self, projeto_id, usuario_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projeto_usuario WHERE projeto_id = ? AND usuario_id = ?",
                           (projeto_id, usuario_id))
            conn.commit()
            
    def get_usuarios_da_equipe(self, equipe_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.nome_completo FROM usuarios u
                JOIN equipe_usuario eu ON u.id = eu.usuario_id
                WHERE eu.equipe_id = ? ORDER BY u.nome_completo
            ''', (equipe_id,))
            return cursor.fetchall()

    def get_usuarios_fora_da_equipe(self, equipe_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, nome_completo FROM usuarios
                WHERE id NOT IN (SELECT usuario_id FROM equipe_usuario WHERE equipe_id = ?) 
                ORDER BY nome_completo
            ''', (equipe_id,))
            return cursor.fetchall()

    def add_usuario_a_equipe(self, equipe_id, usuario_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO equipe_usuario (equipe_id, usuario_id) VALUES (?, ?)",
                           (equipe_id, usuario_id))
            conn.commit()

    def remove_usuario_da_equipe(self, equipe_id, usuario_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM equipe_usuario WHERE equipe_id = ? AND usuario_id = ?",
                           (equipe_id, usuario_id))
            conn.commit()

    def get_contagem_status_projetos(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM projetos GROUP BY status")
            return dict(cursor.fetchall())

    def get_contagem_status_tarefas(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM tarefas GROUP BY status")
            return dict(cursor.fetchall())
    
    def get_progresso_projeto(self, projeto_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tarefas WHERE projeto_id = ?", (projeto_id,))
            total_tarefas = cursor.fetchone()[0]
            if total_tarefas == 0: return 0.0
            cursor.execute("SELECT COUNT(*) FROM tarefas WHERE projeto_id = ? AND status = 'Concluída'", (projeto_id,))
            tarefas_concluidas = cursor.fetchone()[0]
            return tarefas_concluidas / total_tarefas