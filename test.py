import re
from pprint import pprint
import requests
from infoExtractor import *
import pandas as pd
import json


if __name__ == "__main__":
    path = "text/仲裁申请书/jpg(100)/5107.txt"
    a = {}
    # with open(path) as f:
    #     lines = lines_sort(f.readlines())
    #     name_extractor2(lines)
