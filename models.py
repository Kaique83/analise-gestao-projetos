# models.py
# Define as estruturas de dados (classes) que representam as entidades do sistema.

from datetime import datetime

class Usuario:
    def __init__(self, id=None, nome_completo="", cpf="", email="", cargo="", 
                 login="", senha="", perfil=""):
        self.id = id; self.nome_completo = nome_completo; self.cpf = cpf
        self.email = email; self.cargo = cargo; self.login = login
        self.senha = senha; self.perfil = perfil
    
    def __str__(self): return f"{self.nome_completo} ({self.perfil})"
    
    @classmethod
    def from_tuple(cls, data): return cls(*data) if data else None

class Projeto:
    def __init__(self, id=None, nome="", descricao="", data_inicio=None, 
                 data_termino_prevista=None, status="planejado", gerente_id=None, gerente_nome=""):
        self.id = id; self.nome = nome; self.descricao = descricao
        self.data_inicio = data_inicio or datetime.now().date()
        self.data_termino_prevista = data_termino_prevista; self.status = status
        self.gerente_id = gerente_id; self.gerente_nome = gerente_nome
    
    def __str__(self): return f"{self.nome} - {self.status}"
    
    @classmethod
    def from_tuple(cls, data):
        if data:
            return cls(*data[:7], gerente_nome=data[7]) if len(data) > 7 else cls(*data)
        return None

class Equipe:
    def __init__(self, id=None, nome="", descricao=""):
        self.id = id; self.nome = nome; self.descricao = descricao
    
    def __str__(self): return f"{self.nome}"
    
    @classmethod
    def from_tuple(cls, data): return cls(*data) if data else None

class Tarefa:
    def __init__(self, id=None, titulo="", descricao="", data_inicio=None, 
                 data_termino_prevista=None, status="pendente", prioridade="Média", 
                 responsavel_id=None, projeto_id=None, 
                 responsavel_nome="", projeto_nome=""):
        self.id = id; self.titulo = titulo; self.descricao = descricao
        self.data_inicio = data_inicio or datetime.now().date()
        self.data_termino_prevista = data_termino_prevista; self.status = status
        self.prioridade = prioridade; self.responsavel_id = responsavel_id
        self.projeto_id = projeto_id; self.responsavel_nome = responsavel_nome
        self.projeto_nome = projeto_nome
    
    def __str__(self): return f"{self.titulo} [{self.prioridade}] - {self.status}"
    
    @classmethod
    def from_tuple(cls, data):
        if data:
            return cls(*data[:8], responsavel_nome=data[8], projeto_nome=data[9]) if len(data) > 8 else cls(*data)
        return None