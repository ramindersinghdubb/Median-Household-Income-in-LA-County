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


# Dollar-adjusting columns
cpi_adjust_cols(ACS_Codes, col_strings = 'B19013')
logger.info('Inflation adjusted columns in masterfiles')

# Mastergeometry creation
mastergeometry_creation()
logger.info('Created accompanying mastergeometries')

# Accompanying latitudinal and longitudinal center points
lat_lon_center_points()
logger.info('Created latitudinal/longitudinal center points')