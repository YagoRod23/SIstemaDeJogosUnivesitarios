# models.py
import sqlite3
from database import criar_conexao
from config import PONTOS_VITORIA, PONTOS_EMPATE, PONTOS_DERROTA

class Competicao:
    @staticmethod
    def criar(nome, modalidade, formato):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO competicao (nome, modalidade, formato_disputa) VALUES (?, ?, ?)",
                    (nome, modalidade, formato)
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Erro ao criar competição: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def carregar_todas():
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, modalidade FROM competicao")
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao carregar competições: {e}")
            finally:
                conn.close()
        return []



    @staticmethod
    def get_times(competicao_id):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome FROM time WHERE competicao_id = ?", (competicao_id,))
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao carregar times: {e}")
            finally:
                conn.close()
        return []

    @staticmethod
    def get_classificacao(competicao_id):
        conn = criar_conexao()
        if conn:
            try:
                query = """
                SELECT 
                    t.id,
                    t.nome,
                    COUNT(j.id) as jogos,
                    SUM(CASE 
                        WHEN (j.time_casa_id = t.id AND j.placar_casa > j.placar_visitante) OR 
                             (j.time_visitante_id = t.id AND j.placar_visitante > j.placar_casa) THEN 1 
                        ELSE 0 END) as vitorias,
                    SUM(CASE 
                        WHEN j.placar_casa = j.placar_visitante THEN 1 
                        ELSE 0 END) as empates,
                    SUM(CASE 
                        WHEN (j.time_casa_id = t.id AND j.placar_casa < j.placar_visitante) OR 
                             (j.time_visitante_id = t.id AND j.placar_visitante < j.placar_casa) THEN 1 
                        ELSE 0 END) as derrotas,
                    SUM(CASE 
                        WHEN j.time_casa_id = t.id THEN j.placar_casa
                        ELSE j.placar_visitante END) as pontos_pro,
                    SUM(CASE 
                        WHEN j.time_casa_id = t.id THEN j.placar_visitante
                        ELSE j.placar_casa END) as pontos_contra,
                    (SUM(CASE WHEN j.time_casa_id = t.id THEN j.placar_casa ELSE j.placar_visitante END) -
                     SUM(CASE WHEN j.time_casa_id = t.id THEN j.placar_visitante ELSE j.placar_casa END)) as saldo,
                    (SUM(CASE 
                        WHEN (j.time_casa_id = t.id AND j.placar_casa > j.placar_visitante) OR 
                             (j.time_visitante_id = t.id AND j.placar_visitante > j.placar_casa) THEN PONTOS_VITORIA
                        WHEN j.placar_casa = j.placar_visitante THEN PONTOS_EMPATE
                        ELSE PONTOS_DERROTA END)) as pontos
                FROM time t
                LEFT JOIN jogo j ON t.id = j.time_casa_id OR t.id = j.time_visitante_id
                WHERE t.competicao_id = ? AND j.status = 'Concluído'
                GROUP BY t.id
                ORDER BY pontos DESC, saldo DESC, pontos_pro DESC
                """
                cursor = conn.cursor()
                cursor.execute(query, (competicao_id,))
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao calcular classificação: {e}")
            finally:
                conn.close()
        return []

class Time:
    @staticmethod
    def criar(nome, competicao_id):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO time (nome, competicao_id)
                    VALUES (?, ?)
                """, (nome, competicao_id))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao criar time: {e}")
            finally:
                conn.close()
        return None

    @staticmethod
    def carregar_por_competicao(competicao_id):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome FROM time WHERE competicao_id = ?", (competicao_id,))
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao carregar times: {e}")
            finally:
                conn.close()
        return []
    
    @staticmethod
    def get_atletas(time_id):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, numero FROM atleta WHERE time_id = ?", (time_id,))
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao carregar atletas: {e}")
            finally:
                conn.close()
        return []

class Atleta:
    @staticmethod
    def criar(nome, numero, time_id):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO atleta (nome, numero, time_id)
                    VALUES (?, ?, ?)
                """, (nome, numero, time_id))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao criar atleta: {e}")
            finally:
                conn.close()
        return None

class Jogo:
    @staticmethod
    def criar(competicao_id, time_casa_id, time_visitante_id):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO jogo (competicao_id, time_casa_id, time_visitante_id)
                    VALUES (?, ?, ?)
                """, (competicao_id, time_casa_id, time_visitante_id))
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
                cursor.execute("""
                    UPDATE jogo
                    SET placar_casa = ?, placar_visitante = ?, status = 'Concluído'
                    WHERE id = ?
                """, (placar_casa, placar_visitante, jogo_id))
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
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, time_casa_id, time_visitante_id, placar_casa, placar_visitante, status
                    FROM jogo
                    WHERE competicao_id = ?
                    ORDER BY data
                """, (competicao_id,))
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao listar jogos: {e}")
            finally:
                conn.close()
        return []
    
    @staticmethod
    def gerar_confrontos(competicao_id, formato):
        times = [t[0] for t in Time.carregar_por_competicao(competicao_id)]
        confrontos = []
        
        if formato == "Pontos Corridos":
            # Gerar todos os confrontos possíveis (turno e returno)
            for i in range(len(times)):
                for j in range(len(times)):
                    if i != j:
                        confrontos.append((times[i], times[j]))
        elif formato == "Eliminação Direta":
            # Gerar confrontos simples em pares (supondo número par de times)
            for i in range(0, len(times), 2):
                if i+1 < len(times):
                    confrontos.append((times[i], times[i+1]))
        
        # Inserir no banco
        for casa, visitante in confrontos:
            Jogo.criar(competicao_id, casa, visitante)

class Pontuacao:
    @staticmethod
    def registrar_pontos(atleta_id, jogo_id, pontos):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO pontuacao (atleta_id, jogo_id, pontos)
                    VALUES (?, ?, ?)
                """, (atleta_id, jogo_id, pontos))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao registrar pontuação: {e}")
            finally:
                conn.close()
        return None
    
    @staticmethod
    def get_artilheiros(competicao_id):
        conn = criar_conexao()
        if conn:
            try:
                query = """
                SELECT a.nome, SUM(p.pontos) as total_pontos
                FROM pontuacao p
                JOIN atleta a ON p.atleta_id = a.id
                JOIN jogo j ON p.jogo_id = j.id
                WHERE j.competicao_id = ?
                GROUP BY a.id
                ORDER BY total_pontos DESC
                LIMIT 10
                """
                cursor = conn.cursor()
                cursor.execute(query, (competicao_id,))
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao buscar artilheiros: {e}")
            finally:
                conn.close()
        return []
