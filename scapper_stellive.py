from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time, csv
from datetime import datetime


stellive = {
    "아이리 칸나":"https://www.youtube.com/@Kannareplay/videos",
    "아야츠노 유니":"https://www.youtube.com/@Yunireplay/videos",
    "시라유키 히나":"https://www.youtube.com/@hinareplay/videos",
    "네네코 마시로":"https://www.youtube.com/@mashiroreplay/videos",
    "아카네 리제":"https://www.youtube.com/@lizereplay/videos",
    "아라하시 타비":"https://www.youtube.com/@tabireplay/videos",
    "텐코 시부키":"https://www.youtube.com/@shibukireplay/videos",
    "하나코 나나":"https://www.youtube.com/@nana_replay/videos",
    "아오쿠모 린":"https://www.youtube.com/@rinreplay/videos",
    "유즈하 리코":"https://www.youtube.com/@rikoreplay/videos",
}

# playwright를 통해 html 데이터를 반환하는 함수
def html_returner(url:str,total_down:int):
    p = sync_playwright().start()

    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    time.sleep(3)
    if(total_down != 0):
        for i in range(total_down):
            page.keyboard.down("End")
            time.sleep(2)

    htmls = page.content()
    p.stop()
    return htmls
# 스텔라별 다시보기 제목에서 데이터 추출. 최신 다시보기 양식으로 맞춰져있음
def title_stlye(title_text: str,stella: str)->str:
    # [2024.01.01] ~~~
    if(stella=="아이리 칸나" or 
       stella=="아라하시 타비" or
       stella=="하나코 나나"):
        # 문자열 분리
        split_text = title_text.split()
        # 날짜 포멧팅
        date_text = split_text[0]
        date = date_text[1:-1].replace(".","/").rstrip()
        # 제목 조립
        title = " ".join(split_text[1:])

    # 2024 01 01 ~~~~~
    elif(stella=="네네코 마시로"):
        # 문자열 분리
        split_text = title_text.split()
        # 날짜 포멧팅
        date = " ".join(split_text[:3]).replace(" ","/").rstrip()
        # 제목 조립
        title = " ".join(split_text[3:])

    # ~~~ [24. 1. 01] 문제 발생
    elif(stella=="시라유키 히나"):
        # 문자열 분리
        split_text = title_text.split()
        # 날짜 포멧팅
        date_text = " ".join(split_text[-3:]).replace(". ","/")
        date = "20" + date_text[1:-1]
        # 제목 조립
        title = " ".join(split_text[:-3])

    # ~~~ [2024.01.01]
    elif(stella=="유즈하 리코" or 
         stella=="아야츠노 유니" or 
         stella=="아카네 리제"):
        # 문자열 분리
        split_text = title_text.split()
        # 날짜 포멧팅
        date_text = split_text[-1]
        date = date_text[1:-1].replace(".","/")
        # 제목 조립
        title = " ".join(split_text[:-1])

    # [ 2024.01.01 | ~~~~ ] - 린 다시보기
    elif(stella=="아오쿠모 린"):
        # 문자열 분리
        split_text = title_text.split()
        # 날짜 포멧팅
        date = split_text[1]
        # 제목 조립
        title_not_split = " ".join(split_text[3:])
        title = title_not_split.split("] - 린")[0]
    elif(stella=="텐코 시부키"):
        # 문자열 분리
        split_text = title_text.split()
        # 날짜 포멧팅
        date_text = split_text[0]
        date = f"{date_text[:4]}/{date_text[4:6]}/{date_text[6:]}"
        # 제목 조립
        title = " ".join(split_text[1:])
    
    return date, title
# 해당 스텔라 다시보기 사이트 데이터 긁어오기
def scraping(soup,stella):
    # 데이터 담는 변수
    data_list = []

    # 영상 전체를 담고 있는 div 탐색 및 추출
    vedios_div = soup.find("div",id="contents")
    # 이후 div에서 영상 div들 추출
    vedios = vedios_div.find_all("div",id="content")
    for vedio in vedios:
        title_text = vedio.find("yt-formatted-string",id="video-title").text
        day,title = title_stlye(title_text,stella)
        anchor = f"https://www.youtube.com{vedio.find('a',id='thumbnail')['href']}"
        vedio_id = anchor.split("?v=")[1]
        vedio_data = {
            "vedio_id":vedio_id,
            "link": anchor,
            "day": day,
            "title": title,
            "stella": stella,
        }

        data_list.append(vedio_data)
    # 다시보기 데이터 반환
    return data_list

# 데이터 출력용
data_list_dict = ["vedio_id","link","day","title","stella"]

# 테스트 할 스텔라
stella = input("긁어올 스텔라의 이름은?(풀네임으로 적어주시고, 띄어쓰기 해주셔야합니다.): ")
vedios = int(input("가져올 영상의 수는?(숫자 이외 입력시 에러가 발생하며, 숫자가 커지면 오래걸립니다.): "))
int_vedios = int(vedios // 28)
#html 데이터 반환받기 및 해당 스텔라 사이트 데이터 긁어오는 함수 호출
soup = BeautifulSoup(html_returner(stellive[stella],int_vedios),"html.parser")
data_list = scraping(soup,stella)

# 정보 파일화
stella_text =  stella.split()
stella_text.append(str(vedios))
title = "_".join(stella_text)

# 데이터 출력
csv_file_name = f"{title}.csv"
with open(csv_file_name, mode='w', newline='', encoding='utf-8') as file:
    # CSV 작성자 생성
    writer = csv.DictWriter(file, fieldnames=data_list_dict)
    
    # 헤더 작성
    writer.writeheader()
    
    # 데이터 작성
    for data in data_list:
        writer.writerow(data)

print(f"CSV 파일 '{csv_file_name}'이(가) 성공적으로 생성되었습니다.")