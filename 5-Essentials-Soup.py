#
# scraping 5 essentials website, 2018 public report
#

import requests
import re
from bs4 import BeautifulSoup
import json
import pandas
from pandas import json_normalize
import re
import numpy as np

##### Set these constants before running #####
reportyr = 2018

# source: Chicago data portal...update with different years or filter for specific school subsets if desired

schls = pandas.read_csv("data/Chicago_Public_Schools_-_School_Profile_Information_SY1819.csv")
schl_ids = schls["School_ID"]

outpath = "/Users/mercedeswentworth-nice/Documents/Spring Quarter 2020/PBPL 26303/fiveE2018.csv"

##### Funcs #####
def get5Edescription(s):
    s = str(s)
    start = s.find("<br>") + len("<br>")
    end = s.find(".")
    substring = s[start:end]
    return substring

def enumerateYear(x, reportyr):
    if type(x) == list:
        for i in range(0,len(x)):
            if type(x[i]) == list:
                x[i].insert(0, reportyr-i)
    return x

def getSchoolData(cpsid, year):
    # grab page
    page = requests.get("https://www.5-essentials.org/cps/5e/" + str(reportyr) + "/s/"+ str(cpsid) + "/measures/")

    soup = BeautifulSoup(page.content, 'html.parser')

    if soup.find("title").get_text() == "Page Not Found":
        return pandas.DataFrame([])
    else: 
        # get data, in json object form
        data = soup.find(id="data")

        # get title node and extract school name
        title = soup.find("title").text
        schlname = " ".join(filter(lambda x: x != "", re.split("\n| |\t|5Essentials|Report", title)))

        # extract measures from object and convert to pandas data frame
        jsonObj = json.loads(data['data-data'])
        measures = jsonObj["measures"]
        df = json_normalize(measures)

        # clean data frame
        df.insert(0, "schlname", [schlname]*len(df.index))
        df.insert(5, "description", df["text.overview.__html"].apply(get5Edescription))
        df = df.filter(items = ["schlname","name","level", "stem", "description", "subject", "data.all"])
        df = df.applymap(lambda x : enumerateYear(x, 2018))
        df = df.explode("data.all")
        df["year"] = df["data.all"].apply(lambda x: x[0] if type(x) == list else x)
        df["data.all"] = df["data.all"].apply(lambda x: x[1] if type(x) == list else x)
        df["School_ID"] = cpsid
        return df

##### Scrape #####
schl_data = []
for i in schl_ids:
    print(i)
    schl_data.append(getSchoolData(i, reportyr))    

pandas.concat(schl_data).to_csv(outpath)

