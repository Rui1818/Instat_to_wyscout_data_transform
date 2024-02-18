from instat_to_wyscout_pandas import *
from pandas_to_json import *
import warnings


#function to transform a Instat event data file into Wyscout format. 
#Takes the path from the Instat file and the desired name for the final json file as argument

def final_transform(path, filename):
    warnings.filterwarnings('ignore')
    dataframe= pandas_transform(path)
    pandas_to_json(dataframe, filename)