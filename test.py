import re
from pprint import pprint
import requests
from infoExtractor import *
import pandas as pd
import json
import fool


if __name__ == "__main__":
    path = "text/仲裁申请书/jpg(100)/5079.txt"
    
    role, part = [], [[1]]
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df1, df2 = extractor2(df1, df2, "text/仲裁申请书/jpg(100)", "5079.txt")
    a = "dassadad"
    print(a.split())