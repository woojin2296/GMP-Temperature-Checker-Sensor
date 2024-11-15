import time, requests, json
from datetime import datetime

import board
import adafruit_dht

# DHT22 센서를 사용할 GPIO 핀을 지정
sensor1 = adafruit_dht.DHT22(board.D17) 
sensor2 = adafruit_dht.DHT22(board.D27)
# sensor3 = adafruit_dht.DHT22(board.D22)

LH_THRESHOLD = 30
INTERVAL_SEC = 3

class SensorData:
    def __init__(self, temp=0, humid=0):
        self.temp = temp
        self.humid = humid

def get_dht22_data():
    sensor1_temperature = sensor1.temperature
    sensor1_humidity = sensor1.humidity

    sensor2_temperature = sensor2.temperature
    sensor2_humidity = sensor2.humidity

    # sensor3_temperature = sensor3.temperature
    # sensor3_humidity = sensor3.humidity

    return SensorData(sensor1_temperature, sensor1_humidity), SensorData(sensor2_temperature, sensor2_humidity)#, SensorData(sensor3_temperature, sensor3_humidity)

def main():
    print("온습도 센서 데이터 수집 프로그램을 시작합니다.")

    while True:
        start_time = time.time()

        try:
            sensor1_data, sensor2_data = get_dht22_data()

            print(sensor1_data.temp, sensor1_data.humid)
            print(sensor2_data.temp, sensor2_data.humid)
            # print(sensor3_data.temp, sensor3_data.humid)

            timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            # 데이터 서버 전송
            url = "http://158.180.91.120:8080/refrigerator-data"
            data = {
                "timestamp": timestamp,
                "refrigeratorTemp": sensor1_data.temp / 10.0,
                "refrigeratorHumid": sensor1_data.humid / 10.0,
                "freezerTemp": sensor2_data.temp / 10.0,
                "freezerHumid": sensor2_data.humid / 10.0,
            }
            content_length = str(len(json.dumps(data)))
            header = {
                "Content-Type": "application/json",
                "Host": "158.180.91.120:8080",
                "Content-Length": content_length,  
            }
            try:
                response = requests.post(url, json=data, headers=header)
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