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

@app.route(rotas[2])
def grafico2():
     with sqlite3.connect(f'{caminho_banco}{nomebanco}') as conn:
        df = pd.read_sql_query(consultas.consulta02, conn)
        # transforma as colunas cerveja destilados e vinhos e linhas criando no fim duas colunas,
        # uma chamada bebidas com os nomes originais das colunas e outra com a media de porções
        # com seus valores correspondentes
        #MELTED
        df_melted = df.melt(var_name ='Bebidas', value_name = 'Media de Porções')
        figuraGrafico2 = px.bar(
        df_melted,
        x = 'Bebidas',
        y = 'Media de Porções',
        title = 'Media de consumo global por tipo'
         )
        return figuraGrafico2.to_html()

@app.route(rotas[3])
def grafico3():
    regioes = {
        'Europa':['France', 'Germany', 'Spain', 'Italy', 'Portugal'],
        'Asia':['China', 'Japan', 'India', 'Thailand'],
        'Africa':['Angola', 'Nigeria', 'Egypt', 'Algeria'],
        'America':['USA', 'Brazil', 'Canada', 'Argentina','Mexico']
    }
    dados = []
    with sqlite3.connect(f'{caminho_banco}{nomebanco}') as conn:
        # itera sobre o dicionario de regioes onde cada chave (regiao tem uma lista de paises)
        for regiao, pais in regioes.items():
            #criando a lista de placeholders para os paises dessa região
            #isso vai ser usado na consulta sql para filtrar o pais da região

            placeholders = ','.join([f"'{p}'" for p in pais])
            query = f"""
                SELECT SUM (total_litres_of_pure_alcohol) AS total
                FROM bebidas
                WHERE country IN ({placeholders})
            """
            total = pd.read_sql_query(query, conn).iloc[0,0]
            dados.append(
                {
                'Região': regiao,
                'Comsumo Total': total
                }
            )
    dfRegioes = pd.DataFrame(dados)
    figuraGrafico3 = px.pie(
        dfRegioes,
        names = "Região",
        values = "Comsumo Total",
        title = "Consumo total por Região"
    )
    return figuraGrafico3.to_html() + f"<br><a href='{rotas[0]}'>Voltar</ a> "

@app.route(rotas[4])
def grafico4():
    with sqlite3.connect(f'{caminho_banco}{nomebanco}') as conn:
        df = pd.read_sql_query(consultas.consulta03, conn)
        medias = df.mean().reset_index()
        medias.columns = ['Tipo', 'Média']
        figuraGrafico4 = px.pie(
            medias,
            names = "Tipo",
            values = "Média",
            title = "Média entre os tipos de bebidas!"
        )
        return figuraGrafico4.to_html() + f"<br><a href='{rotas[0]}'>Voltar</ a> "

@app.route(rotas[5], methods=['POST','GET'])
def comparar():
    opcoes = [
        'beer_servings',
        'spirit_servings',
        'wine_servings'
    ]

    if request.method == "POST":
       eixoX = request.form_get('eixo_x')
       eixoY = request.form_get('eixo_y')
        
    if eixoX == eixoY:
            return f"<h3> Por favor, selecione campos diferentes! </h3> <br><a href='{rotas[5]}'>Voltar</a> "

            conn = sqlite3.connect(f'{caminho_banco}{nomebanco}')
            df = pd.read_sql_query("SELECT country, {}, {} FROM bebidas".format(eixoX,eixoY), conn)
            conn.colse()
            figuraComparar = px.scatter(
            df,
            x = eixoX,
            y = eixoY,
            title = f'Comparação entre {eixoX} VS {eixoY}'

        )
            figuraComparar.update_traces(textposition = 'top center')

            return figuraComparar.to_html() + f"<br><a href='{rotas[0]}'>Voltar</ a> "


    return render_template_string('''
        <h2> Comparar campos </h2>
        <form method = "POST">
                <label>Eixo x: </label>
                <select name="eixo_x">
                        {% for opcao in opcoes %}
                            <option value= '{{opcao}}'>{{opcao}}</option>
                        {% endfor %}
                </select>
                <br><br>
                
                <label> Exio Y: </label>
                <select name="eixo_y">
                         {% for opcao in opcoes %}
                            <option value= '{{opcao}}'>{{opcao}}</option>
                        {% endfor %}
                </select>
                <br><br>
                
                <input type="submit" value="-- Comparar --">
        </form>
        <br><a href="{{rotainterna}}">Voltar</a>
   ''', opcoes = opcoes, rotainterna = rotas[0])

@app.route(rotas [6], methods = ['GET', 'POST'])
def upload():

    if request.method == "POST":
        recebido = request.files['c_arquivo']
        return f"<h3> Upload Feito com sucesso! </h3> <br><a href='{rotas[6]}'>Voltar</a> "
        if not recebido: 
            return f"<h3> Nenhum arquivo enviado! </h3> <br><a href='{rotas[6]}'>Voltar</a> "
            dfAvengers = pd.read_csv(recebido, encoding='latin1')
            conn = sqlite3.connect(f'{caminho_banco}{nomebanco}')
            dfAvengers.to_sql("vingadores,", conn, if_exists= "replace", index=False)
            conn.commit()
            conn.close()

            return f"<h3> Upload Feito com sucesso! </h3> <br><a href='{rotas[6]}'>Voltar</a> "
    return '''
    <h2> Upload da tabela Avengers! </h2>
    <form method ="POST" enctype= "multipart/form-data">
        <!-- Isso é um comentario em HTML -->
        <input type = "file" name= "c_arquivo" accept =".csv">
        <input type = "submit" value= "-- Carregar --">
    </from>

    '''


#inicia o servidor
if __name__ == '__main__':
    app.run(
        debug = config.FLASK_DEBUG,
        host = config.FLASK_HOST,
        port = config.FLASK_PORT
    )
