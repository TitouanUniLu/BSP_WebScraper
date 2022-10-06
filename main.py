from bs4 import BeautifulSoup
from bs4 import Comment
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

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

all_html_text = text_from_html(html_requests)
#all_results = all_html_text.find(text=re.compile('we'))
string_occurence = all_html_text.count("We")
print(string_occurence)






