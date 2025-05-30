# config.py

DATABASE_NAME = "gestao_esportiva.db"

MODALIDADES = (
    "Futebol",
    "Vôlei",
    "Basquete",
    "Handebol",
    "Queimado",
    "Atletismo",
    "Natação",
    "Xadrez"
)

FORMATOS_DISPUTA = (
    "Torneio eliminatório",
    "Torneio de pontos corridos",
    "Grupos + eliminatórias",
    "Sistema suíço"
)

PONTOS_VITORIA = 3
PONTOS_EMPATE = 1
PONTOS_DERROTA = 0

# Configurações de pontuação por modalidade (exemplo)
PONTUACAO_POR_MODALIDADE = {
    "Futebol": {
        "gol": 1,
        "assistencia": 0.5
    },
    "Vôlei": {
        "ponto": 1,
        "saque": 0.2,
        "bloqueio": 0.5
    },
    "Basquete": {
        "cesta_2pts": 2,
        "cesta_3pts": 3,
        "assistencia": 1
    }
}

# Outras constantes
LIMITE_ATLETAS_POR_TIME = {
    "Futebol": 18,
    "Vôlei": 12,
    "Basquete": 15,
    "Handebol": 14,
    "Padrão": 20
}

DIAS_COMPETICAO = [
    "Segunda", "Quarta", "Sexta"
]

HORARIOS_JOGOS = [
    "09:00", "11:00", "14:00", "16:00"
]
