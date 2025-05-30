# interface.py (parte atualizada)
import tkinter as tk
from tkinter import ttk, messagebox
from models import Competicao
from config import MODALIDADES, FORMATOS_DISPUTA

class CompeticaoFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.widgets = {}
        self.criar_interface()
        self.centralizar_formulario()

    def centralizar_formulario(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
    def criar_interface(self):
        # Container principal
        container = tk.Frame(self, bg='#F5F6FA', padx=40, pady=30)
        container.grid(row=0, column=0, sticky='nsew')

        # Título
        lbl_titulo = tk.Label(container, 
                            text="Nova Competição Esportiva",
                            font=('Helvetica', 16, 'bold'),
                            bg='#F5F6FA',
                            fg='#2D3436')
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=20)

        # Campos do formulário
        campos = [
            ('Nome da Competição:', 'entry', 'nome'),
            ('Modalidade Esportiva:', 'combo', 'modalidade', MODALIDADES),
            ('Formato de Disputa:', 'combo', 'formato', FORMATOS_DISPUTA)
        ]

        for idx, (label, tipo, nome, *opcoes) in enumerate(campos, start=1):
            # Label
            lbl = tk.Label(container, 
                         text=label,
                         font=('Helvetica', 10),
                         bg='#F5F6FA',
                         fg='#636E72',
                         anchor='w')
            lbl.grid(row=idx, column=0, pady=10, sticky='ew')

            # Campo
            if tipo == 'entry':
                widget = tk.Entry(container, 
                                font=('Helvetica', 10),
                                bg='#FFFFFF',
                                relief='flat')
            elif tipo == 'combo':
                widget = ttk.Combobox(container,
                                    values=opcoes[0],
                                    state='readonly',
                                    font=('Helvetica', 10))
                
            widget.grid(row=idx, column=1, padx=20, pady=10, ipady=5, sticky='ew')
            self.widgets[nome] = widget

        # Botão de cadastro
        btn_cadastrar = tk.Button(container,
                                text="Cadastrar Competição",
                                command=self.cadastrar,
                                bg='#0984E3',
                                fg='white',
                                font=('Helvetica', 10, 'bold'),
                                relief='flat',
                                padx=30,
                                pady=10)
        btn_cadastrar.grid(row=4, column=0, columnspan=2, pady=30)

        # Configurar pesos das colunas
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=2)

    def cadastrar(self):
        try:
            dados = {
                'nome': self.widgets['nome'].get().strip(),
                'modalidade': self.widgets['modalidade'].get(),
                'formato': self.widgets['formato'].get()
            }

            # Validação
            if not all(dados.values()):
                raise ValueError("Todos os campos são obrigatórios!")
            
            if Competicao.criar(**dados):
                messagebox.showinfo("Sucesso", "Competição cadastrada com sucesso!")
                self.limpar_formulario()
            else:
                messagebox.showerror("Erro", "Falha ao salvar no banco de dados!")

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def limpar_formulario(self):
        for widget in self.widgets.values():
            if isinstance(widget, ttk.Combobox):
                widget.set('')
            else:
                widget.delete(0, tk.END)

# Adicione após a classe CompeticaoFrame

class TimeFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.criar_interface()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=20, pady=20)
        container.pack(fill='both', expand=True)

        # Cabeçalho
        tk.Label(container, 
                text="Gerenciamento de Times",
                font=('Helvetica', 14, 'bold'),
                bg='#F5F6FA').grid(row=0, column=0, pady=10, columnspan=3)

        # Formulário
        tk.Label(container, text="Nome do Time:", bg='#F5F6FA').grid(row=1, column=0, sticky='e')
        self.entry_time = tk.Entry(container, width=30)
        self.entry_time.grid(row=1, column=1, padx=10, pady=5)

        # Botões
        btn_adicionar = tk.Button(container, 
                                text="Adicionar Time",
                                command=self.adicionar_time,
                                bg='#00B894',
                                fg='white')
        btn_adicionar.grid(row=1, column=2, padx=10)

        # Lista de Times
        colunas = ('ID', 'Nome', 'Qtd. Atletas')
        self.tree = ttk.Treeview(container, columns=colunas, show='headings')
        
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.grid(row=2, column=0, columnspan=3, pady=20, sticky='nsew')
        
        # Atualizar lista
        self.atualizar_lista()

    def adicionar_time(self):
        nome = self.entry_time.get().strip()
        if nome:
            # Implementar conexão com models.Time
            messagebox.showinfo("Sucesso", f"Time {nome} adicionado!")
            self.entry_time.delete(0, 'end')
            self.atualizar_lista()

    def atualizar_lista(self):
        # Implementar carregamento de dados reais
        dados_mock = [
            (1, "Time Alpha", 12),
            (2, "Time Beta", 8)
        ]
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for dado in dados_mock:
            self.tree.insert('', 'end', values=dado)

class AtletaFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.criar_interface()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=20, pady=20)
        container.pack(fill='both', expand=True)

        tk.Label(container, 
               text="Gerenciamento de Atletas",
               font=('Helvetica', 14, 'bold'),
               bg='#F5F6FA').pack(pady=10)

class JogoFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.criar_interface()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=20, pady=20)
        container.pack(fill='both', expand=True)

        tk.Label(container, 
               text="Agendamento de Jogos",
               font=('Helvetica', 14, 'bold'),
               bg='#F5F6FA').pack(pady=10)

# ==================================================
# CLASSE PRINCIPAL
# ==================================================
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestão de Competições")
        self.geometry("1000x600")
        self.criar_interface()
    
    def criar_interface(self):
        # Container principal
        self.container = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.container.pack(fill=tk.BOTH, expand=1)

        # Painel esquerdo
        self.nav_frame = tk.Frame(self.container, width=200, bg='#3f4652')
        self.container.add(self.nav_frame)
        self.criar_menu()
        
        # Área principal
        self.main_frame = tk.Frame(self.container, bg='white')
        self.container.add(self.main_frame)
        
        self.mostrar_tela_inicial()
    
    def criar_menu(self):
        botoes = [
            ("🏆 Competições Ativas", self.mostrar_tela_inicial),
            ("✨ Nova Competição", self.mostrar_tela_cadastro),  # NOVO BOTÃO
            ("⚽ Times", self.mostrar_times),
            ("👤 Atletas", self.mostrar_atletas),
            ("📅 Jogos", self.mostrar_jogos),
            ("🚪 Sair", self.destroy)
        ]
        for texto, comando in botoes:
            btn = tk.Button(self.nav_frame, text=texto, width=18, 
                          command=comando, bg='#4a586a', fg='white',
                          relief='flat', pady=5)
            btn.pack(pady=2)
    
    def limpar_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def mostrar_tela_cadastro(self):  # NOVO MÉTODO
        self.limpar_main_frame()
        frame = CompeticaoFrame(self.main_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def mostrar_tela_inicial(self):
        self.limpar_main_frame()
        lbl = tk.Label(self.main_frame, text="Competições Ativas", 
                      font=('Arial', 14), bg='white')
        lbl.pack(pady=20)
        
        tree = ttk.Treeview(self.main_frame, columns=('ID', 'Nome', 'Modalidade'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Nome', text='Nome')
        tree.heading('Modalidade', text='Modalidade')
        tree.pack(fill=tk.BOTH, expand=True)
        
        for competicao in Competicao.carregar_todas():
            tree.insert('', 'end', values=competicao)
    
    def mostrar_times(self):
        self.limpar_main_frame()
        frame = TimeFrame(self.main_frame)
        frame.pack(fill=tk.BOTH, expand=True)
    
    def mostrar_atletas(self):
        self.limpar_main_frame()
        frame = AtletaFrame(self.main_frame)
        frame.pack(fill=tk.BOTH, expand=True)
    
    def mostrar_jogos(self):
        self.limpar_main_frame()
        frame = JogoFrame(self.main_frame)
        frame.pack(fill=tk.BOTH, expand=True)
class TimeFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.current_competicao = None
        self.widgets = {}
        self.criar_interface()
    
    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=20, pady=20)
        container.pack(fill='both', expand=True)

        # Cabeçalho
        lbl_titulo = tk.Label(container, 
                            text="Gerenciamento de Times",
                            font=('Helvetica', 14, 'bold'),
                            bg='#F5F6FA')
        lbl_titulo.grid(row=0, column=0, columnspan=4, pady=10)

        # Seleção de Competição
        lbl_competicao = tk.Label(container,
                                text="Selecione a Competição:",
                                bg='#F5F6FA')
        lbl_competicao.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        self.cb_competicao = ttk.Combobox(container,
                                        state='readonly',
                                        postcommand=self.atualizar_competicoes)
        self.cb_competicao.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.cb_competicao.bind('<<ComboboxSelected>>', self.carregar_times)

        # Formulário de Cadastro
        lbl_nome = tk.Label(container,
                          text="Nome do Time:",
                          bg='#F5F6FA')
        lbl_nome.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        self.entry_nome = tk.Entry(container, width=30)
        self.entry_nome.grid(row=2, column=1, padx=5, pady=5)

        btn_add = tk.Button(container,
                          text="Adicionar Time",
                          command=self.adicionar_time,
                          bg='#00B894',
                          fg='white')
        btn_add.grid(row=2, column=2, padx=5, pady=5)

        # Lista de Times
        colunas = ('ID', 'Nome', 'Qt. Atletas')
        self.tree = ttk.Treeview(container, columns=colunas, show='headings')
        
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        
        self.tree.grid(row=3, column=0, columnspan=4, pady=10, sticky='nsew')

        # Botões de Ação
        btn_editar = tk.Button(container,
                             text="Editar",
                             command=self.editar_time,
                             bg='#FDCB6E',
                             state='disabled')
        btn_editar.grid(row=4, column=1, padx=5, pady=5)

        btn_excluir = tk.Button(container,
                              text="Excluir",
                              command=self.excluir_time,
                              bg='#D63031',
                              fg='white',
                              state='disabled')
        btn_excluir.grid(row=4, column=2, padx=5, pady=5)

        # Configurar pesos
        container.grid_columnconfigure(1, weight=1)

    def atualizar_competicoes(self):
        competicoes = Competicao.carregar_todas()
        self.cb_competicao['values'] = [f"{c[0]} - {c[1]}" for c in competicoes]

    def carregar_times(self, event=None):
        if self.cb_competicao.get():
            comp_id = self.cb_competicao.get().split(" - ")[0]
            self.current_competicao = int(comp_id)
            times = Time.carregar_por_competicao(comp_id)
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for time in times:
                qtd_atletas = len(Time.get_atletas(time[0]))
                self.tree.insert('', 'end', values=(time[0], time[1], qtd_atletas))

    def adicionar_time(self):
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Digite o nome do time!")
            return
            
        if not self.current_competicao:
            messagebox.showerror("Erro", "Selecione uma competição primeiro!")
            return

        try:
            if Time.criar(nome, self.current_competicao):
                messagebox.showinfo("Sucesso", "Time cadastrado com sucesso!")
                self.entry_nome.delete(0, 'end')
                self.carregar_times()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cadastrar: {str(e)}")

    def editar_time(self):
        # Implementar lógica de edição
        pass

    def excluir_time(self):
        # Implementar lógica de exclusão
        pass


class AtletaFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='white')
        tk.Label(self, text="Gerenciamento de Atletas").pack(pady=50)

class JogoFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='white')
        tk.Label(self, text="Agendamento de Jogos").pack(pady=50)

# ==================================================
# EXECUÇÃO
# ==================================================
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
