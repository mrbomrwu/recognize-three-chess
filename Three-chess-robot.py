import cv2
import numpy as np
from find_chessboard import find_chess_board
from detect_circles import detectCircles
from find_hei_bai_qi import find_qi_blobs

def main(frame):
    rect, largest_rectangle = find_chess_board(frame)
    circles = None  # 初始化 circles 变量
    if rect is not None and largest_rectangle is not None:
        cv2.imshow('rect', rect)
        cv2.drawContours(frame, [largest_rectangle], -1, (0, 255, 0), 2)
        circles = detectCircles(rect)
    else:
        print("No chess board detected")
    if circles:
        for circle in circles:
            if isinstance(circle, np.ndarray) and circle.size > 0:
                find_qi_blobs(circle)
            else:
                print("Invalid circle detected")
    else:
        print("No chess board detected")


if __name__ == "__main__":
    cap = cv2.VideoCapture(1)  # 打开摄像头，0表示默认摄像头
    # 获取摄像头帧率
    fps = cap.get(cv2.CAP_PROP_FPS)

    while True:
        ret, frame = cap.read()  # 从摄像头读取一帧图像
        if not ret:
            print('cannot found anything') 

        # 处理每一帧图像
        main(frame)

        cv2.putText(frame, str(fps), (10, 45), cv2.FONT_HERSHEY_SIMPLEX,
                1, [255, 255, 255])

        cv2.imshow('Frame', frame)  # 显示当前帧图像
        if cv2.waitKey(1) & 0xFF == 27:  
            break
    cap.release()  # 释放摄像头资源
    cv2.destroyAllWindows()  # 关闭所有OpenCV窗口
