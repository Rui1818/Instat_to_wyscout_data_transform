# Instat to wyscout rawdata transform

This code aims to transform Instat rawdata (xml) into wyscout eventdata (json). Code is written and tested for Python 3.10.4 and Pandas 2.1.1. For the transformation use the final_transform function in final_transform.py file with the file path and the resulting file name as input. 

## Additional information

Important files are:
- instat_to_wyscout_pandas.py: Reads an xml file and transforms it to a pandas Dataframe. Afterwards the dataframe is manipulated and turned into a wyscout-like dataframe.
- transformations.py: here are all important helper functions for the manipulation of the dataframe.
- pandas_to_json.py: transforms the processed dataframe to a wyscout compatible json file

Instat positions and action names can be found in Instat_information folder. 
A documentation for how the action tags are extracted and how the transformation is derived can be found in the Documentation file.

## How to use
To use the code first clone the repository and install all dependencies (numpy, pandas). Afterwards import the final_transform function from final_transform.py and run it with the path name of the Instat event file and the desired target name as input. The notebook example in the repository shows how to use it. 
