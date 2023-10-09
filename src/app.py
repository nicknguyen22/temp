from dash import Dash, dcc, html, Input, Output, callback, dash_table
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import date
import pandas as pd

# Fix trading period time
tptime_fix = {
    '0:00':'00:00',  '0:30':'00:30', '1:00':'01:00', '1:30':'01:30',
    '2:00':'02:00',  '2:30':'02:30', '3:00':'03:00', '3:30':'03:30',
    '4:00':'04:00',  '4:30':'04:30','5:00':'05:00', '5:30':'05:30',
    '6:00':'06:00', '6:30':'06:30','7:00':'07:00', '7:30':'07:30',
    '8:00':'08:00', '8:30':'08:30','9:00':'09:00', '9:30':'09:30',
}


app = Dash(__name__,
           external_stylesheets=[
                dbc.themes.BOOTSTRAP, 
                dbc.icons.FONT_AWESOME
                ])
server = app.server
# Loading dataset
df = pd.read_csv('dataframe.csv')
df['Date'] = pd.to_datetime(df['Date'])

dailydf = (df.groupby('Date',as_index=False)
            .agg({
                    'Consumption(kWh)':'sum',
                    'SolarGen(kWh)':'sum',
                    'CI(g/kWh)':'mean',
                    'CE_with_solar(kg)':'sum',
                    'CE_without_solar(kg)':'sum'
                })
        )

def ems_summary_cards(df):
    cards = dbc.Row([
        dbc.Card([
            dbc.CardBody([
                html.H6('Yearly Carbon Emission w/o Solar',style={'textAlign':'center','marginBottom':'15px','font-weight':'bold'}),
                html.H4(f"{(df['CE_without_solar(kg)'].sum()/1000):,.3f} ton",style={'textAlign':'center',
                    'color':'rgb(73,73,73)','font-weight':'bold'})
                ])
            ],style={'width':'290px','marginLeft':'12px'}),

        dbc.Card([
            dbc.CardBody([
                html.H6('Yearly Carbon Emission with Solar',style={'textAlign':'center','marginBottom':'15px','font-weight':'bold'}),
                html.H4(f"{(df['CE_with_solar(kg)'].sum()/1000):,.3f} ton",style={'textAlign':'center',
                    'color':'green','font-weight':'bold'})
                ])
            ],style={'width':'290px','marginLeft':'12px'}),
    ])
    return cards

def main_chart(df):
    fig = make_subplots(rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=('Average Carbon Intensity (g/kWh)',
            'Daily Electricity Consumption & Solar Generation (kWh)',
            'Daily Carbon Emission with and without Solar (kg)'),
        vertical_spacing=0.1,
        row_width=[0.4,0.4,0.2])
    
    fig.add_trace(
        go.Scatter(x=df['Date'], y=(df['CI(g/kWh)']), 
                    name='Average Carbon Intensity (g/kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    line=dict(width=1.5, dash='dot', color='rgba(80, 0, 138, 1)'),
                    hovertemplate = '%{y:,.2f} g/kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Scatter(x=df['Date'], y=(df['SolarGen(kWh)']), 
                    name='Solar Generation(kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    stackgroup='one',
                    line=dict(width=1, color='rgba(252, 108, 5,0.9)'),
                    hovertemplate = '%{y:,.2f} kWh'),row=2,col=1
    )

    fig.add_trace(
        go.Bar(x=df['Date'], y=(df['Consumption(kWh)']), 
                    name='Consumption(kWh)',
                    hoverinfo='x+y',
                    marker_color='rgba(200, 200, 200, 1)',
                    hovertemplate = '%{y:,.2f} kWh'),row=2,col=1
    )

    fig.add_trace(
        go.Bar(x=df['Date'], y=df['CE_without_solar(kg)'], 
                    name='Carbon Emission without Solar(kg)',
                    marker=dict(color='rgba(98, 98, 98, 1)',line = dict(width=0)),
                    hovertemplate = '%{y:,.2f} kg'),row=3,col=1
    )

    fig.add_trace(
        go.Bar(x=df['Date'], y=df['CE_with_solar(kg)'], 
                    name='Carbon Emission with Solar(kg)',
                    marker=dict(color='rgba(155,199,117, 1)',line = dict(width=0)),
                    hovertemplate = '%{y:,.2f} kg'),row=3,col=1
    )

    # Add figure layout
    for n in range (3):
        fig.layout.annotations[n].update(x=0,font_size=14,xanchor ='left',)
    fig.update_layout(
        # title_text= 'Daily ISL2201 Average Spotprice, Electricity Consumption & Solar Generation',
        height = 1000,
        barmode = 'overlay',
        title_yanchor='top',
        hovermode="x unified",
        plot_bgcolor='#FFFFFF',
        margin = dict(r=20,t=20),
        xaxis = dict(tickmode = 'linear',dtick = 'M1'),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1,)
        )
    
    fig.update_yaxes(row=1, col=1, title='Carbon Intensity(g/kWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_yaxes(row=2, col=1, title='Consumption(kWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_yaxes(row=3, col=1, title='Carbon Emission(kg)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_traces(xaxis='x3')
    fig.update_xaxes(showgrid=False, gridwidth=1, title_font_size=12,tickfont=dict(size=12), dtick='M1')

    return fig

def group_charts(df,clk_date):
    fig = make_subplots(rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=('Carbon Intensity (g/kWh)',
            'Electricity Consumption and Solar Generation (kWh)',
            'Carbon Emission with and without Solar (kg)'),
        vertical_spacing=0.1,
        row_width=[0.4,0.4,0.2])

    fig.add_trace(
        go.Scatter(x=df['TP'], y=(df['CI(g/kWh)']), 
                    name='Average Carbon Intensity (g/kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    line=dict(width=1.5, dash='dot', color='rgba(80, 0, 138, 1)'),
                    hovertemplate = '%{y:,.2f} g/kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Scatter(x=df['TP'], y=(df['SolarGen(kWh)']), 
                    name='Solar Generation(kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    stackgroup='one',
                    line=dict(width=1, color='rgba(252, 108, 5,0.9)'),
                    hovertemplate = '%{y:,.2f} kWh'),row=2,col=1
    )

    fig.add_trace(
        go.Bar(x=df['TP'], y=(df['Consumption(kWh)']), 
                    name='Consumption(kWh)',
                    hoverinfo='x+y',
                    marker_color='rgba(200, 200, 200, 1)',
                    hovertemplate = '%{y:,.2f} kWh'),row=2,col=1
    )

    fig.add_trace(
        go.Bar(x=df['TP'], y=df['CE_without_solar(kg)'], 
                    name='Carbon Emission without Solar(kg)',
                    marker=dict(color='rgba(98, 98, 98, 1)',line = dict(width=0)),
                    hovertemplate = '%{y:,.2f} kg'),row=3,col=1
    )

    fig.add_trace(
        go.Bar(x=df['TP'], y=df['CE_with_solar(kg)'], 
                    name='Carbon Emission with Solar(kg)',
                    marker=dict(color='rgba(155,199,117, 1)',line = dict(width=0)),
                    hovertemplate = '%{y:,.2f} kg'),row=3,col=1
    )

    # Add figure layout
    for n in range (3):
        fig.layout.annotations[n].update(x=0,font_size=14,xanchor ='left',)
    fig.update_layout(
        height = 1000,
        barmode = 'overlay',
        title_yanchor='top',
        hovermode="x unified",
        plot_bgcolor='#FFFFFF',
        margin = dict(r=20,t=20),
        xaxis = dict(tickmode = 'linear',dtick = 'M1'),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1,)
        )
    
    fig.update_yaxes(row=1, col=1, title='Carbon Intensity(g/kWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_yaxes(row=2, col=1, title='Consumption(kWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_yaxes(row=3, col=1, title='Carbon Emission(kg)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_traces(xaxis='x3')
    fig.update_xaxes(showgrid=False, gridwidth=1, title_font_size=12,tickfont=dict(size=12))

    return fig

content = html.Div([

    html.H3('Electricity Consumption - Solar Generation',
            style={'text-align':'center'}),
    html.Br(),
    dbc.Row([
            dbc.Col([html.Div(id='summary',children=ems_summary_cards(dailydf))
            ])
        ]),
    html.Br(),
    dbc.Row([  
        dcc.Loading(id='comp_loading',children=
            [
                html.H4('Overview visualisation'),
                dbc.Card(dcc.Graph(id='main-graph', figure=main_chart(dailydf), clickData=None, 
                hoverData=None)
            )],
            type = 'default',
        )
    ]),
    html.Br(),html.Br(),
    dbc.Row([  
        dcc.Loading(id='detail_loading',children=
            [   
                html.H4(id ='d-graph-title',children={}),
                dbc.Card(dcc.Graph(id='detail-graph', figure={}, clickData=None, 
                hoverData=None),
            )],
            type = 'default',
        )
    ]),
])

app.layout = dbc.Container([
    html.H2("Electricity Consumption and Solar System ", style={'font-family':'arial','textAlign':'center'}),
    html.Br(),html.Br(),    
    content
],style={ 'padding':'15px','background-color':'#f5f5f5'},fluid=True)

# Callback
@app.callback(
    Output(component_id='detail-graph', component_property='figure'),
    Output(component_id='d-graph-title', component_property='children'),
    Input(component_id='main-graph', component_property='clickData')
)
def update_group_charts(clk_data):
    if clk_data is None:
        clk_date = df['Date'].min()
        detail_df = df[df['Date']==clk_date]
        fig2 = group_charts(detail_df,clk_date)
        sel_date = str(clk_date).split(' ',1)[0]

        return fig2, f'Visualisation of the {sel_date}'

    else:
        clk_date = clk_data['points'][0]['x']
        detail_df = df[df['Date']==clk_date]
        fig2 = group_charts(detail_df,clk_date)
        sel_date = str(clk_date).split(' ',1)[0]

        return fig2, f'Visualisation of the {sel_date}'

if __name__ == "__main__":
    app.run_server(host='0.0.0.0',port=80,debug=False)