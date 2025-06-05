# models_corrigido.py
import sqlite3
from database import criar_conexao
# Assuming config.py defines these constants, otherwise remove or define them here
# from config import PONTOS_VITORIA, PONTOS_EMPATE, PONTOS_DERROTA

# Define default points if not imported from config
PONTOS_VITORIA = 3
PONTOS_EMPATE = 1
PONTOS_DERROTA = 0

class Competicao:
    @staticmethod
    def criar(nome, modalidade, formato):
        """Cria uma nova competição no banco de dados."""
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO competicao (nome, modalidade, formato_disputa) VALUES (?, ?, ?)",
                    (nome, modalidade, formato)
                )
                conn.commit()
                return True # Indicate success
            except sqlite3.Error as e:
                print(f"Erro ao criar competição: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def listar_todas():
        """Lista todas as competições (ID e Nome) para preencher comboboxes."""
        conn = criar_conexao()
        competicoes = []
        if conn:
            try:
                cursor = conn.cursor()
                # Ensure table name is correct (e.g., 'competicao')
                cursor.execute("SELECT id, nome FROM competicao ORDER BY nome")
                competicoes = cursor.fetchall() # Returns list of (id, nome) tuples
            except sqlite3.Error as e:
                print(f"Erro ao listar competições: {e}")
            finally:
                conn.close()
        return competicoes

    @staticmethod
    def buscar_por_id(competicao_id):
        """Busca uma competição específica pelo ID."""
        conn = criar_conexao()
        competicao_info = None
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, modalidade, formato_disputa FROM competicao WHERE id = ?", (competicao_id,))
                competicao_info = cursor.fetchone() # Returns a single tuple or None
            except sqlite3.Error as e:
                print(f"Erro ao buscar competição por ID {competicao_id}: {e}")
            finally:
                conn.close()
        return competicao_info # Returns (id, nome, modalidade, formato) or None

    # Note: get_times and get_classificacao might be better placed in Time or Jogo models
    # or kept here if Competicao is the main entry point for these actions.

# ==================================================
# Time Model
# ==================================================
class Time:
    @staticmethod
    def criar(nome, competicao_id):
        """Cria um novo time associado a uma competição."""
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO time (nome, competicao_id) VALUES (?, ?)",
                    (nome, competicao_id)
                )
                conn.commit()
                # Return True on success, False otherwise
                return True 
            except sqlite3.Error as e:
                print(f"Erro ao criar time: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def carregar_por_competicao(competicao_id):
        """Carrega todos os times (ID e Nome) de uma competição específica."""
        conn = criar_conexao()
        times = []
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome FROM time WHERE competicao_id = ? ORDER BY nome", (competicao_id,))
                times = cursor.fetchall() # Returns list of (id, nome) tuples
            except sqlite3.Error as e:
                print(f"Erro ao carregar times da competição {competicao_id}: {e}")
            finally:
                conn.close()
        return times

# ==================================================
# Atleta Model
# ==================================================
class Atleta:
    @staticmethod
    def criar(nome, numero, time_id):
        """Cria um novo atleta associado a um time."""
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO atleta (nome, numero, time_id) VALUES (?, ?, ?)",
                    (nome, numero, time_id)
                )
                conn.commit()
                return True # Indicate success
            except sqlite3.Error as e:
                print(f"Erro ao criar atleta: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def carregar_por_time(time_id):
        """Carrega todos os atletas (ID, Nome, Número) de um time específico."""
        conn = criar_conexao()
        atletas = []
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, numero FROM atleta WHERE time_id = ? ORDER BY nome", (time_id,))
                atletas = cursor.fetchall() # Returns list of (id, nome, numero) tuples
            except sqlite3.Error as e:
                print(f"Erro ao carregar atletas do time {time_id}: {e}")
            finally:
                conn.close()
        return atletas

# ==================================================
# Jogo Model (Placeholder/Basic Structure)
# ==================================================
class Jogo:
    @staticmethod
    def criar(competicao_id, time_casa_id, time_visitante_id):
        # Basic implementation - might need date, status etc.
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO jogo (competicao_id, time_casa_id, time_visitante_id, status) VALUES (?, ?, ?, ?)",
                    (competicao_id, time_casa_id, time_visitante_id, 'Agendado') # Default status
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao criar jogo: {e}")
            finally:
                conn.close()
        return None

    @staticmethod
    def finalizar_jogo(jogo_id, placar_casa, placar_visitante):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE jogo SET placar_casa = ?, placar_visitante = ?, status = 'Concluído' WHERE id = ?",
                    (placar_casa, placar_visitante, jogo_id)
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Erro ao atualizar jogo: {e}")
            finally:
                conn.close()
        return False

    @staticmethod
    def listar_por_competicao(competicao_id):
        conn = criar_conexao()
        jogos = []
        if conn:
            try:
                cursor = conn.cursor()
                # Fetch necessary details, potentially joining with team names
                cursor.execute("""
                    SELECT j.id, tc.nome, tv.nome, j.placar_casa, j.placar_visitante, j.status
                    FROM jogo j
                    JOIN time tc ON j.time_casa_id = tc.id
                    JOIN time tv ON j.time_visitante_id = tv.id
                    WHERE j.competicao_id = ?
                    ORDER BY j.id -- Or by date if available
                """, (competicao_id,))
                jogos = cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao listar jogos: {e}")
            finally:
                conn.close()
        return jogos

    @staticmethod
    def gerar_confrontos(competicao_id, formato):
        # This is a complex function and depends heavily on the format
        # Keeping the basic structure from the original file
        try:
            times_data = Time.carregar_por_competicao(competicao_id)
            times = [t[0] for t in times_data] # Get only IDs
            if not times or len(times) < 2:
                print("Não há times suficientes para gerar confrontos.")
                return False

            confrontos = []
            if formato == "Torneio de pontos corridos":
                for i in range(len(times)):
                    for j in range(len(times)):
                        if i != j:
                            confrontos.append((times[i], times[j]))
            elif formato == "Eliminação Direta":
                # Simple pairing, assumes even number for simplicity
                import random
                random.shuffle(times)
                for i in range(0, len(times), 2):
                    if i + 1 < len(times):
                        confrontos.append((times[i], times[i+1]))
            else:
                print(f"Formato de disputa '{formato}' não suportado para geração automática.")
                return False

            # Insert games into the database
            success_count = 0
            for casa_id, visitante_id in confrontos:
                if Jogo.criar(competicao_id, casa_id, visitante_id):
                    success_count += 1
            print(f"{success_count} confrontos gerados para a competição {competicao_id}.")
            return success_count > 0
        except Exception as e:
            print(f"Erro ao gerar confrontos: {e}")
            return False

# ==================================================
# Pontuacao Model (Placeholder/Basic Structure)
# ==================================================
class Pontuacao:
    @staticmethod
    def registrar_pontos(atleta_id, jogo_id, pontos):
        # Assumes a 'pontuacao' table exists
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                # Example: Insert or Update points for an athlete in a game
                # This might need more complex logic depending on requirements
                cursor.execute(
                    "INSERT INTO pontuacao (atleta_id, jogo_id, pontos) VALUES (?, ?, ?)",
                    (atleta_id, jogo_id, pontos)
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Erro ao registrar pontuação: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def get_artilheiros(competicao_id):
        # Assumes 'pontuacao' table and joins are correct
        conn = criar_conexao()
        artilheiros = []
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT a.nome, SUM(p.pontos) as total_pontos
                    FROM pontuacao p
                    JOIN atleta a ON p.atleta_id = a.id
                    JOIN jogo j ON p.jogo_id = j.id
                    WHERE j.competicao_id = ?
                    GROUP BY a.id, a.nome
                    ORDER BY total_pontos DESC
                    LIMIT 10
                """
                cursor.execute(query, (competicao_id,))
                artilheiros = cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao buscar artilheiros: {e}")
            finally:
                conn.close()
        return artilheiros

