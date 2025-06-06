# models_com_classificacao.py
import sqlite3
import random
from collections import defaultdict
from database import criar_conexao

# Define default points if not imported from config
PONTOS_VITORIA = 3
PONTOS_EMPATE = 1
PONTOS_DERROTA = 0

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
    def listar_todas():
        conn = criar_conexao()
        competicoes = []
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome FROM competicao ORDER BY nome")
                competicoes = cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao listar competições: {e}")
            finally:
                conn.close()
        return competicoes

    @staticmethod
    def buscar_por_id(competicao_id):
        conn = criar_conexao()
        competicao_info = None
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, modalidade, formato_disputa FROM competicao WHERE id = ?", (competicao_id,))
                competicao_info = cursor.fetchone()
            except sqlite3.Error as e:
                print(f"Erro ao buscar competição por ID {competicao_id}: {e}")
            finally:
                conn.close()
        return competicao_info

    @staticmethod
    def calcular_classificacao(competicao_id):
        """Calcula a tabela de classificação para uma competição."""
        conn = criar_conexao()
        if not conn:
            return []

        try:
            # 1. Get all teams in the competition
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM time WHERE competicao_id = ?", (competicao_id,))
            times_data = cursor.fetchall()
            if not times_data:
                return [] # No teams, no classification

            # Initialize stats for each team
            classificacao = {time_id: {
                'nome': nome,
                'P': 0, 'J': 0, 'V': 0, 'E': 0, 'D': 0,
                'GP': 0, 'GC': 0, 'SG': 0
            } for time_id, nome in times_data}

            # 2. Get all completed games for the competition
            cursor.execute("""
                SELECT time_casa_id, time_visitante_id, placar_casa, placar_visitante
                FROM jogo
                WHERE competicao_id = ? AND status = 'Concluído'
            """, (competicao_id,))
            jogos_concluidos = cursor.fetchall()

            # 3. Process each completed game
            for casa_id, vis_id, p_casa, p_vis in jogos_concluidos:
                # Ensure scores are not None
                if p_casa is None or p_vis is None:
                    continue 

                # Update stats for home team
                if casa_id in classificacao:
                    classificacao[casa_id]['J'] += 1
                    classificacao[casa_id]['GP'] += p_casa
                    classificacao[casa_id]['GC'] += p_vis
                    classificacao[casa_id]['SG'] += (p_casa - p_vis)
                    if p_casa > p_vis:
                        classificacao[casa_id]['V'] += 1
                        classificacao[casa_id]['P'] += PONTOS_VITORIA
                    elif p_casa == p_vis:
                        classificacao[casa_id]['E'] += 1
                        classificacao[casa_id]['P'] += PONTOS_EMPATE
                    else:
                        classificacao[casa_id]['D'] += 1
                        classificacao[casa_id]['P'] += PONTOS_DERROTA

                # Update stats for away team
                if vis_id in classificacao:
                    classificacao[vis_id]['J'] += 1
                    classificacao[vis_id]['GP'] += p_vis
                    classificacao[vis_id]['GC'] += p_casa
                    classificacao[vis_id]['SG'] += (p_vis - p_casa)
                    if p_vis > p_casa:
                        classificacao[vis_id]['V'] += 1
                        classificacao[vis_id]['P'] += PONTOS_VITORIA
                    elif p_vis == p_casa:
                        classificacao[vis_id]['E'] += 1
                        classificacao[vis_id]['P'] += PONTOS_EMPATE
                    else:
                        classificacao[vis_id]['D'] += 1
                        classificacao[vis_id]['P'] += PONTOS_DERROTA

            # 4. Convert to list and sort
            tabela_final = list(classificacao.values())
            # Sort by: Points (desc), Wins (desc), Goal Diff (desc), Goals For (desc), Name (asc)
            tabela_final.sort(key=lambda x: (x['P'], x['V'], x['SG'], x['GP'], x['nome']), reverse=True)

            return tabela_final

        except sqlite3.Error as e:
            print(f"Erro ao calcular classificação: {e}")
            return []
        finally:
            conn.close()

# ==================================================
# Time Model
# ==================================================
class Time:
    @staticmethod
    def criar(nome, competicao_id):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO time (nome, competicao_id) VALUES (?, ?)",
                    (nome, competicao_id)
                )
                conn.commit()
                return True 
            except sqlite3.Error as e:
                print(f"Erro ao criar time: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def carregar_por_competicao(competicao_id):
        conn = criar_conexao()
        times = []
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome FROM time WHERE competicao_id = ? ORDER BY nome", (competicao_id,))
                times = cursor.fetchall()
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
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO atleta (nome, numero, time_id) VALUES (?, ?, ?)",
                    (nome, numero, time_id)
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Erro ao criar atleta: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def carregar_por_time(time_id):
        conn = criar_conexao()
        atletas = []
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, numero FROM atleta WHERE time_id = ? ORDER BY nome", (time_id,))
                atletas = cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao carregar atletas do time {time_id}: {e}")
            finally:
                conn.close()
        return atletas

# ==================================================
# Jogo Model (Updated for Sumula)
# ==================================================
class Jogo:
    @staticmethod
    def criar(competicao_id, time_casa_id, time_visitante_id):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO jogo (competicao_id, time_casa_id, time_visitante_id, status) VALUES (?, ?, ?, ?)",
                    (competicao_id, time_casa_id, time_visitante_id, 'Agendado')
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao criar jogo: {e}")
            finally:
                conn.close()
        return None

    @staticmethod
    def buscar_detalhes(jogo_id):
        conn = criar_conexao()
        jogo_info = None
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT 
                        j.id, j.competicao_id, 
                        j.time_casa_id, j.time_visitante_id, 
                        j.placar_casa, j.placar_visitante, j.status,
                        tc.nome as nome_casa, tv.nome as nome_visitante
                    FROM jogo j
                    JOIN time tc ON j.time_casa_id = tc.id
                    JOIN time tv ON j.time_visitante_id = tv.id
                    WHERE j.id = ?
                """
                cursor.execute(query, (jogo_id,))
                jogo_info = cursor.fetchone()
            except sqlite3.Error as e:
                print(f"Erro ao buscar detalhes do jogo {jogo_id}: {e}")
            finally:
                conn.close()
        return jogo_info 

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
                return cursor.rowcount > 0 
            except sqlite3.Error as e:
                print(f"Erro ao finalizar jogo {jogo_id}: {e}")
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
                cursor.execute("""
                    SELECT j.id, tc.nome, tv.nome, j.placar_casa, j.placar_visitante, j.status
                    FROM jogo j
                    JOIN time tc ON j.time_casa_id = tc.id
                    JOIN time tv ON j.time_visitante_id = tv.id
                    WHERE j.competicao_id = ?
                    ORDER BY j.id
                """, (competicao_id,))
                jogos = cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao listar jogos da competição {competicao_id}: {e}")
            finally:
                conn.close()
        return jogos

    @staticmethod
    def gerar_confrontos(competicao_id, formato):
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
                if len(times) % 2 != 0:
                    print("Número ímpar de times não suportado para Eliminação Direta simples.")
                    return False
                random.shuffle(times)
                for i in range(0, len(times), 2):
                     confrontos.append((times[i], times[i+1]))
            else:
                print(f"Formato de disputa '{formato}' não suportado para geração automática.")
                return False

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
# Pontuacao Model (Updated for Sumula)
# ==================================================
class Pontuacao:
    @staticmethod
    def registrar_pontos(atleta_id, jogo_id, pontos):
        conn = criar_conexao()
        if conn:
            try:
                cursor = conn.cursor()
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
    def listar_por_jogo(jogo_id):
        conn = criar_conexao()
        pontuacoes = []
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT 
                        p.atleta_id, 
                        a.nome as nome_atleta, 
                        t.id as time_id, 
                        t.nome as nome_time, 
                        SUM(p.pontos) as total_pontos
                    FROM pontuacao p
                    JOIN atleta a ON p.atleta_id = a.id
                    JOIN time t ON a.time_id = t.id
                    WHERE p.jogo_id = ?
                    GROUP BY p.atleta_id, a.nome, t.id, t.nome
                    ORDER BY t.id, total_pontos DESC
                """
                cursor.execute(query, (jogo_id,))
                pontuacoes = cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao listar pontuações do jogo {jogo_id}: {e}")
            finally:
                conn.close()
        return pontuacoes

    @staticmethod
    def get_artilheiros(competicao_id):
        conn = criar_conexao()
        artilheiros = []
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT 
                        a.nome, 
                        SUM(p.pontos) as total_pontos
                    FROM pontuacao p
                    JOIN atleta a ON p.atleta_id = a.id
                    JOIN jogo j ON p.jogo_id = j.id
                    WHERE j.competicao_id = ?
                    GROUP BY a.id, a.nome
                    HAVING SUM(p.pontos) > 0
                    ORDER BY total_pontos DESC
                    LIMIT 20
                """
                cursor.execute(query, (competicao_id,))
                artilheiros = cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Erro ao buscar artilheiros da competição {competicao_id}: {e}")
            finally:
                conn.close()
        return artilheiros

