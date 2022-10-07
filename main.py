from bs4 import BeautifulSoup
from bs4 import Comment
import requests
import pandas
import re
import time
import multiprocessing

#CREATING A LIST OF ALL WEBSITE FROM THE XLSX FILE
workbook = pandas.read_excel('ALL_INDICES-2021.xlsx')
df = pandas.DataFrame(workbook, columns=['Company website'])
website_list = df['Company website'].tolist()

#return true or false if the element is visible or not
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']: #invisible elements
        return False
    if isinstance(element, Comment): #check if its a comment
        return False
    return True

#return all the text of the html body
def text_from_html(body):
    soup = BeautifulSoup(body, 'lxml')
    texts = soup.findAll(text=True)     
    visible_texts = filter(tag_visible, texts) #second function call, to check if text is visible 
    return u" ".join(t.strip() for t in visible_texts)  #.strip() removes extra spaces

#get word to look for
def mainLoop():
    try:
        userInput = input("What word do you want to look for?   ").lower()
        start_time=time.time()
        for website in website_list:
            html_request = requests.get(website).text

            #get all text from wepage (and lowercase it)
            all_html_text = text_from_html(html_request).lower()

            #find all occurences of word usign RE
            matches = re.findall(userInput, all_html_text)

            print("\nWord occurences: ", len(matches),
                "\nWebsite scraped: ", website)
            
            print("\nTime elapsed:",round(time.time()-start_time,0),'secs',end='\n')
    except Exception as e:
        print("little error but should be fine :)\n")

if __name__ == "__main__":
    print("-- STARTING THE PROGRAM --")
    mainLoop()