from bs4 import BeautifulSoup
import requests
import pandas
import re

#CREATING A LIST OF ALL WEBSITE FROM THE XLSX FILE
workbook = pandas.read_excel('ALL_INDICES-2021.xlsx')
df = pandas.DataFrame(workbook, columns=['Company website'])
website_list = df['Company website'].tolist()

#CURRENTLY ONLY LOOKING ONLY IN THE FIRST LINK 
html_requests = requests.get(website_list[0]).text
soup = BeautifulSoup(html_requests, 'lxml')

string_occurence = 0
all_results = soup.find(text=re.compile('we'))
try:
    for result in all_results:
        string_occurence += 1
except:
    print("list is empty...")

print(string_occurence)





