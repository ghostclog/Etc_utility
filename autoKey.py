import pyautogui
import time

def auto_type():
    try:
        while True:
            pyautogui.press('c')
            time.sleep(1.5)  # 1.5초 대기
    except KeyboardInterrupt:
        print("오토 입력 종료.")

if __name__ == "__main__":
    print("오토 입력을 시작. 종료는 control + C")
    auto_type()