# database_corrigido.py
import sqlite3
from sqlite3 import Error
# Assuming config.py defines DATABASE_NAME, otherwise define it here
# from config import DATABASE_NAME 
DATABASE_NAME = "competicoes.db" # Default name if not in config

def criar_conexao():
    """Cria conexão com o banco SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON") 
        return conn
    except Error as e:
        print(f"Erro ao conectar ao banco: {e}")
    return conn

def criar_tabelas():
    """Cria as tabelas do banco de dados se não existirem."""
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
                    FOREIGN KEY (competicao_id) REFERENCES competicao(id) ON DELETE CASCADE
                )
            """)
            
            # Tabela Atletas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS atleta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    numero INTEGER NOT NULL,
                    time_id INTEGER NOT NULL,
                    FOREIGN KEY (time_id) REFERENCES time(id) ON DELETE CASCADE
                )
            """)
            
            # Tabela Jogos (ADDED)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jogo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    competicao_id INTEGER NOT NULL,
                    time_casa_id INTEGER NOT NULL,
                    time_visitante_id INTEGER NOT NULL,
                    placar_casa INTEGER,
                    placar_visitante INTEGER,
                    status TEXT DEFAULT 'Agendado', -- e.g., 'Agendado', 'Concluído'
                    data DATETIME, -- Optional: Add date/time if needed
                    FOREIGN KEY (competicao_id) REFERENCES competicao(id) ON DELETE CASCADE,
                    FOREIGN KEY (time_casa_id) REFERENCES time(id) ON DELETE CASCADE,
                    FOREIGN KEY (time_visitante_id) REFERENCES time(id) ON DELETE CASCADE
                )
            """)

            # Tabela Pontuacao (ADDED - Basic structure)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pontuacao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    atleta_id INTEGER NOT NULL,
                    jogo_id INTEGER NOT NULL,
                    pontos INTEGER NOT NULL DEFAULT 0, -- Goals, points, etc.
                    FOREIGN KEY (atleta_id) REFERENCES atleta(id) ON DELETE CASCADE,
                    FOREIGN KEY (jogo_id) REFERENCES jogo(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            print("Tabelas verificadas/criadas com sucesso.")
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")
        finally:
            conn.close()

# Executar criação de tabelas ao iniciar (ou pode ser chamado explicitamente)
# Consider moving this call to main.py before starting the App if issues persist
if __name__ == "__main__":
    # This allows running `python database.py` to ensure tables are created
    print(f"Verificando/Criando tabelas no banco '{DATABASE_NAME}'...")
    criar_tabelas()
else:
    # Call when imported, but consider if this is the best place
    # It's generally safer to call this explicitly once in main.py
    criar_tabelas() 

