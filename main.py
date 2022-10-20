from bs4 import BeautifulSoup
from bs4 import Comment
import requests
import pandas
import re
import time
import csv
import os
import urllib.request

#CREATING A LIST OF ALL WEBSITE FROM THE XLSX FILE
workbook = pandas.read_excel('ALL_INDICES-2021.xlsx')
df = pandas.DataFrame(workbook)
website_list = df['Company website'].tolist()
board_web_list = df['Website Board of Directors'].tolist()
all_regular_expressions = df.columns[2:len(df.columns)-4].tolist()


for i in range(0, len(all_regular_expressions)-1):
    all_regular_expressions[i] = all_regular_expressions[i].replace("OR", "|")
    all_regular_expressions[i] = all_regular_expressions[i].replace("+", " ") #is plus a space in the expression??
    all_regular_expressions[i] = all_regular_expressions[i].replace("%22", "")
    #until index 23 we don't have AND

temp_regex = all_regular_expressions[0:23]

#broken websites
broken_websites = ["http://www.intel.fr/", "http://wwwb.comcast.com/", "http://www.costco.com/", "http://www.catamaranrx.com/", 
                    "http://www.biogenidec.com/", "http://www.analog.com/", "http://www.akamai.com/", "http://www.altera.com/",
                    "http://www.lgi.com/", "http://www.linear.com/", "http://www.adobe.com/", "http://www.sigmaaldrich.com/"]
for website in broken_websites:
    website_list.remove(website)

'''new ^( product _ service _ pro-
355 cess _ application _ solution _ feature _ release _ version _ launch

356 _ introduction _ introduce _ ‘‘new product’’ _ ‘‘new service’’ _
357 ‘‘new process’’).'''

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

def get_sub_links(html_request, website):
    soup = BeautifulSoup(html_request, 'lxml')
    all_sub_links = []
    for link in soup.find_all('a', attrs={'href': re.compile("^https://")}):
        #link = str(link)
        #if website in link:
        all_sub_links.append(link.get('href'))
    return all_sub_links


file = open('results.csv', 'w', newline='')
writer = csv.writer(file)

#get word to look for
def mainLoop(list, regex_list, file):
    start_time=time.time()
    header = ["Website Name"]
    for elem in regex_list: header.append(elem)
    writer.writerow(header)
    for website in list:
        print("\nWebsite number", list.index(website)+1, "scraped: ", website)
        data = []
        data.append(website)
        try:
            error_msg = "error: " + str(requests.get(website).raise_for_status())
            print(error_msg)
            html_request = requests.get(website).text

            #get all text from wepage (and lowercase it)
            all_html_text = text_from_html(html_request).lower()

            #find all sub links hidden or visible in the website
            website_sub_links = get_sub_links(html_request, website)
            for link in website_sub_links:
                print(link)
            #time.sleep(5)


            #find all occurences of word usign RE
            for regex in regex_list:
                matches = re.findall(re.compile(regex), all_html_text)
                #print(regex+":", len(matches))
                data.append(len(matches))
            #ex for garmin.com, i get results (which are true) unlike the results in all_indices.xlsx
            writer.writerow(data)
            
            
        except Exception as e:
            print("error: ", e) 
            for i in range(0, len(header)-1):
                data.append("error")
            writer.writerow(data)
        
        print("Time elapsed:",round(time.time()-start_time,0),'secs',end='\n')
        #os.system('cls')
       

if __name__ == "__main__":
    print("-- STARTING THE PROGRAM --")
    mainLoop(website_list, temp_regex, file)