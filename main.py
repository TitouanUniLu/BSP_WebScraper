from bs4 import BeautifulSoup
from bs4 import Comment
import requests
import pandas
import re
import time
import csv
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

''' downloading the required NLTK dependencies '''
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

''' CREATING A LIST OF ALL WEBSITE FROM THE XLSX FILE '''
workbook = pandas.read_excel('ALL_INDICES-2021.xlsx')
df = pandas.DataFrame(workbook)
website_list = df['Company website'].tolist()
board_web_list = df['Website Board of Directors'].tolist()
all_regular_expressions = df.columns[2:len(df.columns)-4].tolist()

''' clear the regex given to something python can read'''
for i in range(0, len(all_regular_expressions)-1):
    all_regular_expressions[i] = all_regular_expressions[i].replace("OR", "|")
    all_regular_expressions[i] = all_regular_expressions[i].replace("+", " ")  # is plus a space in the expression??
    all_regular_expressions[i] = all_regular_expressions[i].replace("AND", "+")
    all_regular_expressions[i] = all_regular_expressions[i].replace("%22", "")
    #all_regular_expressions[i] = all_regular_expressions[i].replace(" ", "")
    #print(all_regular_expressions[i], bool(re.compile(all_regular_expressions[i])))
    # until index 23 we don't have AND

''' use only temporarly until AND operator is fixed'''
#temp_regex = all_regular_expressions[0:24]
temp_regex = all_regular_expressions

# broken websites
broken_websites = ["http://www.intel.fr/", "http://wwwb.comcast.com/", "http://www.costco.com/", "http://www.catamaranrx.com/",
                   "http://www.biogenidec.com/", "http://www.analog.com/", "http://www.akamai.com/", "http://www.altera.com/",
                   "http://www.lgi.com/", "http://www.linear.com/", "http://www.adobe.com/", "http://www.sigmaaldrich.com/"]
'''for website in broken_websites:
    website_list.remove(website)
'''
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
}


''' return all the content we need by looking at the tags in the html body '''
def tag_visible(element):
    # invisible elements
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):  # check if its a comment
        return False
    return True

''' get all text in html body of a website'''
def text_from_html(body):
    soup = BeautifulSoup(body, 'lxml')
    texts = soup.findAll(text=True)
    # second function call, to check if text is visible
    visible_texts = filter(tag_visible, texts)
    # .strip() removes extra spaces
    return u" ".join(t.strip() for t in visible_texts)


''' returns all links from the main website scraped with the same domain (no duplicates) '''
def get_sub_links(html_request, website):
    soup = BeautifulSoup(html_request, 'lxml')
    all_sub_links = []
    CAP = 100000    #variable to avoid having too many website, change value if needed
    
    for link in soup.find_all('a', attrs={'href': re.compile("^https://")}):
        link = link.get('href')
        if website in link and link not in all_sub_links and not link.endswith('.pdf'):
            #print(link)
            all_sub_links.append(link)
    return all_sub_links[0:CAP]

''' GET AMOUNT OF KEYWORDS PER RE FOR A WEBSITE'''
def occurencePerWebsite(website, regex_list):
    data = []
    try:
        #print("\nWebsite scraped: ", website)
        html_request = requests.get(website, headers=headers, timeout=10).text
        #print("error: " + str(requests.get(website, headers=headers, timeout=10).raise_for_status()))

        #get all text from wepage (and lowercase it)
        all_html_text = text_from_html(html_request).lower()

        #find all occurences of word usign RE
        for i in range(0,len(regex_list)):
            matches = re.findall(re.compile(regex_list[i]), all_html_text)
            #print(regex, len(matches))         #debug line
            #for elem in matches: print(elem)
            data.append(len(matches))
        return data
                  
    except Exception as e:
        print(e)

''' ADD THE SUB WEBSITE RESULTS TO MAIN WEBSITE RESULTS'''
def sumResults(fullData, subData):
    for i in range(0, len(fullData)):
        fullData[i] += subData[i]
    return fullData


''' MAIN LOOP TO RUN TO OBTAIN RESULTS '''
def mainLoop(list, regex_list, file):
    writer = csv.writer(file)

    #black_list = ['https://www.ebay.com/feed', 'https://www.ebay.com/myb/SavedSellers', 'https://www.ebay.com/myb/SavedSearches',
    #'https://www.microchip.com/en-us/products/embedded-controllers-and-super-io']


    header = ["Website Name", "Amount of Sub-Websites"]
    for elem in regex_list:
        header.append(elem)
    writer.writerow(header)

    start_time = time.time()
    for website in list:
        print("Main website scraped: ", website)
        #print(str(requests.get(website).raise_for_status()))

        data = [0] * len(regex_list)
        #print(data)
        website_domain = re.findall('//(.*)/', website)[0]

        try:
            #print("error: " + str(requests.get(website).raise_for_status()))
            
            html_request = requests.get(website, headers=headers, timeout=10).text

            #find all sub links hidden or visible in the website
            all_websites = get_sub_links(html_request, website_domain)
            print(len(all_websites))

            '''for elem in black_list: 
                if elem in all_websites: all_websites.remove(elem)'''

            #print("The amount of sub-websites that will be scraped is: ", len(all_websites))
            print("amount of websites that will be scraped in same domain:  ", len(all_websites))
            for sub_website in all_websites:
                #data.append(sub_website)
                #print(sub_website)
                tempData = occurencePerWebsite(sub_website, regex_list)
                data = sumResults(data, tempData)
                #print(data)
            data = [website] + [len(all_websites)] + data
            print('\n', data)
            writer.writerow(data)
        
        except Exception as e:
            print("error: ", e) 
            '''for i in range(0, len(header)-1):
                data.append("error")'''
            data = [website] + [len(all_websites)] + data
            #data.append("error")
            writer.writerow(data)


        print("Time elapsed:", round(time.time()-start_time, 0), 'secs \n \n')
        # os.system('cls')

def getDirectorsNames(website_list):
    for website in website_list:
        all_names = []
        try:
            html_request = requests.get(website, headers=headers, timeout=5).text
            text = text_from_html(html_request)
            #print(text)
            #time.sleep(50)

            '''nltk_results = ne_chunk(pos_tag(word_tokenize(text)))
            for nltk_result in nltk_results:
                if type(nltk_result) == Tree and nltk_result.label() == 'PERSON':
                    name = ''
                    for nltk_result_leaf in nltk_result.leaves():
                        name += nltk_result_leaf[0] + ' '
                        print ('Type: ', nltk_result.label(), 'Name: ', name) 
                    if name not in all_names: all_names.append(name)
            print(website, all_names)'''
            tokens = nltk.tokenize.word_tokenize(text)
            pos = nltk.pos_tag(tokens)
            sentt = nltk.ne_chunk(pos, binary = False)
            person_list = []
            person = []
            name = ""
            for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
                for leaf in subtree.leaves():
                    person.append(leaf[0])
                if len(person) > 1: #avoid grabbing lone surnames
                    for part in person:
                        name += part + ' '
                    if name[:-1] not in person_list:
                        person_list.append(name[:-1])
                    name = ''
                person = []
            print(website, person_list, '\n\n')
        except Exception as e:
            print(e)

    return True

''' MAIN '''
if __name__ == "__main__":
    print("\n-- STARTING THE PROGRAM --")
    file = open('results.csv', 'w', newline='')
    print(getDirectorsNames(board_web_list))
    time.sleep(20)
    mainLoop(website_list, temp_regex, file)

    
