#importacion de librerias
mport pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output


#enlazar mi drive con colab
from google.colab import drive
drive.mount('/content/drive')

# Ajusta la ruta  archivo
df = pd.read_csv('/content/drive/MyDrive/data.csv')
df.head()

#crear el dashboard

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])  # puedes probar también FLATLY o SANDSTONE
app.title = "Riesgo Crediticio"

# Definiendo mis layout (estructura visual Columnas y filas)
app.layout = dbc.Container([
    dbc.Row([html.H1("Dashboard de riesgo crediticio")]),

    # Tarjeta con filtros
    dbc.Card([
        dbc.CardHeader("Filtros"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Zona:"),
                    dcc.Dropdown(
                        id='selector_zona',
                        options=[{'label': z, 'value': z} for z in df['zona'].unique()],
                        value=df['zona'].unique()[0]
                    )
                ], md=6),
                dbc.Col([
                    html.Label("Nivel de ahorro:"),
                    dcc.Dropdown(
                        id='selector_ahorro',
                        options=[{'label': a, 'value': a} for a in df['nivel_ahorro'].unique()],
                        value=df['nivel_ahorro'].unique()[0]
                    )
                ], md=6),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("Edad:"),
                    dcc.RangeSlider(
                        id='selector_edad',
                        min=int(df['edad'].min()),
                        max=int(df['edad'].max()),
                        value=[int(df['edad'].min()), int(df['edad'].max())],
                        step=1
                    )
                ], md=12),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("Clasificación SBS:"),
                    dbc.Checklist(
                        id='selector_sbs',
                        options=[{'label': c, 'value': c} for c in df['clasif_sbs'].unique()],
                        value=[df['clasif_sbs'].unique()[0]],
                        inline=True
                    )
                ], md=12),
            ]),
            dbc.Row([
                dbc.Button("Aplicar filtros", color="secondary", className="me-2"),
                dbc.Button("Resetear", color="dark")
            ])
        ])
    ], className="mb-4"),

    # Gráficas
    dbc.Row([
        dbc.Col([dcc.Graph(id='grafica_ingreso')], md=6),
        dbc.Col([dcc.Graph(id='grafica_score')], md=6)
    ])
])

#callbacks logica de actualizacion

@app.callback(
    [Output('grafica_ingreso', 'figure'),
     Output('grafica_score', 'figure')],
    [Input('selector_zona', 'value'),
     Input('selector_ahorro', 'value'),
     Input('selector_edad', 'value'),
     Input('selector_sbs', 'value')]
)
def actualizar(zona, ahorro, rango_edad, clasif_sbs):
    clasif_sbs = clasif_sbs if isinstance(clasif_sbs, list) else [clasif_sbs]

    df_filtrado = df[
        (df['zona'] == zona) &
        (df['nivel_ahorro'] == ahorro) &
        (df['edad'] >= rango_edad[0]) &
        (df['edad'] <= rango_edad[1]) &
        (df['clasif_sbs'].isin(clasif_sbs))
    ]

    if df_filtrado.empty:
        return px.bar(title="Sin datos"), px.scatter(title="Sin datos")

    fig_ingreso = px.bar(df_filtrado, x='edad', y='ingreso', color='nivel_ahorro',
                         title='Ingreso por edad y nivel de ahorro',
                         template="plotly_white")  # estilo sobrio
    fig_score = px.scatter(df_filtrado, x='deuda_sf', y='score', color='clasif_sbs',
                           size='ingreso', hover_data=['nivel_educ'],
                           title='Score vs Deuda',
                           template="plotly_white")
    return fig_ingreso, fig_score

#ejecutar la visual de una manera externa

app.run_server(mode="external")