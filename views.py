# views.py
# Contém todas as classes de interface gráfica (GUI) da aplicação.

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from PIL import Image

class MainApp:
    def __init__(self, usuario_data, db, root):
        self.usuario = usuario_data; self.db = db; self.root = root
        self.selected_project_id = None 
        
        self.root.title("Sistema de Gestão de Projetos")
        self.root.geometry("1200x700"); self.root.state('zoomed')
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
        self.create_widgets()
    
    def create_widgets(self):
        self.root.grid_columnconfigure(1, weight=1); self.root.grid_rowconfigure(0, weight=1)
        
        sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew"); sidebar.grid_propagate(False)
        
        self.content = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_columnconfigure(0, weight=1); self.content.grid_rowconfigure(1, weight=1)
        
        self.setup_sidebar(sidebar); self.show_dashboard()
    
    def setup_sidebar(self, parent):
        ctk.CTkLabel(parent, text="📊 GESTPRO", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 25))
        botoes_menu = [("🏠  Dashboard", self.show_dashboard)]
        if self.usuario[7] == 'administrador': botoes_menu.append(("👤  Usuários", self.show_usuarios))
        botoes_menu.extend([("📁  Projetos", self.show_projetos),
                             ("👨‍👩‍👧‍👦  Equipes", self.show_equipes),
                             ("✅  Quadro de Tarefas", self.show_tarefas)])
        
        for texto, comando in botoes_menu:
            btn = ctk.CTkButton(parent, text=texto, command=comando, fg_color="transparent", 
                               anchor="w", height=40, font=ctk.CTkFont(size=14))
            btn.pack(fill="x", padx=20, pady=5)
        
        user_frame = ctk.CTkFrame(parent, fg_color="transparent")
        user_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        ctk.CTkLabel(user_frame, text=f"{self.usuario[1]}", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(user_frame, text=self.usuario[7].capitalize(), text_color="gray").pack(anchor="w")
        ctk.CTkButton(user_frame, text="Sair", command=self.root.quit, height=30, text_color="gray", 
                     fg_color="transparent", hover_color="#2A2D2E").pack(fill="x", pady=(10, 0))
    
    def clear_content(self):
        for widget in self.content.winfo_children(): widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        title_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20)); title_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(title_frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(title_frame, text="Atualizar", command=self.update_dashboard, width=100).grid(row=0, column=1, sticky="e")
        
        # --- NOVO DASHBOARD COM GRÁFICO ---
        dashboard_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        dashboard_frame.grid(row=1, column=0, sticky="nsew")
        dashboard_frame.grid_columnconfigure(0, weight=1)
        dashboard_frame.grid_columnconfigure(1, weight=1) # Duas colunas

        # Coluna da Esquerda para os cards
        card_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        card_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        projetos_status = self.db.get_contagem_status_projetos()
        stats_data = [("Projetos em Andamento", projetos_status.get("em andamento", 0), "#3498db"),
                      ("Total de Usuários", len(self.db.get_all_usuarios()), "#2ecc71"),
                      ("Total de Projetos", len(self.db.get_all_projetos()), "#e74c3c")]

        for i, (title, value, color) in enumerate(stats_data):
            card = ctk.CTkFrame(card_frame, height=100, corner_radius=8)
            card.pack(fill="x", pady=10, expand=True)
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16)).grid(row=0, column=0, pady=(10,5), padx=20, sticky="w")
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=36, weight="bold"), text_color=color).grid(row=1, column=0, pady=(0,10), padx=20, sticky="w")
            
        # Coluna da Direita para o Gráfico
        chart_frame = ctk.CTkFrame(dashboard_frame)
        chart_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.create_task_status_chart(chart_frame)

    def create_task_status_chart(self, parent):
        tarefas_status = self.db.get_contagem_status_tarefas()
        
        if not tarefas_status:
            ctk.CTkLabel(parent, text="Sem dados de tarefas para exibir.").pack(expand=True)
            return

        labels = tarefas_status.keys()
        sizes = tarefas_status.values()
        colors = ['#f1c40f', '#3498db', '#2ecc71', '#e74c3c'] # Pendente, Em Andamento, Concluída, Cancelada

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors,
               textprops={'color': 'white', 'fontsize': 10})
        ax.axis('equal')
        ax.set_title("Distribuição de Tarefas por Status", color="white", fontsize=14)
        fig.patch.set_facecolor('#242424') # Cor de fundo do CTkinter dark

        chart_path = "task_status_chart.png"
        fig.savefig(chart_path, bbox_inches='tight', pad_inches=0.1)
        plt.close(fig)

        chart_image = ctk.CTkImage(light_image=Image.open(chart_path),
                                   dark_image=Image.open(chart_path),
                                   size=(500, 400))
        
        image_label = ctk.CTkLabel(parent, image=chart_image, text="")
        image_label.pack(expand=True, fill="both", padx=10, pady=10)

    def update_dashboard(self): self.show_dashboard()
    
    # ... O restante do código (show_usuarios, show_projetos, etc.) permanece o mesmo da resposta anterior ...
    # Abaixo está o código completo para garantir que não haja erros.
    
    def show_usuarios(self):
        self.clear_content()
        title_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10)); title_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(title_frame, text="Gestão de Usuários", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w")
        
        btn_frame = ctk.CTkFrame(title_frame, fg_color="transparent"); btn_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(btn_frame, text="Novo", command=self.novo_usuario).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Editar", command=self.editar_usuario).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Excluir", command=self.excluir_usuario, fg_color="#e74c3c").pack(side="left", padx=5)
        
        table_frame = ctk.CTkFrame(self.content); table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1); table_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("ID", "Nome", "CPF", "Email", "Cargo", "Login", "Perfil")
        self.usuarios_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns: self.usuarios_tree.heading(col, text=col); self.usuarios_tree.column(col, width=100, anchor="center")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.usuarios_tree.yview)
        self.usuarios_tree.configure(yscrollcommand=scrollbar.set)
        self.usuarios_tree.grid(row=0, column=0, sticky="nsew"); scrollbar.grid(row=0, column=1, sticky="ns")
        self.carregar_usuarios()
    
    def carregar_usuarios(self):
        for item in self.usuarios_tree.get_children(): self.usuarios_tree.delete(item)
        for usuario in self.db.get_all_usuarios(): self.usuarios_tree.insert("", "end", values=usuario)
    
    def novo_usuario(self):
        dialog = UsuarioDialog(self.root, self.db, "Novo Usuário"); self.root.wait_window(dialog)
        self.carregar_usuarios(); self.update_dashboard()
    
    def editar_usuario(self):
        if not self.usuarios_tree.selection(): messagebox.showwarning("Aviso", "Selecione um usuário para editar."); return
        item = self.usuarios_tree.item(self.usuarios_tree.selection()[0])['values']
        dialog = UsuarioDialog(self.root, self.db, "Editar Usuário", self.db.get_usuario(item[0]))
        self.root.wait_window(dialog); self.carregar_usuarios()
    
    def excluir_usuario(self):
        if not self.usuarios_tree.selection(): messagebox.showwarning("Aviso", "Selecione um usuário para excluir."); return
        item = self.usuarios_tree.item(self.usuarios_tree.selection()[0])['values']
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o usuário {item[1]}?"):
            self.db.delete_usuario(item[0])
            self.carregar_usuarios(); self.update_dashboard()

    def show_projetos(self):
        self.clear_content()
        title_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10)); title_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(title_frame, text="Gestão de Projetos", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w")
        
        btn_frame = ctk.CTkFrame(title_frame, fg_color="transparent"); btn_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(btn_frame, text="Novo Projeto", command=self.novo_projeto).pack(side="left", padx=5)
        
        self.projetos_scroll_frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        self.projetos_scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.carregar_projetos()

    def carregar_projetos(self):
        for widget in self.projetos_scroll_frame.winfo_children(): widget.destroy()
        for projeto in self.db.get_all_projetos():
            p_id, nome, _, _, _, status, gerente = projeto
            progresso = self.db.get_progresso_projeto(p_id)
            
            card = ctk.CTkFrame(self.projetos_scroll_frame, border_width=1, border_color="gray30")
            card.pack(fill="x", padx=5, pady=5)
            card.grid_columnconfigure(1, weight=1)
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
            info_frame.grid_columnconfigure(0, weight=1)
            
            ctk.CTkButton(info_frame, text=nome, font=ctk.CTkFont(size=16, weight="bold"), 
                         fg_color="transparent", text_color=("black", "white"),
                         command=lambda p=p_id: self.selecionar_projeto_e_ver_tarefas(p)).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(info_frame, text=f"Status: {status}", font=ctk.CTkFont(size=12, slant="italic")).grid(row=1, column=0, sticky="w")
            ctk.CTkLabel(info_frame, text=f"Gerente: {gerente}", text_color="gray", font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w")
            
            progress_frame = ctk.CTkFrame(card, fg_color="transparent")
            progress_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="ew")
            progress_frame.grid_columnconfigure(0, weight=1)
            progress_bar = ctk.CTkProgressBar(progress_frame); progress_bar.set(progresso)
            progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            ctk.CTkLabel(progress_frame, text=f"{progresso:.0%}").grid(row=0, column=1, sticky="w")

            action_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            action_frame.grid(row=0, column=1, rowspan=3, sticky="e")
            ctk.CTkButton(action_frame, text="Editar", width=80, command=lambda p=p_id: self.editar_projeto(p)).pack(side="left", padx=5)
            ctk.CTkButton(action_frame, text="Membros", width=80, command=lambda p=p_id, n=nome: self.gerenciar_membros_projeto(p, n)).pack(side="left", padx=5)
            ctk.CTkButton(action_frame, text="Excluir", width=80, fg_color="#e74c3c", command=lambda p=p_id, n=nome: self.excluir_projeto(p, n)).pack(side="left", padx=5)

    def novo_projeto(self):
        dialog = ProjetoDialog(self.root, self.db, "Novo Projeto"); self.root.wait_window(dialog)
        self.carregar_projetos(); self.update_dashboard()
    
    def editar_projeto(self, projeto_id):
        projeto_data = self.db.get_projeto(projeto_id)
        dialog = ProjetoDialog(self.root, self.db, "Editar Projeto", projeto_data); self.root.wait_window(dialog)
        self.carregar_projetos()
        
    def gerenciar_membros_projeto(self, projeto_id, projeto_nome):
        dialog = MembrosDialog(self.root, self.db, "projeto", projeto_id, projeto_nome); self.root.wait_window(dialog)
    
    def excluir_projeto(self, projeto_id, projeto_nome):
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o projeto {projeto_nome}?"):
            self.db.delete_projeto(projeto_id)
            self.carregar_projetos(); self.update_dashboard()
            
    def selecionar_projeto_e_ver_tarefas(self, projeto_id):
        self.selected_project_id = projeto_id
        self.show_tarefas()

    def show_equipes(self):
        self.clear_content()
        title_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10)); title_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(title_frame, text="Gestão de Equipes", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w")
        
        btn_frame = ctk.CTkFrame(title_frame, fg_color="transparent"); btn_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(btn_frame, text="Nova", command=self.nova_equipe).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Editar", command=self.editar_equipe).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Gerenciar Membros", command=self.gerenciar_membros_equipe).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Excluir", command=self.excluir_equipe, fg_color="#e74c3c").pack(side="left", padx=5)
        
        table_frame = ctk.CTkFrame(self.content); table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1); table_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("ID", "Nome", "Descrição"); self.equipes_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns: self.equipes_tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.equipes_tree.yview)
        self.equipes_tree.configure(yscrollcommand=scrollbar.set)
        self.equipes_tree.grid(row=0, column=0, sticky="nsew"); scrollbar.grid(row=0, column=1, sticky="ns")
        self.carregar_equipes()
    
    def carregar_equipes(self):
        for item in self.equipes_tree.get_children(): self.equipes_tree.delete(item)
        for equipe in self.db.get_all_equipes(): self.equipes_tree.insert("", "end", values=equipe)
    
    def nova_equipe(self):
        dialog = EquipeDialog(self.root, self.db, "Nova Equipe"); self.root.wait_window(dialog)
        self.carregar_equipes(); self.update_dashboard()
    
    def editar_equipe(self):
        if not self.equipes_tree.selection(): messagebox.showwarning("Aviso", "Selecione uma equipe para editar."); return
        item = self.equipes_tree.item(self.equipes_tree.selection()[0])['values']
        dialog = EquipeDialog(self.root, self.db, "Editar Equipe", self.db.get_equipe(item[0])); self.root.wait_window(dialog)
        self.carregar_equipes()
    
    def gerenciar_membros_equipe(self):
        if not self.equipes_tree.selection(): messagebox.showwarning("Aviso", "Selecione uma equipe para gerenciar os membros."); return
        item = self.equipes_tree.item(self.equipes_tree.selection()[0])['values']
        dialog = MembrosDialog(self.root, self.db, "equipe", item[0], item[1]); self.root.wait_window(dialog)

    def excluir_equipe(self):
        if not self.equipes_tree.selection(): messagebox.showwarning("Aviso", "Selecione uma equipe para excluir."); return
        item = self.equipes_tree.item(self.equipes_tree.selection()[0])['values']
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir a equipe {item[1]}?"):
            self.db.delete_equipe(item[0])
            self.carregar_equipes(); self.update_dashboard()

    def show_tarefas(self):
        self.clear_content()
        if self.selected_project_id is None:
            ctk.CTkLabel(self.content, text="Vá para a tela 'Projetos' e clique no nome de um projeto para ver seu quadro.",
                         font=ctk.CTkFont(size=16)).pack(expand=True, padx=20, pady=20)
            return

        projeto_info = self.db.get_projeto(self.selected_project_id)
        title_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10)); title_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(title_frame, text=f"Quadro de Tarefas: {projeto_info[1]}", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w")
        
        btn_frame = ctk.CTkFrame(title_frame, fg_color="transparent"); btn_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(btn_frame, text="Nova Tarefa", command=self.nova_tarefa).pack(side="left", padx=5)

        kanban_container = ctk.CTkFrame(self.content, fg_color="transparent")
        kanban_container.grid(row=1, column=0, sticky="nsew")
        KanbanBoard(kanban_container, self.db, self.selected_project_id, self)
        
    def nova_tarefa(self):
        dialog = TarefaDialog(self.root, self.db, "Nova Tarefa", None, self.selected_project_id)
        self.root.wait_window(dialog)
        self.show_tarefas(); self.update_dashboard()
        
class KanbanBoard:
    def __init__(self, parent, db, project_id, app):
        self.parent = parent; self.db = db; self.project_id = project_id; self.app = app
        self.columns = ["Pendente", "Em Andamento", "Concluída"]
        
        self.parent.grid_columnconfigure(list(range(len(self.columns))), weight=1)
        self.create_columns(); self.populate_tasks()

    def create_columns(self):
        self.column_frames = {}
        for i, col_name in enumerate(self.columns):
            col_container = ctk.CTkFrame(self.parent)
            col_container.grid(row=0, column=i, sticky="nsew", padx=5, pady=5); col_container.grid_rowconfigure(1, weight=1)
            ctk.CTkLabel(col_container, text=col_name.upper(), font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, pady=5)
            scroll_frame = ctk.CTkScrollableFrame(col_container, fg_color=("gray86", "gray20"))
            scroll_frame.grid(row=1, column=0, sticky="nsew"); self.column_frames[col_name] = scroll_frame

    def populate_tasks(self):
        tarefas = self.db.get_tarefas_por_projeto(self.project_id)
        prioridade_cores = {"Alta": "#e74c3c", "Média": "#f1c40f", "Baixa": "#2ecc71"}

        for t_id, titulo, prioridade, status, responsavel in tarefas:
            if status in self.column_frames:
                card = ctk.CTkFrame(self.column_frames[status], border_width=1, border_color="gray40")
                card.pack(fill="x", pady=5, padx=5)
                ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,0))
                ctk.CTkLabel(card, text=f"Resp: {responsavel}", text_color="gray", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10)
                
                prioridade_frame = ctk.CTkFrame(card, fg_color=prioridade_cores.get(prioridade, "gray"), corner_radius=6)
                prioridade_frame.pack(anchor="w", padx=10, pady=5)
                ctk.CTkLabel(prioridade_frame, text=prioridade, font=ctk.CTkFont(size=10), text_color="white").pack(padx=8, pady=2)

                # Frame para botões de ação do card
                card_actions_frame = ctk.CTkFrame(card, fg_color="transparent")
                card_actions_frame.pack(fill="x", padx=10, pady=(0,5))
                ctk.CTkButton(card_actions_frame, text="Excluir", height=25, width=60, fg_color="#e74c3c",
                              command=lambda t=t_id, title=titulo: self.delete_task(t, title)).pack(anchor="se", side="right")
                ctk.CTkButton(card_actions_frame, text="Editar", height=25, width=60,
                              command=lambda t=t_id: self.edit_task(t)).pack(anchor="se", side="right", padx=5)
    
    def edit_task(self, task_id):
        tarefa_data = self.db.get_tarefa(task_id)
        dialog = TarefaDialog(self.app.root, self.db, "Editar Tarefa", tarefa_data, self.project_id)
        self.app.root.wait_window(dialog); self.app.show_tarefas()
    
    def delete_task(self, task_id, task_title):
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir a tarefa '{task_title}'?"):
            self.db.delete_tarefa(task_id)
            self.app.show_tarefas(); self.app.update_dashboard()
        
class LoginWindow:
    def __init__(self, root, on_login_success, db):
        self.root = root; self.db = db; self.on_login_success = on_login_success
        self.root.title("Gestão de Projetos - Login"); self.root.geometry("400x450"); self.root.resizable(False, False)
        self.center_window(); self.create_widgets()
    
    def center_window(self):
        self.root.update_idletasks()
        w = 400; h = 450; x = (self.root.winfo_screenwidth()//2) - (w//2); y = (self.root.winfo_screenheight()//2) - (h//2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
        
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent"); main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        logo_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); logo_frame.pack(pady=10)
        ctk.CTkLabel(logo_frame, text="📊", font=ctk.CTkFont(size=40)).pack()
        ctk.CTkLabel(logo_frame, text="Gestão de Projetos", font=ctk.CTkFont(size=20, weight="bold")).pack()
        
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); form_frame.pack(fill="x", pady=15)
        ctk.CTkLabel(form_frame, text="Login", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.login_entry = ctk.CTkEntry(form_frame, placeholder_text="Usuário"); self.login_entry.pack(fill="x", pady=5); self.login_entry.insert(0, "admin")
        ctk.CTkLabel(form_frame, text="Senha", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.senha_entry = ctk.CTkEntry(form_frame, placeholder_text="Senha", show="*"); self.senha_entry.pack(fill="x", pady=5); self.senha_entry.insert(0, "admin123")
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); button_frame.pack(fill="x", pady=15)
        ctk.CTkButton(button_frame, text="ENTRAR", command=self.authenticate, height=35).pack(fill="x", pady=5)
        ctk.CTkButton(button_frame, text="SAIR", command=self.root.quit, height=30, fg_color="transparent").pack(fill="x")
        ctk.CTkLabel(main_frame, text="admin / admin123", text_color="gray", font=ctk.CTkFont(size=12)).pack(pady=5)
        
        self.login_entry.bind("<Return>", lambda e: self.senha_entry.focus()); self.senha_entry.bind("<Return>", lambda e: self.authenticate())
        self.root.after(100, lambda: self.login_entry.focus())
        
    def authenticate(self):
        login = self.login_entry.get().strip(); senha = self.senha_entry.get().strip()
        if not login or not senha: messagebox.showerror("Erro", "Preencha todos os campos."); return
        usuario_data = self.db.get_usuario_by_login(login)
        if usuario_data and usuario_data[6] == senha: self.on_login_success(usuario_data)
        else: messagebox.showerror("Erro", "Credenciais inválidas!"); self.senha_entry.delete(0, 'end')

class UsuarioDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, title, usuario_data=None):
        super().__init__(parent); self.title(title); self.geometry("400x500"); self.resizable(False, False)
        self.db = db; self.usuario_data = usuario_data; self.create_widgets(); self.grab_set()
    
    def create_widgets(self):
        main_frame = ctk.CTkScrollableFrame(self); main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        ctk.CTkLabel(main_frame, text="Dados do Usuário", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        campos = [("Nome Completo", "nome_completo", "text"), ("CPF", "cpf", "text"), ("Email", "email", "text"), 
                  ("Cargo", "cargo", "text"), ("Login", "login", "text"), ("Senha", "senha", "password"), ("Perfil", "perfil", "combo")]
        self.entries = {}
        for label, field, tipo in campos:
            ctk.CTkLabel(main_frame, text=label, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
            if tipo == "combo": entry = ctk.CTkComboBox(main_frame, values=["administrador", "gerente", "colaborador"]); entry.set("colaborador")
            else: entry = ctk.CTkEntry(main_frame, show="*" if tipo == "password" else None)
            entry.pack(fill="x", pady=5); self.entries[field] = entry
        
        if self.usuario_data:
            self.entries['nome_completo'].insert(0, self.usuario_data[1]); self.entries['cpf'].insert(0, self.usuario_data[2])
            self.entries['email'].insert(0, self.usuario_data[3]); self.entries['cargo'].insert(0, self.usuario_data[4])
            self.entries['login'].insert(0, self.usuario_data[5]); self.entries['senha'].insert(0, self.usuario_data[6])
            self.entries['perfil'].set(self.usuario_data[7])
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); button_frame.pack(fill="x", pady=15)
        ctk.CTkButton(button_frame, text="Salvar", command=self.salvar).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="transparent", border_width=1).pack(side="right", padx=5)
    
    def salvar(self):
        try:
            dados = [e.get() for e in self.entries.values()]
            if any(not dados[i] for i in [0,1,2,3,4,6]): messagebox.showerror("Erro", "Todos os campos, exceto senha em edição, são obrigatórios."); return
            if self.usuario_data:
                if not dados[5]: dados[5] = self.usuario_data[6]
                self.db.update_usuario(self.usuario_data[0], dados); messagebox.showinfo("Sucesso", "Usuário atualizado!")
            else:
                if not dados[5]: messagebox.showerror("Erro", "Senha é obrigatória."); return
                self.db.insert_usuario(dados); messagebox.showinfo("Sucesso", "Usuário criado!")
            self.destroy()
        except Exception as e: messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

class ProjetoDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, title, projeto_data=None):
        super().__init__(parent); self.title(title); self.geometry("500x550"); self.resizable(False, False)
        self.db = db; self.projeto_data = projeto_data; self.create_widgets(); self.grab_set()
    
    def create_widgets(self):
        main_frame = ctk.CTkScrollableFrame(self); main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        ctk.CTkLabel(main_frame, text="Dados do Projeto", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        campos = [("Nome", "nome", "text"), ("Descrição", "descricao", "text"), ("Data Início", "data_inicio", "text"), 
                  ("Data Término", "data_termino", "text"), ("Status", "status", "combo"), ("Gerente", "gerente", "combo")]
        self.entries = {}
        for label, field, tipo in campos:
            ctk.CTkLabel(main_frame, text=label, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
            if tipo == "combo":
                if field == "status": entry = ctk.CTkComboBox(main_frame, values=["planejado", "em andamento", "concluído", "cancelado"]); entry.set("planejado")
                else:
                    items = self.db.get_gerentes_para_combo()
                    valores = [f"{i[0]} - {i[1]}" for i in items] if items else ["Nenhum gerente disponível"]
                    entry = ctk.CTkComboBox(main_frame, values=valores);
                    if valores: entry.set(valores[0])
            else:
                entry = ctk.CTkEntry(main_frame)
                if field == "data_inicio": entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
                elif field == "data_termino": entry.insert(0, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
            entry.pack(fill="x", pady=5); self.entries[field] = entry
        
        if self.projeto_data:
            self.entries['nome'].insert(0, self.projeto_data[1]); self.entries['descricao'].insert(0, self.projeto_data[2] or "")
            self.entries['data_inicio'].delete(0, 'end'); self.entries['data_inicio'].insert(0, self.projeto_data[3])
            self.entries['data_termino'].delete(0, 'end'); self.entries['data_termino'].insert(0, self.projeto_data[4])
            self.entries['status'].set(self.projeto_data[5])
            if self.projeto_data[6]:
                for item in self.entries['gerente'].cget("values"):
                    if str(item).startswith(f"{self.projeto_data[6]} -"): self.entries['gerente'].set(item); break
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); button_frame.pack(fill="x", pady=15, side="bottom")
        ctk.CTkButton(button_frame, text="Salvar", command=self.salvar).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="transparent", border_width=1).pack(side="right", padx=5)
    
    def salvar(self):
        try:
            dados = {f: e.get() for f, e in self.entries.items()}
            if any(not dados[f] for f in ["nome", "data_inicio", "data_termino"]): messagebox.showerror("Erro", "Nome e datas são obrigatórios."); return
            gerente_id = int(dados['gerente'].split(" - ")[0]) if " - " in dados['gerente'] else None
            p_data = [dados['nome'], dados['descricao'], dados['data_inicio'], dados['data_termino'], dados['status'], gerente_id]
            if self.projeto_data: self.db.update_projeto(self.projeto_data[0], p_data); messagebox.showinfo("Sucesso", "Projeto atualizado!")
            else: self.db.insert_projeto(p_data); messagebox.showinfo("Sucesso", "Projeto criado!")
            self.destroy()
        except Exception as e: messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

class EquipeDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, title, equipe_data=None):
        super().__init__(parent); self.title(title); self.geometry("400x300"); self.resizable(False, False)
        self.db = db; self.equipe_data = equipe_data; self.create_widgets(); self.grab_set()
    
    def create_widgets(self):
        main_frame = ctk.CTkScrollableFrame(self); main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        ctk.CTkLabel(main_frame, text="Dados da Equipe", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        campos = [("Nome", "nome"), ("Descrição", "descricao")]; self.entries = {}
        for label, field in campos:
            ctk.CTkLabel(main_frame, text=label, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
            entry = ctk.CTkEntry(main_frame); entry.pack(fill="x", pady=5); self.entries[field] = entry
        if self.equipe_data:
            self.entries['nome'].insert(0, self.equipe_data[1]); self.entries['descricao'].insert(0, self.equipe_data[2] or "")
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); button_frame.pack(fill="x", pady=15, side="bottom")
        ctk.CTkButton(button_frame, text="Salvar", command=self.salvar).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="transparent", border_width=1).pack(side="right", padx=5)
    
    def salvar(self):
        try:
            dados = [self.entries['nome'].get(), self.entries['descricao'].get()]
            if not dados[0]: messagebox.showerror("Erro", "Nome é obrigatório."); return
            if self.equipe_data: self.db.update_equipe(self.equipe_data[0], dados); messagebox.showinfo("Sucesso", "Equipe atualizada!")
            else: self.db.insert_equipe(dados); messagebox.showinfo("Sucesso", "Equipe criada!")
            self.destroy()
        except Exception as e: messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

class TarefaDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, title, tarefa_data=None, projeto_id_selecionado=None):
        super().__init__(parent); self.title(title); self.geometry("500x550"); self.resizable(False, False)
        self.db = db; self.tarefa_data = tarefa_data; self.projeto_id_selecionado = projeto_id_selecionado
        self.create_widgets(); self.grab_set()
    
    def create_widgets(self):
        main_frame = ctk.CTkScrollableFrame(self); main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        ctk.CTkLabel(main_frame, text="Dados da Tarefa", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        campos = [("Título", "titulo", "text"), ("Descrição", "descricao", "text"), ("Data Início", "data_inicio", "text"), 
                  ("Data Término", "data_termino", "text"), ("Status", "status", "combo"), ("Prioridade", "prioridade", "combo"), 
                  ("Responsável", "responsavel", "combo"), ("Projeto", "projeto", "combo")]
        self.entries = {}
        for label, field, tipo in campos:
            ctk.CTkLabel(main_frame, text=label, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
            if tipo == "combo":
                if field == "status": entry = ctk.CTkComboBox(main_frame, values=["Pendente", "Em Andamento", "Concluída"]); entry.set("Pendente")
                elif field == "prioridade": entry = ctk.CTkComboBox(main_frame, values=["Baixa", "Média", "Alta"]); entry.set("Média")
                else:
                    items = self.db.get_usuarios_para_combo() if field == "responsavel" else self.db.get_projetos_para_combo()
                    valores = [f"{i[0]} - {i[1]}" for i in items] if items else ["Nenhum item disponível"]
                    entry = ctk.CTkComboBox(main_frame, values=valores)
                    if valores: entry.set(valores[0])
            else:
                entry = ctk.CTkEntry(main_frame)
                if field == "data_inicio": entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
                elif field == "data_termino": entry.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
            entry.pack(fill="x", pady=5); self.entries[field] = entry
        
        if self.projeto_id_selecionado and not self.tarefa_data:
            for item in self.entries['projeto'].cget("values"):
                if str(item).startswith(f"{self.projeto_id_selecionado} -"): self.entries['projeto'].set(item); break
        
        if self.tarefa_data:
            self.entries['titulo'].insert(0, self.tarefa_data[1]); self.entries['descricao'].insert(0, self.tarefa_data[2] or "")
            self.entries['data_inicio'].delete(0,'end'); self.entries['data_inicio'].insert(0, self.tarefa_data[3])
            self.entries['data_termino'].delete(0,'end'); self.entries['data_termino'].insert(0, self.tarefa_data[4])
            self.entries['status'].set(self.tarefa_data[5]); self.entries['prioridade'].set(self.tarefa_data[6])
            if self.tarefa_data[7]:
                for item in self.entries['responsavel'].cget("values"):
                    if str(item).startswith(f"{self.tarefa_data[7]} -"): self.entries['responsavel'].set(item); break
            if self.tarefa_data[8]:
                for item in self.entries['projeto'].cget("values"):
                    if str(item).startswith(f"{self.tarefa_data[8]} -"): self.entries['projeto'].set(item); break

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); button_frame.pack(fill="x", pady=15, side="bottom")
        ctk.CTkButton(button_frame, text="Salvar", command=self.salvar).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="transparent", border_width=1).pack(side="right", padx=5)
    
    def salvar(self):
        try:
            dados = {f: e.get() for f, e in self.entries.items()}
            if any(not dados[f] for f in ["titulo", "data_inicio", "data_termino", "responsavel", "projeto"]):
                messagebox.showerror("Erro", "Todos os campos, exceto descrição, são obrigatórios."); return
            resp_id = int(dados['responsavel'].split(" - ")[0]) if " - " in dados['responsavel'] else None
            proj_id = int(dados['projeto'].split(" - ")[0]) if " - " in dados['projeto'] else None
            t_data = [dados['titulo'], dados['descricao'], dados['data_inicio'], dados['data_termino'],
                      dados['status'], dados['prioridade'], resp_id, proj_id]
            if self.tarefa_data: self.db.update_tarefa(self.tarefa_data[0], t_data); messagebox.showinfo("Sucesso", "Tarefa atualizada!")
            else: self.db.insert_tarefa(t_data); messagebox.showinfo("Sucesso", "Tarefa criada!")
            self.destroy()
        except Exception as e: messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

class MembrosDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, tipo, item_id, item_nome):
        super().__init__(parent); self.db = db; self.tipo = tipo; self.item_id = item_id
        self.title(f"Membros de: {item_nome}"); self.geometry("700x500"); self.resizable(False, False); self.grab_set()
        self.available_widgets = []; self.member_widgets = []
        self.create_widgets(); self.populate_lists()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self); main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure((0, 2), weight=1); main_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(main_frame, text="Usuários Disponíveis").grid(row=0, column=0)
        self.available_list_frame = ctk.CTkScrollableFrame(main_frame); self.available_list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); action_frame.grid(row=1, column=1, padx=5)
        ctk.CTkButton(action_frame, text="▶", width=40, command=self.add_membros).pack(pady=5)
        ctk.CTkButton(action_frame, text="◀", width=40, command=self.remove_membros).pack(pady=5)

        ctk.CTkLabel(main_frame, text=f"Membros d{'a' if self.tipo=='equipe' else 'o'} {self.tipo.capitalize()}").grid(row=0, column=2)
        self.members_list_frame = ctk.CTkScrollableFrame(main_frame); self.members_list_frame.grid(row=1, column=2, sticky="nsew", padx=(5, 0))

        ctk.CTkButton(main_frame, text="Fechar", command=self.destroy).grid(row=2, column=2, sticky="e", pady=10)

    def populate_lists(self):
        for w, _ in self.available_widgets: w.destroy()
        for w, _ in self.member_widgets: w.destroy()
        self.available_widgets.clear(); self.member_widgets.clear()

        if self.tipo == "projeto":
            available = self.db.get_usuarios_fora_do_projeto(self.item_id)
            members = self.db.get_usuarios_do_projeto(self.item_id)
        else:
            available = self.db.get_usuarios_fora_da_equipe(self.item_id)
            members = self.db.get_usuarios_da_equipe(self.item_id)

        for user_id, name in available:
            cb = ctk.CTkCheckBox(self.available_list_frame, text=name)
            cb.pack(anchor="w", padx=10, pady=2); self.available_widgets.append((cb, user_id))

        for user_id, name in members:
            cb = ctk.CTkCheckBox(self.members_list_frame, text=name)
            cb.pack(anchor="w", padx=10, pady=2); self.member_widgets.append((cb, user_id))

    def add_membros(self):
        for cb, user_id in self.available_widgets:
            if cb.get():
                if self.tipo == "projeto": self.db.add_usuario_ao_projeto(self.item_id, user_id)
                else: self.db.add_usuario_a_equipe(self.item_id, user_id)
        self.populate_lists()

    def remove_membros(self):
        for cb, user_id in self.member_widgets:
            if cb.get():
                if self.tipo == "projeto": self.db.remove_usuario_do_projeto(self.item_id, user_id)
                else: self.db.remove_usuario_da_equipe(self.item_id, user_id)
        self.populate_lists()