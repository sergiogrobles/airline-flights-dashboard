# Modules
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

# Read the airline data into pandas dataframe
airline_data =  pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/airline_data.csv', 
                            encoding = "ISO-8859-1",
                            dtype={'Div1Airport': str, 'Div1TailNum': str, 
                                   'Div2Airport': str, 'Div2TailNum': str})

# create app
app = Dash(__name__)

# create app layout
app.layout = html.Div(children = [html.H1('US Domestic Flight Performance', style = {'textAlign': 'center', 
                                                                                     'font-size': 24, 
                                                                                     'color': '#503D36'}), 
                                  dcc.Dropdown(id = 'report-type', options = [
                                      {'label': 'Yearly Performance Performance', 'value': 'OPT1'}, 
                                      {'label': 'Yearly Airline Delay Report', 'value': 'OPT2'}],
                                               placeholder = 'Choose a report type', 
                                               searchable = False,
                                               style = {'width': '80%', 'padding':'3px', 
                                                        'font-size': '20px', 'textAlign': 'center'}), 
                                  html.Br(),
                                  html.Div(['Input Year: ', dcc.Input(id = 'year-type', 
                                                                      value = '2010', 
                                                                      type = 'number', 
                                                                      style = {'height': '35px', 'font-size': 30})],
                                           style = {'font-size': 30}), 
                                  html.Div([
                                      html.Div([], id = 'plot-1')], 
                                           style = {'width': '100%'}),
                                  html.Div([
                                      html.Div([], id = 'plot-2'), 
                                      html.Div([], id = 'plot-3')],
                                           style = {'display': 'flex'}),
                                  html.Div([
                                      html.Div([], id = 'plot-4'), 
                                      html.Div([], id = 'plot-5')],
                                           style = {'display': 'flex'}),
                                  ])
# define global variables to optimize
def global_variables(airline_data, entered_year):
    df = airline_data[airline_data['Year'] == int(entered_year)]
    
    # define  OPT1 global variables for performance
    avg_AirTime = df.groupby(['Month', 'Reporting_Airline'])['AirTime'].mean().reset_index()
    
    flights_cancelled = df.groupby('CancellationCode')['Flights'].sum().reset_index()
    
    diverted_landing = df.groupby('Reporting_Airline')['Diverted'].sum().reset_index()
    
    origin_state = df.groupby('OriginState')['Flights'].sum().reset_index()
    
    tree_data = df.groupby(['DestStateName', 'Reporting_Airline'])['Flights'].sum().reset_index()
    
    # define  OPT2 global variables for delay averages
    avg_carrier = df.groupby(['Month', 'Reporting_Airline'])['CarrierDelay'].mean().reset_index()
    
    avg_weather = df.groupby(['Month', 'Reporting_Airline'])['WeatherDelay'].mean().reset_index()
    
    avg_NAS = df.groupby(['Month', 'Reporting_Airline'])['NASDelay'].mean().reset_index()
    
    avg_sec = df.groupby(['Month', 'Reporting_Airline'])['SecurityDelay'].mean().reset_index()
    
    avg_late = df.groupby(['Month', 'Reporting_Airline'])['LateAircraftDelay'].mean().reset_index()
    
    return avg_AirTime, flights_cancelled, diverted_landing, origin_state, tree_data, avg_carrier, avg_weather, avg_NAS, avg_sec, avg_late

# add callback decorator
@app.callback([
    Output(component_id = 'plot-1', component_property = 'children'),
    Output(component_id = 'plot-2', component_property = 'children'),
    Output(component_id = 'plot-3', component_property = 'children'),
    Output(component_id = 'plot-4', component_property = 'children'),
    Output(component_id = 'plot-5', component_property = 'children')], 
              [Input(component_id = 'report-type', component_property = 'value'), 
               Input(component_id = 'year-type', component_property = 'value')]) 
def update_report_df(report, entered_year):
    (avg_AirTime, flights_cancelled, diverted_landing, origin_state, tree_data, avg_carrier, 
     avg_weather, avg_NAS, avg_sec, avg_late) = global_variables(airline_data, entered_year) 
    
    if report == 'OPT1':
        
        air_time_fig = px.line(avg_AirTime, x = 'Month', y = 'AirTime', color = 'Reporting_Airline', 
                               title = 'Average monthly Air Time (minutes) by Airline')
        
        cancelled_fig = px.bar(flights_cancelled, x = 'CancellationCode', y = 'Flights', color = 'CancellationCode', 
                               title = 'Flights Cancelled by Cancellation Code', text_auto='.2s')
        
        diverted_fig = px.pie(diverted_landing, values = 'Diverted', names = 'Reporting_Airline', 
                              title = 'Percentage of Diverted Flights by Airline')
        diverted_fig.update_traces(textposition = 'inside', textinfo = 'percent+label')
        
        map_fig = px.choropleth(origin_state, locations = 'OriginState', color = 'Flights', 
                    locationmode = "USA-states", scope = 'usa', title = 'Map of Flight Origins')
        
        tree_fig = px.treemap(tree_data, path = [px.Constant('State'),'DestStateName', 'Reporting_Airline'], 
                      values = 'Flights', color = 'Flights', color_continuous_scale = 'RdBu')
        
        return [dcc.Graph(figure = air_time_fig), dcc.Graph(figure = cancelled_fig), dcc.Graph(figure = diverted_fig), 
                dcc.Graph(figure = map_fig), dcc.Graph(figure = tree_fig)]
    else:
        carrier_fig = px.line(avg_carrier, x = 'Month', y = 'CarrierDelay', color = 'Reporting_Airline', 
                              title = 'Average Carrier Delay Time (minutes) by Airline')
        
        weather_fig = px.line(avg_weather, x = 'Month', y = 'WeatherDelay', color = 'Reporting_Airline', 
                              title = 'Average Weather Delay Time (minutes) by Airline')
        
        NAS_fig = px.line(avg_NAS, x = 'Month', y = 'NASDelay', color = 'Reporting_Airline', 
                          title = 'Average NAS Delay Time (minutes) by Airline')
        
        sec_fig = px.line(avg_sec, x = 'Month', y = 'SecurityDelay', color = 'Reporting_Airline', 
                          title = 'Average Security Delay Time (minutes) by Airline')
        
        late_fig = px.line(avg_late, x = 'Month', y = 'LateAircraftDelay', color = 'Reporting_Airline', 
                           title = 'Average Late Aircraft Delay Time (minutes) by Airline')
        
        return [dcc.Graph(figure = carrier_fig), dcc.Graph(figure = weather_fig), dcc.Graph(figure = NAS_fig), 
                dcc.Graph(figure = sec_fig), dcc.Graph(figure = late_fig)]    


if __name__ == '__main__':
    app.run_server(debug = True)