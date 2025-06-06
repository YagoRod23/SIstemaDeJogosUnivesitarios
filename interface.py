# interface_completo_corrigido.py
import tkinter as tk
from tkinter import ttk, messagebox
# Assuming models.py contains Competicao, Time, Atleta, Jogo, Pontuacao classes
from models import Competicao, Time, Atleta, Jogo, Pontuacao 
from config import MODALIDADES, FORMATOS_DISPUTA

# ==================================================
# SumulaWindow (Toplevel for Game Details)
# ==================================================
class SumulaWindow(tk.Toplevel):
    def __init__(self, master, app, jogo_id):
        super().__init__(master)
        self.master = master # The JogoFrame instance
        self.app = app
        self.jogo_id = jogo_id
        self.atletas_casa = []
        self.atletas_visitante = []

        self.title(f"Súmula - Jogo ID: {self.jogo_id}")
        self.geometry("700x550")
        self.transient(master)
        self.grab_set()

        self.criar_interface()
        self.carregar_dados_jogo()

    def criar_interface(self):
        main_frame = tk.Frame(self, padx=15, pady=15)
        main_frame.pack(fill='both', expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # --- Game Info and Score ---
        info_frame = tk.Frame(main_frame)
        info_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky='ew')
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(3, weight=1)

        self.lbl_jogo_info = tk.Label(info_frame, text="Jogo: Carregando...", font=('Helvetica', 12, 'bold'))
        self.lbl_jogo_info.grid(row=0, column=0, columnspan=4, pady=(0, 10))

        tk.Label(info_frame, text="Placar Casa:").grid(row=1, column=0, padx=5, sticky='e')
        self.entry_placar_casa = tk.Spinbox(info_frame, from_=0, to=999, width=5)
        self.entry_placar_casa.grid(row=1, column=1, padx=5, sticky='w')

        tk.Label(info_frame, text="Placar Visitante:").grid(row=1, column=2, padx=5, sticky='e')
        self.entry_placar_visitante = tk.Spinbox(info_frame, from_=0, to=999, width=5)
        self.entry_placar_visitante.grid(row=1, column=3, padx=5, sticky='w')

        # --- Point/Goal Registration ---
        pontos_frame = tk.LabelFrame(main_frame, text="Registrar Pontos/Gols", padx=10, pady=10)
        pontos_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')
        pontos_frame.columnconfigure(1, weight=1)

        tk.Label(pontos_frame, text="Atleta:").grid(row=0, column=0, padx=5, sticky='w')
        self.cb_atleta_pontuador = ttk.Combobox(pontos_frame, state='readonly', width=40)
        self.cb_atleta_pontuador.grid(row=0, column=1, padx=5, sticky='ew')

        tk.Label(pontos_frame, text="Pontos:").grid(row=0, column=2, padx=5, sticky='w')
        self.entry_pontos = tk.Spinbox(pontos_frame, from_=1, to=10, width=5)
        self.entry_pontos.grid(row=0, column=3, padx=5)

        btn_registrar_ponto = tk.Button(pontos_frame, text="Registrar", command=self.registrar_ponto, bg='#00B894', fg='white', relief='flat')
        btn_registrar_ponto.grid(row=0, column=4, padx=10)

        # --- Athlete and Score Lists ---
        listas_frame = tk.Frame(main_frame)
        listas_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky='nsew')
        listas_frame.columnconfigure(0, weight=1)
        listas_frame.columnconfigure(1, weight=1)
        listas_frame.rowconfigure(0, weight=1)

        # Home Team List
        frame_casa = tk.LabelFrame(listas_frame, text="Time Casa - Pontuadores", padx=5, pady=5)
        frame_casa.grid(row=0, column=0, padx=(0, 5), sticky='nsew')
        frame_casa.rowconfigure(0, weight=1)
        frame_casa.columnconfigure(0, weight=1)
        col_casa = ('atleta', 'pontos')
        self.tree_casa = ttk.Treeview(frame_casa, columns=col_casa, show='headings', height=8)
        self.tree_casa.heading('atleta', text='Atleta')
        self.tree_casa.heading('pontos', text='Pontos')
        self.tree_casa.column('pontos', width=60, anchor='center')
        self.tree_casa.grid(row=0, column=0, sticky='nsew')
        sc_casa = ttk.Scrollbar(frame_casa, orient='vertical', command=self.tree_casa.yview)
        self.tree_casa.configure(yscrollcommand=sc_casa.set)
        sc_casa.grid(row=0, column=1, sticky='ns')

        # Away Team List
        frame_vis = tk.LabelFrame(listas_frame, text="Time Visitante - Pontuadores", padx=5, pady=5)
        frame_vis.grid(row=0, column=1, padx=(5, 0), sticky='nsew')
        frame_vis.rowconfigure(0, weight=1)
        frame_vis.columnconfigure(0, weight=1)
        col_vis = ('atleta', 'pontos')
        self.tree_vis = ttk.Treeview(frame_vis, columns=col_vis, show='headings', height=8)
        self.tree_vis.heading('atleta', text='Atleta')
        self.tree_vis.heading('pontos', text='Pontos')
        self.tree_vis.column('pontos', width=60, anchor='center')
        self.tree_vis.grid(row=0, column=0, sticky='nsew')
        sc_vis = ttk.Scrollbar(frame_vis, orient='vertical', command=self.tree_vis.yview)
        self.tree_vis.configure(yscrollcommand=sc_vis.set)
        sc_vis.grid(row=0, column=1, sticky='ns')

        # --- Final Buttons ---
        botoes_frame = tk.Frame(main_frame)
        botoes_frame.grid(row=3, column=0, columnspan=2, pady=(15, 0))

        btn_salvar = tk.Button(botoes_frame, text="Salvar Placar e Finalizar Jogo", command=self.salvar_e_finalizar, bg='#0984E3', fg='white', relief='flat', font=('Helvetica', 10, 'bold'))
        btn_salvar.pack(side='left', padx=10)

        btn_fechar = tk.Button(botoes_frame, text="Fechar Súmula", command=self.destroy, bg='#636E72', fg='white', relief='flat')
        btn_fechar.pack(side='left', padx=10)

    def carregar_dados_jogo(self):
        try:
            jogo_info = Jogo.buscar_detalhes(self.jogo_id)
            if not jogo_info:
                messagebox.showerror("Erro", f"Jogo ID {self.jogo_id} não encontrado.", parent=self)
                self.destroy()
                return

            j_id, c_id, tc_id, tv_id, p_casa, p_vis, status, n_casa, n_vis = jogo_info

            self.lbl_jogo_info.config(text=f"Jogo: {n_casa} vs {n_vis} (ID: {j_id})")

            if status == 'Concluído':
                self.entry_placar_casa.delete(0, 'end')
                self.entry_placar_casa.insert(0, str(p_casa if p_casa is not None else 0))
                self.entry_placar_visitante.delete(0, 'end')
                self.entry_placar_visitante.insert(0, str(p_vis if p_vis is not None else 0))
                # Optionally disable score entry for finished games
                # self.entry_placar_casa.config(state='disabled')
                # self.entry_placar_visitante.config(state='disabled')
            else:
                self.entry_placar_casa.delete(0, 'end')
                self.entry_placar_casa.insert(0, '0')
                self.entry_placar_visitante.delete(0, 'end')
                self.entry_placar_visitante.insert(0, '0')

            self.atletas_casa = Atleta.carregar_por_time(tc_id)
            self.atletas_visitante = Atleta.carregar_por_time(tv_id)

            lista_formatada = []
            if self.atletas_casa:
                lista_formatada.extend([f"{a[0]} - {a[1]} ({n_casa})" for a in self.atletas_casa])
            if self.atletas_visitante:
                 lista_formatada.extend([f"{a[0]} - {a[1]} ({n_vis})" for a in self.atletas_visitante])

            self.cb_atleta_pontuador['values'] = lista_formatada
            if lista_formatada:
                self.cb_atleta_pontuador.current(0)
            else:
                 self.cb_atleta_pontuador.set('')

            self.carregar_pontuacoes_existentes()

        except Exception as e:
            messagebox.showerror("Erro ao Carregar Jogo", f"Não foi possível carregar dados do jogo: {e}", parent=self)

    def carregar_pontuacoes_existentes(self):
        for item in self.tree_casa.get_children(): self.tree_casa.delete(item)
        for item in self.tree_vis.get_children(): self.tree_vis.delete(item)

        try:
            pontuacoes = Pontuacao.listar_por_jogo(self.jogo_id)
            jogo_info = Jogo.buscar_detalhes(self.jogo_id)
            if not jogo_info:
                 print(f"Erro: Não foi possível buscar detalhes do jogo {self.jogo_id} para carregar pontuações.")
                 return 
            time_casa_id = jogo_info[2]

            for p_data in pontuacoes:
                a_id, a_nome, t_id, t_nome, total_pts = p_data
                if t_id == time_casa_id:
                    self.tree_casa.insert('', 'end', values=(f"{a_id} - {a_nome}", total_pts))
                else:
                    self.tree_vis.insert('', 'end', values=(f"{a_id} - {a_nome}", total_pts))

        except Exception as e:
            print(f"Erro ao carregar pontuações existentes: {e}")
            messagebox.showwarning("Atenção", "Não foi possível carregar as pontuações já registradas.", parent=self)

    def registrar_ponto(self):
        selecionado = self.cb_atleta_pontuador.get()
        pontos_str = self.entry_pontos.get()

        if not selecionado or " - " not in selecionado:
            messagebox.showwarning("Atenção", "Selecione um atleta válido.", parent=self)
            return

        try:
            atleta_id = int(selecionado.split(" - ")[0])
            pontos = int(pontos_str)
            if pontos <= 0:
                raise ValueError("Pontos devem ser positivos.")
        except ValueError:
            messagebox.showwarning("Atenção", "ID do atleta ou valor de pontos inválido.", parent=self)
            return

        try:
            if Pontuacao.registrar_pontos(atleta_id=atleta_id, jogo_id=self.jogo_id, pontos=pontos):
                self.carregar_pontuacoes_existentes()
                self.cb_atleta_pontuador.set('')
                self.entry_pontos.delete(0, 'end')
                self.entry_pontos.insert(0, '1')
            else:
                messagebox.showerror("Erro", "Falha ao registrar pontuação no banco.", parent=self)
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}", parent=self)

    def salvar_e_finalizar(self):
        placar_casa_str = self.entry_placar_casa.get()
        placar_vis_str = self.entry_placar_visitante.get()

        try:
            placar_casa = int(placar_casa_str)
            placar_visitante = int(placar_vis_str)
            if placar_casa < 0 or placar_visitante < 0:
                raise ValueError("Placar não pode ser negativo.")
        except ValueError:
            messagebox.showwarning("Atenção", "Valores de placar inválidos.", parent=self)
            return

        confirm = messagebox.askyesno("Confirmar Finalização",
                                      f"Deseja finalizar o jogo ID {self.jogo_id} com o placar {placar_casa} x {placar_visitante}?",
                                      parent=self)

        if confirm:
            try:
                if Jogo.finalizar_jogo(self.jogo_id, placar_casa, placar_visitante):
                    messagebox.showinfo("Sucesso", "Jogo finalizado e placar salvo!", parent=self)
                    # Refresh the game list in the parent JogoFrame
                    if hasattr(self.master, 'listar_jogos'): 
                        self.master.listar_jogos()
                    self.destroy()
                else:
                    messagebox.showerror("Erro", "Falha ao finalizar o jogo no banco.", parent=self)
            except Exception as e:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}", parent=self)

# ==================================================
# CompeticaoFrame
# ==================================================
class CompeticaoFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.app = app
        self.widgets = {}
        self.criar_interface()
        self.carregar_competicoes()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=40, pady=30)
        container.pack(fill='both', expand=True)

        lbl_titulo = tk.Label(container,
                            text="Gestão de Competições",
                            font=('Helvetica', 16, 'bold'),
                            bg='#F5F6FA',
                            fg='#2D3436')
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='ew')

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
                    self.cb_competicao.set('')
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
                self.app.set_current_competicao(None)
            except Exception as e:
                 messagebox.showerror("Erro", f"Erro ao definir competição: {e}")
                 self.app.set_current_competicao(None)
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
        # Call atualizar_times initially to set the combobox state
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
        # Use postcommand to refresh list just before dropdown
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
        # Clear values before fetching new ones
        self.cb_time['values'] = [] 
        self.cb_time.set('')
        # Don't clear athlete list here, wait for selection
        # self.limpar_lista_atletas()
        # self.current_time_id = None

        if comp_id:
            try:
                times = Time.carregar_por_competicao(comp_id)
                if times:
                    valores = [f"{t[0]} - {t[1]}" for t in times]
                    self.cb_time['values'] = valores
                    # Restore selection if it's still valid
                    if current_selection in valores:
                        self.cb_time.set(current_selection)
                        # No need to load athletes here, wait for bind event
                    # else: # If previous selection is gone, clear athlete list
                    #     self.limpar_lista_atletas()
                    #     self.current_time_id = None
                # else: # No teams found
                #     self.limpar_lista_atletas()
                #     self.current_time_id = None
            except Exception as e:
                messagebox.showerror("Erro ao Carregar Times", f"Não foi possível carregar times: {e}")
                self.cb_time.set("Erro ao carregar times")
        else:
             self.cb_time.set("Selecione Competição")
             self.limpar_lista_atletas()
             self.current_time_id = None

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
                # Correct way to reset Spinbox
                self.entry_numero.delete(0, 'end') 
                self.entry_numero.insert(0, '0')  
                self.carregar_atletas() # Refresh list
            else:
                messagebox.showerror("Erro", f"Não foi possível adicionar o atleta '{nome}'.")
        except Exception as e:
            # Log the full error for debugging
            print(f"Erro detalhado ao adicionar atleta: {e}") 
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao adicionar o atleta: {e}")

# ==================================================
# JogoFrame
# ==================================================
class JogoFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.app = app
        self.criar_interface()
        self.listar_jogos()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        lbl_titulo = tk.Label(container,
                            text="Gerenciamento de Jogos",
                            font=('Helvetica', 14, 'bold'),
                            bg='#F5F6FA')
        lbl_titulo.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        action_frame = tk.Frame(container, bg='#F5F6FA')
        action_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky='ew')

        btn_gerar = tk.Button(action_frame,
                            text="Gerar Confrontos",
                            command=self.gerar_jogos,
                            bg='#FD79A8',
                            fg='white',
                            font=('Helvetica', 10, 'bold'),
                            relief='flat', padx=10, pady=5)
        btn_gerar.pack(side='left', padx=(0, 10))

        self.btn_sumula = tk.Button(action_frame,
                                text="Abrir Súmula",
                                command=self.abrir_sumula,
                                bg='#FDCB6E',
                                fg='#2D3436',
                                font=('Helvetica', 10, 'bold'),
                                relief='flat', padx=10, pady=5,
                                state='disabled')
        self.btn_sumula.pack(side='left', padx=10)

        btn_atualizar = tk.Button(action_frame,
                            text="Atualizar Lista",
                            command=self.listar_jogos,
                            bg='#6C5CE7',
                            fg='white',
                            font=('Helvetica', 10, 'bold'),
                            relief='flat', padx=10, pady=5)
        btn_atualizar.pack(side='right', padx=(10, 0))

        list_frame = tk.Frame(container, bg='#F5F6FA')
        list_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky='nsew')
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        colunas = ('id', 'time_casa', 'placar', 'time_visitante', 'status')
        self.tree = ttk.Treeview(list_frame, columns=colunas, show='headings', height=15, selectmode='browse')

        self.tree.heading('id', text='ID')
        self.tree.column('id', width=40, anchor='center')
        self.tree.heading('time_casa', text='Time Casa')
        self.tree.column('time_casa', width=150)
        self.tree.heading('placar', text='Placar')
        self.tree.column('placar', width=80, anchor='center')
        self.tree.heading('time_visitante', text='Time Visitante')
        self.tree.column('time_visitante', width=150)
        self.tree.heading('status', text='Status')
        self.tree.column('status', width=100, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.tree.bind('<<TreeviewSelect>>', self.on_jogo_select)

    def on_jogo_select(self, event=None):
        selected_item = self.tree.selection()
        if selected_item:
            self.btn_sumula.config(state='normal')
        else:
            self.btn_sumula.config(state='disabled')

    def abrir_sumula(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um jogo na lista para abrir a súmula.")
            return

        try:
            jogo_values = self.tree.item(selected_item[0], 'values')
            jogo_id = int(jogo_values[0])
            # Open SumulaWindow as a child of the main App window (self.app)
            SumulaWindow(self.app, self.app, jogo_id) 
        except (IndexError, ValueError):
            messagebox.showerror("Erro", "Não foi possível obter o ID do jogo selecionado.")
        except Exception as e:
             messagebox.showerror("Erro Inesperado", f"Erro ao abrir súmula: {e}")

    def gerar_jogos(self):
        comp_id = self.app.get_current_competicao()
        if not comp_id:
            messagebox.showwarning("Atenção", "Selecione uma competição primeiro na tela de Competições.")
            return

        try:
            comp_info = Competicao.buscar_por_id(comp_id)
            if not comp_info or len(comp_info) < 4:
                 messagebox.showerror("Erro", f"Não foi possível obter informações da competição {comp_id}.")
                 return
            formato = comp_info[3]
            if not formato:
                 messagebox.showwarning("Atenção", f"A competição {comp_id} não tem um formato definido.")
                 return
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar formato da competição: {e}")
            return

        confirm = messagebox.askyesno("Confirmar Geração",
                                      f"Deseja gerar os confrontos para a competição ID {comp_id} (Formato: {formato})?\nIsso pode apagar jogos existentes se gerados novamente.")

        if confirm:
            try:
                success = Jogo.gerar_confrontos(comp_id, formato)
                if success:
                    messagebox.showinfo("Sucesso", "Confrontos gerados com sucesso!")
                    self.listar_jogos()
                else:
                    messagebox.showerror("Erro", "Falha ao gerar confrontos. Verifique o console para mais detalhes.")
            except Exception as e:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao gerar confrontos: {e}")

    def listar_jogos(self):
        self.btn_sumula.config(state='disabled')
        for item in self.tree.get_children():
            self.tree.delete(item)

        comp_id = self.app.get_current_competicao()
        if not comp_id:
            # Optionally display a message in the treeview
            # self.tree.insert('', 'end', values=('', 'Selecione uma competição', '', '', ''))
            return

        try:
            jogos = Jogo.listar_por_competicao(comp_id)
            if jogos:
                for jogo_data in jogos:
                    jogo_id, time_casa, time_visitante, p_casa, p_vis, status = jogo_data
                    placar_str = "-"
                    if status == 'Concluído' and p_casa is not None and p_vis is not None:
                        placar_str = f"{p_casa} x {p_vis}"
                    self.tree.insert('', 'end', values=(jogo_id, time_casa, placar_str, time_visitante, status))
            # else: # Optionally display message if no games
                # self.tree.insert('', 'end', values=('', 'Nenhum jogo encontrado', '', '', ''))
        except Exception as e:
            messagebox.showerror("Erro ao Listar Jogos", f"Não foi possível carregar os jogos: {e}")

# ==================================================
# ClassificacaoFrame (Added)
# ==================================================
class ClassificacaoFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.app = app
        self.criar_interface()
        self.carregar_classificacao()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1) # Allow treeview frame to expand

        # Title and Refresh Button
        title_frame = tk.Frame(container, bg='#F5F6FA')
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky='ew')
        title_frame.columnconfigure(0, weight=1)

        lbl_titulo = tk.Label(title_frame,
                            text="Tabela de Classificação",
                            font=('Helvetica', 14, 'bold'),
                            bg='#F5F6FA')
        lbl_titulo.pack(side='left')

        btn_atualizar = tk.Button(title_frame,
                            text="Atualizar",
                            command=self.carregar_classificacao,
                            bg='#6C5CE7',
                            fg='white',
                            font=('Helvetica', 10, 'bold'),
                            relief='flat', padx=10, pady=3)
        btn_atualizar.pack(side='right')

        # Treeview Frame
        list_frame = tk.Frame(container, bg='#F5F6FA')
        list_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='nsew')
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Define columns for the classification table
        colunas = ('pos', 'time', 'P', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG')
        self.tree = ttk.Treeview(list_frame, columns=colunas, show='headings', height=18)

        # Define headings and column properties
        self.tree.heading('pos', text='Pos')
        self.tree.column('pos', width=40, anchor='center')
        self.tree.heading('time', text='Time')
        self.tree.column('time', width=200)
        self.tree.heading('P', text='P')
        self.tree.column('P', width=40, anchor='center')
        self.tree.heading('J', text='J')
        self.tree.column('J', width=40, anchor='center')
        self.tree.heading('V', text='V')
        self.tree.column('V', width=40, anchor='center')
        self.tree.heading('E', text='E')
        self.tree.column('E', width=40, anchor='center')
        self.tree.heading('D', text='D')
        self.tree.column('D', width=40, anchor='center')
        self.tree.heading('GP', text='GP')
        self.tree.column('GP', width=40, anchor='center')
        self.tree.heading('GC', text='GC')
        self.tree.column('GC', width=40, anchor='center')
        self.tree.heading('SG', text='SG')
        self.tree.column('SG', width=40, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

    def carregar_classificacao(self):
        # Clear previous entries
        for item in self.tree.get_children():
            self.tree.delete(item)

        comp_id = self.app.get_current_competicao()
        if not comp_id:
            self.tree.insert('', 'end', values=('', "Selecione uma competição", '', '', '', '', '', '', '', ''))
            return

        try:
            tabela = Competicao.calcular_classificacao(comp_id)
            if tabela:
                for i, time_stats in enumerate(tabela):
                    # Order must match the columns defined in self.tree
                    # ('pos', 'time', 'P', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG')
                    values = (
                        i + 1, # Position
                        time_stats['nome'],
                        time_stats['P'],
                        time_stats['J'],
                        time_stats['V'],
                        time_stats['E'],
                        time_stats['D'],
                        time_stats['GP'],
                        time_stats['GC'],
                        time_stats['SG']
                    )
                    self.tree.insert('', 'end', values=values)
            else:
                self.tree.insert('', 'end', values=('', "Nenhum time ou jogo concluído", '', '', '', '', '', '', '', ''))

        except Exception as e:
            messagebox.showerror("Erro ao Carregar Classificação", f"Não foi possível calcular/carregar a classificação: {e}")
            self.tree.insert('', 'end', values=('', "Erro ao carregar", '', '', '', '', '', '', '', ''))

