from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

# playwright를 통해 html 데이터를 반환하는 함수
def html_returner(url):
    p = sync_playwright().start()

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    time.sleep(3)
    page.click("yt-chip-cloud-chip-renderer:has-text('날짜순')")
    # for i in range(25):
    #     time.sleep(2)
    #     page.keyboard.down("End")
    time.sleep(2)
    htmls = page.content()
    p.stop()
    return htmls

def scraping(soup):
    # 데이터 담는 변수
    data_list = []

    # 영상 전체를 담고 있는 div 탐색 및 추출
    vedios_div = soup.find("div",id="contents")
    # 이후 div에서 영상 div들 추출
    vedios = vedios_div.find_all("div",id="content")
    for vedio in vedios:
        title_text = vedio.find("yt-formatted-string",id="video-title").text
        # 다시보기 여부 확인
        if(title_text.endswith(" - 【 J1NU 】")):
            day = title_text.split()[1]
            anchor = f"https://www.youtube.com{vedio.find('a',id='thumbnail')['href']}"
            how_long_vedio = vedio.find("div",class_="badge-shape-wiz__text").text
            
            vedio_data = {
                "title": title_text,
                "day": day,
                "how_long_vedio": how_long_vedio,
                "link": anchor,
            }

            data_list.append(vedio_data)
    # 다시보기 데이터 반환
    return data_list

url = "https://www.youtube.com/@K1MJINWOO/videos"
data_list_dict = ["title","day","how_long_vedio","link"]
soup = BeautifulSoup(html_returner(url),"html.parser")
data_list = scraping(soup)

for data in data_list:
    for i in data_list_dict:
        print("-",data[i])
    print()