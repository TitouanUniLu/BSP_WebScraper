from bs4 import BeautifulSoup
from bs4 import Comment
import requests
import pandas
import re
import time

#CREATING A LIST OF ALL WEBSITE FROM THE XLSX FILE
workbook = pandas.read_excel('ALL_INDICES-2021.xlsx')
df = pandas.DataFrame(workbook, columns=['Company website'])
website_list = df['Company website'].tolist()
broken_websites = ["http://www.intel.fr/", "http://wwwb.comcast.com/", "http://www.costco.com/", "http://www.catamaranrx.com/", 
                    "http://www.biogenidec.com/", "http://www.analog.com/", "http://www.akamai.com/", "http://www.altera.com/",
                    "http://www.lgi.com/", "http://www.linear.com/", "http://www.adobe.com/", "http://www.sigmaaldrich.com/"]
for website in broken_websites:
    website_list.remove(website)

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
def mainLoop(list):
    userInput = input("What word do you want to look for?   ").lower()
    start_time=time.time()
    for website in list:
        print("\nWebsite number", list.index(website), "scraped: ", website)
        try:
            print("error: ", requests.get(website).raise_for_status())
            html_request = requests.get(website).text

            #get all text from wepage (and lowercase it)
            all_html_text = text_from_html(html_request).lower()

            #find all occurences of word usign RE
            matches = re.findall(userInput, all_html_text)

            print("Word occurences: ", len(matches))
            
        except Exception as e:
            print("error: ", e) 
        
        print("Time elapsed:",round(time.time()-start_time,0),'secs',end='\n')
       

if __name__ == "__main__":
    print("-- STARTING THE PROGRAM --")
    mainLoop(website_list)