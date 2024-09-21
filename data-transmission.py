import serial
import time

# 设置串口通信参数
ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

def send_data(data):
    # 将数据转为字节并发送
    ser.write(data.encode())

try:
    while True:
        data_to_send = "Hello STM32\n"  # 待发送的数据
        send_data(data_to_send)
        print(f"Sent: {data_to_send}")
        time.sleep(1)  # 每秒发送一次

except KeyboardInterrupt:
    print("Transmission stopped")
finally:
    ser.close()  # 关闭串口
