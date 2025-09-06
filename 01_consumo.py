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
        <li> <a href="{rotas[7]}">Apagar tabela</a>  </li>
        <li> <a href="{rotas[8]}">Ver tabela</a>  </li>
        <li> <a href="{rotas[9]}">V.A.A</a>  </li>
    </ul>
'''

#iniciar o flask
app = Flask(__name__)

def getDbConnect():
    conn = sqlite3.connect(f'{caminho_banco}{nomebanco}')
    conn.row_factory = sqlite3.Row
    return conn
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

            return f"<h3> Upload Feito com sucesso! </h3> <br><a href='{rotas[0]}'>Voltar</a> "
    return '''
    <h2> Upload da tabela Avengers! </h2>
    <form method ="POST" enctype= "multipart/form-data">
        <!-- Isso é um comentario em HTML -->
        <input type = "file" name= "c_arquivo" accept =".csv">
        <input type = "submit" value= "-- Carregar --">
    </from>

    '''
@app.route('/apagar_tabela/<nome_tabela>', methods=['GET'])
def apagarTabela(nome_tabela):
    conn = getDbConnect()
    # realiza o apontamento para o banco que será manipulado
    cursor = conn.cursor()
    #usaremos o try except para controlar possiveis erros
    # confirmar antes se a tabela existe
    cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{nome_tabela}'")
    # pega o resultado da cntagem(0 se nao existir e 1 se existir)
    existe = cursor.fetchone()[0] 
    if not exists :
        conn.close()
        return "Tabela não encontrada"

    try:
        cursor.execute(f'DROP TABLE "{nome_tabela}"')
        conn.commit()
        conn.close()
        return f"Tabela {nome_tabela} apagada com ssuceso!"

    except Exception as erro:
        conn.close()
        return f"Não foi possivel apagar a tabela erro: {erro}"

@app.route(rotas[8], methods=["POST","GET"])
def ver_tabela():
    if request.method == "POST":
        nome_tabela = request.form.get('tabela')
        if nome_tabela not in ['bebidas','vingadores']:
            return f"<h3>Tabela {nome_tabela} não encontrada!</h3><br><a href={rotas[8]}>Voltar</a>"

        conn =getDbConnect()
        df = pd.read_sql_query(f"SELECT * from {nome_tabela}", conn)
        conn.close()
        tabela_html = df.to_html(classes='table table-striped')
        return f'''
            <h3>Conteudo da tabela {nome_tabela}:</h3>
            {tabela_html}
            <br><a href={rotas[8]}>Voltar</a>
        '''

    return render_template_string('''
        <marquee>Selecione a tabela a ser visualizada:</marquee>
        <form method="POST">
            <label for="tabela">Escolha a tabela abaixo:</label>
            <select name="tabela">
                <option value="bebidas">Bebidas</option>
                <option value="vingadores">Vingadores</option>
            </select>
       
        <hr>
        <input type="submit" value="Consultar Tabela">
        </form>
        <br><a href={{rotas[0]}}>Voltar</a>
    ''', rotas=rotas)

@app.route(rotas[7], methods=['POST', 'GET'])
def apagarV2():

    if request.method == "POST":
        nome_tabela = request.form.get('tabela')
        if nome_tabela not in ['bebidas', 'vingadores']:
            return f"<h3>Tabela {nome_tabela} não encontrada!</h3><br><a href={rotas[7]}>Voltar</a>"
    confirmacao = request.form.get('confirmacao')
    conn = getDbConnect()
    if confirmacao == "Sim":
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?',(nome_tabela,))
            if cursor.fetchone() is None:
                return f"<h3>Tabela {nome_tabela} não encontrada no banco de dados!</h3><br><a href={rotas[7]}>Voltar</a>"
            cursor.execute(f'DROP TABLE IF EXISTS "{nome_tabela}"')
            conn.commit()
            conn.close()
            return f"<h3>Tabela {nome_tabela} excluida com suscesso! </h3><br><a href={rotas[7]}>Voltar</a>"
            
        except Exception as erro:
            conn.close()
            return f"<h3>Erro ao apagar a tabela {nome_tabela} Erro: {erro} </h3><br><a href={rotas[7]}>Voltar</a>"


    return f'''
    <html>
        <head>
        <title><marquee> CUDADO! </marquee></title>
    </head>
    <body>
    <h2> Selecione a tabela para apagar  </h1>
    <form method="POST"    id="formApagar">
        <label for="tabela"> Escolha na tabela abaixo </label>
            <select name="tabela" id="tabela">
                <option value="bebidas">Bebidas</option>
                <option value="vingadores">Vingadores</option>
            </select>
        <input type="hidden" name="confirmacao" value="" id="confirmação">
        <input type="submit" value="-- Apagar! --" onclick="return confirmarExclusao();">

      </form>
      <br><a href={{rotas[0]}}>Voltar</a>
       <script type="text/javascript">
        function confirmarExclusao
        var ok = confirm('Tem certeza de que deseja apagar a tabela selecionada');
        if(ok) {{
            document.getElementById('confirmacao').value = 'Sim';
            return true;
        }}
        else {{
            document.getElementById('confirmacao').value - 'Não';
            return false;
        }}      
       </script>
        </body>
        </html>    
    '''
@app.route(rotas[9], methods = ['GET', 'POST'])
def vaa_mortes_consumo():
    metricas_beb = {
        "Total (L de Alcool)":"total_litres_of_pure_alcochol",
        "Cerveja (Doses)":"bear_servings",
        "Destilados (Doses)":"spirit_servings",
        "Vinhos(Doses)":"wine_servings"
    } 

    if request.method == "POST":
        met_beb_key = request.form.get("metrica_beb") or "Total (L de Alcool)"
        met_beb = metricas_beb.get(met_beb_key, "total_litres_of_pure_alcochol")

        #semente opcional para reproduzir a mesma distribuição de paises nos vingadores
        try:
            semente = int(request.form.get("semente"))

        except:
            semente = 42
        sementeAleatoria = random.Random(semente) #gera o valor aleatorio baseado na semente escolhida

    #le os dados do sql
    with getDbConnect() as conn:
        dfA = pd.read_sql_query('SELECT * FROM vingadores', conn)
        dfB = pd.read_sql_query('SELECT country, beer_servings, spirit_servings, wine_servings, total_litres_of_pure_alcohol FROM bebidas', conn)

    # ---- Morte dos vingadores
    # estrategia: somar colunas que contenha o death como true (case-insensitie)
    # contamos não-nulos como 1, ou seja, death1 tem True? vale 1, caso contrario 0

    death_cols = [c for c in dfA.columns if "death" in c.lower()]
    if death_cols:
        dfA["Mortes"] = dfA[death_cols].notna().astype(int).sum(axis=1)
    elif "Deaths" in dfA.columns:
        #fallback
        dfA["Mortes"] = pd.to_numeric(df["Deaths"], errors="coerce").fillna(0).astype(int)

    else: 
        dfA["Mortes"] = 0

    if "Name/Alias" in dfA.columns:
        col_name = "Name/Alias"
    elif "Name" in dfA.columns:
        col_name = "Name"
    elif "Name" in dfA.columns:
        col_name = "Alias"

    else:
        possivel_texto = [c for c in dfA.columns if dfA[c].dtype == "object"]
        col_nome = possivel_texto[0] if possivel_texto else dfA.columns[0]

    dfA.rename(columns={col_name: "Personagem"}, inplace=True)

    # ------- sortear um pais para cada vingador
    paises = dfB["country"].dropna().astype(str).to_list()
    if not paises:
        return f"<h3>Não há paises na tabela de bebidas!</h3><a href= {{rotas[9]}}>Voltar</a>"

    dfA["Pais"] = [sementeAleatoria.choice(paises) for _ in range(len(dfA))]

    dfB_cons = dfB[["country", met_beb]].rename(columns={
        "contry":'pais',
        met_beb: "consumo"
    })
    base = dfA[["Personagem", "Mortes","Pais"]].merge(dfB_cons, on="Pais", how="left")

    #filtar apenas linhas validas
    base = base.dropna=(subset==['consumo'])
    base["Mortes"] = pd.to_numeric(base["Mortes"], errors="coerce").fillna(0).astype(int)
    base = base[base["Mortes"] >= 0]
    #correlacao (se possivel)
    corr_txt = ""
    if base['consumo'].notna().sum() >= 3 and base["Mortes"].notna().sum() >= 3:
        try:
            corr = base["consumo"].corr(base["Morte"])
            corr_txt = f'• r = {corr:.3f}'
        except: Exception
        pass

    #------------ GRAFICO SCATTER 2D: CONSUMO X MORTES (COR = PAIS) ------
    fig2d = px.Scatter(
        base,
        x = "consumo",
        y = "mortes",
        color = "pais",
        hover_name="personagem",
        hover_data = { 
        "pais":True,
        "consumo": True,
        "mortes": True
        },
        title = f"Vingadores - Mortes VS consumo de alcool do pais({met_beb_key}){corr_txt}"

    )
    fig2d.update_layout(
        xaxis_title = f"{met_beb_key}",
        yaxis_title = "Mortes (contagem)",
        margin = dict(l=40, r=20, t=70, b=40)

    )
    return (
        "<h3> --- Grafico 2D ---- </h3>",
        fig2d.to_html(full_html=False)
        + "<hr>"
        + "<h3> --- Grafico 3D --- </h3>"
        + "<p> Em Breve </p>"
        + "<hr>"
        + "<h3> ----- preview dos dados ---- </h3>"
        + "<p> Em Breve </p>"
        + "<hr>"
        + f"<a href ={rotas[9]}>Voltar</a>"
        +"<br>"
        + f"<a href ={rotas[0]}>Menu Inicial</a>"
    ) 


    return render_template_string('''
    <style>
   
    body {
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f4f6f8;
    color: #333;
    line-height: 1.6;
}


form {
    max-width: 600px;
    margin: 40px auto;
    padding: 30px;
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}


h2 {
    text-align: center;
    color: #2c3e50;
    margin-top: 40px;
}


label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #34495e;
}


select,
input[type="number"] {
    width: 100%;
    padding: 10px 12px;
    margin-bottom: 20px;
    border: 1px solid #ccc;
    border-radius: 6px;
    background-color: #fefefe;
    font-size: 1rem;
}


input[type="submit"] {
    width: 100%;
    padding: 12px;
    background-color: #2980b9;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

input[type="submit"]:hover {
    background-color: #1f6391;
}


p {
    max-width: 700px;
    margin: 20px auto;
    padding: 0 20px;
    color: #555;
    text-align: center;
}


a {
    display: block;
    text-align: center;
    margin-top: 20px;
    color: #2980b9;
    text-decoration: none;
    font-weight: bold;
}

a:hover {
    text-decoration: underline;
}


@media (max-width: 600px) {
    form {
        margin: 20px;
        padding: 20px;
    }
}
    
    </style>
    
    <h2> V.A.A - Pais X Consumo X Mortes </h2>
        <form method="POST">
            <label for="metricas_beb"> metrica de consumo </label>
            <select name="metricas_beb" id="metricas_beb>
                {% for metricas in metricas_beb.keys() %}<opition value= "{{metricas}}"> {{metricas}} </ option>
                
                {% endfor %}

            </select>
            <br><br>
            <label for="semente"> <b>Semente: </b> (<i>opcional, p/ reprodutibilidade</i>) </label>
            <input type="number" name="semente" id="semente" value="42">

            <br><br>
            <input type="submit" value="-- Gerar Grafico --">

        </form>
    
        <p>
            Esta visão sorteia um pais de cada vingador, soma as mortes dos personagens (Usando todas as colunas que contenham Death) e anexa o consumo de alcool do pais, ao fim pilota um scatter 2d e 3d
            </p>
            <br>
            <a href= {{rotas[0]}}>Voltar</a>
    ''', metricas_beb = metricas_beb, rotas=rotas)

#inicia o servidor

if __name__ == '__main__':
    app.run(
        debug = config.FLASK_DEBUG,
        host = config.FLASK_HOST,
        port = config.FLASK_PORT
    )
    