# utils.py
import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta
import csv
import os
from database import criar_conexao
from config import DIAS_COMPETICAO, HORARIOS_JOGOS, FORMATOS_DISPUTA, LIMITE_ATLETAS_POR_TIME
from models import Competicao, Time, Atleta, Jogo, Pontuacao

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

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

# ==================================================
# EXPORTAÇÃO DE RELATÓRIOS
# ==================================================
def exportar_relatorio_csv(competicao_id, tipo_relatorio, caminho_arquivo):
    """Exporta relatório em CSV."""
    try:
        with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            if tipo_relatorio == "classificacao":
                classificacao = Competicao.calcular_classificacao(competicao_id)
                writer.writerow(['Posição', 'Time', 'Pontos', 'Jogos', 'Vitórias', 'Empates', 'Derrotas', 'Gols Pró', 'Gols Contra', 'Saldo'])
                for pos, time_data in enumerate(classificacao, 1):
                    writer.writerow([pos, time_data['nome'], time_data['P'], time_data['J'], time_data['V'], time_data['E'], time_data['D'], time_data['GP'], time_data['GC'], time_data['SG']])

            elif tipo_relatorio == "jogos":
                jogos = Jogo.listar_por_competicao(competicao_id)
                writer.writerow(['ID', 'Time Casa', 'Placar', 'Time Visitante', 'Status'])
                for jogo in jogos:
                    placar = f"{jogo[3] or 0} x {jogo[4] or 0}" if jogo[5] == 'Concluído' else "-"
                    writer.writerow([jogo[0], jogo[1], placar, jogo[2], jogo[5]])

            elif tipo_relatorio == "artilheiros":
                artilheiros = Pontuacao.get_artilheiros(competicao_id)
                writer.writerow(['Nome', 'Pontos'])
                for nome, pontos in artilheiros:
                    writer.writerow([nome, pontos])

        return True
    except Exception as e:
        print(f"Erro ao exportar CSV: {e}")
        return False

def exportar_relatorio_pdf(competicao_id, tipo_relatorio, caminho_arquivo):
    """Exporta relatório em PDF usando reportlab."""
    if not REPORTLAB_AVAILABLE:
        print("ReportLab não está instalado. Instale com: pip install reportlab")
        return False

    try:
        c = canvas.Canvas(caminho_arquivo, pagesize=letter)
        width, height = letter

        # Título
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 50, f"Relatório - {tipo_relatorio.capitalize()}")

        y = height - 80

        if tipo_relatorio == "classificacao":
            classificacao = Competicao.calcular_classificacao(competicao_id)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, y, "Classificação")
            y -= 20
            c.setFont("Helvetica", 10)
            for pos, time_data in enumerate(classificacao, 1):
                linha = f"{pos}. {time_data['nome']} - {time_data['P']} pts"
                c.drawString(100, y, linha)
                y -= 15
                if y < 50:
                    c.showPage()
                    y = height - 50

        elif tipo_relatorio == "jogos":
            jogos = Jogo.listar_por_competicao(competicao_id)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, y, "Histórico de Jogos")
            y -= 20
            c.setFont("Helvetica", 10)
            for jogo in jogos:
                placar = f"{jogo[3] or 0} x {jogo[4] or 0}" if jogo[5] == 'Concluído' else "Não realizado"
                linha = f"{jogo[1]} {placar} {jogo[2]} ({jogo[5]})"
                c.drawString(100, y, linha)
                y -= 15
                if y < 50:
                    c.showPage()
                    y = height - 50

        c.save()
        return True
    except Exception as e:
        print(f"Erro ao exportar PDF: {e}")
        return False

def salvar_versao_relatorio(competicao_id, tipo_relatorio, conteudo):
    """Salva versão do relatório para histórico."""
    conn = criar_conexao()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relatorio_versoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    competicao_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,
                    conteudo TEXT NOT NULL,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (competicao_id) REFERENCES competicao(id)
                )
            """)
            cursor.execute("INSERT INTO relatorio_versoes (competicao_id, tipo, conteudo) VALUES (?, ?, ?)",
                          (competicao_id, tipo_relatorio, conteudo))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao salvar versão do relatório: {e}")
            return False
        finally:
            conn.close()
    return False
