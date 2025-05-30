# database.py
import sqlite3
from sqlite3 import Error
from config import DATABASE_NAME  # Agora encontrará a constante

def criar_conexao():
    """Cria conexão com o banco SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        return conn
    except Error as e:
        print(f"Erro ao conectar ao banco: {e}")
    return conn

def criar_tabelas():
    """Cria as tabelas do banco de dados"""
    conn = criar_conexao()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Tabela Competições
            cursor.execute("""
    CREATE TABLE IF NOT EXISTS competicao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        modalidade TEXT NOT NULL,
        formato_disputa TEXT NOT NULL,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

            
            # Tabela Times
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS time (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    competicao_id INTEGER NOT NULL,
                    FOREIGN KEY (competicao_id) REFERENCES competicao(id)
                )
            """)
            
            # Tabela Atletas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS atleta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    numero INTEGER NOT NULL,
                    time_id INTEGER NOT NULL,
                    FOREIGN KEY (time_id) REFERENCES time(id)
                )
            """)
            
            conn.commit()
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")
        finally:
            conn.close()

# Executar criação de tabelas ao importar o módulo
criar_tabelas()
