from selenium import webdriver
import pandas as pd
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import re
url_1 = ''
url_2 = ''
url_list = [url_1, url_2]
alls = []
for i in url_list:
    chrome_options = Options()
    # chrome_options.add_argument("--headless") #Hides the browser window
    chrome_path = r"C:\Users\hsaid\Desktop\chromedriver_win32\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=chrome_path)  # ,options=chrome_options)

    driver.get(i)
    # Scrole page to load whole content
    last_height = driver.execute_script('"return document.body.scrollHeight"')
    while True:
        # Scroll down to bottom
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        # wait to load the page
        time.sleep(2)
        # Calculate new scroll height and compare last height
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height
    htmltext = driver.page_source
    driver.quit()
    # Parse HTML structure
    soup = BeautifulSoup(htmltext, 'html.parser')
    for films in soup.find_all('div', {'class': '_2Ay0F4'}):

        tt = films.find('div', {'class': '_1y15Fl dvui-beardContainer D0Lu_p av-grid-beard'})
        yy = tt.find('div', {'class': '_1Opa2_ dvui-packshot av-grid-packshot'})
        f_link = yy.find('a', {'href': True})['href']
        link = 'https://www.amazon.co.uk' + str(f_link)

        ts = films.find('div', {'class': '_1yEE4p'})

        b = ts.find('div', {'class': 'zSuwlR'})

        y = b.find_all('div', {'class': 'NOucmK'})[2]
        z = y.find('div', {'class': 'Das1hS'})
        try:
            name = z.find('h1', {'class': '_28Acs_ tst-hover-title'}).text
        except:
            continue
        try:
            description = z.find('p', {'class': '_36qUej nLJhm6 tst-hover-synopsis'}).text
        except:
            continue
        t = b.find_all('div', {'class': 'NOucmK'})[3]
        try:
            imdb = t.find_all('div', {'class': '_1qxpZ5 _2wV5Zf'})[0].text
        except:
            continue
        try:
            duration = t.find_all('div', {'class': '_1qxpZ5 _2wV5Zf'})[1].text
        except:
            continue
        try:
            year = t.find_all('div', {'class': '_1qxpZ5 _2wV5Zf'})[2].text
        except:
            continue
        try:
            age = t.find('span', {'class': '_1zslxR _9VzAtc tst-hover-maturity-rating _1-QtkI'})['title']
        except:
            continue

        # url1 = str(link)
        # page1 = requests.get(url1)
        # soup1 = BeautifulSoup(page1.text, 'html.parser')
        # movie = soup1.find_all('div', {'class': '_2Ke7Sf'})
        time.sleep(1)

        all1 = []

        if name is not None:
            all1.append(name)
        else:
            all1.append("unknown")

        if year is not None:
            all1.append(year)
        else:
            all1.append("unknown")

        if duration[:-3] is not None:
            all1.append(duration[:-3])
        else:
            all1.append("unknown")

        if link is not None:
            all1.append(str(link))
        else:
            all1.append('unknown')

        if description is not None:
            all1.append(str(description))
        else:
            all1.append('unknown')

        if imdb is not None:
            all1.append(str(imdb))
        else:
            all1.append('unknown')

        alls.append(all1)

df = pd.DataFrame(alls)
print(df.columns)
df.to_csv('Amazon_movies_new.csv')
