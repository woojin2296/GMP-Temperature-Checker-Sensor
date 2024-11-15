import time
import requests
import RPi.GPIO as GPIO
from datetime import datetime
from smbus2 import SMBus
import threading

# DHT-22 관련 상수 정의
DHT_GPIO_REFRIGERATOR = 27
DHT_GPIO_FREEZER = 17
LH_THRESHOLD = 30

INTERVAL_SEC = 3

# LCD 초기화
bus = SMBus(1)

class SensorData:
    def __init__(self, temp=0, humid=0, success=False):
        self.temp = temp
        self.humid = humid
        self.success = success

def read_data(DHT_GPIO):
    GPIO.setmode(GPIO.BCM)
    data = [0] * 5
    result = SensorData()

    try:
        GPIO.setup(DHT_GPIO, GPIO.OUT)
        GPIO.output(DHT_GPIO, GPIO.LOW)
        time.sleep(0.018)
        GPIO.output(DHT_GPIO, GPIO.HIGH)
        GPIO.setup(DHT_GPIO, GPIO.IN)

        # 데이터 읽기
        for i in range(5):
            for j in range(8):
                while GPIO.input(DHT_GPIO) == GPIO.LOW:
                    continue
                width = 0
                while GPIO.input(DHT_GPIO) == GPIO.HIGH:
                    width += 1
                    time.sleep(0.000001)
                    if width > 1000:
                        break
                data[i] |= (width > LH_THRESHOLD) << (7 - j)

        humid = data[0] << 8 | data[1]
        temp = data[2] << 8 | data[3]
        chk_sum = sum(data[:4]) & 0xFF

        if chk_sum == data[4]:
            result.success = True
            result.temp = temp
            result.humid = humid
        else:
            result.success = False
            print(f"센서 {DHT_GPIO} 읽기 오류: 체크섬 불일치")

    except Exception as e:
        result.success = False
        print(f"센서 {DHT_GPIO} 읽기 오류: {e}")

    return result

def main():
    print("온습도 센서 데이터 수집 프로그램을 시작합니다.")

    while True:
        start_time = time.time()

        try:
            refrigerator_data = read_data(DHT_GPIO_REFRIGERATOR)
            freezer_data = read_data(DHT_GPIO_FREEZER)

            timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            # 데이터 서버 전송
            url = "http://158.180.91.120:8080/refrigerator-data"
            data = {
                "timestamp": timestamp,
                "refrigeratorTemp": refrigerator_data.temp / 10.0,
                "refrigeratorHumid": refrigerator_data.humid / 10.0,
                "freezerTemp": freezer_data.temp / 10.0,
                "freezerHumid": freezer_data.humid / 10.0,
            }
            try:
                response = requests.post(url, json=data)
                if response.status_code == 200:
                    print("데이터 전송 성공")
                else:
                    print("데이터 전송 실패:", response.status_code)
            except requests.RequestException as e:
                print("데이터 전송 오류:", e)

        except Exception as e:
            print("메인 루프 오류:", e)

        # 주기적으로 실행되도록 슬립
        elapsed = time.time() - start_time
        if elapsed < INTERVAL_SEC:
            time.sleep(INTERVAL_SEC - elapsed)
        else:
            print("주의: 센서 읽기 및 처리 시간이 주기보다 깁니다.")

if __name__ == "__main__":
    main()