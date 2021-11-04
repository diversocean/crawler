from urllib.request import urlopen
from urllib.parse import quote_plus
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv


class GooglePlace(object):
    def __init__(
        self,
        baseUrl="https://www.google.com/search?tbs=lrf:!1m4!1u3!2m2!3m1!1e1!2m1!1e3!3sIAE,lf:1,lf_ui:4&tbm=lcl&sxsrf=AOaemvLlmSgd_57QwWo0ESSFQQZXIXZ1ag:1635680689664&q=",
        window=True,
        dropna=True,
    ):
        self.input = input('search : ')
        self.url = baseUrl + self.input
        self.window = window
        self.dropna = dropna

        if self.window:
            self.driver = webdriver.Chrome('./chromedriver')
            self.driver.get(self.url)
        else:
            """
            WARNING : headless모드로 실행시 봇으로 간주되서 제재당할 수 있음.
            Bypass : 아래 user-agent에 자신의 크롬브라우저 user-agent 값으로 수정한다.
            ## user-agent 확인하는 방법 : 크롬창을 하나 열어서 'Ctrl + Shift + i' 를 누르면 콘솔창이 뜨는데 거기에서 Console 탭 클릭 -> navigator.userAgent 입력후 엔터
            """
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")
            options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36")
            self.driver = webdriver.Chrome('./chromedriver', chrome_options=options)
            self.driver.get(self.url)

    def parse(self):
        f = open(f'{self.input}.csv', 'w', encoding='utf-8', newline='')
        csvWriter = csv.writer(f)

        page_number = 0
        end = 0
        while True:
            try:
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                btn = self.driver.find_element_by_xpath('//*[@id="pnnext"]')
            except:
                btn = None

            page_number += 1
            print(f'\rpage_number : {page_number} page', end='')

            names = []
            details = []

            place_names = soup.find_all(class_='dbg0pd eDIkBe')
            place_details = soup.find_all(class_='rllt__details')
            place_info = zip(place_names, place_details)

            for n_idx, d_idx in place_info:
                if n_idx.span and d_idx.div:
                    names.append(n_idx.span.text)
                    details.append(d_idx.div.text)
                else:
                    pass

            searchList = dict(zip(names, details))
            for name, detail in searchList.items():
                if self.dropna:
                    if detail.find('·') == -1:
                        pass
                    else:
                        address = detail.split('·')[0]
                        phone = detail.split('·')[1]
                else:
                    if detail.find('·') == -1:
                        if detail.startswith('0'):
                            address = 'null'
                            phone = detail
                        else:
                            address = detail
                            phone = 'null'
                    else:
                        address = detail.split('·')[0]
                        phone = detail.split('·')[1]
                csvWriter.writerow([name, address, phone])
                
            if end:
                self.driver.close()
                break

            if self.window:
                if bool(btn):
                    btn.click()
                else:
                    end = 1
            else:
                if bool(btn):
                    btn.send_keys(Keys.ENTER)
                else:
                    end = 1
            time.sleep(2.5)

        f.close()
        print('\ndone')


if __name__ == '__main__':
    scraper = GooglePlace(window=True, dropna=True)
    scraper.parse()
