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
masterfile_creation(ACS_Codes, API_key = os.environ['SECRET_KEY'], batch_size = 400)

# Dollar-adjusting columns
cpi_adjust_cols(ACS_Codes, col_strings = 'B19013')

# Mastergeometry creation
mastergeometry_creation()

# Accompanying latitudinal and longitudinal center points
lat_lon_center_points()