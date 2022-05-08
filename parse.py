from regex import F
import requests
from bs4 import BeautifulSoup as BS
import time
import re

HOST = "https://www.culture.ru"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0"
}

page = 1
url = "https://www.culture.ru/literature/poems/author-vladimir-mayakovskii?page=" + str(page)
response = requests.get(url, headers=headers)

def get_composition(url):
    response = requests.get(url, headers=headers)
    html = BS(response.content, "html.parser")

    title_composition = html.find("div", class_="xtEsw").text.strip().replace("?", "")
    text_items = html.find("div", class_="xZmPc").find_all("p")

    print(title_composition)
    text_composition = ""
    

    with open("file.txt", "w", encoding="utf-8") as file:
        for text_item in text_items:
            for i in text_item.contents:
                #for j in i:
                print("class" in i)
                text_composition += str(i)
                text_composition += "\n"
        file.write(text_composition)

    #with open(f"Стихи/{title_composition}.txt", "w", encoding="utf-8") as file:
        #text_composition = ""
        #for text_item in text_items:
            #text_composition +=  str(text_item).replace("<br/>", "\n")

        #file.write(re.findall(r"\w*\s*>(.*)<", text_composition, re.DOTALL)[0])


if response:
    while True:
        html = BS(response.content, "html.parser")
        links = html.find_all("a", class_="_9OVEn")
        if len(links) > 0:   
            for link in links:
                get_composition(HOST + link.get("href"))
                #time.sleep(1)

            page += 1
            url = "https://www.culture.ru/literature/poems/author-vladimir-mayakovskii?page=" + str(page)
            response = requests.get(url, headers=headers)

            print(f"Страница {page}")
else:
    print("Ошибка.")