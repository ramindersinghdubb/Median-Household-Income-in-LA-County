# ------------ LIBRARIES ------------ #
import dash
from dash import dcc, html, clientside_callback, ClientsideFunction
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import feffery_markdown_components as fmc


import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
from copy import deepcopy
import os


# ------------ DATA COLLECTION ------------ #

assets_path = "assets/"

data_path = "masterfiles/"


# -- Masterfile -- #
masterfile = pd.DataFrame()
years = range(2010, 2024)

for year in years:
    file_path = f'{data_path}median_income_masterfile_{year}.csv'
    df = pd.read_csv(file_path)
    map_path = f'{assets_path}median_income_mastergeometry_{year}.json'
    gdf = gpd.read_file(map_path)
    df = pd.merge(df, gdf[['PLACE', 'NAME', 'GEO_ID','INTPTLAT','INTPTLON']], on=['PLACE', 'NAME', 'GEO_ID'], how='left')

    # For the trace
    df['dummy'] = 1

    # String formatting for the hovertext
    columns = df.columns.to_list()
    selected_columns = [col for col in columns if 'B19013' in col]
    for col in selected_columns:
        col_string = f'{col}_string'
        df[col_string] = '$' + df[col].astype(str)
        df[col_string] = df[col_string].str.replace('.0', '')
        df.loc[df[col_string] == '$nan', col_string] = 'Not available'
        df.loc[df[col_string] == '$250001', col_string] = 'Not available. Exceeds $250000!' # Income imputation capped at $250k
    
    columns = df.columns.to_list()
    drop_columns = [col for col in columns if col.endswith("001M")]
    df.drop(columns=drop_columns, inplace=True)

    masterfile = pd.concat([masterfile, df], ignore_index = True)



# ------------ UTILITY FUNCTIONS ------------ #

# Function for creating a dictionary where the places (keys) hold lists of dictionaries for our year dropdown
def place_year_dictionary():
    place_year_dict = dict()

    places = masterfile['PLACE'].unique().tolist()
    masterfile['NAME'].unique
    for place in places:
        df = masterfile[masterfile['PLACE'] == place]
        list_of_years = df['YEAR'].unique().tolist()
        dummy_dict = [{'label': year, 'value': year} for year in list_of_years]
        place_year_dict[place] = dummy_dict

    return place_year_dict




# ------------ CONTAINERS AND STRINGS------------ #

# Container for geospatial choropleth map
geodata_map = html.Div([
    dcc.Graph(
        id = "chloropleth_map",
        config={'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d', 'resetview'],
                'displaylogo': False
               },
    )
])

# Container for rent plot
geodata_plot = html.Div([
    dcc.Graph(
        id = "income_plot",
        config={'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d', 'resetview'],
                'displaylogo': False
               },
    )
])



# Footer string
footer_string = """
### <b style='color:#800000;'>Information</b>

This website allows you to view median household income in the past 12 months (in 2023 Consumer Price Index-adjusted dollars) for various census tracts across various cities in Los Angeles county. <br>

Use the dropdowns to choose a city of interest and a year of interest. You can also choose to visualize median household income for various racial demographics. <br>

Hover over the map to view median household income information. <br>

Click on a census tract to visualize how median household income has evolved over time in the plot. You can also hover over points in the
plot to view additional information on median household income by racial demographic.

<hr style="height:2px; border-width:0; color:#212122; background-color:#212122">

### <b style='color:#800000;'>Notes</b>
1. Income, per the <u style='color:#800000;'><a href="https://www2.census.gov/programs-surveys/acs/methodology/design_and_methodology/2024/acs_design_methodology_report_2024.pdf" style='color:#800000;'>December 2024 American Community Survey and Puerto Rico Community Survey Design and Methodology</a></u>, is defined as <br>

   <blockquote> <q> ...the sum of the amounts reported separately for wage or salary income; net self-employment income; interest, dividends, or net rental
   or royalty income, or income from estates and trusts; social security or railroad retirement income; Supplemental Security Income; public assistance or welfare payments;
   retirement, survivor, or disability pensions; and all other income. Income is reported for the past 12 months from the date of the interview. The estimates are inflation-adjusted
   using the Consumer Price Index.</q> (Chapter 6) </blockquote>

2. Data for median household income in the past 12 months (in 2023 inflation-adjusted dollars) were taken from the United States Census Bureau <u style='color:#800000;'><a href="https://www.census.gov/programs-surveys/acs.html" style='color:#800000;'>American Community Survey</a></u> (ACS codes B19013, B19013A, B19013B, B19013C, B19013D, B19013E, B19013F, B19013G, B19013H and B19013I).
3. Redistricting over the years affects the availability of some census tracts in certain cities. Unavailability of data for certain census tracts during select years may affect whether or not census tracts are displayed on the map. For these reasons, some census tracts and their data may only be available for a partial range of years.
4. The American Community Survey caps the imputation of median household incomes at $250k. As a result, some data on select census tracts may be unavailable in virtue of being higher than those permissible by these thresholds.

### <b style='color:#800000;'>Disclaimer</b>

This tool is developed for illustrative purposes. This tool is constructed with the assistance of the United States Census Bureau’s American Community Survey data.
Survey data is based on individuals’ voluntary participation in questionnaires. Racial categories are social and political constructs, reflective of the socialization
process at large. The creator is not liable for any missing, inaccurate, or incorrect data. This tool is not affiliated with, nor endorsed by, the government of the
United States.

### <b style='color:#800000;'>Appreciation</b>
Thank you to <u style='color:#800000;'><a href="https://www.wearelbre.org/" style='color:#800000;'>Long Beach Residents Empowered (LiBRE)</a></u> for providing the opportunity to work on this project.

### <b style='color:#800000;'>Author Information</b>
Raminder Singh Dubb <br>
<u style='color:#800000;'><a href="https://github.com/ramindersinghdubb/Median-Household-Income-in-LA-County" style='color:#800000;'>GitHub</a></u>

© 2025 Raminder Singh Dubb
"""




# ------------ Initialization ------------ #
place_year_dict = place_year_dictionary()
demographics_list = ['Overall Population', 'White Householders', 'Black or African American Householders',
                     'American Indian and Alaska Native Householders', 'Asian Householders',
                     'Native Hawaiian and Other Pacific Islander Householders', 'Some Other Race Householders',
                     'Two or More Races Householders', 'White Alone, Not Hispanic or Latino Householders',
                     'Hispanic or Latino Householders'
                    ]

# ------------ Colors ------------ #
Cream_color = '#FAE8E0'
SnowWhite_color = '#F5FEFD'
AlabasterWhite_color = '#FEF9F3'
LightBrown_color = '#F7F2EE'
Rose_color = '#FF7F7F'
MaroonRed_color = '#800000'
SinopiaRed_color = '#C0451C'
Teal_color = '#2A9D8F'
ObsidianBlack_color = '#020403'
CherryRed_color = '#E3242B'



# ------------ APP ------------ #

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.SIMPLEX,
                                      "assets/style.css"
                                     ]
               )
server=app.server
app.title = 'Median Household Income in Los Angeles County'



app.layout = dbc.Container([
    # ------------ Title ------------ #
    html.Div([
        html.B("Median Household Income in Los Angeles County")
    ], style = {'display': 'block',
                'color': MaroonRed_color,
                'margin': '0.2em 0',
                'padding': '0px 0px 0px 0px', # Numbers represent spacing for the top, right, bottom, and left (in that order)
                'font-family': 'Trebuchet MS, sans-serif',
                'font-size': '220.0%'
               }
            ),
    # ------------ Subtitle ------------ #
    html.Div([
        html.P("Median Household Income (in 2023 Consumer Price Index Adjusted Dollars) for Census Tracts across Cities and Census-Designated Places in Los Angeles County, 2010 to 2023")
    ], style = {'display': 'block',
                'color': ObsidianBlack_color,
                'margin': '-0.5em 0',
                'padding': '0px 0px 0px 0px',
                'font-family': 'Trebuchet MS, sans-serif',
                'font-size': '100.0%'
               }
            ),
    # ------------ Horizontal line rule ------------ #
    html.Div([
        html.Hr()
    ], style = {'display': 'block',
                'height': '1px',
                'border': 0,
                'margin': '-0.9em 0',
                'padding': 0
               }
            ),
    # ------------ Labels for dropdowns (discarded) ------------ #
    
    # ------------ Dropdowns ------------ #
    html.Div([
        html.Div([
            dcc.Dropdown(id='place-dropdown',
                         placeholder='Select a place',
                         options=[{'label': p, 'value': p} for p in list(place_year_dict.keys())],
                         value='Long Beach',
                         clearable=False
                        )
        ], style = {'display': 'inline-block',
                    'margin': '0 0',
                    'padding': '30px 15px 0px 0px',
                    'width': '22.5%'
                   }
                ),
        html.Div([
            dcc.Dropdown(id='year-dropdown',
                         placeholder='Select a year',
                         clearable=False
                        )
        ], style = {'display': 'inline-block',
                    'margin': '0 0',
                    'padding': '30px 15px 0px 0px',
                    'width': '12.5%',
                   }
                ),
        html.Div([
            dcc.Dropdown(id='racial-category-dropdown',
                         placeholder='Select a racial demographic',
                         options=[{'label': p, 'value': p} for p in demographics_list],
                         value='Overall Population',
                         clearable=False
                        )
        ], style = {'display': 'inline-block',
                    'margin': '0 0',
                    'padding': '30px 15px 0px 0px',
                    'width': '37.5%',
                   }
                ),
        html.Div([
            dcc.Dropdown(id='census-tract-dropdown',
                         placeholder = 'Click on a census tract in the map',
                         clearable=True
                        )
        ], style = {'display': 'inline-block',
                    'padding': '30px 30px 0px 0px',
                    'margin': '0 0',
                    'width': '25.0%'
                   }
                ),
    ], style={"padding": "0px 0px 10px 15px"}, className = 'row'
            ),
    # ------------ Spatial map with plot ------------ #
    html.Div([
            dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(children = [html.B("Median Household Income"), " for ", html.B(id="map-title1"), " in ", html.B(id="map-title2"), " by Census Tract, ", html.B(id="map-title3")],
                                   style = {'background-color': MaroonRed_color,
                                            'color': '#FFFFFF'}
                                  ),
                    dbc.CardBody([geodata_map],
                                 style = {'background-color': AlabasterWhite_color}
                                )
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(children = html.B(id = "plot-title"),
                                   style = {'background-color': Teal_color,
                                            'color': '#FFFFFF'}
                                  ),
                    dbc.CardBody([geodata_plot],
                                 style = {'background-color': AlabasterWhite_color}
                                )
                ])
            ])
        ], align='center', justify='center'
               )
    ], style = {
                'padding': '10px 0px 20px 0px',
               }
            ),
    # ------------ Footer ------------ #
    html.Div([
        fmc.FefferyMarkdown(markdownStr    = footer_string,
                            renderHtml     = True,
                            style          = {'background': LightBrown_color,
                                              'margin-top': '1em'
                                             }
                           )
    ]
            ),
    # ------------ Data ------------ #
    dcc.Store(id='masterfile_data',
              data=masterfile.to_dict("records")
             ),
    dcc.Store(id='place_year_dict',
              data=place_year_dict
             )
], style = {'background-color': LightBrown_color, "padding": "0px 0px 20px 0px",})



# ------------ CALLBACKS ------------ #
#
# Summary (inputs -> outputs)
#
#
# Dropdowns:
#  place value -> year options
#  year options -> default year value
#  place options, year options, map ClickData -> census tract options
#  click data -> census tract value
#
# Titles:
#  place value, year value, radio options -> map title
#  place value, census tract value -> plot title
#
# Graphs:
#  place value, year value, census tract value, radio options -> map
#  place value, census tract value, radio options -> plot
#
# Alert:
#  place value, year value, radio options -> tract display
#
# ----------------------------------- #


# ------------ Dropdowns ------------ #

# Year tract options
app.clientside_callback(
    """
    function(selected_place, place_year_dict) {
        return place_year_dict[selected_place]
    }
    """,
    Output('year-dropdown', 'options'),
    [Input('place-dropdown', 'value'),
     Input('place_year_dict', 'data')
    ]
)


# Year tract value
app.clientside_callback(
    """
    function(options) {
        var opt = options.find(x => x['label'] === 2023);
        return opt['label']
    }
    """,
    Output('year-dropdown', 'value'),
    Input('year-dropdown', 'options')
)


# Census tract options
app.clientside_callback(
    """
    function(selected_place, selected_year, masterfile_data) {
        var selected_place = `${selected_place}`;
        var options = masterfile_data.filter(x => x['YEAR'] === selected_year && x['PLACE'] === selected_place);
        var tract_options = options.map(item => { return item.NAME });
        return tract_options
    }
    """,
    Output('census-tract-dropdown', 'options'),
    [Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('masterfile_data', 'data')
    ]
)




# Census tract value based on click data
app.clientside_callback(
    """
    function(clickData) {
        return clickData['points']['0']['customdata']
    }
    """,
    Output('census-tract-dropdown', 'value'),
    Input('chloropleth_map', 'clickData')
)




# ------------ Titles ------------ #


# Map title
app.clientside_callback(
    """
    function(selected_demographic, selected_place, selected_year) {
        var selected_demographic = `${selected_demographic}`;
        var selected_place = `${selected_place}`;
        var selected_year = `${selected_year}`;

        return [selected_demographic, selected_place, selected_year];
    }
    """,
    [Output('map-title1', 'children'),
     Output('map-title2', 'children'),
     Output('map-title3', 'children')
    ],
    [Input('racial-category-dropdown', 'value'),
     Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
    ]
)

# Plot title
app.clientside_callback(
    """
    function(selected_place, selected_tract) {
        if (selected_tract == undefined){
            return "Please click on a tract.";
        } else {
            return `${selected_place}, ${selected_tract}`;
        }
    }
    """,
    Output('plot-title', 'children'),
    [Input('place-dropdown', 'value'),
     Input('census-tract-dropdown', 'value')
    ]
)


# ------------ Graphs ------------ #

# Choropleth map
app.clientside_callback(
    """
    function(selected_demographic, selected_place, selected_year, selected_tract, masterfile_data){
        var selected_demographic = `${selected_demographic}`;
        var selected_place = `${selected_place}`;
        if ( selected_place.includes("Flintridge") ) {
           var selected_place = 'La Ca' + \u00f1 + 'ada Flintridge';
           return selected_place;
        }
        var selected_year = Number(selected_year);
        var my_array = masterfile_data.filter(item => item['PLACE'] === selected_place && item['YEAR'] === selected_year);
        
        var place_string = selected_place.replaceAll(' ','');
        var url_path = 'https://raw.githubusercontent.com/ramindersinghdubb/Rent-Burden-in-LA-County/refs/heads/main/as' + 'sets/' + `${selected_year}/rent_burden_mastergeometry_${selected_year}_${place_string}.json`;
        
        var locations_array = my_array.map(({GEO_ID}) => GEO_ID);
        var customdata_array = my_array.map(({NAME}) => NAME);

        
        var long_array = my_array.map(({INTPTLON})=>INTPTLON);
        var long_center = long_array.reduce((a, b) => a + b) / long_array.length;
        const lon_center = parseFloat(long_center.toFixed(5));
        
        var lat_array = my_array.map(({INTPTLAT})=>INTPTLAT);
        var lati_center = lat_array.reduce((a, b) => a + b) / lat_array.length;
        const lat_center = parseFloat(lati_center.toFixed(5));


        var Overall_z_array = my_array.map(({B19013_001E}) => B19013_001E);
        var WA_z_array = my_array.map(({B19013A_001E}) => B19013A_001E);
        var BAAA_z_array = my_array.map(({B19013B_001E}) => B19013B_001E);
        var AIANA_z_array = my_array.map(({B19013C_001E}) => B19013C_001E);
        var AA_z_array = my_array.map(({B19013D_001E}) => B19013D_001E);
        var NHOPA_z_array = my_array.map(({B19013E_001E}) => B19013E_001E);
        var SORA_z_array = my_array.map(({B19013F_001E}) => B19013F_001E);
        var TMR_z_array = my_array.map(({B19013G_001E}) => B19013G_001E);
        var WANHL_z_array = my_array.map(({B19013H_001E}) => B19013H_001E);
        var HL_z_array = my_array.map(({B19013I_001E}) => B19013I_001E);
        
        


        var Overall_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "<b style='font-size:15px;'>Overall Population</b>  <br>"
            + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013_001E_string'] + "</b>  <br>"
            + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013_001M_string'] + "</b>  <br>"
            + "<extra></extra>";
            });
        
        var Overall_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Greens',
            'reversescale': true,
            'z': Overall_z_array,
            'zmin': 0, 'zmax': 200000,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': Overall_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'tickprefix': '$',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Median<br>Household<br>Income ($)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];
        
        var WA_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "<b style='font-size:15px;'>White Householders</b>  <br>"
            + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013A_001E_string'] + "</b>  <br>"
            + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013A_001M_string'] + "</b>  <br>"
            + "<extra></extra>";
            });
        
        var WA_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Greens',
            'reversescale': true,
            'z': WA_z_array,
            'zmin': 0, 'zmax': 200000,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': WA_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'tickprefix': '$',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Median<br>Household<br>Income ($)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];

        var BAAA_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "<b style='font-size:15px;'>Black or African American  <br>Householders</b><br>"
            + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013B_001E_string'] + "</b>  <br>"
            + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013B_001M_string'] + "</b>  <br>"
            + "<extra></extra>";
            });
        
        var BAAA_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Greens',
            'reversescale': true,
            'z': BAAA_z_array,
            'zmin': 0, 'zmax': 200000,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': BAAA_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'tickprefix': '$',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Median<br>Household<br>Income ($)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];

        var AIANA_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "<b style='font-size:15px;'>American Indian and Alaska  <br>Native Householders</b><br>"
            + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013C_001E_string'] + "</b>  <br>"
            + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013C_001M_string'] + "</b>  <br>"
            + "<extra></extra>";
            });
        
        var AIANA_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Greens',
            'reversescale': true,
            'z': AIANA_z_array,
            'zmin': 0, 'zmax': 200000,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': AIANA_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'tickprefix': '$',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Median<br>Household<br>Income ($)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];

        var AA_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "<b style='font-size:15px;'>Asian Householders</b>  <br>"
            + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013D_001E_string'] + "</b>  <br>"
            + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013D_001M_string'] + "</b>  <br>"
            + "<extra></extra>";
            });
        
        var AA_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Greens',
            'reversescale': true,
            'z': AA_z_array,
            'zmin': 0, 'zmax': 200000,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': AA_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'tickprefix': '$',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Median<br>Household<br>Income ($)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];

        var NHOPA_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "<b style='font-size:15px;'>Native Hawaiian and Other  <br>Pacific Islander Householders</b><br>"
            + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013E_001E_string'] + "</b>  <br>"
            + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013E_001M_string'] + "</b>  <br>"
            + "<extra></extra>";
            });
        
        var NHOPA_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Greens',
            'reversescale': true,
            'z': NHOPA_z_array,
            'zmin': 0, 'zmax': 200000,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': NHOPA_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'tickprefix': '$',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Median<br>Household<br>Income ($)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];

        var SORA_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "<b style='font-size:15px;'>Some Other Race Householders</b>  <br>"
            + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013F_001E_string'] + "</b>  <br>"
            + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013F_001M_string'] + "</b>  <br>"
            + "<extra></extra>";
            });
        
        var SORA_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Greens',
            'reversescale': true,
            'z': SORA_z_array,
            'zmin': 0, 'zmax': 200000,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': SORA_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'tickprefix': '$',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Median<br>Household<br>Income ($)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];

        var TMR_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "<b style='font-size:15px;'>Two or More Races Householders</b>  <br>"
            + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013G_001E_string'] + "</b>  <br>"
            + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013G_001M_string'] + "</b>  <br>"
            + "<extra></extra>";
            });
        
        var TMR_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Greens',
            'reversescale': true,
            'z': TMR_z_array,
            'zmin': 0, 'zmax': 200000,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': TMR_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'tickprefix': '$',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Median<br>Household<br>Income ($)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];

        var WANHL_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "<b style='font-size:15px;'>White Alone, Not Hispanic or  <br>Latino Householders</b><br>"
            + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013H_001E_string'] + "</b>  <br>"
            + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013H_001M_string'] + "</b>  <br>"
            + "<extra></extra>";
            });
        
        var WANHL_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Greens',
            'reversescale': true,
            'z': WANHL_z_array,
            'zmin': 0, 'zmax': 200000,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': WANHL_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'tickprefix': '$',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Median<br>Household<br>Income ($)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];

        var HL_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "<b style='font-size:15px;'>Hispanic or Latino Householders</b>  <br>"
            + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013I_001E_string'] + "</b>  <br>"
            + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013I_001M_string'] + "</b>  <br>"
            + "<extra></extra>";
            });
        
        var HL_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Greens',
            'reversescale': true,
            'z': HL_z_array,
            'zmin': 0, 'zmax': 200000,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': HL_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'tickprefix': '$',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Median<br>Household<br>Income ($)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];



        
        var layout = {
            'autosize': true,
            'hoverlabel': {'align': 'left'},
            'map': {'center': {'lat': lat_center, 'lon': lon_center}, 'style': 'streets', 'zoom': 10},
            'margin': {'b': 0, 'l': 0, 'r': 0, 't': 0},
            'paper_bgcolor': '#FEF9F3',
            'plot_bgcolor': '#FEF9F3',
        };


        if (selected_tract != undefined){
            var aux_array = my_array.filter(item => item['NAME'] === selected_tract);
            var aux_locations_array = aux_array.map(({GEO_ID}) => GEO_ID);
            var aux_z_array = aux_array.map(({dummy})=>dummy);
                
            var aux_data = {
                'type': 'choroplethmap',
                'geojson': url_path,
                'locations': aux_locations_array,
                'featureidkey': 'properties.GEO_ID',
                'colorscale': 'Reds',
                'showscale': false,
                'z': aux_z_array,
                'zmin': 0, 'zmax': 1,
                'marker': {'line': {'color': '#04D9FF', 'width': 4}},
                'selected': {'marker': {'opacity': 0.4}},
                'hoverinfo': 'skip',
            }
        }


        if (selected_demographic == 'Overall Population') {
            if (selected_tract != undefined){
                Overall_main_data.push(aux_data);
            }
            return {'data': Overall_main_data, 'layout': layout};
        }

        
        else if (selected_demographic == 'White Householders') {
            if (selected_tract != undefined){
                WA_main_data.push(aux_data);
            }
            return {'data': WA_main_data, 'layout': layout};
        }
        
        else if (selected_demographic == 'Black or African American Householders') {
            if (selected_tract != undefined){
                BAAA_main_data.push(aux_data);
            }
            return {'data': BAAA_main_data, 'layout': layout};
        }

        else if (selected_demographic == 'American Indian and Alaska Native Householders') {
            if (selected_tract != undefined){
                AIANA_main_data.push(aux_data);
            }
            return {'data': AIANA_main_data, 'layout': layout};
        }

        else if (selected_demographic == 'Asian Householders') {
            if (selected_tract != undefined){
                AA_main_data.push(aux_data);
            }
            return {'data': AA_main_data, 'layout': layout};
        }

        else if (selected_demographic == 'Native Hawaiian and Other Pacific Islander Householders') {
            if (selected_tract != undefined){
                NHOPA_main_data.push(aux_data);
            }
            return {'data': NHOPA_main_data, 'layout': layout};
        }

        else if (selected_demographic == 'Some Other Race Householders') {
            if (selected_tract != undefined){
                SORA_main_data.push(aux_data);
            }
            return {'data': SORA_main_data, 'layout': layout};
        }

        else if (selected_demographic == 'Two or More Races Householders') {
            if (selected_tract != undefined){
                TMR_main_data.push(aux_data);
            }
            return {'data': TMR_main_data, 'layout': layout};
        }

        else if (selected_demographic == 'White Alone, Not Hispanic or Latino Householders') {
            if (selected_tract != undefined){
                WANHL_main_data.push(aux_data);
            }
            return {'data': WANHL_main_data, 'layout': layout};
        }

        else if (selected_demographic == 'Hispanic or Latino Householders') {
            if (selected_tract != undefined){
                HL_main_data.push(aux_data);
            }
            return {'data': HL_main_data, 'layout': layout};
        }
    }
    """,
    Output('chloropleth_map', 'figure'),
    [Input('racial-category-dropdown', 'value'),
     Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('census-tract-dropdown', 'value'),
     Input('masterfile_data', 'data')
    ]
)



# Plot
app.clientside_callback(
    """
    function(selected_demographic, selected_place, selected_tract, masterfile_data){        
        if (selected_tract != undefined) {
            var selected_demographic = `${selected_demographic}`;
            var selected_place = `${selected_place}`;
            var selected_tract = `${selected_tract}`;
            var my_array = masterfile_data.filter(item => item['PLACE'] === selected_place && item['NAME'] === selected_tract);


            var customdata_array = my_array.map(({NAME}) => NAME);

            
            var x_array = my_array.map(({YEAR})=>YEAR);

            var Overall_y_array = my_array.map(({B19013_001E}) => B19013_001E);
            var WA_y_array = my_array.map(({B19013A_001E}) => B19013A_001E);
            var BAAA_y_array = my_array.map(({B19013B_001E}) => B19013B_001E);
            var AIANA_y_array = my_array.map(({B19013C_001E}) => B19013C_001E);
            var AA_y_array = my_array.map(({B19013D_001E}) => B19013D_001E);
            var NHOPA_y_array = my_array.map(({B19013E_001E}) => B19013E_001E);
            var SORA_y_array = my_array.map(({B19013F_001E}) => B19013F_001E);
            var TMR_y_array = my_array.map(({B19013G_001E}) => B19013G_001E);
            var WANHL_y_array = my_array.map(({B19013H_001E}) => B19013H_001E);
            var HL_y_array = my_array.map(({B19013I_001E}) => B19013I_001E);



            var Overall_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                + "<b style='font-size:15px;'>Overall Population</b>  <br>"
                + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013_001E_string'] + "</b>  <br>"
                + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013_001M_string'] + "</b>  <br>"
                + "<extra></extra>";
            });
            var WA_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                +  "<b style='font-size:15px;'>White Householders</b>  <br>"
                + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013A_001E_string'] + "</b>  <br>"
                + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013A_001M_string'] + "</b>  <br>"
                + "<extra></extra>";
            });
            var BAAA_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                + "<b style='font-size:15px;'>Black or African American  <br>Householders</b><br>"
                + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013B_001E_string'] + "</b>  <br>"
                + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013B_001M_string'] + "</b>  <br>"
                + "<extra></extra>";
            });
            var AIANA_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                + "<b style='font-size:15px;'>American Indian and Alaska  <br>Native Householders</b><br>"
                + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013C_001E_string'] + "</b>  <br>"
                + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013C_001M_string'] + "</b>  <br>"
                + "<extra></extra>";
            });
            var AA_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                + "<b style='font-size:15px;'>Asian Householders</b>  <br>"
                + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013D_001E_string'] + "</b>  <br>"
                + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013D_001M_string'] + "</b>  <br>"
                + "<extra></extra>";
            });
            var NHOPA_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                + "<b style='font-size:15px;'>Native Hawaiian and Other  <br>Pacific Islander Householders</b><br>"
                + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013E_001E_string'] + "</b>  <br>"
                + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013E_001M_string'] + "</b>  <br>"
                + "<extra></extra>";
            });
            var SORA_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                + "<b style='font-size:15px;'>Some Other Race Householders</b>  <br>"
                + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013F_001E_string'] + "</b>  <br>"
                + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013F_001M_string'] + "</b>  <br>"
                + "<extra></extra>";
            });
            var TMR_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                + "<b style='font-size:15px;'>Two or More Races Householders</b>  <br>"
                + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013G_001E_string'] + "</b>  <br>"
                + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013G_001M_string'] + "</b>  <br>"
                + "<extra></extra>";
            });
            var WANHL_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                + "<b style='font-size:15px;'>White Alone, Not Hispanic or  <br>Latino Householders</b><br>"
                + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013H_001E_string'] + "</b>  <br>"
                + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013H_001M_string'] + "</b>  <br>"
                + "<extra></extra>";
            });
            var HL_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                + "<b style='font-size:15px;'>Hispanic or Latino Householders</b>  <br>"
                + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013I_001E_string'] + "</b>  <br>"
                + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013I_001M_string'] + "</b>  <br>"
                + "<extra></extra>";
            });

            

            var Overall_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': Overall_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': Overall_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
            var WA_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': WA_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': WA_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
            var BAAA_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': BAAA_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': BAAA_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
            var AIANA_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': AIANA_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': AIANA_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
            var AA_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': AA_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': AA_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
            var NHOPA_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': NHOPA_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': NHOPA_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
            var SORA_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': SORA_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': SORA_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
            var TMR_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': TMR_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': TMR_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
            var WANHL_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': WANHL_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': WANHL_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
            var HL_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': HL_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': HL_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
        
            var layout = {
                'font': {'color': '#020403'},
                'hoverlabel': {'align': 'left'},
                'margin': {'b': 40, 't': 50, 'r': 20},
                'autosize': true,
                'uirevision': true,
                'paper_bgcolor': '#FEF9F3',
                'plot_bgcolor': '#FEF9F3',
                'title': {'text': `Median Household Income (2023 CPI-Adjusted Dollars), ${Math.min(...x_array)} to ${Math.max(...x_array)}`,
                          'x': 0.05,
                          },
                'xaxis': {'title': {'text': 'Year', 'ticklabelstandoff': 10}, 'showgrid': false, 'tickvals': x_array},
                'yaxis': {'title': {'text': 'Median Household Income ($)', 'standoff': 15}, 'tickprefix': '$', 'gridcolor': '#E0E0E0', 'ticklabelstandoff': 5},
            };

            
            if (selected_demographic == 'Overall Population') {
                return {'data': Overall_data, 'layout': layout};
            }
            else if (selected_demographic == 'White Householders') {
                return {'data': WA_data, 'layout': layout};
            }
            else if (selected_demographic == 'Black or African American Householders') {
                return {'data': BAAA_data, 'layout': layout};
            }
            else if (selected_demographic == 'American Indian and Alaska Native Householders') {
                return {'data': AIANA_data, 'layout': layout};
            }
            else if (selected_demographic == 'Asian Householders') {
                return {'data': AA_data, 'layout': layout};
            }
            else if (selected_demographic == 'Native Hawaiian and Other Pacific Islander Householders') {
                return {'data': NHOPA_data, 'layout': layout};
            }
            else if (selected_demographic == 'Some Other Race Householders') {
                return {'data': SORA_data, 'layout': layout};
            }
            else if (selected_demographic == 'Two or More Races Householders') {
                return {'data': TMR_data, 'layout': layout};
            }
            else if (selected_demographic == 'White Alone, Not Hispanic or Latino Householders') {
                return {'data': WANHL_data, 'layout': layout};
            }
            else if (selected_demographic == 'Hispanic or Latino Householders') {
                return {'data': HL_data, 'layout': layout};
            }
        }
    }
    """,
    Output('income_plot', 'figure'),
    [Input('racial-category-dropdown', 'value'),
     Input('place-dropdown', 'value'),
     Input('census-tract-dropdown', 'value'),
     Input('masterfile_data', 'data')
    ]
)







# ------------ EXECUTE THE APP ------------ #
if __name__ == "__main__":
    app.run(debug=False)
