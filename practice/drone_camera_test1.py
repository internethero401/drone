# auto-testとcamera,顔検出
 
import socket
import time
import cv2
import numpy as np
import av
import threading

# TelloのIPアドレスとポート番号
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)
LOCAL_PORT = 9000
VIDEO_PORT = 11111

# UDPソケットの作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', LOCAL_PORT))

def send(message):
    try:
        sock.sendto(message.encode(), TELLO_ADDRESS)
        print(f"Sending message: {message}")
    except Exception as e:
        print(f"Error sending message: {e}")

def receive():
    try:
        response, _ = sock.recvfrom(1024)  # response:受信データ , _:送信元アドレス
        print(f"Received message: {response.decode()}")
    except Exception as e:
        print(f"Error receiving message: {e}")

# スレッド終了用のイベントフラグ
stop_event = threading.Event()

# カスケードファイルのパスを設定
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# カメラ映像を表示する関数
def receive_video():
    container = av.open(f'udp://@0.0.0.0:{VIDEO_PORT}')
    frame_skip = 0  # フレームスキップ用のカウンタ
    for frame in container.decode(video=0):
        if stop_event.is_set():
            break
        image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)
        
        frame_skip += 1
        cv2.imshow('Tello', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break
        if cv2.waitKey(1) & 0xFF == ord('w'):
            cv2.imwrite("picture.png", image)
    cv2.destroyAllWindows()

# 別スレッドでビデオストリームを受信
video_thread = threading.Thread(target=receive_video)
video_thread.start()

# SDKモードを開始
send("command")
receive()

# カメラストリームをオンにする
send("streamon")
receive()

time.sleep(120)

# カメラストリームをオフにする
send("streamoff")
receive()

# スレッドを停止する
stop_event.set()
video_thread.join()

# ソケットを閉じる
sock.close()

# OpenCVウィンドウを閉じる
cv2.destroyAllWindows()



"""
遅延が気になるのであれば左右向いたときのsleep時間(滞在時間)を多めに取り,1回の顔認識を行う毎フレームを下げる
帰ってくる時が上手くいかない(前のsleep時間を変えたりして改良必要有)
"""