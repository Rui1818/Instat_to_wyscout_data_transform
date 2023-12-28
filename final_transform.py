from instat_to_wyscout_pandas import *
from pandas_to_json import *
import warnings


def final_transform(path, filename):
    warnings.filterwarnings('ignore')
    dataframe= pandas_transform(path)
    pandas_to_json(dataframe, filename)