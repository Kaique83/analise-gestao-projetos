# main.py
# Ponto de entrada da aplicação. Responsável por instanciar e executar o sistema.

import customtkinter as ctk
from database import Database
from views import LoginWindow, MainApp

class App:
    """
    Classe principal que gerencia o ciclo de vida da aplicação.
    """
    def __init__(self):
        """
        Inicializa a conexão com o banco de dados e a janela principal (root).
        """
        self.db = Database()
        self.current_user = None
        self.root = ctk.CTk()
        # Garante que a janela principal seja destruída ao fechar
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
        
    def on_login_success(self, usuario):
        """
        Callback executado quando o login é bem-sucedido.
        Destrói a janela de login e abre a janela principal da aplicação.
        
        Args:
            usuario (tuple): Dados do usuário que efetuou o login.
        """
        self.current_user = usuario
        self.root.destroy()  # Fecha a janela de login
        
        # Cria uma nova janela principal para o aplicativo
        new_root = ctk.CTk()
        main_app = MainApp(usuario, self.db, new_root)
        new_root.mainloop()
    
    def run(self):
        """
        Inicia a aplicação, exibindo a janela de login.
        """
        login_window = LoginWindow(self.root, self.on_login_success, self.db)
        self.root.mainloop()

if __name__ == "__main__":
    # Define a aparência global da aplicação
    ctk.set_appearance_mode("Dark")  # Modos: "System" (padrão), "Dark", "Light"
    ctk.set_default_color_theme("dark-blue")  # Temas: "blue" (padrão), "green", "dark-blue"
    
    app = App()
    app.run()