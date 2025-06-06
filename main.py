# main_corrigido_v2.py
import tkinter as tk
from tkinter import ttk, messagebox
# Import necessary frames from interface.py
# Make sure to import the new ClassificacaoFrame
from interface import CompeticaoFrame, TimeFrame, AtletaFrame, JogoFrame, ClassificacaoFrame, ArtilheirosFrame, RelatoriosFrame, TelaInicialFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestão Esportiva")
        self.geometry("1024x768")
        self.current_competicao = None # Initialize current competition ID

        # Configure sidebar
        self.sidebar = tk.Frame(self, bg='#2D3436', width=200)
        self.sidebar.pack(side='left', fill='y')

        # Main container
        self.container = tk.Frame(self)
        self.container.pack(side='right', fill='both', expand=True)

        self.criar_menu()
        self.mostrar_tela_inicial() # Show the initial frame

    def get_current_competicao(self):
        """Returns the ID of the currently selected competition."""
        return self.current_competicao

    def set_current_competicao(self, competicao_id):
        """Sets the ID of the currently selected competition."""
        self.current_competicao = competicao_id
        print(f"Competição atual definida para: {self.current_competicao}") # Debug print
        # Optionally, refresh the current view if needed
        # self.refresh_current_view()

    def mostrar_artilheiros(self):
        """Shows the top scorers frame."""
        self.mostrar_tela(ArtilheirosFrame)

    def mostrar_relatorios(self):
        """Shows the reports frame."""
        self.mostrar_tela(RelatoriosFrame)

    def mostrar_tela(self, frame_class):
        """Clears the container and displays the specified frame class."""
        # Destroy existing widgets in the container
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Create and pack the new frame, passing the app instance
        # Ensure the frame class accepts 'app' as an argument in __init__
        try:
            nova_tela = frame_class(self.container, app=self) 
            nova_tela.pack(fill='both', expand=True)
        except TypeError as e:
            if "unexpected keyword argument 'app'" in str(e):
                messagebox.showerror("Erro de Programação", 
                                     f"A classe {frame_class.__name__} precisa aceitar 'app' no seu __init__.")
            else:
                messagebox.showerror("Erro ao Mudar Tela", f"Erro inesperado: {e}")
        except Exception as e:
             messagebox.showerror("Erro ao Mudar Tela", f"Erro inesperado: {e}")

    def criar_menu(self):
        """Creates the sidebar menu buttons."""
        # Button configuration (Corrected: removed invalid backslashes)
        button_config = {
            'bg': '#636E72',
            'fg': 'white',
            'font': ('Helvetica', 10, 'bold'),
            'relief': 'flat',
            'anchor': 'w',
            'padx': 15,
            'pady': 10
        }

        # Define buttons: (Text, Command)
        botoes = [
            ("🏠 Tela Inicial", self.mostrar_tela_inicial),
            ("🏆 Competições", self.mostrar_competicoes),
            ("⚽ Times", self.mostrar_times),
            ("👤 Atletas", self.mostrar_atletas),
            ("📅 Jogos", self.mostrar_jogos),
            ("📊 Classificação", self.mostrar_classificacao),
            ("📊 Relatórios", self.mostrar_relatorios),
            ("🏆 Artilheiros", self.mostrar_artilheiros),# New Button
            # Add other buttons as needed
            ("🚪 Sair", self.quit) # Use self.quit or self.destroy
        ]

        # Create and pack buttons
        for texto, comando in botoes:
            btn = tk.Button(self.sidebar, text=texto, command=comando, **button_config)
            # Use fill='x' to make buttons expand horizontally
            btn.pack(pady=2, padx=5, fill='x')

    # --- Methods to show specific frames ---
    def mostrar_tela_inicial(self):
        """Shows the initial/welcome screen (using CompeticaoFrame for now)."""
        self.mostrar_tela(TelaInicialFrame) 

    def mostrar_competicoes(self):
        """Shows the competition management frame."""
        self.mostrar_tela(CompeticaoFrame)

    def mostrar_times(self):
        """Shows the team management frame."""
        self.mostrar_tela(TimeFrame)

    def mostrar_atletas(self):
        """Shows the athlete management frame."""
        self.mostrar_tela(AtletaFrame)

    def mostrar_jogos(self):
        """Shows the game management frame."""
        self.mostrar_tela(JogoFrame)

    def mostrar_classificacao(self): # New Method
        """Shows the classification table frame."""
        self.mostrar_tela(ClassificacaoFrame)

# --- Main execution block ---
if __name__ == "__main__":
    app = App()
    app.mainloop()

