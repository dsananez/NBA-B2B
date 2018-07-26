import NBA
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import io
import base64
import csv

#Archivos a usar para NBA
#base_clientes = pd.read_csv('clientes_pruebas.csv',sep=';')
#ofert = pd.read_csv('listado_campanas.txt', sep=",")
#plataforma = pd.read_csv('modelo_plataforma_cc.txt', sep=",")

#Variables entrada al NBA
#func_obj = None
#tipo_canal = None
#vision_meses = None

#Variables de salida del NBA
#oferta_cuit = pd.DataFrame()
#NBA_ = pd.DataFrame()
#q = pd.DataFrame()
#fact = pd.DataFrame()

app = dash.Dash()
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})
app.config['suppress_callback_exceptions']=True



##Lista de funciones objetivos
func_options = []
func_options.append({'label':'Valor Actual Neto','value':'van'})
func_options.append({'label':'Customer Lifetime Value','value':'ltv'})

##Lista de canales de oferte
canales_options = []
canales_options.append({'label':'Canal OUT','value':'OUT'})
canales_options.append({'label':'Canal IN','value':'IN'})


app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            html.A('Seleccionar los archivos del NBA aquí')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),

    html.Button(
    id='carga-button',
    n_clicks=0,
    children='Cargar archivos',
    style={'fontSize':20}
    ),  # horizontal line,
    html.Div([
        html.P(id='nba_params')
    ]),
    html.Div([
            html.P(id='oferta-picker-1')
    ])

    #html.Div(id='output-data-upload2'),
    #html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])


@app.callback(Output('submit-button3','children'),
             [Input('submit-button3','n_clicks')])
def download_file(n_clicks):
    if n_clicks >= 1:
        dt1.to_csv('base_NBA.csv',sep=';')
        return 'DESCARGADO'
    return 'DESCARGAR NBA'

def parse_contents(contents, filename, date):

    global ofert
    global base_clientes
    global plataforma

    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')),sep=';')
            if 'clientes' in filename:
                base_clientes = df.copy()
                #ok_1 = ok_1 + 1
            elif 'campanas' in filename:
                ofert = df.copy()
                #ok_1 = ok_1 + 1
            elif 'plataforma' in filename:
                plataforma = df.copy()
                #ok_1 = ok_1 + 1
        elif 'txt' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')),sep=',')
            if 'clientes' in filename:
                base_clientes = df.copy()
                #ok_1 = ok_1 + 1
            elif 'campanas' in filename:
                ofert = df.copy()
                #ok_1 = ok_1 +1
            elif 'plataforma' in filename:
                plataforma = df.copy()
                #ok_1 = ok_1 +1
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            if 'clientes' in filename:
                base_clientes = df.copy()
                #ok_1 = ok_1 + 1
            elif 'campana' in filename:
                ofert = df.copy()
                #ok_1 = ok_1 + 1
            elif 'plataforma' in filename:
                plataforma = df.copy()
                #ok_1 = ok_1 + 1
    except Exception as e:
        print(e)
        return html.Div([
            'Hubo un error procesando el/los archivo.'
        ])

    return html.Div([
        html.P(filename),
        #html.H6(datetime.datetime.fromtimestamp(date)),

        # Use the DataTable prototype component:
        # github.com/plotly/dash-table-experiments
        #dt.DataTable(rows=df.to_dict('records')),

        #html.Hr()  # horizontal line,

    ])


def contar_entidades_ok(oferta_entidad,oferta,umbral):
    a = list((oferta_entidad.T)[oferta])
    anis_ok = sum(x > umbral for x in a)

    lista = []
    for i in range(0,len(oferta_entidad.columns)):
        lista.append(oferta_entidad.columns.tolist()[i].split('_')[1])
    unique =list(set(lista))
    count_cuits = 0
    for cuit in unique:
        van_cuits = list(oferta_entidad.T[oferta].filter(like='empresa_'+cuit, axis=0))
        value = sum(x>umbral for x in van_cuits)
        if(value>=1):
            count_cuits += 1

    return anis_ok,count_cuits

def count_anis_ok_sobre_total(oferta,umbral):
    ##Lista de cuit que aceptaron la oferta

    lista= []
    for i in range(0,len(NBA_.columns)):
        lista.append(NBA_.columns.tolist()[i].split('_')[1])
    lista_cuits =list(set(lista))
    ind = (NBA_.T.index)
    lista_a = []
    lista_b = []
    for k in range(0,len(lista_cuits)):
        lista_a.append({'empresa':lista_cuits[k],'total':sum(ind.str.contains('empresa_'+lista_cuits[k], regex=False))})
        lista_b.append({'empresa':lista_cuits[k],'aceptados':sum(NBA_.T[ind.str.contains('empresa_'+lista_cuits[k], regex=False)][oferta]>umbral)})
    return lista_a,lista_b

##CALLBACK PARA ACTUALIZAR ESTADISTICAS EN TEXTO
@app.callback(Output('numero-aceptados','children'),
              [Input('submit-button2','n_clicks')],
              [State('oferta-picker', 'value'),
               State('umbral-picker','value')])
def update_aceptados(n_clicks,oferta,umbral):
    #cant_cuits_ok = contar_entidades_ok(oferta_cuit,oferta,umbral)
    [cant_anis_ok,cant_cuits_ok] = contar_entidades_ok(NBA_,oferta,umbral)
    porcentaje = ((((fact[oferta].tolist())[-1])-((fact['sin oferta'].tolist())[-1]))/((fact['sin oferta'].tolist())[-1]))*100
    if n_clicks>=1:
        return [html.H1('CUITS AFECTADOS: '+str(cant_cuits_ok)+'/'+str(len(oferta_cuit.columns))),
                html.H1('ANIS AFECTADOS: '+str(cant_anis_ok)+'/'+str(len(NBA_.columns))),
                html.Hr(),
                html.H1('Facturacion esperada: $ '+str(int((fact[oferta].tolist())[-1]))),
                html.H3('Porcentaje respecto de no hacer nada: '+str(int(porcentaje))+'%')]


##CALLBACK DEL GRAFICO DE BARRAS
@app.callback(Output('bar-output','figure'),
              [Input('submit-button2','n_clicks')],
              [State('oferta-picker', 'value'),
               State('umbral-picker','value')])
def update_barchart(n_clicks,oferta,umbral):

    [lista_a,lista_b] = count_anis_ok_sobre_total(oferta,umbral)
    if(len(lista_a)<=5):
        a = pd.DataFrame(lista_a).sample(len(lista_a))
        b = pd.DataFrame(lista_b).sample(len(lista_a))
    else:
        a = pd.DataFrame(lista_a).sample(5)
        b = pd.DataFrame(lista_b).sample(5)

    trace1 = go.Bar(
        y=a['empresa'].tolist(),
        x=a['total'].tolist(),
        name='Total de ANIS',
        orientation = 'h',
        marker = dict(
            color = 'rgba(246, 78, 139, 0.6)',
            line = dict(
                color = 'rgba(246, 78, 139, 1.0)',
                width = 3)
        )
    )
    trace2 = go.Bar(
        y=b['empresa'].tolist(),
        x=b['aceptados'].tolist(),
        name='Total ANIS que superan el umbral',
        orientation = 'h',
        marker = dict(
            color = 'rgba(58, 71, 80, 0.6)',
            line = dict(
                color = 'rgba(58, 71, 80, 1.0)',
                width = 3)
        )
    )

    data = [trace1, trace2]
    layout = go.Layout(title='ANIS ACEPTADOS POR CUIT',
        hovermode='closest',
        barmode='group'
    )

    fig = go.Figure(data=data, layout=layout)

    return fig


##CALLBACK PARA MOSTRAR LOS TABS
@app.callback(Output('oferta-picker-1', 'children'),
    [Input('submit-button','n_clicks')],
    [State('func-picker', 'value'),
     State('canal-picker','value'),
     State('meses-picker','value'),
     State('umbral-picker','value')])
def update_tabs_section(n_clicks,func,canal,meses,umbral):
    global oferta_cuit
    global NBA_
    global q
    global fact



    if n_clicks>=1:
        [oferta_cuit,NBA_,q,fact] = NBA.NBA(base_clientes,ofert,plataforma,func,canal,meses,umbral)

        return html.Div([dcc.Tabs(
                        tabs=[
                            {'label':'Resultados NBA','value':1},{'label': 'Evaluación oferta', 'value':2}
                        ],
                        id='tabs'
                        ),
                        html.Div(id='tab-output')
                        ], style={
                                    'width': '100%',
                                    'fontFamily': 'Sans-Serif',
                                    'margin-left': 'auto',
                                    'margin-right': 'auto'
                                }
                       )


@app.callback(Output('tab-output', 'children'), [Input('tabs', 'value')])
def display_content(value):

    if value == 2:

        oferta_options = []
        for oferta in ofert['id_oferta'].unique():
            oferta_options.append({'label':oferta,'value':oferta})

        return html.Div([dcc.Dropdown(id='oferta-picker',options=oferta_options,value=ofert['id_oferta'][1]),
                        html.Button(
                        id='submit-button2',
                        n_clicks=0,
                        children='OK',
                        style={'fontSize':20}
                        ),html.Div([
                                    html.Div([dcc.Graph(id='graph1')],className='six columns',style={'margin-top': '30'}),
                                    html.Div([dcc.Graph(id='graph2')],className='six columns',style={'margin-top': '30'})
                                    ]),
                            html.Div([
                                  html.Div([html.P(id='numero-aceptados')],className='six columns',style={'margin-top': '30'}),
                                  html.Div([dcc.Graph(id='bar-output')],className='six columns',style={'margin-top': '0'})
                            ])])
    elif value == 1:
        global dt1

        podio = []
        for i in range(0,len(NBA_.index)):
            podio.append(i+1)

        dt1 = pd.DataFrame(columns=podio,index=NBA_.columns)

        for linea in dt1.index.tolist():
            lista = (NBA_[linea].sort_values(ascending=False)).index.tolist()
            for i in range(0,len(dt1.columns)):
                dt1.loc[linea,i+1] = lista[i]

        lista_cuits = []
        lista_anis = []
        for i in range(0,len(dt1.index)):
            lista_cuits.append(dt1.index.tolist()[i].split('_')[1])
            lista_anis.append(dt1.index.tolist()[i].split('_')[2])


        dt1['linea'] = (lista_anis)
        dt1['cuit'] = (lista_cuits)
        dt1 = dt1[['cuit','linea',1,2,3]]

        return  [html.Div([html.H4('MEJOR OFERTA POR LINEA',style={'text-align':'center'}),html.Div([dt.DataTable(
                            rows=dt1.to_dict('records'),

                            # optional - sets the order of columns
                            columns=(dt1.columns),
                            row_selectable=False,
                            filterable=True,
                            sortable=False,
                            #selected_row_indices=[],
                            id='datatable-nba'
                            )],style={'padding':'10px'}),
                               html.P(html.Button(
                                        id='submit-button3',
                                        n_clicks=0,

                                        style={'fontSize':20,'text-align':'right','align':'right'}
                                        ),style={'text-align':'right','align':'right'})
                            ], className="container")]



##CALLBACK GRAFICO FACTURACION ACUMULADA
@app.callback(
    Output('graph1', 'figure'),
    [Input('submit-button2','n_clicks')],
    [State('oferta-picker', 'value')])
def update_fact(n_clicks,oferta):

    if n_clicks>=1:
        data = [{
        'x': fact.index,
        'y': fact[oferta],
        'name': oferta},
        {
        'x': fact.index,
        'y': fact['sin oferta'],
        'name': 'sin oferta'
        }]
        layout = go.Layout(
        title='Facturacion acumulada mes a mes',
        hovermode='closest'
        )

        return go.Figure(data=data, layout=layout)

##CALLBACK GRAFICO DE Q CLIENTES
@app.callback(
    Output('graph2', 'figure'),
    [Input('submit-button2','n_clicks')],
    [State('oferta-picker', 'value')])
def update_q(n_clicks,oferta):

    if n_clicks>=1:
        data = [{
        'x': q.index,
        'y': q[oferta],
        'name': oferta},
        {
        'x': q.index,
        'y': q['sin oferta'],
        'name': 'sin oferta'
        }]
        layout = go.Layout(
        title='Cantidad lineas mes a mes',
        hovermode='closest'
        )

        return go.Figure(data=data, layout=layout)

#CALLBACK SALIDA DE PARAMETROS
@app.callback(Output('nba_params','children'),
             [Input('carga-button','n_clicks')])
def update_nba(n_clicks):
    if n_clicks >=1:
        ##Lista de Ofertas para selector


        return [dcc.Dropdown(id='func-picker',options=func_options,value=func_options[0]['value']),
                dcc.Dropdown(id='canal-picker',options=canales_options,value=canales_options[0]['value']),
                dcc.Input(id='meses-picker',placeholder='Ingresar cantidad de meses de visión',type='number'),
                dcc.Input(id='umbral-picker',placeholder='Ingresar umbral de decisión',type='number'),
                html.Button(
                id='submit-button',
                n_clicks=0,
                children='Correr',
                style={'fontSize':20}
                )
                #html.H1(id='mensaje-out')
                ]


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename'),
               Input('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(Output('upload-data','children'),
             [Input('carga-button','n_clicks')])
def update_file(n_clicks):
    if (n_clicks >=1):
        return html.Div([html.A('Archivos cargados')])
    else:
        return html.Div([
            html.A('Seleccionar los archivos del NBA aquí')
        ])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})



if __name__ == '__main__':
    app.run_server()
