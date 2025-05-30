# utils.py
import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta
from database import criar_conexao
from config import DIAS_COMPETICAO, HORARIOS_JOGOS, FORMATOS_DISPUTA

# ==================================================
# VALIDAÇÃO DE DADOS
# ==================================================
def validar_nome(nome, tipo_objeto):
    """Valida nomes de competições, times e atletas"""
    if not nome or len(nome.strip()) < 3:
        raise ValueError(f"Nome de {tipo_objeto} muito curto (mínimo 3 caracteres)")
    if len(nome) > 100:
        raise ValueError(f"Nome de {tipo_objeto} muito longo (máximo 100 caracteres)")
    return nome.strip()

def validar_numero(numero, campo):
    """Valida números de atletas e campos numéricos"""
    try:
        valor = int(numero)
        if valor <= 0:
            raise ValueError(f"{campo} deve ser maior que zero")
        return valor
    except ValueError:
        raise ValueError(f"{campo} deve ser um número inteiro válido")

# ==================================================
# MANIPULAÇÃO DE DATAS
# ==================================================
def gerar_calendario(data_inicio):
    """Gera datas de jogos conforme configurações"""
    datas = []
    data_atual = datetime.strptime(data_inicio, "%Y-%m-%d")
    
    for _ in range(20):  # Gera até 20 datas
        if data_atual.strftime("%A") in DIAS_COMPETICAO:
            for hora in HORARIOS_JOGOS:
                datas.append({
                    "data": data_atual.strftime("%Y-%m-%d"),
                    "hora": hora
                })
        data_atual += timedelta(days=1)
    return datas[:len(HORARIOS_JOGOS)*3]  # Limita a 3 semanas

# ==================================================
# OPERAÇÕES ESPECÍFICAS
# ==================================================
def sortear_grupos(times, num_grupos):
    """Distribui times em grupos para formato de disputa"""
    grupos = [[] for _ in range(num_grupos)]
    for i, time in enumerate(times):
        grupos[i % num_grupos].append(time)
    return grupos

def gerar_confrontos(times, formato):
    """Gera pares de confrontos conforme formato selecionado"""
    if formato == "Torneio eliminatório":
        return [(times[i], times[~i]) for i in range(len(times)//2)]
    
    elif formato == "Torneio de pontos corridos":
        confrontos = []
        for i in range(len(times)):
            for j in range(i+1, len(times)):
                confrontos.append((times[i], times[j]))
        return confrontos
    
    raise ValueError("Formato de disputa não suportado")

# ==================================================
# RELATÓRIOS E ESTATÍSTICAS
# ==================================================
def calcular_estatisticas_time(time_id):
    """Retorna estatísticas detalhadas de um time"""
    conn = criar_conexao()
    estatisticas = {
        'jogos': 0,
        'vitorias': 0,
        'empates': 0,
        'derrotas': 0,
        'gols_pro': 0,
        'gols_contra': 0
    }
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT placar_casa, placar_visitante 
            FROM jogo 
            WHERE time_casa_id = ? OR time_visitante_id = ?
        """, (time_id, time_id))
        
        for placar in cursor.fetchall():
            estatisticas['jogos'] += 1
            gols_casa = placar[0] or 0
            gols_visitante = placar[1] or 0
            
            if time_id == placar[0]:
                estatisticas['gols_pro'] += gols_casa
                estatisticas['gols_contra'] += gols_visitante
                if gols_casa > gols_visitante:
                    estatisticas['vitorias'] += 1
                elif gols_casa == gols_visitante:
                    estatisticas['empates'] += 1
                else:
                    estatisticas['derrotas'] += 1
            else:
                estatisticas['gols_pro'] += gols_visitante
                estatisticas['gols_contra'] += gols_casa
                if gols_visitante > gols_casa:
                    estatisticas['vitorias'] += 1
                elif gols_visitante == gols_casa:
                    estatisticas['empates'] += 1
                else:
                    estatisticas['derrotas'] += 1
    
    except Error as e:
        print(f"Erro ao calcular estatísticas: {e}")
    finally:
        if conn:
            conn.close()
    
    return estatisticas

# ==================================================
# VALIDAÇÕES COMPLEXAS
# ==================================================
def verificar_limite_atletas(time_id, modalidade):
    """Verifica se atingiu limite máximo de atletas por time"""
    conn = criar_conexao()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM atleta WHERE time_id = ?", (time_id,))
        quantidade = cursor.fetchone()[0]
        
        limite = LIMITE_ATLETAS_POR_TIME.get(modalidade, LIMITE_ATLETAS_POR_TIME['Padrão'])
        return quantidade >= limite
    
    except Error as e:
        print(f"Erro ao verificar limite de atletas: {e}")
        return False
    finally:
        if conn:
            conn.close()

# ==================================================
# BACKUP E RECUPERAÇÃO
# ==================================================
def fazer_backup(path_destino):
    """Cria uma cópia do banco de dados"""
    conn = criar_conexao()
    try:
        cursor = conn.cursor()
        
        # Cria backup completo
        with open(path_destino, 'w') as f:
            for linha in conn.iterdump():
                f.write(f'{linha}\n')
        return True
    except Error as e:
        print(f"Erro ao fazer backup: {e}")
        return False
    finally:
        if conn:
            conn.close()
