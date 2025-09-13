import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from models import Competicao, Time, Atleta, Jogo, Pontuacao
from config import MODALIDADES, FORMATOS_DISPUTA
from utils import exportar_relatorio_pdf, exportar_relatorio_csv, gerar_confrontos
import os
from PIL import Image, ImageTk

# ==================================================
# SumulaWindow (Toplevel for Game Details)
# ==================================================
class SumulaWindow(tk.Toplevel):
    def __init__(self, master, app, jogo_id):
        super().__init__(master)
        self.master = master
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

        # Game Info and Score
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

        # Point/Goal Registration
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

        # Athlete and Score Lists
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

        # Final Buttons
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
        for item in self.tree_casa.get_children(): 
            self.tree_casa.delete(item)
        for item in self.tree_vis.get_children(): 
            self.tree_vis.delete(item)

        try:
            pontuacoes = Pontuacao.listar_por_jogo(self.jogo_id)
            jogo_info = Jogo.buscar_detalhes(self.jogo_id)
            if not jogo_info:
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
                    if hasattr(self.master, 'listar_jogos'):
                        self.master.listar_jogos()
                    self.destroy()
                else:
                    messagebox.showerror("Erro", "Falha ao finalizar o jogo no banco.", parent=self)
            except Exception as e:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}", parent=self)

# ==================================================
# TelaInicialFrame
# ==================================================
class TelaInicialFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg='#F5F6FA')
        self.master = master
        self.app = app
        self.criar_interface()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA')
        container.pack(expand=True, fill='both', padx=20, pady=20)

        titulo_frame = tk.Frame(container, bg='#F5F6FA')
        titulo_frame.pack(expand=True)

        lbl_titulo_principal = tk.Label(
            titulo_frame,
            text="Sistema de Gerenciamento\nde Competições Esportivas - UFCA",
            font=('Helvetica', 24, 'bold'),
            bg='#F5F6FA',
            fg='#2D3436'
        )
        lbl_titulo_principal.pack(pady=20)

        # Logo UFCA
        try:
            caminho_logo = os.path.join(os.path.dirname(__file__), 'assets', 'logo_ufca.png')
            imagem_pil = Image.open(caminho_logo)
            largura_maxima = 250
            proporcao = largura_maxima / imagem_pil.width
            nova_altura = int(imagem_pil.height * proporcao)
            imagem_redimensionada = imagem_pil.resize((largura_maxima, nova_altura), Image.LANCZOS)
            logo = ImageTk.PhotoImage(imagem_redimensionada)
            lbl_logo = tk.Label(titulo_frame, image=logo, bg='#F5F6FA')
            lbl_logo.image = logo
            lbl_logo.pack(pady=10)
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")

        lbl_info = tk.Label(
            titulo_frame,
            text="Desenvolvido por Yago Rodrigues\nVersão 1.0.0",
            font=('Helvetica', 12),
            bg='#F5F6FA',
            fg='#636E72'
        )
        lbl_info.pack(pady=20)

        btn_iniciar = tk.Button(
            titulo_frame,
            text="Iniciar Sistema",
            command=self.ir_para_competicoes,
            bg='#0984e3',
            fg='white',
            font=('Helvetica', 14, 'bold'),
            padx=20,
            pady=10
        )
        btn_iniciar.pack(pady=20)

        lbl_rodape = tk.Label(
            container,
            text="© 2025 UFCA - Todos os direitos reservados",
            font=('Helvetica', 10),
            bg='#F5F6FA',
            fg='#B2BEC3'
        )
        lbl_rodape.pack(side='bottom', pady=10)

    def ir_para_competicoes(self):
        self.app.mostrar_competicoes()

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
        self.carregar_competicoes_lista()

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

        # Lista de Competições
        list_frame = tk.LabelFrame(container, text="Competições Cadastradas", bg='#F5F6FA', padx=15, pady=10, font=('Helvetica', 10))
        list_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky='nsew')
        container.rowconfigure(2, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        colunas = ('id', 'nome', 'modalidade', 'formato')
        self.tree_competicoes = ttk.Treeview(list_frame, columns=colunas, show='headings', height=8)
        self.tree_competicoes.heading('id', text='ID')
        self.tree_competicoes.column('id', width=50, anchor='center')
        self.tree_competicoes.heading('nome', text='Nome')
        self.tree_competicoes.column('nome', width=200)
        self.tree_competicoes.heading('modalidade', text='Modalidade')
        self.tree_competicoes.column('modalidade', width=100)
        self.tree_competicoes.heading('formato', text='Formato')
        self.tree_competicoes.column('formato', width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_competicoes.yview)
        self.tree_competicoes.configure(yscrollcommand=scrollbar.set)
        self.tree_competicoes.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Botões de ação
        btn_frame = tk.Frame(container, bg='#F5F6FA')
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky='ew')

        btn_editar = tk.Button(btn_frame, text="Editar Selecionada", command=self.editar_competicao, bg='#FDCB6E', fg='#2D3436', font=('Helvetica', 10, 'bold'), relief='flat', padx=10, pady=5)
        btn_editar.pack(side='left', padx=5)

        btn_excluir = tk.Button(btn_frame, text="Excluir Selecionada", command=self.excluir_competicao, bg='#E17055', fg='white', font=('Helvetica', 10, 'bold'), relief='flat', padx=10, pady=5)
        btn_excluir.pack(side='left', padx=5)

        btn_selecionar = tk.Button(btn_frame, text="Selecionar para Uso", command=self.selecionar_competicao_atual, bg='#0984E3', fg='white', font=('Helvetica', 10, 'bold'), relief='flat', padx=10, pady=5)
        btn_selecionar.pack(side='right', padx=5)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

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
                self.carregar_competicoes_lista()
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

    def carregar_competicoes_lista(self):
        for item in self.tree_competicoes.get_children():
            self.tree_competicoes.delete(item)

        try:
            competicoes = Competicao.listar_todas()
            if competicoes:
                for comp in competicoes:
                    comp_id, nome = comp
                    comp_info = Competicao.buscar_por_id(comp_id)
                    if comp_info:
                        modalidade = comp_info[2]
                        formato = comp_info[3]
                        self.tree_competicoes.insert('', 'end', values=(comp_id, nome, modalidade, formato))
        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Não foi possível carregar competições: {e}")

    def editar_competicao(self):
        selected_item = self.tree_competicoes.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione uma competição para editar.")
            return

        try:
            values = self.tree_competicoes.item(selected_item[0], 'values')
            comp_id = int(values[0])
            comp_info = Competicao.buscar_por_id(comp_id)
            if not comp_info:
                messagebox.showerror("Erro", "Competição não encontrada.")
                return

            # Pop-up para edição
            edit_window = tk.Toplevel(self)
            edit_window.title("Editar Competição")
            edit_window.geometry("400x300")
            edit_window.transient(self)
            edit_window.grab_set()

            tk.Label(edit_window, text="Nome:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
            entry_nome = tk.Entry(edit_window, width=30)
            entry_nome.grid(row=0, column=1, padx=10, pady=5)
            entry_nome.insert(0, comp_info[1])

            tk.Label(edit_window, text="Modalidade:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
            combo_modalidade = ttk.Combobox(edit_window, values=MODALIDADES, state='readonly')
            combo_modalidade.grid(row=1, column=1, padx=10, pady=5)
            combo_modalidade.set(comp_info[2])

            tk.Label(edit_window, text="Formato:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
            combo_formato = ttk.Combobox(edit_window, values=FORMATOS_DISPUTA, state='readonly')
            combo_formato.grid(row=2, column=1, padx=10, pady=5)
            combo_formato.set(comp_info[3])

            def salvar_edicao():
                nome = entry_nome.get().strip()
                modalidade = combo_modalidade.get()
                formato = combo_formato.get()

                if not nome or not modalidade or not formato:
                    messagebox.showwarning("Atenção", "Todos os campos são obrigatórios.")
                    return

                if Competicao.editar(comp_id, nome=nome, modalidade=modalidade, formato=formato):
                    messagebox.showinfo("Sucesso", "Competição editada com sucesso!")
                    edit_window.destroy()
                    self.carregar_competicoes_lista()
                else:
                    messagebox.showerror("Erro", "Falha ao editar competição.")

            tk.Button(edit_window, text="Salvar", command=salvar_edicao, bg='#0984E3', fg='white').grid(row=3, column=0, columnspan=2, pady=20)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir edição: {e}")

    def excluir_competicao(self):
        selected_item = self.tree_competicoes.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione uma competição para excluir.")
            return

        try:
            values = self.tree_competicoes.item(selected_item[0], 'values')
            comp_id = int(values[0])
            comp_nome = values[1]

            confirm = messagebox.askyesno("Confirmar Exclusão",
                                          f"Deseja excluir a competição '{comp_nome}' e todos os dados relacionados?\nEsta ação não pode ser desfeita.")

            if confirm:
                if Competicao.excluir(comp_id):
                    messagebox.showinfo("Sucesso", "Competição excluída com sucesso!")
                    self.carregar_competicoes_lista()
                else:
                    messagebox.showerror("Erro", "Falha ao excluir competição.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {e}")

    def selecionar_competicao_atual(self):
        selected_item = self.tree_competicoes.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione uma competição para definir como atual.")
            return

        try:
            values = self.tree_competicoes.item(selected_item[0], 'values')
            comp_id = int(values[0])
            self.app.set_current_competicao(comp_id)
            messagebox.showinfo("Sucesso", f"Competição {values[1]} selecionada como atual.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar competição: {e}")

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

        # Botões de ação
        btn_frame = tk.Frame(container, bg='#F5F6FA')
        btn_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky='ew')

        btn_editar = tk.Button(btn_frame, text="Editar Selecionado", command=self.editar_time, bg='#FDCB6E', fg='#2D3436', font=('Helvetica', 10, 'bold'), relief='flat', padx=10, pady=5)
        btn_editar.pack(side='left', padx=5)

        btn_excluir = tk.Button(btn_frame, text="Excluir Selecionado", command=self.excluir_time, bg='#E17055', fg='white', font=('Helvetica', 10, 'bold'), relief='flat', padx=10, pady=5)
        btn_excluir.pack(side='left', padx=5)

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

    def editar_time(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um time para editar.")
            return

        try:
            values = self.tree.item(selected_item[0], 'values')
            time_id = int(values[0])
            time_nome = values[1]

            # Pop-up para edição
            edit_window = tk.Toplevel(self)
            edit_window.title("Editar Time")
            edit_window.geometry("300x150")
            edit_window.transient(self)
            edit_window.grab_set()

            tk.Label(edit_window, text="Nome do Time:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
            entry_nome = tk.Entry(edit_window, width=25)
            entry_nome.grid(row=0, column=1, padx=10, pady=10)
            entry_nome.insert(0, time_nome)

            def salvar_edicao():
                novo_nome = entry_nome.get().strip()
                if not novo_nome:
                    messagebox.showwarning("Atenção", "Nome do time é obrigatório.")
                    return

                if Time.editar(time_id, nome=novo_nome):
                    messagebox.showinfo("Sucesso", "Time editado com sucesso!")
                    edit_window.destroy()
                    self.atualizar_lista()
                else:
                    messagebox.showerror("Erro", "Falha ao editar time.")

            tk.Button(edit_window, text="Salvar", command=salvar_edicao, bg='#0984E3', fg='white').grid(row=1, column=0, columnspan=2, pady=20)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir edição: {e}")

    def excluir_time(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um time para excluir.")
            return

        try:
            values = self.tree.item(selected_item[0], 'values')
            time_id = int(values[0])
            time_nome = values[1]

            confirm = messagebox.askyesno("Confirmar Exclusão",
                                          f"Deseja excluir o time '{time_nome}' e todos os atletas relacionados?\nEsta ação não pode ser desfeita.")

            if confirm:
                if Time.excluir(time_id):
                    messagebox.showinfo("Sucesso", "Time excluído com sucesso!")
                    self.atualizar_lista()
                else:
                    messagebox.showerror("Erro", "Falha ao excluir time.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {e}")

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

        # Botões de ação
        btn_frame = tk.Frame(container, bg='#F5F6FA')
        btn_frame.grid(row=4, column=0, columnspan=5, pady=10, sticky='ew')

        btn_editar = tk.Button(btn_frame, text="Editar Selecionado", command=self.editar_atleta, bg='#FDCB6E', fg='#2D3436', font=('Helvetica', 10, 'bold'), relief='flat', padx=10, pady=5)
        btn_editar.pack(side='left', padx=5)

        btn_excluir = tk.Button(btn_frame, text="Excluir Selecionado", command=self.excluir_atleta, bg='#E17055', fg='white', font=('Helvetica', 10, 'bold'), relief='flat', padx=10, pady=5)
        btn_excluir.pack(side='left', padx=5)

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

        # Validação: Verificar se o número da camisa é único no time
        if not Atleta.verificar_numero_unico(self.current_time_id, numero):
            messagebox.showwarning("Atenção", f"O número {numero} já está em uso por outro atleta neste time.")
            return

        # Validação: Verificar limite de atletas por modalidade
        comp_id = self.app.get_current_competicao()
        if comp_id:
            comp_info = Competicao.buscar_por_id(comp_id)
            if comp_info:
                modalidade = comp_info[2]
                if not Atleta.verificar_limite_atletas(self.current_time_id, modalidade):
                    messagebox.showwarning("Atenção", f"Limite de atletas atingido para a modalidade {modalidade}.")
                    return

        try:
            if Atleta.criar(nome=nome, numero=numero, time_id=self.current_time_id):
                messagebox.showinfo("Sucesso", f"Atleta '{nome}' adicionado ao time!")
                self.entry_nome.delete(0, 'end')
                self.entry_numero.delete(0, 'end')
                self.entry_numero.insert(0, '0')
                self.carregar_atletas()
            else:
                messagebox.showerror("Erro", f"Não foi possível adicionar o atleta '{nome}'.")
        except Exception as e:
            print(f"Erro detalhado ao adicionar atleta: {e}")
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao adicionar o atleta: {e}")

    def editar_atleta(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um atleta para editar.")
            return

        try:
            values = self.tree.item(selected_item[0], 'values')
            atleta_id = int(values[0])
            atleta_nome = values[1]
            atleta_numero = int(values[2])

            # Pop-up para edição
            edit_window = tk.Toplevel(self)
            edit_window.title("Editar Atleta")
            edit_window.geometry("350x200")
            edit_window.transient(self)
            edit_window.grab_set()

            tk.Label(edit_window, text="Nome do Atleta:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
            entry_nome = tk.Entry(edit_window, width=25)
            entry_nome.grid(row=0, column=1, padx=10, pady=10)
            entry_nome.insert(0, atleta_nome)

            tk.Label(edit_window, text="Número:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
            entry_numero = tk.Spinbox(edit_window, from_=0, to=999, width=10)
            entry_numero.grid(row=1, column=1, padx=10, pady=10)
            entry_numero.delete(0, 'end')
            entry_numero.insert(0, str(atleta_numero))

            def salvar_edicao():
                novo_nome = entry_nome.get().strip()
                try:
                    novo_numero = int(entry_numero.get())
                except ValueError:
                    messagebox.showwarning("Atenção", "Número inválido.")
                    return

                if not novo_nome:
                    messagebox.showwarning("Atenção", "Nome do atleta é obrigatório.")
                    return

                # Verificar se o número é único (exceto para o próprio atleta)
                if novo_numero != atleta_numero and not Atleta.verificar_numero_unico(self.current_time_id, novo_numero):
                    messagebox.showwarning("Atenção", f"O número {novo_numero} já está em uso por outro atleta neste time.")
                    return

                if Atleta.editar(atleta_id, nome=novo_nome, numero=novo_numero):
                    messagebox.showinfo("Sucesso", "Atleta editado com sucesso!")
                    edit_window.destroy()
                    self.carregar_atletas()
                else:
                    messagebox.showerror("Erro", "Falha ao editar atleta.")

            tk.Button(edit_window, text="Salvar", command=salvar_edicao, bg='#0984E3', fg='white').grid(row=2, column=0, columnspan=2, pady=20)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir edição: {e}")

    def excluir_atleta(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um atleta para excluir.")
            return

        try:
            values = self.tree.item(selected_item[0], 'values')
            atleta_id = int(values[0])
            atleta_nome = values[1]

            confirm = messagebox.askyesno("Confirmar Exclusão",
                                          f"Deseja excluir o atleta '{atleta_nome}'?\nEsta ação não pode ser desfeita.")

            if confirm:
                if Atleta.excluir(atleta_id):
                    messagebox.showinfo("Sucesso", "Atleta excluído com sucesso!")
                    self.carregar_atletas()
                else:
                    messagebox.showerror("Erro", "Falha ao excluir atleta.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {e}")

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
        except Exception as e:
            messagebox.showerror("Erro ao Listar Jogos", f"Não foi possível carregar os jogos: {e}")

# ==================================================
# ClassificacaoFrame
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
        container.rowconfigure(1, weight=1)

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
                    values = (
                        i + 1,  # Position
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

# ==================================================
# ArtilheirosFrame
# ==================================================
class ArtilheirosFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.app = app
        self.criar_interface()
        self.carregar_artilheiros()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        # Título e Botão de Atualizar
        title_frame = tk.Frame(container, bg='#F5F6FA')
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky='ew')
        title_frame.columnconfigure(0, weight=1)

        lbl_titulo = tk.Label(title_frame,
                            text="Artilheiros da Competição",
                            font=('Helvetica', 14, 'bold'),
                            bg='#F5F6FA')
        lbl_titulo.pack(side='left')

        btn_atualizar = tk.Button(title_frame,
                            text="Atualizar",
                            command=self.carregar_artilheiros,
                            bg='#6C5CE7',
                            fg='white',
                            font=('Helvetica', 10, 'bold'),
                            relief='flat', padx=10, pady=3)
        btn_atualizar.pack(side='right')

        # Frame da Lista de Artilheiros
        list_frame = tk.Frame(container, bg='#F5F6FA')
        list_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='nsew')
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Definir colunas para artilheiros
        colunas = ('pos', 'nome', 'pontos')
        self.tree = ttk.Treeview(list_frame, columns=colunas, show='headings', height=18)

        # Definir cabeçalhos e propriedades das colunas
        self.tree.heading('pos', text='Pos')
        self.tree.column('pos', width=50, anchor='center')
        self.tree.heading('nome', text='Atleta')
        self.tree.column('nome', width=250)
        self.tree.heading('pontos', text='Pontos / Gols')
        self.tree.column('pontos', width=100, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

    def carregar_artilheiros(self):
        # Limpar entradas anteriores
        for item in self.tree.get_children():
            self.tree.delete(item)

        comp_id = self.app.get_current_competicao()
        if not comp_id:
            self.tree.insert('', 'end', values=('', "Selecione uma competição", ''))
            return

        try:
            artilheiros = Pontuacao.get_artilheiros(comp_id)
            if artilheiros:
                for i, (nome, pontos) in enumerate(artilheiros, 1):
                    self.tree.insert('', 'end', values=(i, nome, pontos))
            else:
                self.tree.insert('', 'end', values=('', "Nenhum artilheiro encontrado", ''))

        except Exception as e:
            messagebox.showerror("Erro ao Carregar Artilheiros",
                                 f"Não foi possível carregar os artilheiros: {e}")
            self.tree.insert('', 'end', values=('', "Erro ao carregar", ''))

# ==================================================
# RelatoriosFrame
# ==================================================
class RelatoriosFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg='#FFFFFF')
        self.master = master
        self.app = app
        self.current_tipo_relatorio = None
        self.criar_interface()

    def criar_interface(self):
        container = tk.Frame(self, bg='#F5F6FA', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        container.columnconfigure(0, weight=1)

        # Título
        lbl_titulo = tk.Label(container,
                            text="Relatórios da Competição",
                            font=('Helvetica', 14, 'bold'),
                            bg='#F5F6FA')
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Frame de Botões de Relatórios
        btn_frame = tk.Frame(container, bg='#F5F6FA')
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')

        # Botões de Relatórios
        relatorios = [
            ("Relatório Geral", self.gerar_relatorio_geral),
            ("Desempenho dos Times", self.gerar_relatorio_times),
            ("Histórico de Jogos", self.gerar_relatorio_jogos),
            ("Estatísticas de Atletas", self.gerar_relatorio_atletas)
        ]

        for i, (texto, comando) in enumerate(relatorios):
            btn = tk.Button(btn_frame,
                            text=texto,
                            command=comando,
                            bg='#0984e3',
                            fg='white',
                            font=('Helvetica', 10, 'bold'),
                            relief='flat',
                            padx=15,
                            pady=10)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='ew')

        # Área de Exibição de Relatório
        self.text_relatorio = tk.Text(container,
                                      height=20,
                                      width=80,
                                      font=('Courier', 10),
                                      wrap=tk.WORD)
        self.text_relatorio.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky='nsew')

        # Scrollbar para o Text
        scrollbar = ttk.Scrollbar(container, command=self.text_relatorio.yview)
        scrollbar.grid(row=2, column=2, sticky='ns')
        self.text_relatorio.config(yscrollcommand=scrollbar.set)

        # Botões de Exportação
        export_frame = tk.Frame(container, bg='#F5F6FA')
        export_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky='ew')

        btn_export_csv = tk.Button(export_frame,
                                  text="Exportar CSV",
                                  command=self.exportar_csv,
                                  bg='#00B894',
                                  fg='white',
                                  font=('Helvetica', 10, 'bold'),
                                  relief='flat', padx=10, pady=5)
        btn_export_csv.pack(side='left', padx=5)

        btn_export_pdf = tk.Button(export_frame,
                                  text="Exportar PDF",
                                  command=self.exportar_pdf,
                                  bg='#FDCB6E',
                                  fg='#2D3436',
                                  font=('Helvetica', 10, 'bold'),
                                  relief='flat', padx=10, pady=5)
        btn_export_pdf.pack(side='left', padx=5)

        container.rowconfigure(2, weight=1)

    def validar_competicao(self):
        comp_id = self.app.get_current_competicao()
        if not comp_id:
            messagebox.showwarning("Atenção", "Selecione uma competição primeiro.")
            return None
        return comp_id

    def gerar_relatorio_geral(self):
        comp_id = self.validar_competicao()
        if not comp_id:
            return

        try:
            comp_info = Competicao.buscar_por_id(comp_id)
            times = Time.carregar_por_competicao(comp_id)
            jogos = Jogo.listar_por_competicao(comp_id)

            relatorio = f"""RELATÓRIO GERAL DA COMPETIÇÃO

Nome: {comp_info[1]}
Modalidade: {comp_info[2]}
Formato de Disputa: {comp_info[3]}

Estatísticas Gerais:
Total de Times: {len(times)}
Total de Jogos: {len(jogos)}
Jogos Concluídos: {len([j for j in jogos if j[5] == 'Concluído'])}
Jogos Pendentes: {len([j for j in jogos if j[5] != 'Concluído'])}
"""
            self.text_relatorio.delete(1.0, tk.END)
            self.text_relatorio.insert(tk.END, relatorio)
            self.current_tipo_relatorio = "geral"

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível gerar o relatório: {e}")

    def gerar_relatorio_times(self):
        comp_id = self.validar_competicao()
        if not comp_id:
            return

        try:
            tabela_classificacao = Competicao.calcular_classificacao(comp_id)

            relatorio = "DESEMPENHO DOS TIMES\n"
            relatorio += "====================\n\n"

            for time in tabela_classificacao:
                relatorio += f"Time: {time['nome']}\n"
                relatorio += f"Pontos: {time['P']} | Jogos: {time['J']}\n"
                relatorio += f"Vitórias: {time['V']} | Empates: {time['E']} | Derrotas: {time['D']}\n"
                relatorio += f"Gols Pró: {time['GP']} | Gols Contra: {time['GC']} | Saldo de Gols: {time['SG']}\n"
                relatorio += "-" * 40 + "\n\n"

            self.text_relatorio.delete(1.0, tk.END)
            self.text_relatorio.insert(tk.END, relatorio)
            self.current_tipo_relatorio = "times"

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível gerar o relatório: {e}")

    def gerar_relatorio_jogos(self):
        comp_id = self.validar_competicao()
        if not comp_id:
            return

        try:
            jogos = Jogo.listar_por_competicao(comp_id)

            relatorio = "HISTÓRICO DE JOGOS\n"
            relatorio += "==================\n\n"

            for jogo in jogos:
                jogo_id, time_casa, time_visitante, p_casa, p_vis, status = jogo
                placar = f"{p_casa} x {p_vis}" if status == 'Concluído' else "Não realizado"

                relatorio += f"Jogo {jogo_id}: {time_casa} x {time_visitante}\n"
                relatorio += f"Placar: {placar}\n"
                relatorio += f"Status: {status}\n"
                relatorio += "-" * 40 + "\n\n"

            self.text_relatorio.delete(1.0, tk.END)
            self.text_relatorio.insert(tk.END, relatorio)
            self.current_tipo_relatorio = "jogos"

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível gerar o relatório: {e}")

    def gerar_relatorio_atletas(self):
        comp_id = self.validar_competicao()
        if not comp_id:
            return

        try:
            artilheiros = Pontuacao.get_artilheiros(comp_id)

            relatorio = "ESTATÍSTICAS DE ATLETAS\n"
            relatorio += "=======================\n\n"

            relatorio += "TOP 20 ARTILHEIROS:\n"
            for i, (nome, pontos) in enumerate(artilheiros, 1):
                relatorio += f"{i}. {nome}: {pontos} pontos\n"

            self.text_relatorio.delete(1.0, tk.END)
            self.text_relatorio.insert(tk.END, relatorio)
            self.current_tipo_relatorio = "atletas"

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível gerar o relatório: {e}")

    def exportar_csv(self):
        comp_id = self.validar_competicao()
        if not comp_id:
            return

        if not self.current_tipo_relatorio:
            messagebox.showwarning("Atenção", "Gere um relatório primeiro.")
            return

        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Salvar Relatório CSV"
        )

        if caminho_arquivo:
            if exportar_relatorio_csv(comp_id, self.current_tipo_relatorio, caminho_arquivo):
                messagebox.showinfo("Sucesso", f"Relatório exportado para {caminho_arquivo}")
            else:
                messagebox.showerror("Erro", "Falha ao exportar relatório CSV.")

    def exportar_pdf(self):
        comp_id = self.validar_competicao()
        if not comp_id:
            return

        if not self.current_tipo_relatorio:
            messagebox.showwarning("Atenção", "Gere um relatório primeiro.")
            return

        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Salvar Relatório PDF"
        )

        if caminho_arquivo:
            if exportar_relatorio_pdf(comp_id, self.current_tipo_relatorio, caminho_arquivo):
                messagebox.showinfo("Sucesso", f"Relatório exportado para {caminho_arquivo}")
            else:
                messagebox.showerror("Erro", "Falha ao exportar relatório PDF.")

# ==================================================
# Main Application Class
# ==================================================
class SistemaCompeticoesApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Competições Esportivas - UFCA")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Maximizar janela no Linux
        
        # Variável para armazenar a competição atual
        self.current_competicao_id = None
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Criar interface principal
        self.criar_interface_principal()
        
        # Mostrar tela inicial
        self.mostrar_tela_inicial()

    def configurar_estilo(self):
        self.root.configure(bg='#F5F6FA')
        
        # Configurar estilo do ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores personalizadas
        style.configure('TNotebook', background='#F5F6FA')
        style.configure('TNotebook.Tab', padding=[20, 10])

    def criar_interface_principal(self):
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg='#F5F6FA')
        self.main_frame.pack(fill='both', expand=True)
        
        # Barra de navegação
        self.criar_barra_navegacao()
        
        # Área de conteúdo
        self.content_frame = tk.Frame(self.main_frame, bg='#FFFFFF')
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def criar_barra_navegacao(self):
        nav_frame = tk.Frame(self.main_frame, bg='#2D3436', height=60)
        nav_frame.pack(fill='x', padx=10, pady=10)
        nav_frame.pack_propagate(False)
        
        # Logo/Título
        lbl_titulo = tk.Label(nav_frame, 
                             text="Sistema de Competições Esportivas", 
                             font=('Helvetica', 16, 'bold'),
                             bg='#2D3436', 
                             fg='white')
        lbl_titulo.pack(side='left', padx=20, pady=15)
        
        # Botões de navegação
        botoes = [
            ("🏠 Início", self.mostrar_tela_inicial),
            ("🏆 Competições", self.mostrar_competicoes),
            ("👥 Times", self.mostrar_times),
            ("🏃 Atletas", self.mostrar_atletas),
            ("⚽ Jogos", self.mostrar_jogos),
            ("📊 Classificação", self.mostrar_classificacao),
            ("🥇 Artilheiros", self.mostrar_artilheiros),
            ("📋 Relatórios", self.mostrar_relatorios)
        ]
        
        for texto, comando in botoes:
            btn = tk.Button(nav_frame,
                           text=texto,
                           command=comando,
                           bg='#0984E3',
                           fg='white',
                           font=('Helvetica', 10, 'bold'),
                           relief='flat',
                           padx=15,
                           pady=5,
                           cursor='hand2')
            btn.pack(side='left', padx=5, pady=10)

    def limpar_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def mostrar_tela_inicial(self):
        self.limpar_content_frame()
        frame = TelaInicialFrame(self.content_frame, self)
        frame.pack(fill='both', expand=True)

    def mostrar_competicoes(self):
        self.limpar_content_frame()
        frame = CompeticaoFrame(self.content_frame, self)
        frame.pack(fill='both', expand=True)

    def mostrar_times(self):
        self.limpar_content_frame()
        frame = TimeFrame(self.content_frame, self)
        frame.pack(fill='both', expand=True)

    def mostrar_atletas(self):
        self.limpar_content_frame()
        frame = AtletaFrame(self.content_frame, self)
        frame.pack(fill='both', expand=True)

    def mostrar_jogos(self):
        self.limpar_content_frame()
        frame = JogoFrame(self.content_frame, self)
        frame.pack(fill='both', expand=True)

    def mostrar_classificacao(self):
        self.limpar_content_frame()
        frame = ClassificacaoFrame(self.content_frame, self)
        frame.pack(fill='both', expand=True)

    def mostrar_artilheiros(self):
        self.limpar_content_frame()
        frame = ArtilheirosFrame(self.content_frame, self)
        frame.pack(fill='both', expand=True)

    def mostrar_relatorios(self):
        self.limpar_content_frame()
        frame = RelatoriosFrame(self.content_frame, self)
        frame.pack(fill='both', expand=True)

    def get_current_competicao(self):
        return self.current_competicao_id

    def set_current_competicao(self, comp_id):
        self.current_competicao_id = comp_id

    def run(self):
        self.root.mainloop()

# ==================================================
# Função principal para executar a aplicação
# ==================================================
if __name__ == "__main__":
    app = SistemaCompeticoesApp()
    app.run()
