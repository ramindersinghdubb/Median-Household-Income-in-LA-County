import os
import pandas as pd
from datetime import datetime
from util_func import (
    masterfiles_folder,
    masterfile_creation,
    cpi_adjust_cols,
    mastergeometry_creation,
    lat_lon_center_points,
)

# Masterfile creation
ACS_Codes = ['B19013'] + [f'B19013{chr(i)}' for i in range(ord('A'), ord('I') + 1)]
masterfile_creation(ACS_Codes, API_key = os.environ['SECRET_KEY'])

# Dollar-adjusting columns
cpi_adjust_cols(ACS_Codes, 'B19013')

# Formatting
ABBREV_NAMES = [file.split('_')[0] for file in os.listdir(masterfiles_folder) if 'masterfile.csv' in file]

for ABBREV_NAME in ABBREV_NAMES:
    CSV_file_path = f'{masterfiles_folder}{ABBREV_NAME}_masterfile.csv'
    df = pd.read_csv(CSV_file_path)
    
    # String formatting for the hovertext
    selected_columns = [col for col in df.columns if 'B19013' in col]
    for col in selected_columns:
        col_string = f'{col}_string'
        df[col_string] = '$' + df[col].astype(str)
        df[col_string] = df[col_string].str.replace('.0', '')
        df.loc[df[col_string] == '$nan', col_string] = 'Not available'
        df.loc[df[col_string] == '$250001', col_string] = 'Not available. Exceeds $250K!' # Income imputation capped at $250k
    
    # For the trace
    df['dummy'] = 1

    df.to_csv(CSV_file_path, index = False)

    JSON_file_path = f'{masterfiles_folder}{ABBREV_NAME}_masterfile.json'
    df.to_json(JSON_file_path, orient='records')

# Mastergeometry creation
mastergeometry_creation()

# Accompanying latitudinal and longitudinal center points
lat_lon_center_points()