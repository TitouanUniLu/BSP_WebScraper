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
from names_dataset import NameDataset, NameWrapper
import gender_guesser.detector as gender

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
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


''' returns all links from the main website scraped with the same domain (no duplicates) '''
def get_sub_links(html_request, website):
    soup = BeautifulSoup(html_request, 'lxml')
    all_sub_links = []
    CAP = 500    #variable to avoid having too many website, change value if needed
    
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
        html_request = requests.get(website, headers=headers, timeout=5).text

        all_html_text = text_from_html(html_request).lower()

        #find all occurences of word usign RE
        for i in range(0,len(regex_list)):
            matches = re.findall(re.compile(regex_list[i]), all_html_text)
            #print(regex, len(matches))         #debug line
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
    header = ["Website Name", "Amount of Sub-Websites"]
    for elem in regex_list:
        header.append(elem.lower())
    writer.writerow(header)
    start_time = time.time()
    for website in list:
        print("Main website scraped: ", website)

        data = [0] * len(regex_list)
        website_domain = re.findall('//(.*)', website)[0]
        print(website_domain)
        try:           
            html_request = requests.get(website, headers=headers, timeout=5).text

            all_websites = get_sub_links(html_request, website_domain)
            print(len(all_websites))

            print("amount of websites that will be scraped in same domain:  ", len(all_websites))
            for sub_website in all_websites:

                tempData = occurencePerWebsite(sub_website, regex_list)
                data = sumResults(data, tempData)
            data = [website] + [len(all_websites)] + data
            print('\n', data)
            writer.writerow(data)
        
        except Exception as e:
            print("error: ", e) 
            data = [website] + [len(all_websites)] + data
            writer.writerow(data)

        print("Time elapsed:", round(time.time()-start_time, 0), 'secs \n \n')


def directorGender(list):
    d = gender.Detector()
    checked_directors = []
    gender_count = [0, 0, 0] # male - female -androgynous
    possible_outcomes = ['andy', 'male', 'female', 'mostly_male', 'mostly_female']
    for dir in list:
        first_name = dir.split()[0]
        last_name = dir.split()[1]
        if d.get_gender(first_name) in possible_outcomes: # and d.get_gender(last_name) in possible_outcomes:
            checked_directors.append(dir)
            if d.get_gender(first_name) == 'andy':
                gender_count[2] += 1
            if d.get_gender(first_name) in ['male', 'mostly_male']:
                gender_count[0] += 1
            if d.get_gender(first_name) in ['female', 'mostly_female']:
                gender_count[1] += 1
            #print(d.get_gender(first_name))
    return checked_directors, gender_count


def getDirectorsNames(website_list):
    writer.writerow(['website address', 'male', 'female', 'androgynous'])
    nd = NameDataset()
    for website in website_list:
        try:
            html_request = requests.get(website, headers=headers, timeout=5).text
            text = text_from_html(html_request)
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
            final_names = []
                    
            for fullname in person_list:
                if fullname not in final_names: final_names.append(fullname)
            
            final_names, gender_stats = directorGender(final_names)
            data = [website] + gender_stats #add final_names here to see directors names
            print(website, final_names, '\n')
            writer.writerow(data)
        except Exception as e:
            print(website, " access error\n")
            data = [website, 'error']
            writer.writerow(data)
    return True


''' MAIN '''
if __name__ == "__main__":
    print("\n-- STARTING THE PROGRAM --")

    ''' downloading the required NLTK dependencies '''
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    }
    
    board_file = open('board_of_directors.csv', 'w', newline='')
    regex_file = open('results.csv', 'w', newline='')

    ''' CREATING A LIST OF ALL WEBSITE FROM THE XLSX FILE '''
    sheet_names=['FRANCE']   #'NASDAQ-2021', 'INNOVATION-2021', 'FTSE-2021', 'GERMANY', , 'HOSPITALITY'
    for sheet in sheet_names:
        workbook = pandas.read_excel('ALL_INDICES-2021.xlsx', sheet_name=sheet)     #or board_of_dir_REALVALUES.xlsx 
        df = pandas.DataFrame(workbook)

        #board_web_list = df['Website Board of Directors'].tolist()
        website_list = df['Company website'].tolist()

        all_regular_expressions = df.columns[4:len(df.columns)-4].tolist() #change if needed
        ''' clear the regex given to something python can read'''
        for i in range(0, len(all_regular_expressions)-1):
            all_regular_expressions[i] = all_regular_expressions[i].replace("OR", "|")
            all_regular_expressions[i] = all_regular_expressions[i].replace("+", " ")  # is plus a space in the expression??
            all_regular_expressions[i] = all_regular_expressions[i].replace("AND", "+")
            all_regular_expressions[i] = all_regular_expressions[i].replace("%22", "")
        ''' second part of RE'''
        second_regex = [
            'new product | new service | new process | new application | new solution | new feature | new release | new version | new launch | new introduction | new introduce | new new-product | new new-service | new new-process | new new-solution | new product-lauch',
            'Gender equality | Gender promoting balance inclusion | equality plans | equality measures | promoting equality | in equality | inclusive | equal opportunities | ensure women participation | equal opportunities for leadership | fostering equality | equal inclusion | equality between men and women | balanced and inclusive working environment',
            'Gender formal equality policies | Gender balance is adequately promoted | Gender legislation and strategic plans on equality | Gender legislation and recommendations on equality | Gender anti discrimination strategy | Gender mainstreaming strategy | Gender institutional change projects | Gender equality measures | Gender equality training',
            'Gender related strength and weakness | Gender differences between men and women | Gender does not take into account differences | Gender diversity perspective',
            'Gender representation of women and men | Gender institutional change | Gender mainstream | Gender mainstreaming platform',
            'Gender reshape the field | Gender promoting | Gender awareness-raising | Gender promote institutional change | Gender sensitive institutional transformation',
            'Gender innovation | Gender participation of women | Gender increasing female expertise in the field | Gender sensitive research innovation | Gender diverse',
            'Gender Participatory Audit | Gender Audit Facilitators | Gender impact assessment | Gender disaggregated statistics | Gender sensitive indicators | Gender gendering the content and methods of research | Gender sex-disaggregated data production | Gender evaluation',
            'Gender committees | Gender advisor | Gender advice equality | Gender experstise | Gender sensitive parliament',
            'Gender public allocations | Gender budgeting',
            'Gender gap | Gender wage gap',
            'Gender balance report | Gender composition | Gender share of female | Gander proportion of women | Gender parity indices | Gender balance monitoring | Gender underrepresentation of women | Gender monitoring instruments | Gender under-represented sex | Gender monitoring | Gender indicators | Gender ratios',
            'Women empowerment of all girls | Women needs and the perspective',
            'Gender related disputes | Gender based discriminations | Gender negative stereotypes | Gender disparities | Gender stereotypes | Gender issues | Gender implications | gender stereotypical roles | Gender equality related issues | Gender bias | Gender unconscious bias | Gender science stereotypes | Gender blind | Gender gender-based offenses | Gender segregated | Gender based mobbing and harassment | Gender sexist attitudes and bahaviours',
            'Gender inclusive language | Gender grammatical | Gender inclusive communication | Gender biased expressions | Gender neutral words | Gender biased language | Gender traditional form of nouns | Gender neutral alternative for nouns | Gender non-discriminatory language | Gender feminine and masculine pronouns | Gender non-Sexist Language | Gender Sexist language',
            'Gender sensitive | Gender friendly | Gender relevant',
            'Gender research and curricula | Gender studies'
            ]
        temp_regex = all_regular_expressions[0:23] 
        main_regex = temp_regex + second_regex

        '''
        writer = csv.writer(board_file)
        getDirectorsNames(board_web_list)
        '''
        
        writer = csv.writer(regex_file)
        mainLoop(website_list, main_regex, regex_file)