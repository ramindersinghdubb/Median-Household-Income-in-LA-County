import os
import pandas as pd
from dash import dcc, html
from datetime import datetime


ref_df = pd.read_csv('data/reference.txt', sep='|')

# --
# Dropdown options
# --

ALL_ABBREV_NAMES = list(ref_df['ABBREV_NAME'])
ALL_PLACES_OPTIONS = [{'label': html.Span([i], style = {'color': '#151E3D'}), 'value': j} for i, j in zip(ref_df['CITY'], ALL_ABBREV_NAMES)]

ALL_YEARS = list(range(min(ref_df['INITIAL_YEAR']), max(ref_df['RECENT_YEAR']) + 1))
ALL_YEARS_OPTIONS = [{'label': html.Span([i], style = {'color': '#151E3D'}), 'value': i} for i in ALL_YEARS]

# Generate available year options for the selected place
PLACE_YEAR_OPTIONS = {}
for ABBREV_NAME in ALL_ABBREV_NAMES:
    int_year = ref_df.loc[ref_df['ABBREV_NAME'] == ABBREV_NAME, 'INITIAL_YEAR'].iloc[0]
    rec_year = ref_df.loc[ref_df['ABBREV_NAME'] == ABBREV_NAME, 'RECENT_YEAR'].iloc[0]

    avail_years = list(range(int_year, rec_year + 1))
    unavail_years = [i for i in ALL_YEARS if i not in avail_years]

    year_options = [dict(item, **{'disabled': True}) if item['value'] in unavail_years else dict(item) for item in ALL_YEARS_OPTIONS]

    PLACE_YEAR_OPTIONS[ABBREV_NAME] = year_options

# Generate available place options for the selected year
files = [f'data/masterfiles/{file}' for file in os.listdir('data/masterfiles/') if file.endswith('masterfile.csv')]
df_list = []
for file in files:
    df_list.append( pd.read_csv(file) )
df = pd.concat(df_list, ignore_index = True)

YEAR_PLACE_OPTIONS = {}
for YEAR in ALL_YEARS:
    dummy_df = df[df['YEAR'] == YEAR]

    avail_places = list(dummy_df['ABBREV_NAME'].unique())
    unavail_places = [i for i in ALL_ABBREV_NAMES if i not in avail_places]

    place_options = [dict(item, **{'disabled': True}) if item['value'] in unavail_places else dict(item) for item in ALL_PLACES_OPTIONS]

    YEAR_PLACE_OPTIONS[YEAR] = place_options

# Demographic options
DEMOGRAPHICS = [
    'Overall Population',
    'White Householders',
    'Black or African American Householders',
    'American Indian and Alaska Native Householders',
    'Asian Householders',
    'Native Hawaiian and Other Pacific Islander Householders',
    'Some Other Race Householders',
    'Two or More Races Householders',
    'White Alone, Not Hispanic or Latino Householders',
    'Hispanic or Latino Householders'
]
ACS_CODES = ['B19013_001E'] + [f'B19013{chr(i)}_001E' for i in range(ord('A'), ord('I') + 1)]
DEMOGRAPHICS_OPTIONS = [{'label': html.Span([i], style = {'color': '#151E3D'}), 'value': j} for i, j in zip(DEMOGRAPHICS, ACS_CODES)]

# -- -- -- -- --
# Footer string
# -- -- -- -- --
footer_string = f"""
### <b style='color:#800000;'>Information</b>

This website allows you to view median household income in the past 12 months (in {max(ALL_YEARS)} Consumer Price Index-adjusted dollars) for various census tracts across various cities in Los Angeles county. <br>

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

2. Data for median household income in the past 12 months (in {max(ALL_YEARS)} inflation-adjusted dollars) were taken from the United States Census Bureau <u style='color:#800000;'><a href="https://www.census.gov/programs-surveys/acs.html" style='color:#800000;'>American Community Survey</a></u> (ACS codes B19013, B19013A, B19013B, B19013C, B19013D, B19013E, B19013F, B19013G, B19013H and B19013I). Adjustment to {max(ALL_YEARS)} Consumer Price Index-dollars is conducted with the <u style='color:#800000;'><a href="https://www.census.gov/topics/income-poverty/income/guidance/current-vs-constant-dollars.html" style='color:#800000;'>Consumer Price Index Retroactive Series (R-CPI-U-RS)</a></u>.
3. Redistricting over the years affects the availability of some census tracts in certain cities. Unavailability of data for certain census tracts during select years may affect whether or not census tracts are displayed on the map. For these reasons, some census tracts and their data may only be available for a partial range of years.

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

© {datetime.now().year} Raminder Singh Dubb
"""

# -- -- -- --
# Containers
# -- -- -- --

# Container for geospatial choropleth map
geodata_map = html.Div([
    dcc.Graph(
        id = "chloropleth_map",
        config={'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d', 'resetview'],
                'displaylogo': False
               },
    )
])

# Container for income plot
geodata_plot = html.Div([
    dcc.Graph(
        id = "income_plot",
        config={'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d', 'resetview'],
                'displaylogo': False
               },
    )
])