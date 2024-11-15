import time
import requests
from datetime import datetime
import Adafruit_DHT

# DHT22 설정
sensor = Adafruit_DHT.DHT22

# DHT-22 관련 상수 정의
DHT_GPIO_REFRIGERATOR = 27
DHT_GPIO_FREEZER = 17
LH_THRESHOLD = 30

INTERVAL_SEC = 3

class SensorData:
    def __init__(self, temp=0, humid=0, success=False):
        self.temp = temp
        self.humid = humid
        self.success = success

def get_dht22_data(pin):
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return SensorData(temperature, humidity, (humidity is not None and temperature is not None))

def main():
    print("온습도 센서 데이터 수집 프로그램을 시작합니다.")

    while True:
        start_time = time.time()

        try:
            refrigerator_data = get_dht22_data(DHT_GPIO_REFRIGERATOR)
            freezer_data = get_dht22_data(DHT_GPIO_FREEZER)

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