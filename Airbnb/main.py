import pandas as pd
import numpy as np
import plotly.graph_objs as go

folder = 'C:/Users/noturno/Desktop/Python 2 - Gustavo/Airbnb/'
t_ny = 'ny.csv'
t_rj = 'rj.csv'

def standartize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    lat_candidates = ['lat','latidute','Latitude','LAT','Lat','LATITUDE']
    lon_candidates = ['lon','LON','Lon','Longitude','LONGITUDE', 'Long', 'Lng']
    cost_candidates = ['custo','valor','coust','cost','price','preço']
    name_candidates = ['nome', 'name', 'titulo', 'title', 'local', 'place', 'descricao']

    def pick(colnames, candidates):
        #colnames: lista de nomes das colunas da tabela
        #candidates: lista de possiveis nomes das colunas a serem encontradas
        for c in candidates:
        #percorre cada candidato (c) dentro da lista de candidatos
            if c in colnames:
            # se o candidato for exatamente igual a um dos nomes em colnames (tabela)
                return c
                # retorna esse candidato imediatamente
        for c in candidates:
            #se nao encontrou a correspondencia
            #percorre novamente cada coluna
            for col in colnames:
                #aqui percorre cada nome de coluna
                if c.lower() in col.lower():
                   #apenas com minusculas 
                    return col
                    # retorna a coluna imediatamente       
        return None
        #se não encontrou nenhuma coluna, nem exato nem parcial, retorna none