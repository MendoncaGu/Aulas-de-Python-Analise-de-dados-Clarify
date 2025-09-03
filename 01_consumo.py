from flask import Flask, request, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.io as pio
import random
import config_PythonsDeElite as config
import consultas

caminho_banco = config.DB_PATH

pio.renderers.default = 'browser'
nomebanco = config.NOMEBANCO
rotas = config.ROTAS
tabela_a = config.TABELA_A
tabela_b = config.TABELA_B
#Arquivos a serem carregados
dfDrinks = pd.read_csv(f'{caminho_banco}{tabela_a}')
dfAvengers = pd.read_csv(f'{caminho_banco}{tabela_b}', encoding = 'latin1')

#outros exemplos de encodings :utf-8, CP1256, iso8859-1

#criamos o banco de dados em SQL caso não exista
conn = sqlite3.connect(f'{caminho_banco}{nomebanco}')

dfDrinks.to_sql('bebidas', conn, if_exists = 'replace', index = False)

dfAvengers.to_sql('vingadores', conn, if_exists = 'replace', index = False)

conn.commit()
conn.close()

html_template = f'''

    <h1>Dashboards</h1>
    <h2>Parte 01   </h2>
    <ul>
        <li> <a href="{rotas[1]}">Top 10 Paises em comsumo</a>  </li>
        <li> <a href="{rotas[2]}">Media de consumo por tipo</a>  </li>
        <li> <a href="{rotas[3]}">Consumo por regiao</a>  </li>
        <li> <a href="{rotas[4]}">Comparativo entre tipos</a>  </li>
        
    </ul>
    <h2>parte 02</h2>
    <ul>
        <li> <a href="{rotas[5]}">Comprar</a>  </li>
        <li> <a href="{rotas[6]}">Upload</a>  </li>
        <li> <a href="{rotas[7]}">Apagar</a>  </li>
        <li> <a href="{rotas[8]}>Ver tabela</a>  </li>
        <li> <a href="{rotas[9]}">V.A.A</a>  </li>
    </ul>
'''

#iniciar o flask
app = Flask(__name__)

@app.route(rotas [0])
def index():
    return render_template_string(html_template)

@app.route(rotas [1])
def grafico1():
    with sqlite3.connect(f'{caminho_banco}{nomebanco}') as conn:
        df = pd.read_sql_query(consultas.consulta01, conn)
    figuraGrafico1 = px.bar(
        df,
        x = 'country',
        y = 'total_litres_of_pure_alcohol',
        title = 'Top 10 paises em comsumo de alcool!'     
    )
    return figuraGrafico1.to_html()



#inicia o servidor
if __name__ == '__main__':
    app.run(debug=True)
