# Libraries
from dash import dcc, html, Dash
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import feffery_markdown_components as fmc

from utils.app_setup import (
    YEAR_PLACE_OPTIONS,
    PLACE_YEAR_OPTIONS,
    DEMOGRAPHICS_OPTIONS,
    ALL_YEARS,
    footer_string,
    geodata_map, geodata_plot
)


# -- -- --
# Colors
# -- -- --
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


# -- --
# App
# -- --
app = Dash(__name__,
           external_stylesheets = [dbc.themes.SIMPLEX, "assets/style.css"])
server=app.server
app.title = 'Median Household Income in Los Angeles County'



app.layout = dbc.Container([
    # Title
    html.Div([html.B("Median Household Income in Los Angeles County")],
             style = {'display': 'block',
                'color': MaroonRed_color,
                'margin': '0.2em 0',
                'padding': '0px 0px 0px 0px', # Numbers represent spacing for the top, right, bottom, and left (in that order)
                'font-family': 'Trebuchet MS, sans-serif',
                'font-size': '220.0%'
               }
            ),
    # Subtitle
    html.Div([html.P(f"Median Household Income (in {max(ALL_YEARS)} Consumer Price Index Adjusted Dollars) for Census Tracts across Cities and Census-Designated Places in Los Angeles County, {min(ALL_YEARS)} to {max(ALL_YEARS)}")],
             style = {'display': 'block',
                'color': ObsidianBlack_color,
                'margin': '-0.5em 0',
                'padding': '0px 0px 0px 0px',
                'font-family': 'Trebuchet MS, sans-serif',
                'font-size': '100.0%'
               }
            ),
    # Horizontal line rule
    html.Div([html.Hr()],
             style = {'display': 'block',
                'height': '1px',
                'border': 0,
                'margin': '-0.9em 0',
                'padding': 0
               }
            ),
    
    # Dropdowns
    html.Div([
        html.Div([
            dcc.Dropdown(id          = 'place-dropdown',
                         placeholder = 'Select a place',
                         options     = YEAR_PLACE_OPTIONS[2023],
                         value       = 'LongBeach',
                         clearable   = False
                        )
        ], style = {'display': 'inline-block',
                    'margin': '0 0',
                    'padding': '30px 15px 0px 0px',
                    'width': '22.5%'
                   }
                ),
        html.Div([
            dcc.Dropdown(id          = 'year-dropdown',
                         placeholder = 'Select a year',
                         options     = PLACE_YEAR_OPTIONS['LongBeach'],
                         value       = 2023,
                         clearable   = False
                        )
        ], style = {'display': 'inline-block',
                    'margin': '0 0',
                    'padding': '30px 15px 0px 0px',
                    'width': '12.5%',
                   }
                ),
        html.Div([
            dcc.Dropdown(id          = 'demographics-dropdown',
                         placeholder = 'Select a racial demographic',
                         options     = DEMOGRAPHICS_OPTIONS,
                         value       = 'B19013_001E',
                         clearable   = False
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
                    'width': '27.5%'
                   }
                ),
    ], style={"padding": "0px 0px 10px 15px"}, className = 'row'
            ),
    # Map and plot
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
    # Footer
    html.Div([
        fmc.FefferyMarkdown(markdownStr    = footer_string,
                            renderHtml     = True,
                            style          = {'background': LightBrown_color,
                                              'margin-top': '1em'
                                             }
                           )
    ]
            ),
    # Data
    dcc.Store( id = 'MASTERFILE' ),
    dcc.Store( id = 'LAT-LON' ),
    dcc.Store( id = 'YEAR_PLACE_OPTIONS', data = YEAR_PLACE_OPTIONS ),
    dcc.Store( id = 'PLACE_YEAR_OPTIONS', data = PLACE_YEAR_OPTIONS ),
    dcc.Store( id = 'DEMOGRAPHICS_OPTIONS', data = DEMOGRAPHICS_OPTIONS )

], style = {'background-color': LightBrown_color, "padding": "0px 0px 20px 0px",})



# ------------ CALLBACKS ------------ #
#
# Data:
#  place value -> masterfile data
#  year value -> lat/lon center point data
#
# Dropdowns:
#  place value -> year options
#  year options -> default year value
#  place options, year options, map ClickData -> census tract options
#  click data -> census tract value
#
# Titles:
#  place value, year value, demographic value -> map title
#  place value, census tract value -> plot title
#
# Graphs:
#  place value, year value, census tract value, demographic value -> map
#  place value, census tract value, demographic value -> plot
#
# ----------------------------------- #

# -- -- -- --
# Data
# -- -- -- --

# Masterfile
app.clientside_callback(
    """
    async function(selected_place) {
        const url = `https://raw.githubusercontent.com/ramindersinghdubb/Median-Household-Income-in-LA-County/refs/heads/main/data/masterfiles/${selected_place}_masterfile.json`;
        const response = await fetch(url);
        const data = await response.json();
        return data;
    }
    """,
    Output('MASTERFILE', 'data'),
    Input('place-dropdown', 'value')
)

# Latitudinal/longitudinal center points
app.clientside_callback(
    """
    async function(selected_year) {
        const url = `https://raw.githubusercontent.com/ramindersinghdubb/Median-Household-Income-in-LA-County/refs/heads/main/data/lat_lon_center_points/${selected_year}_latlon_center_points.json`;
        const response = await fetch(url);
        const data = await response.json();
        return data;
    }
    """,
    Output('LAT-LON', 'data'),
    Input('year-dropdown', 'value')
)


# -- -- -- --
# Dropdowns
# -- -- -- --

# Place dropdown options
app.clientside_callback(
    """
    function(selected_year, YEAR_PLACE_OPTIONS) {
        return YEAR_PLACE_OPTIONS[selected_year]
    }
    """,
    Output('place-dropdown', 'options'),
    [Input('year-dropdown', 'value'),
     Input('YEAR_PLACE_OPTIONS', 'data')
    ]
)

# Year dropdown options
app.clientside_callback(
    """
    function(selected_place, PLACE_YEAR_OPTIONS) {
        return PLACE_YEAR_OPTIONS[selected_place]
    }
    """,
    Output('year-dropdown', 'options'),
    [Input('place-dropdown', 'value'),
     Input('PLACE_YEAR_OPTIONS', 'data')
    ]
)

# Census tract options
app.clientside_callback(
    """
    function(selected_place, selected_year, MASTERFILE) {
        var options = MASTERFILE.filter(x => x['YEAR'] === selected_year);
        var tract_options = options.map(item => { return item.TRACT });
        return tract_options
    }
    """,
    Output('census-tract-dropdown', 'options'),
    [Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('MASTERFILE', 'data')
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


# -- -- -- --
# Titles
# -- -- -- --

# Map title
app.clientside_callback(
    """
    function(selected_demographic, selected_year, DEMOGRAPHICS_OPTIONS, MASTERFILE) {
        var my_array = MASTERFILE.filter(item => item['YEAR'] === selected_year);
        var city_array = my_array.map(({CITY}) => CITY);
        var selected_city = city_array[0];

        var demographic = DEMOGRAPHICS_OPTIONS.filter(item => item['value'] == selected_demographic);
        var demographic = demographic[0]['label']['props']['children'];

        return [demographic, selected_city, selected_year];
    }
    """,
    [Output('map-title1', 'children'),
     Output('map-title2', 'children'),
     Output('map-title3', 'children')
    ],
    [Input('demographics-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('DEMOGRAPHICS_OPTIONS', 'data'),
     Input('MASTERFILE', 'data'),
    ]
)

# Plot title
app.clientside_callback(
    """
    function(selected_tract, MASTERFILE) {
        if (selected_tract == undefined){
            return "Please click on a tract.";
        } else {
            var selected_city = MASTERFILE[0]['CITY'];
            return `${selected_city}, ${selected_tract}`;
        }
    }
    """,
    Output('plot-title', 'children'),
    [Input('census-tract-dropdown', 'value'),
     Input('MASTERFILE', 'data')
    ]
)


# -- -- --
# Graphs
# -- -- --

# Choropleth map
app.clientside_callback(
    """
    function(selected_demographic, selected_place, selected_year, selected_tract, MASTERFILE, LAT_LON){
        var my_array = MASTERFILE.filter(item => item['YEAR'] == selected_year);
        
        var url_path = `https://raw.githubusercontent.com/ramindersinghdubb/Median-Household-Income-in-LA-County/refs/heads/main/data/mastergeometries/${selected_year}_mastergeometry.geojson`;
        
        var locations_array = my_array.map(({GEO_ID}) => GEO_ID);
        var customdata_array = my_array.map(({TRACT}) => TRACT);

        
        var lat_lon_array = LAT_LON.filter(item => item['ABBREV_NAME'] === selected_place);
        const lon_center = lat_lon_array[0]['LON_CENTER'];
        const lat_center = lat_lon_array[0]['LAT_CENTER'];

        eval(`var z_array = my_array.map( ( {${selected_demographic}} ) => ${selected_demographic});`)
        
        if (selected_demographic == 'B19013_001E') {
            var map_title = "<b style='font-size:15px;'>Overall Population</b>  <br>";
        } else if (selected_demographic == 'B19013A_001E') {
            var map_title = "<b style='font-size:15px;'>White Householders</b>  <br>";
        } else if (selected_demographic == 'B19013B_001E') {
            var map_title = "<b style='font-size:15px;'>Black or African American  <br>Householders</b><br>";
        } else if (selected_demographic == 'B19013C_001E') {
            var map_title = "<b style='font-size:15px;'>American Indian and Alaska  <br>Native Householders</b><br>";
        } else if (selected_demographic == 'B19013D_001E') {
            var map_title = "<b style='font-size:15px;'>Asian Householders</b>  <br>";
        } else if (selected_demographic == 'B19013E_001E') {
            var map_title = "<b style='font-size:15px;'>Native Hawaiian and Other  <br>Pacific Islander Householders</b><br>";
        } else if (selected_demographic == 'B19013F_001E') {
            var map_title = "<b style='font-size:15px;'>Some Other Race Householders</b>  <br>";
        } else if (selected_demographic == 'B19013G_001E') {
            var map_title = "<b style='font-size:15px;'>Two or More Races Householders</b>  <br>";
        } else if (selected_demographic == 'B19013H_001E') {
            var map_title = "<b style='font-size:15px;'>White Alone, Not Hispanic or  <br>Latino Householders</b><br>";
        } else if (selected_demographic == 'B19013I_001E') {
            var map_title = "<b style='font-size:15px;'>Hispanic or Latino Householders</b>  <br>";
        }


        var strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['TRACT'] + "</b><br>" + item['CITY'] + ", Los Angeles County<br><br>"
            + map_title
            + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item[`${selected_demographic}_string`] + "</b>  <br>"
            + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item[`${selected_demographic.replace('_001E', '_001M')}_string`] + "</b>  <br>"
            + "<extra></extra>";
        });
        
        var data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Greens',
            'reversescale': true,
            'z': z_array,
            'zmin': 0, 'zmax': 200000,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.7},
            'text': strings,
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
            var aux_array = my_array.filter(item => item['TRACT'] === selected_tract);
            var aux_locations_array = aux_array.map(({GEO_ID}) => GEO_ID);
            var aux_z_array = aux_array.map(({dummy})=>dummy);
                
            var aux_data = {
                'type': 'choroplethmap',
                'geojson': url_path,
                'locations': aux_locations_array,
                'featureidkey': 'properties.GEO_ID',
                'colorscale': [[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],
                'showscale': false,
                'z': aux_z_array,
                'zmin': 0, 'zmax': 1,
                'marker': {'line': {'color': '#E3242B', 'width': 4}},
                'selected': {'marker': {'opacity': 0.4}},
                'hoverinfo': 'skip',
            }
            data.push(aux_data);
        }

        return {'data': data, 'layout': layout};

    }
    """,
    Output('chloropleth_map', 'figure'),
    [Input('demographics-dropdown', 'value'),
     Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('census-tract-dropdown', 'value'),
     Input('MASTERFILE', 'data'),
     Input('LAT-LON', 'data'),
    ]
)



# Plot
app.clientside_callback(
    """
    function(selected_demographic, selected_place, selected_tract, MASTERFILE){        
        if (selected_tract != undefined) {
            var my_array = MASTERFILE.filter(item => item['TRACT'] === selected_tract);
            var my_array = my_array.sort((a, b) => a.YEAR - b.YEAR);

            var x_array = my_array.map( ({YEAR}) => YEAR );
            eval(`var y_array = my_array.map( ( { ${selected_demographic} } ) => ${selected_demographic});`)

            if (selected_demographic == 'B19013_001E') {
                var plot_title_text = "<b style='font-size:15px;'>Overall Population</b>  <br>";
            } else if (selected_demographic == 'B19013A_001E') {
                var plot_title_text = "<b style='font-size:15px;'>White Householders</b>  <br>";
            } else if (selected_demographic == 'B19013B_001E') {
                var plot_title_text = "<b style='font-size:15px;'>Black or African American  <br>Householders</b><br>";
            } else if (selected_demographic == 'B19013C_001E') {
                var plot_title_text = "<b style='font-size:15px;'>American Indian and Alaska  <br>Native Householders</b><br>";
            } else if (selected_demographic == 'B19013D_001E') {
                var plot_title_text = "<b style='font-size:15px;'>Asian Householders</b>  <br>";
            } else if (selected_demographic == 'B19013E_001E') {
                var plot_title_text = "<b style='font-size:15px;'>Native Hawaiian and Other  <br>Pacific Islander Householders</b><br>";
            } else if (selected_demographic == 'B19013F_001E') {
                var plot_title_text = "<b style='font-size:15px;'>Some Other Race Householders</b>  <br>";
            } else if (selected_demographic == 'B19013G_001E') {
                var plot_title_text = "<b style='font-size:15px;'>Two or More Races Householders</b>  <br>";
            } else if (selected_demographic == 'B19013H_001E') {
                var plot_title_text = "<b style='font-size:15px;'>White Alone, Not Hispanic or  <br>Latino Householders</b><br>";
            } else if (selected_demographic == 'B19013I_001E') {
                var plot_title_text = "<b style='font-size:15px;'>Hispanic or Latino Householders</b>  <br>";
            }

            var strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['TRACT'] + ", " + item['CITY'] + " <br><br>"
                + plot_title_text
                + "Median Household Income: <b style='font-size:14px; color:#597D35'>" + item['B19013_001E_string'] + "</b>  <br>"
                + "Margin of Error: <b style='font-size:14px; color:#597D35'>"         + item['B19013_001M_string'] + "</b>  <br>"
                + "<extra></extra>";
            });
            

            var data = [{
                'type': 'scatter',
                'x': x_array,
                'y': y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': strings,
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
                'title': {'text': `Median Household Income (CPI-Adjusted Dollars), ${Math.min(...x_array)} to ${Math.max(...x_array)}`,
                          'x': 0.05,
                          },
                'xaxis': {'title': {'text': 'Year', 'ticklabelstandoff': 10}, 'showgrid': false, 'tickvals': x_array},
                'yaxis': {'title': {'text': 'Median Household Income ($)', 'standoff': 15}, 'tickprefix': '$', 'gridcolor': '#E0E0E0', 'ticklabelstandoff': 5},
            };

            return {'data': data, 'layout': layout};
        }
    }
    """,
    Output('income_plot', 'figure'),
    [Input('demographics-dropdown', 'value'),
     Input('place-dropdown', 'value'),
     Input('census-tract-dropdown', 'value'),
     Input('MASTERFILE', 'data')
    ]
)







# Execute the app
if __name__ == "__main__":
    app.run(debug=False)
