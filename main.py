import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.io import show, curdoc
from bokeh.plotting import figure
from bokeh.models.widgets import Select, RangeSlider
from bokeh.layouts import column, grid, row
from bokeh.server.server import Server


def bkapp(doc):
    dff = None

    def banco(estado, ano_min, ano_max, produto):
        global dff
        df = pd.read_csv('2004-2019.tsv', sep='\t')
        df['mes_ano'] = list(zip(df['MÊS'], df['ANO']))
        df2 = df[['ESTADO', 'PRODUTO', 'PREÇO MÉDIO REVENDA', 'MÊS', 'ANO',
                  'mes_ano']]
        df3 = df2[(df2['ESTADO'] == estado) & (df2['ANO'] >= ano_min) &
                  (df2['ANO'] <= ano_max) & (df2['PRODUTO'] == produto)]
        df4 = df3.groupby(['MÊS', 'ANO'])['PREÇO MÉDIO REVENDA'].mean().reset_index(name='preço')
        df4 = df4.sort_values(by=['ANO', 'MÊS'])
        df4['x'] = range(len(df4))
        dff = df4
        return ColumnDataSource(data=df4)

    def datas(df):
        dff = df
        meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAIO', 'JUN',
                 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
        numeros = range(1, 13)
        dic = dict(zip(numeros, meses))
        datas = [x for x in list(zip(dff['MÊS'], dff['ANO']))]
        datas2 = [list(x) for x in datas]
        datas3 = [dic[x[0]] + '/' + str(x[1]) for x in datas2]
        return datas3

    def plot(source):
        global dff
        p = figure(x_axis_label='Mês/Ano', y_axis_label='Preço',
                   plot_width=800, plot_height=300)
        p.line(x='x', y='preço', source=source)
        p.xaxis.major_label_overrides = dict(zip(range(len(dff)), datas(dff)))
        return p

    def plot2(source):
        global dff
        p = figure(x_axis_label='Mês/Ano', y_axis_label='Preço',
                   plot_width=800, plot_height=300)
        p.line(x='x', y='preço', source=source)
        p.xaxis.major_label_overrides = dict(zip(range(len(dff)), datas(dff)))
        return p

    def update(attr, old, new):
        estado = select_estado.value
        estado2 = select_estado2.value
        produto = select_produto.value
        produto2 = select_produto2.value
        ano_min, ano_max = range_slider.value

        novo_banco = banco(estado, ano_min, ano_max, produto)
        novo_banco2 = banco(estado2, ano_min, ano_max, produto2)
        source.data.update(novo_banco.data)
        source2.data.update(novo_banco2.data)

    df_ = pd.read_csv('2004-2019.tsv', sep='\t')

    produtos = list(np.unique(df_['PRODUTO']))
    estados = list(np.unique(df_['ESTADO']))
    select_estado = Select(title='Estado:', value='PERNAMBUCO',
                           options=estados)
    select_estado2 = Select(title='Estado:', value='ALAGOAS',
                            options=estados)
    select_produto = Select(title='Produto:', value='GASOLINA COMUM',
                            options=produtos)
    select_produto2 = Select(title='Produto:', value='GASOLINA COMUM',
                             options=produtos)
    range_slider = RangeSlider(start=2004, end=2019, value=(2004, 2019), step=1,
                               title='Anos')


    select_estado.on_change('value', update)
    select_produto.on_change('value', update)
    select_estado2.on_change('value', update)
    select_produto2.on_change('value', update)
    range_slider.on_change('value', update)

    source = banco(select_estado.value, 2004, 2019, select_produto.value)
    source2 = banco(select_estado2.value, 2004, 2019, select_produto2.value)
    plot = plot(source)
    plot2 = plot2(source2)

    doc.add_root(row(column(select_estado, select_estado2, select_produto,
                 select_produto2, range_slider),
                 column(plot, plot2)))
    curdoc().title = 'Preço do combustivel'

server = Server({'/': bkapp}, num_procs=1)
server.start()

if __name__ == '__main__':
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
