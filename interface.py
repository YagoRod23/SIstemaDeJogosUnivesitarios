# interface_corrigido.py
import tkinter as tk
from tkinter import ttk, messagebox
# Assuming models.py contains Competicao, Time, Atleta, Jogo classes with necessary methods
from models import Competicao, Time, Atleta, Jogo
from config import MODALIDADES, FORMATOS_DISPUTA

class CompeticaoFrame(tk.Frame):
    # Added 'app' parameter to __init__
    def __init__(self, master, app):
        super().__init__(master, bg='#FFFFFF')
        self.master = master # master is the container frame from App
        self.app = app       # app is the instance of the main App class
        self.widgets = {}
        self.criar_interface()
        self.carregar_competicoes()

    def criar_interface(self):
        # Container principal within the frame
        container = tk.Frame(self, bg='#F5F6FA', padx=40, pady=30)
        container.pack(fill='both', expand=True)

        # Título
        lbl_titulo = tk.Label(container,
                            text="Gestão de Competições",
                            font=('Helvetica', 16, 'bold'),
                            bg='#F5F6FA',
                            fg='#2D3436')
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='ew')

        # --- Formulário de Cadastro ---
        form_frame = tk.LabelFrame(container, text="Nova Competição", bg='#F5F6FA', padx=15, pady=10, font=('Helvetica', 10))
        form_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')
        form_frame.columnconfigure(1, weight=1)

        campos = [
            ('Nome:', 'entry', 'nome'),
            ('Modalidade:', 'combo', 'modalidade', MODALIDADES),
            ('Formato:', 'combo', 'formato', FORMATOS_DISPUTA)
        ]

        for idx, (label, tipo, nome, *opcoes) in enumerate(campos):
            lbl = tk.Label(form_frame, text=label, font=('Helvetica', 10), bg='#F5F6FA', fg='#636E72', anchor='w')
            lbl.grid(row=idx, column=0, pady=5, padx=5, sticky='w')

            if tipo == 'entry':
                widget = tk.Entry(form_frame, font=('Helvetica', 10), bg='#FFFFFF', relief='flat', borderwidth=1)
            elif tipo == 'combo':
                combo_values = opcoes[0] if opcoes and isinstance(opcoes[0], (list, tuple)) else []
                widget = ttk.Combobox(form_frame, values=combo_values, state='readonly', font=('Helvetica', 10))

            widget.grid(row=idx, column=1, padx=5, pady=5, ipady=3, sticky='ew')
            self.widgets[nome] = widget

        btn_cadastrar = tk.Button(form_frame,
                                text="Cadastrar Competição",
                                command=self.cadastrar,
                                bg='#0984E3',
                                fg='white',
                                font=('Helvetica', 10, 'bold'),
                                relief='flat',
                                padx=20,
                                pady=5)
        btn_cadastrar.grid(row=len(campos), column=0, columnspan=2, pady=15)

        # --- Seleção de Competição Existente ---
        select_frame = tk.LabelFrame(container, text="Selecionar Competição", bg='#F5F6FA', padx=15, pady=10, font=('Helvetica', 10))
        select_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky='ew')
        select_frame.columnconfigure(0, weight=1)

        self.cb_competicao = ttk.Combobox(select_frame,
                                        state='readonly',
                                        font=('Helvetica', 10))
        self.cb_competicao.grid(row=0, column=0, padx=5, pady=5, ipady=3, sticky='ew')
        self.cb_competicao.bind("<<ComboboxSelected>>", self.selecionar_competicao)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

    def carregar_competicoes(self):
        try:
            competicoes = Competicao.listar_todas()
            if competicoes:
                valores = [f"{c[0]} - {c[1]}" for c in competicoes]
                self.cb_competicao['values'] = valores
                current_comp_id = self.app.get_current_competicao()
                if current_comp_id:
                    for val in valores:
                        if val.startswith(f"{current_comp_id} - "):
                            self.cb_competicao.set(val)
                            break
            else:
                self.cb_competicao['values'] = []
                self.cb_competicao.set("Nenhuma competição cadastrada")
        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Não foi possível carregar competições: {e}")
            self.cb_competicao['values'] = []
            self.cb_competicao.set("Erro ao carregar")

    def selecionar_competicao(self, event=None):
        selecionado = self.cb_competicao.get()
        if selecionado and " - " in selecionado:
            try:
                comp_id = int(selecionado.split(" - ")[0])
                self.app.set_current_competicao(comp_id)
            except ValueError:
                messagebox.showerror("Erro", "ID de competição inválido na seleção.")
            except Exception as e:
                 messagebox.showerror("Erro", f"Erro ao definir competição: {e}")
        else:
            self.app.set_current_competicao(None)

    def cadastrar(self):
        try:
            dados = {
                'nome': self.widgets['nome'].get().strip(),
                'modalidade': self.widgets['modalidade'].get(),
                'formato': self.widgets['formato'].get()
            }

            if not dados['nome'] or not dados['modalidade'] or not dados['formato']:
                raise ValueError("Todos os campos (Nome, Modalidade, Formato) são obrigatórios!")

            if Competicao.criar(**dados):
                messagebox.showinfo("Sucesso", "Competição cadastrada com sucesso!")
                self.limpar_formulario()
                self.carregar_competicoes()
            else:
                messagebox.showerror("Erro", "Falha ao salvar competição no banco de dados!")

        except ValueError as ve:
             messagebox.showwarning("Atenção", str(ve))
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {str(e)}")

    def limpar_formulario(self):
        for widget in self.widgets.values():
            if isinstance(widget, ttk.Combobox):
                widget.set('')
            elif isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)

# ==================================================
# TimeFrame
# ==================================================
class TimeFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.app = app
        self.widgets = {}
        self.criar_interface()
        self.atualizar_lista()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        container.columnconfigure(1, weight=1)

        lbl_titulo = tk.Label(container,
                            text="Gerenciamento de Times",
                            font=('Helvetica', 14, 'bold'),
                            bg='#F5F6FA')
        lbl_titulo.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        self.lbl_competicao_atual = tk.Label(container, text="Competição: Nenhuma selecionada", bg='#F5F6FA', font=('Helvetica', 10, 'italic'))
        self.lbl_competicao_atual.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky='w')

        form_frame = tk.Frame(container, bg='#F5F6FA')
        form_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky='ew')
        form_frame.columnconfigure(1, weight=1)

        lbl_nome = tk.Label(form_frame, text="Nome do Time:", bg='#F5F6FA')
        lbl_nome.grid(row=0, column=0, padx=5, sticky='w')

        self.entry_time = tk.Entry(form_frame, width=40, font=('Helvetica', 10))
        self.entry_time.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        btn_adicionar = tk.Button(form_frame,
                                text="Adicionar Time",
                                command=self.adicionar_time,
                                bg='#00B894',
                                fg='white',
                                font=('Helvetica', 10, 'bold'),
                                relief='flat', padx=10, pady=3)
        btn_adicionar.grid(row=0, column=2, padx=10)

        list_frame = tk.Frame(container, bg='#F5F6FA')
        list_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky='nsew')
        container.rowconfigure(3, weight=1)
        list_frame.columnconfigure(0, weight=1)

        colunas = ('id', 'nome')
        self.tree = ttk.Treeview(list_frame, columns=colunas, show='headings', height=10)

        self.tree.heading('id', text='ID')
        self.tree.column('id', width=50, anchor='center')
        self.tree.heading('nome', text='Nome do Time')
        self.tree.column('nome', width=300)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

    def adicionar_time(self):
        nome = self.entry_time.get().strip()
        comp_id = self.app.get_current_competicao()

        if not comp_id:
            messagebox.showwarning("Atenção", "Selecione uma competição primeiro na tela de Competições.")
            return

        if not nome:
            messagebox.showwarning("Atenção", "Digite o nome do time.")
            return

        try:
            if Time.criar(nome=nome, competicao_id=comp_id):
                messagebox.showinfo("Sucesso", f"Time '{nome}' adicionado à competição {comp_id}!")
                self.entry_time.delete(0, 'end')
                self.atualizar_lista()
            else:
                messagebox.showerror("Erro", f"Não foi possível adicionar o time '{nome}'.")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao adicionar o time: {e}")

    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        comp_id = self.app.get_current_competicao()

        if comp_id:
            try:
                comp_info = Competicao.buscar_por_id(comp_id)
                comp_nome = comp_info[1] if comp_info else f"ID: {comp_id}"
                self.lbl_competicao_atual.config(text=f"Competição Atual: {comp_nome}")
            except Exception:
                 self.lbl_competicao_atual.config(text=f"Competição Atual: ID {comp_id}")

            try:
                times = Time.carregar_por_competicao(comp_id)
                if times:
                    for time_data in times:
                        self.tree.insert('', 'end', values=time_data)
            except Exception as e:
                messagebox.showerror("Erro ao Carregar Times", f"Não foi possível carregar os times: {e}")
                self.lbl_competicao_atual.config(text="Erro ao carregar times")
        else:
            self.lbl_competicao_atual.config(text="Competição: Nenhuma selecionada")

# ==================================================
# AtletaFrame
# ==================================================
class AtletaFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.app = app
        self.current_time_id = None
        self.widgets = {}
        self.criar_interface()
        self.atualizar_times()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        container.columnconfigure(1, weight=1)
        container.columnconfigure(3, weight=1)
        container.rowconfigure(3, weight=1)

        lbl_titulo = tk.Label(container,
                            text="Gerenciamento de Atletas",
                            font=('Helvetica', 14, 'bold'),
                            bg='#F5F6FA')
        lbl_titulo.grid(row=0, column=0, columnspan=5, pady=(0, 15))

        lbl_time = tk.Label(container, text="Selecione o Time:", bg='#F5F6FA')
        lbl_time.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.cb_time = ttk.Combobox(container, state='readonly', width=35, font=('Helvetica', 10))
        self.cb_time.config(postcommand=self.atualizar_times)
        self.cb_time.grid(row=1, column=1, columnspan=4, padx=5, pady=5, sticky='ew')
        self.cb_time.bind('<<ComboboxSelected>>', self.selecionar_time)

        form_frame = tk.Frame(container, bg='#F5F6FA')
        form_frame.grid(row=2, column=0, columnspan=5, pady=10, sticky='ew')
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=0)

        lbl_nome = tk.Label(form_frame, text="Nome do Atleta:", bg='#F5F6FA')
        lbl_nome.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_nome = tk.Entry(form_frame, font=('Helvetica', 10))
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        lbl_numero = tk.Label(form_frame, text="Número:", bg='#F5F6FA')
        lbl_numero.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.entry_numero = tk.Spinbox(form_frame, from_=0, to=999, width=5, font=('Helvetica', 10))
        self.entry_numero.grid(row=0, column=3, padx=5, pady=5)

        btn_add = tk.Button(form_frame,
                          text="Adicionar Atleta",
                          command=self.adicionar_atleta,
                          bg='#0984e3', fg='white', font=('Helvetica', 10, 'bold'), relief='flat', padx=10, pady=3)
        btn_add.grid(row=0, column=4, padx=10, pady=5)

        list_frame = tk.Frame(container, bg='#F5F6FA')
        list_frame.grid(row=3, column=0, columnspan=5, pady=10, sticky='nsew')
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        colunas = ('id', 'nome', 'numero')
        self.tree = ttk.Treeview(list_frame, columns=colunas, show='headings', height=10)
        self.tree.heading('id', text='ID')
        self.tree.column('id', width=50, anchor='center')
        self.tree.heading('nome', text='Nome do Atleta')
        self.tree.column('nome', width=250)
        self.tree.heading('numero', text='Número')
        self.tree.column('numero', width=80, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

    def atualizar_times(self):
        comp_id = self.app.get_current_competicao()
        current_selection = self.cb_time.get()
        self.cb_time['values'] = []
        self.cb_time.set('')

        if comp_id:
            try:
                times = Time.carregar_por_competicao(comp_id)
                if times:
                    valores = [f"{t[0]} - {t[1]}" for t in times]
                    self.cb_time['values'] = valores
                    if current_selection in valores:
                        self.cb_time.set(current_selection)
            except Exception as e:
                messagebox.showerror("Erro ao Carregar Times", f"Não foi possível carregar times: {e}")
                self.cb_time.set("Erro ao carregar times")

    def selecionar_time(self, event=None):
        selecionado = self.cb_time.get()
        if selecionado and " - " in selecionado:
            try:
                self.current_time_id = int(selecionado.split(" - ")[0])
                self.carregar_atletas()
            except ValueError:
                messagebox.showerror("Erro", "ID de time inválido na seleção.")
                self.current_time_id = None
                self.limpar_lista_atletas()
        else:
            self.current_time_id = None
            self.limpar_lista_atletas()

    def limpar_lista_atletas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def carregar_atletas(self):
        self.limpar_lista_atletas()

        if self.current_time_id:
            try:
                atletas = Atleta.carregar_por_time(self.current_time_id)
                if atletas:
                    for atl in atletas:
                        self.tree.insert('', 'end', values=atl)
            except Exception as e:
                messagebox.showerror("Erro ao Carregar Atletas", f"Não foi possível carregar atletas: {e}")

    def adicionar_atleta(self):
        nome = self.entry_nome.get().strip()
        numero_str = self.entry_numero.get()

        if not self.current_time_id:
            messagebox.showwarning("Atenção", "Selecione um time primeiro.")
            return

        if not nome:
            messagebox.showwarning("Atenção", "Digite o nome do atleta.")
            return

        try:
            numero = int(numero_str)
        except ValueError:
            messagebox.showwarning("Atenção", "Número da camisa inválido.")
            return

        try:
            if Atleta.criar(nome=nome, numero=numero, time_id=self.current_time_id):
                messagebox.showinfo("Sucesso", f"Atleta '{nome}' adicionado ao time!")
                self.entry_nome.delete(0, 'end')
                self.entry_numero.set(0)
                self.carregar_atletas()
            else:
                messagebox.showerror("Erro", f"Não foi possível adicionar o atleta '{nome}'.")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao adicionar o atleta: {e}")

# ==================================================
# JogoFrame (Placeholder)
# ==================================================
class JogoFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.app = app
        self.criar_interface()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=20, pady=20)
        container.pack(fill='both', expand=True)

        tk.Label(container,
               text="Gerenciamento de Jogos (Em Desenvolvimento)",
               font=('Helvetica', 14, 'bold'),
               bg='#F5F6FA').pack(pady=10)

        tk.Label(container, text="Funcionalidade de Jogos ainda não implementada.", bg='#F5F6FA').pack(pady=20)
