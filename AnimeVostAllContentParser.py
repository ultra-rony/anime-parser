from bs4 import BeautifulSoup
import requests 
import json
import re
import colorama 
from colorama import Fore, Style

domain = "https://v7.vost.pw/"
# Получить все года выходов аниме
def getAllYears(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.text, "html.parser")
    selectMenu = soup.find('div', class_='menu').find('ul', {"id": "topnav"}).findAll('li')[3]
    years = []
    for i in selectMenu.findAll('a'):
        years.append(i.text)
    years.pop(0)
    return years
# Получить максимальное количество пагинаций страницы
def getNumberPages(soup):
    block = soup.find('div', class_='block_2')
    if block != None:
        td = block.find('td', class_='block_4')
        if td != None:
            pg = td.findAll('a')
            if len(pg) > 0:
                return int(pg[-1].text)
    return 1
# Получить ссылки аниме
def getAnimeLinks(soup):
    result = []
    for i in soup.find('div', {"id": "dle-content"}).findAll('h2'):
        result.append(i.find('a')['href'])
    return result
# Получить полное описание аниме
def getAnime(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.find('div', class_='shortstoryContent')
    headersLong = soup.find('div', class_='shortstoryHead').text.replace("\n", "").replace("  ", "").split(' / ')
    headersShort = content.find('img', class_='imgRadius').get('title').replace("/ ", "/").replace("/\t", "/").split('/')
    arrContent = content.find('table').findAll('p')
    screenshotsContent = content.find('fieldset', class_='skrin')
    if screenshotsContent != None:
        screenshotsContent = screenshotsContent.findAll('a')
    else:
        screenshotsContent = []
    screenshots = []
    for i in screenshotsContent:
        screenshots.append(i['href'])
    return {
        'title_ru': headersShort[0],
        'title_en': headersShort[1],
        'img': content.find('img', class_='imgRadius').get('src'),
        'description': content.find('span', {'itemprop': 'description'}).text,
        'year': arrContent[0].text.replace('Год выхода: ', ''),
        'genres': arrContent[1].text.replace('Жанр: ', ''),
        'type': arrContent[2].text.replace('Тип: ', ''),
        'series_option': arrContent[3].text.replace('Количество серий: ', ''),
        'producer': arrContent[4].text.replace('Режиссёр: ', ''),
        'screenshots': str(screenshots),
        'url': url.replace(domain, "")
    }
# Спарсить весь контент
arrYears = getAllYears(domain)
for year in arrYears:
    resPg = requests.get(f"{domain}god/{year}/")
    soupPg = BeautifulSoup(resPg.text, "html.parser")
    numberPages = getNumberPages(soupPg)
    print(f"{Fore.BLUE}кол-во страниц: {numberPages}; год: {year};{Style.RESET_ALL}")
    num = 1
    while num <= numberPages:
        resNum = requests.get(f"{domain}god/{year}/page/{num}/")
        soupNum = BeautifulSoup(resNum.text, "html.parser")
        links = getAnimeLinks(soupNum)
        print(f"{Fore.YELLOW}\tкол-во аниме: {len(links)}; на странице: {num}/{numberPages}{Style.RESET_ALL}")
        for anime in links:
            obj = getAnime(anime)
            print(f"{Fore.GREEN}\t\t{obj['title_ru']}{Style.RESET_ALL}")
        num = num+1
