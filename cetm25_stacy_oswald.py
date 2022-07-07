import calendar
import pandas as pd
import plotly.express as px  
import plotly.graph_objects as go
import dash
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  
from pandas.io.json import json_normalize
import json
from geojson_rewind import rewind

#Colour Scheme Hex Value Key
#ffa600 - orange
#003f5c - blue
#bc5090 - purple

app = Dash(__name__)

colors = {
    'background': '#ffffff',
    'text': '#003f5c'
}

# -- Import and clean data (importing csv into pandas)

# nhse_total_deaths_by_region.csv Reference: Greater London Authority. (2021) nhse_total_deaths_by_region.csv - data.gov.uk. 
#             [online] Data.gov.uk. Available at: https://data.gov.uk/dataset/43b2334a-6970-4e71-a27a-630dc4901e04/coronavirus-covid-19-deaths [Accessed 3 December 2021].
init_df = pd.read_csv("nhse_total_deaths_by_region.csv", parse_dates=['date'], dayfirst=True)
init_df['month'] = pd.DatetimeIndex(init_df['date']).month
init_df['month'] = init_df['month'].apply(lambda x: calendar.month_name[x])

df = init_df.groupby(['month', 'nhs_england_region'])[['new_deaths_with_positive_test', 'new_deaths_without_positive_test', 'new_deaths_total',
                        'cumulative_deaths_with_positive_test', 'cumulative_deaths_without_positive_test', 'cumulative_deaths_total']].sum()
df.reset_index(inplace=True)

df2 = init_df.groupby(['date', 'month'])[['new_deaths_with_positive_test', 'new_deaths_without_positive_test', 'new_deaths_total', 
                        'cumulative_deaths_with_positive_test', 'cumulative_deaths_without_positive_test', 'cumulative_deaths_total']].sum()
df2.reset_index(inplace=True)

def map_values(row, values_dict):
    return values_dict[row]

#set up the geographical dataframe and geoJSON file   
geo_df = init_df.copy()
geo_df["nhser20cd"] = geo_df["nhs_england_region"]
values_dict = {"London": "E40000003", "South East":"E40000005", "South West": "E40000006", "East Of England": "E40000007", "Midlands": "E40000008", "North East And Yorkshire": "E40000009", "North West": "E40000010"}
geo_df["nhser20cd"] = geo_df["nhs_england_region"].apply(map_values, args = (values_dict,))

# NHS_England_Regions_(April_2020)_Boundaries_EN_BGC.geojson Reference: Office for National Statistics (2020) Data.gov.uk: NHS England Regions (April 2020) Boundaries EN BGC - data.gov.uk. 
#                 Available from: https://data.gov.uk/dataset/66a7bb97-3da6-4e19-975b-1f0784909cd5/nhs-england-regions-april-2020-boundaries-en-bgc [Accessed 28 December 2021].
with open('NHS_England_Regions_(April_2020)_Boundaries_EN_BGC.geojson') as data_file:    
    region_json = json.load(data_file)
region_json = rewind(region_json, rfc7946=False)


#External Stylesheet Reference: Parmer, C., 2022. Dash Styleguide. [online] codepen.io. 
#	       Available at: <https://codepen.io/chriddyp/pen/bWLwgP> [Accessed 5 January 2022].
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

#define the app layout
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

     html.H1("COVID-19 Death Data", style={"textAlign":"center",
                                    'color': colors['text'], 'font-weight': 'bold'}),
                                    
     html.P("This is a prototype product and only contains data for August, September and October 2021 currently.", style={'color': colors['text'], 'font-weight': 'bold'}),
     
     html.Hr(),
     
     html.H2("National Data", style={"textAlign":"center", 'color': colors['text'], 'font-weight': 'bold'}),
     
     html.P("Choose the desired month:", style={'color': colors['text']} ),
     
     html.Div(html.Div([
            dcc.Dropdown(id='month', clearable = False, 
            options=[
             {"label": "January", "value": "January"},
             {"label": "February", "value": "February"},
             {"label": "March", "value": "March"},
             {"label": "April", "value": "April"},
             {"label": "May", "value": "May"},
             {"label": "June", "value": "June"},
             {"label": "July", "value": "July"},
             {"label": "August", "value": "August"},
             {"label": "September", "value": "September"},
             {"label": "October", "value": "October"},
             {"label": "November", "value": "November"},
             {"label": "December", "value": "December"}],
             multi=False,
             value="August",
             style={'width': "40%", 'color': colors['text']})
        ])),
     
     html.Div(id="graph_div_1", children=[]),
     
     html.Hr(),
     
     html.H2("Regional Data", style={"textAlign":"center", 'color': colors['text'], 'font-weight': 'bold'}),
     
     html.P("Choose the desired region and month:",  style={'color': colors['text']}),
     
     html.Div(
     className = "row", children = [
        html.Div(className = 'two columns', children = [
        dcc.Dropdown(id='nhs_england_region', clearable = False, 
            options=[{'label': x, 'value': x} for x in
                df["nhs_england_region"].unique()],
            value="London")]),
        html.Div(className = 'two columns', children = [
            dcc.Dropdown(id='month2', clearable = False, 
            options=[
             {"label": "January", "value": "January"},
             {"label": "February", "value": "February"},
             {"label": "March", "value": "March"},
             {"label": "April", "value": "April"},
             {"label": "May", "value": "May"},
             {"label": "June", "value": "June"},
             {"label": "July", "value": "July"},
             {"label": "August", "value": "August"},
             {"label": "September", "value": "September"},
             {"label": "October", "value": "October"},
             {"label": "November", "value": "November"},
             {"label": "December", "value": "December"}],
             multi=False,
             value="August")])]),
        
    html.Div(id="graph_div_2", children=[]),
 ])

# Create the callback
@app.callback(Output(component_id = "graph_div_1", component_property = "children"),
                Input(component_id = "month", component_property = "value"),
    )

def create_graphs(chosen_month):

    #Regional bar chart
    region_df = df.copy()
    region_df = region_df[region_df["month"] == chosen_month]
    region_fig = px.bar(
        data_frame=region_df,
        x = 'nhs_england_region',
        y = 'new_deaths_total',
        labels={'nhs_england_region':'NHS England Region',
                'new_deaths_total':'Number of Deaths'},
        title = 'Total Monthly New Deaths by Region',
        template='seaborn', color_discrete_sequence=["#bc5090"]
    )
    region_fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
    )
    region_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    region_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    
    #Total new deaths line chart
    month_new_death_df = df2.copy()
    month_new_death_df = month_new_death_df[month_new_death_df["month"] == chosen_month]
    month_new_death_line = px.line(
        data_frame=month_new_death_df,
        x = 'date',
        y = 'new_deaths_total',
        labels={'date':'Date',
                'new_deaths_total':'Number of Deaths'},
        title = 'Total Daily New Deaths',
        template='seaborn', color_discrete_sequence=["#bc5090"]
    )
    month_new_death_line.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
    )
    month_new_death_line.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    month_new_death_line.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    
    #New deaths with positive test line chart
    month_new_pos_death_df = df2.copy()
    month_new_pos_death_df = month_new_pos_death_df[month_new_pos_death_df["month"] == chosen_month]
    month_new_pos_death_line = px.line(
        data_frame=month_new_pos_death_df,
        x = 'date',
        y = 'new_deaths_with_positive_test',
        labels={'date':'Date',
                'new_deaths_with_positive_test':'Number of Deaths'},
        title = 'Daily New Deaths with a Postive Test',
        template='seaborn', color_discrete_sequence=["#bc5090"]
    )
    month_new_pos_death_line.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
    )
    month_new_pos_death_line.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    month_new_pos_death_line.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    
    #New deaths without positive test line chart
    month_new_neg_death_df = df2.copy()
    month_new_neg_death_df = month_new_neg_death_df[month_new_neg_death_df["month"] == chosen_month]
    month_new_neg_death_line = px.line(
        data_frame=month_new_neg_death_df,
        x = 'date',
        y = 'new_deaths_without_positive_test',
        labels={'date':'Date',
                'new_deaths_without_positive_test':'Number of Deaths'},
        title = 'Daily New Deaths without a Postive Test',
        template='seaborn', color_discrete_sequence=["#bc5090"]
    )
    month_new_neg_death_line.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
    )
    month_new_neg_death_line.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    month_new_neg_death_line.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    
    return [
        html.Div([
            html.Div([dcc.Graph(figure = region_fig)], className = "six columns"),
            html.Div([dcc.Graph(figure = month_new_death_line)], className = "six columns")
        ], className = "row"),
        html.Div([
            html.Div([dcc.Graph(figure = month_new_pos_death_line)], className = "six columns"),
            html.Div([dcc.Graph(figure = month_new_neg_death_line)], className = "six columns")
        ], className = "row"),
    ]
    
# Create the second callback
@app.callback(Output(component_id = "graph_div_2", component_property = "children"),
                [Input(component_id = "nhs_england_region", component_property = "value"),
                Input(component_id = "month2", component_property = "value")],
    )

def create_graphs(chosen_region, chosen_month):

    #Monthly bar chart
    month_df = df.copy()
    month_df = month_df[month_df["nhs_england_region"] == chosen_region]
    month_for_region_bar = px.bar(
        data_frame=month_df,
        x = 'month',
        y = 'new_deaths_total',
        labels={'month':'Month',
                'new_deaths_total':'Number of Deaths'},
        title = 'Total New Deaths by Month',
        template='seaborn', color_discrete_sequence=["#bc5090"]
    )
    month_for_region_bar.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
    )
    month_for_region_bar.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    month_for_region_bar.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    
    #create overall choropleth
    total_geo_df = geo_df.groupby(['nhs_england_region', 'nhser20cd'])[['new_deaths_total']].sum()
    total_geo_df.reset_index(inplace=True)
    total_geo_choropleth = px.choropleth(total_geo_df, featureidkey="properties.nhser20cd", geojson=region_json, locations='nhser20cd', color='new_deaths_total', hover_name='nhs_england_region',
                           color_continuous_scale="thermal",
                           labels={'new_deaths_total':'Number of Deaths'}
                          )
    total_geo_choropleth.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    total_geo_choropleth.update_geos(fitbounds="locations", visible=False)
    total_geo_choropleth.update_layout(title={'text':'Total New Deaths by Region', 'xanchor': 'center','x':0.5, 'y':0.95},)
    
    
    #create monthly choropleth
    monthly_geo_df = geo_df[geo_df["month"] == chosen_month]
    monthly_geo_df = monthly_geo_df.groupby(['nhs_england_region', 'nhser20cd'])[['new_deaths_total']].sum()
    monthly_geo_df.reset_index(inplace=True)
    month_geo_fig = px.choropleth(monthly_geo_df, featureidkey="properties.nhser20cd", geojson=region_json, locations='nhser20cd', color='new_deaths_total', hover_name='nhs_england_region',
                           color_continuous_scale="thermal",
                           labels={'new_deaths_total':'Number of Deaths'}
                          )
    month_geo_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    month_geo_fig.update_geos(fitbounds="locations", visible=False)
    month_geo_fig.update_layout(title={'text':'Number of New Deaths by Region in Month', 'xanchor': 'center','x':0.5, 'y':0.95},)
   
    #Regional and monthly new death line chart
    reg_new_death_df = init_df.copy()
    reg_new_death_df = reg_new_death_df[reg_new_death_df["nhs_england_region"] == chosen_region]
    reg_new_death_df = reg_new_death_df[reg_new_death_df["month"] == chosen_month]
    reg_new_death_line = px.line(
        data_frame=reg_new_death_df,
        x = 'date',
        y = 'new_deaths_total',
        labels={'date':'Date',
                'new_deaths_total':'Number of Deaths'},
        title = 'Total New Deaths by Day',
        template='seaborn', color_discrete_sequence=["#bc5090"]
    )
    reg_new_death_line.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
    )
    reg_new_death_line.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    reg_new_death_line.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#DBA1C4')
    
    return [
        html.Div([
            html.Div([dcc.Graph(figure = month_for_region_bar)], className = "six columns"),
            html.Div([dcc.Graph(figure = reg_new_death_line)], className = "six columns")
        ], className = "row"),
        html.Div([
            html.Div([dcc.Graph(figure = total_geo_choropleth)], className = "six columns"),
            html.Div([dcc.Graph(figure = month_geo_fig)], className = "six columns")
        ], className = "two rows"),
    ]

#Run the dashboard
if __name__ == '__main__':
    app.run_server()