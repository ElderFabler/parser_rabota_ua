import requests
import glob
import re
import json
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup as Bfs


def get_source_html(url_path,lang_list):
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    data_dir = os.path.join(os.getcwd(), "data_page_html",)
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    for i in lang_list:
        driver.get(url_path)
        sleep(3)
        text_str = driver.find_element(By.XPATH,"//input[@class = 'ng-untouched ng-pristine ng-valid']")
        text_str.clear()
        text_str.send_keys(i)
        sleep(3)
        text_str.send_keys(Keys.RETURN)
        sleep(10)
        try:
            paginator = driver.find_element(By.XPATH, "//div[@class = 'paginator santa-text-16 ng-star-inserted']")
            if paginator.find_elements(By.CLASS_NAME, "side-btn"):
                pag_elem = paginator.find_elements(By.TAG_NAME, 'div')[-2].text
            else:
                pag_elem = paginator.find_elements(By.TAG_NAME, 'div')[-1].text
            if int(pag_elem) > 4:
                pag_elem = 4
            else:
                pag_elem = int(pag_elem)
            cur_url = driver.current_url
            for j in range(1,pag_elem+1):
                driver.get(f"{cur_url}?page={j}")

                sleep(3)

                [driver.find_element(By.TAG_NAME,"body").send_keys(Keys.PAGE_DOWN) for i in range(0,40)]
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                sleep(3)
                
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.HOME)
                sleep(3)
                
                with open(f"data_page_html\\{i}_page_source_{j}.html","w",encoding="utf-8") as file_w:
                    file_w.write(driver.page_source)
                sleep(10)
        except Exception as ex:
            print(ex)
            [driver.find_element(By.TAG_NAME,"body").send_keys(Keys.PAGE_DOWN) for i in range(0,40)]
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            sleep(3)
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.HOME)
            sleep(3)
            with open(f"data_page_html\\{i}_page_source.html","w",encoding="utf-8") as file_w:
                file_w.write(driver.page_source)


    driver.close()
    driver.quit()

def get_data_url(url_path):
    glob_path = glob.glob("data_page_html\\*.html")
    urls = []

    for i in glob_path:
        with open(i,"r",encoding="utf-8") as file_r:
            src = file_r.read()
        soup = Bfs(src,"lxml")
        items =  soup.find("body").find("div", {"class":"list-container"}).find("div", {"class":"santa-flex santa-flex-col ng-star-inserted"})
        item_divs = items.find_all("div",{"style":"min-height: 100px;"})

        for j in item_divs:
            item_url = j.find("alliance-vacancy-card-desktop").find("a").get("href")
            urls.append(item_url)
            
    with open(f"vacancy_links.txt","w") as file_w:
        for i in urls:
            file_w.write(f"{url_path}{i}\n")

def get_data(lang_list):
    lang_l = [i.split(" ")[0] for i in lang_list]

    driver = webdriver.Chrome()
    driver.maximize_window
    with open("vacancy_links.txt","r") as file_r:
        urls_list = [i.strip() for i in file_r.readlines()]
    
    results = []
    for i in urls_list:
        driver.get(i)
        sleep(5)
        soup = Bfs(driver.page_source,"lxml")

        try:
            name = soup.find("h1",{"data-id":"vacancy-title"}).text.strip()
        except Exception as ex:
            print(f"name: {ex}")
            name = "No data"

        try:
            salary = soup.find("span", {"data-id":"vacancy-salary"}).text.strip()
        except Exception as ex:
            print(f"salary: {ex}")
            salary = "No data"

        try:
            city = soup.find("span",{"data-id":"vacancy-city"}).text.strip()
            try:
                adress = soup.find("span",{"data-id":"vacancy-adress"}).text.strip()
            except Exception as er:
                adress = ""
            loc = city + adress
        except Exception as ex:
            print(f"loc: {ex}")
            loc = "No data"
                    
        try:
            sub_item = soup.find("div",{"class":"santa-flex santa-items-center santa-flex-wrap santa-typo-regular santa-mb-10 760:santa-mb-20 ng-star-inserted"})
            company = sub_item.find("a",{"target":"_blank"}).find("span").text.strip()
        except Exception as ex:
            print(f"company: {ex}")
            company = "No data"

        try:
            date = soup.find("span",{"class":"santa-text-white santa-flex santa-justify-center santa-typo-additional ng-star-inserted"}).text.strip()
        except Exception as ex:
            print(f"date: {ex}")
            date = "No data"

        try:
            item_descr = soup.find("div",{"id":"description-wrap"}).text
            langs = list(filter(lambda x: x in item_descr,lang_l))
            if langs == False:
                langs = ["Other"]
            else:
                pass
        except Exception as ex:
            print(f"langs: {ex}")
            langs = "No availavle data"

        sleep(5)

        results.append(
            {
                "item_name":name,
                "item_salary":salary,
                "item_loc":loc,
                "item_company":company,
                "item_date":date,
                "item_langs":langs,
            }
        )

    driver.close()
    driver.quit()

    with open("results.json","w",encoding = "utf-8") as file_w:
        json.dump(results,file_w,indent = 4,ensure_ascii = False)

    return "[INFO] Data collected"

def main():
    url_path = "https://rabota.ua/ua"
    lang_list = ["python","JS developer","C++ developer","C# developer","Golang developer"]
    get_source_html(url_path,lang_list)
    get_data_url(url_path)
    get_data(lang_list)

if __name__ == "__main__":
    main()