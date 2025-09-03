#  ____        _   _                           _        _____ _ _ _       
# |  _ \ _   _| |_| |__   ___  _ __  ___    __| | ___  | ____| (_) |_ ___ 
# | |_) | | | | __| '_ \ / _ \| '_ \/ __|  / _` |/ _ \ |  _| | | | __/ _ \
# |  __/| |_| | |_| | | | (_) | | | \__ \ | (_| |  __/ | |___| | | ||  __/
# |_|    \__, |\__|_| |_|\___/|_| |_|___/  \__,_|\___| |_____|_|_|\__\___|
#        |___/                                                            

# Autor: Gustavo
# Versão 0.0.1v 09-2025
#caminho da pasta
DB_PATH = 'C:/Users/noturno/Desktop/Python 2 - Gustavo/'
NOMEBANCO = 'bancoDeElite.db'

TABELA_A = 'drinks.csv'
TABELA_B = 'avengers.csv'

#definições do servidor
FLASK_DEBUG = True
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000

#rotas (caminhos de cada pagina)
ROTAS = [
    '/',                # rota00
    '/grafico1',        # rota01
    '/grafico2',        # rota02
    '/grafico3',        # rota03
    '/grafico4',        # rota04
    '/comparar',        # rota05
    '/upload',          # rota06
    '/apagar',          # rota07
    '/ver',             # rota08
    '/final'            # rota09
]

#----------------------------------------------------
#consultas SQL
#----------------------------------------------------

