# main_corrigido.py
import tkinter as tk
# Import necessary frames from interface.py
from interface import CompeticaoFrame, TimeFrame, AtletaFrame, JogoFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestão Esportiva")
        self.geometry("1024x768")
        self.current_competicao = None # Initialize competition ID tracker

        # --- UI Setup ---
        # Sidebar Frame
        self.sidebar = tk.Frame(self, bg='#2D3436', width=200, relief='sunken', borderwidth=0)
        self.sidebar.pack(side='left', fill='y', padx=0, pady=0)

        # Main Content Container Frame
        self.container = tk.Frame(self, bg='white') # Added background color for clarity
        self.container.pack(side='right', fill='both', expand=True, padx=10, pady=10) # Added padding

        # --- Initialization ---
        self.criar_menu() # Create sidebar buttons
        self.mostrar_tela_inicial() # Show the initial frame

    def get_current_competicao(self):
        """Returns the ID of the currently selected competition."""
        return self.current_competicao

    def set_current_competicao(self, comp_id):
        """Sets the ID of the currently selected competition."""
        # Optional: Add validation or logging here if needed
        self.current_competicao = comp_id
        print(f"Competição atual definida para: {self.current_competicao}") # For debugging

    def mostrar_tela(self, frame_class):
        """Clears the main container and displays the requested frame."""
        # Destroy existing widgets in the container
        for widget in self.container.winfo_children():
            widget.destroy()

        # Create and pack the new frame, passing the container as master and self (the App instance) as 'app'
        # This allows frames to access App methods/attributes via self.app
        nova_tela = frame_class(self.container, app=self) 
        nova_tela.pack(fill='both', expand=True)

    def criar_menu(self):
        """Creates the navigation buttons in the sidebar."""
        # Button style configuration
        button_config = {
            'bg': '#4a586a',
            'fg': 'white',
            'relief': 'flat',
            'anchor': 'w', # Align text to the left
            'padx': 10,
            'pady': 8,
            'font': ('Helvetica', 10)
        }

        # Define buttons: (Text, Command to execute on click)
        botoes = [
            ("🏠 Tela Inicial", self.mostrar_tela_inicial),
            ("🏆 Competições", self.mostrar_competicoes), # Changed from 'Nova Competição'
            ("⚽ Times", self.mostrar_times),
            ("👤 Atletas", self.mostrar_atletas),
            ("📅 Jogos", self.mostrar_jogos),
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
        self.mostrar_tela(CompeticaoFrame)

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

# --- Main execution block ---
if __name__ == "__main__":
    app = App()
    app.mainloop()
