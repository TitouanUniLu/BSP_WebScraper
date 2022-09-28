from bs4 import BeautifulSoup
import requests

html_requests = requests.get('https://store.steampowered.com/explore/new/').text
soup = BeautifulSoup(html_requests, 'lxml')


games = soup.find_all('a', class_ = 'tab_item')
for game in games:
    genre = game.find('div', class_ = 'tab_item_top_tags').text
    name = game.find('div', class_ = 'tab_item_name').text
    link = game.get('href')
    print(f'''
    Game Name: {name}
    Game Genre: {genre}
    Game Link: {link}
    ''')


