import os
import numpy as np
import pandas as pd
from datetime import datetime
from util_func import (
    masterfiles_folder,
    masterfile_creation,
    cpi_adjust_cols,
    mastergeometry_creation,
    lat_lon_center_points,
)

import logging

logger = logging.getLogger(__name__)
logger.setLevel("INFO")
console_handler = logging.StreamHandler()
logger_fmt = logging.Formatter(
    fmt     = "%(asctime)s - %(name)s (%(filename)s, Line %(lineno)s): %(levelname)s - %(message)s",
    datefmt = "%m-%d-%Y, %I:%M:%S %p"
)
console_handler.setFormatter(logger_fmt)
logger.addHandler(console_handler)


# Masterfile creation
ACS_Codes = ['B19013'] + [f'B19013{chr(i)}' for i in range(ord('A'), ord('I') + 1)]
masterfile_creation(ACS_Codes, API_key = os.environ['SECRET_KEY'], batch_size = 400)
logger.info('Masterfiles created for ACS Codes: %s', ACS_Codes)

# Pre-adjustment formatting
for ACS_code in ACS_Codes:
    for root, dirs, files in os.walk(f'{masterfiles_folder}ACS_Codes/{ACS_code}'):
        for file in files:
            ACS_file_path = os.path.join(root, file)
            df = pd.read_csv( ACS_file_path )
            for col in [col for col in df.columns if 'B19013' in col]:
                df.loc[df[col] == 250001, col] = np.nan
            df.to_csv(ACS_file_path, index = False)

# Dollar-adjusting columns
cpi_adjust_cols(ACS_Codes, col_strings = 'B19013')
logger.info('Inflation adjusted columns in masterfiles')

# Post-adjustment formatting
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

    df = df.sort_values(by = ['YEAR', 'GEO_ID'], ignore_index = True)

    df.to_csv(CSV_file_path, index = False)

    JSON_file_path = f'{masterfiles_folder}{ABBREV_NAME}_masterfile.json'
    df.to_json(JSON_file_path, orient='records')

# Mastergeometry creation
mastergeometry_creation()
logger.info('Created accompanying mastergeometries')

# Accompanying latitudinal and longitudinal center points
lat_lon_center_points()
logger.info('Created latitudinal/longitudinal center points')