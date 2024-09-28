import cv2
import numpy as np

def find_chess_board(img):
    # 灰度化处理
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 中值模糊
    blurred = cv2.medianBlur(gray, 5)
    # Canny边缘检测
    edges = cv2.Canny(blurred, 50, 150)
    # 形态学操作
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edges = cv2.dilate(edges, kernel, iterations=1)
    edges = cv2.erode(edges, kernel, iterations=1)

    # 查找轮廓
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    largest_rectangle = None
    for cnt in contours:
        # 轮廓近似
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        # 过滤非矩形轮廓
        if len(approx) == 4:
            # 面积过滤
            area = cv2.contourArea(approx)
            if area > max_area:
                max_area = area
                largest_rectangle = approx
                
    if largest_rectangle is not None:
        x, y, w, h = cv2.boundingRect(largest_rectangle)
        print(w, h)
        roi = img[y:y+h, x:x+w]
        if roi.size > 0:  # 确保 roi 不为空
            return roi, largest_rectangle
    return None, None
    
if __name__ == "__main__":
    cap = cv2.VideoCapture(1)  # 打开摄像头，0表示默认摄像头

    while True:
        ret, frame = cap.read()  # 从摄像头读取一帧图像
        if not ret:
            break  # 如果读取失败，退出循环

        # 处理每一帧图像
        roi, largest_rectangle = find_chess_board(frame)
        if roi is not None:
            print(len(roi[0, :]))
            cv2.drawContours(frame, [largest_rectangle], -1, (0, 255, 0), 2)
            cv2.imshow('ROI', roi)  # 显示检测到的ROI

        cv2.imshow('Frame', frame)  # 显示当前帧图像
        if cv2.waitKey(1) & 0xFF == 27:  # 按ESC键退出
            break

    cap.release()  # 释放摄像头资源
    cv2.destroyAllWindows()  # 关闭所有OpenCV窗口
