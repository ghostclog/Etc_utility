# 선택요일 기준 자난달 이번달 다음달의 법정 공휴일 및 주말을 추출해서 json 형태로 저장하는 코드
# 사내 솔루션 개발 중 만든 기능으로 오픈 소스와 라이브러리를 활용하여 영업일 계산을 위해 만든 코드입니다.


import os
import json
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv, find_dotenv
import xml.etree.ElementTree as ET

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv(find_dotenv('main_api_server.env'))

# 환경 변수를 가져옵니다.
KEY = os.environ['OPEN_DATA_KEY']

def get_business_days(date_str):
    # 입력 날짜를 datetime 객체로 변환
    date = datetime.strptime(date_str, '%Y-%m-%d')
    year = date.year
    month = date.month

    start_date = datetime(year, month, 1) - timedelta(days=30)
    end_date = datetime(year, month, 1) + timedelta(days=62)
    start_date = start_date.replace(day=1)
    end_date = end_date.replace(day=1) + timedelta(days=-1)

    # 주말 계산
    weekends = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() >= 5:  # 토요일(5), 일요일(6)
            weekends.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    # 공휴일 API 호출
    url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo'
    holidays = []

    # 공휴일 데이터 가져오기
    def fetch_holidays(year, month):
        params = {
            'serviceKey': KEY,
            'pageNo': '1',
            'numOfRows': '30',
            'solYear': str(year),
            'solMonth': f'{month:02d}',
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.content)
                items = root.findall('.//item')
                for item in items:
                    locdate = item.find('locdate').text
                    holiday_date = datetime.strptime(locdate, '%Y%m%d').strftime('%Y-%m-%d')
                    holidays.append(holiday_date)
            except ET.ParseError as e:
                print(f"XML 파싱 오류: {e}")
                print(f"응답 내용: {response.content}")
        else:
            print(f"Error fetching holidays: {response.status_code}")
            print(f"응답 내용: {response.content}")

    # 현재 월과 다음 두 달의 공휴일 데이터 가져오기
    fetch_holidays(year, month)
    fetch_holidays(year, month + 1)
    fetch_holidays(year, month + 2)

    # 주말과 공휴일을 하나의 리스트로 합치고 중복 제거
    special_dates = sorted(list(set(weekends + holidays)))

    # JSON 파일 저장 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, '..', '..', 'assets/cached_data')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "special_dates.json")

    # JSON 파일 저장
    special_dates_data = {"special_dates": special_dates}
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(special_dates_data, file, indent=4, ensure_ascii=False)

    # 비즈니스 데이 계산
    business_days = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        if date_str not in special_dates:
            business_days.append(date_str)
        current_date += timedelta(days=1)

    return business_days

# 예시 실행
print(get_business_days("2025-12-09"))
