from instat_to_wyscout_pandas import *
from pandas_to_json import *


def final_transform(path, filename):
    dataframe= pandas_transform(path)
    pandas_to_json(dataframe, filename)