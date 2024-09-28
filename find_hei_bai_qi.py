import cv2 as cv
import numpy as np

def find_qi_blobs(frame):
    if frame is None or not isinstance(frame, np.ndarray):
        raise ValueError("Invalid frame: frame is either None or not a numpy array")
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)  # hsv 色彩空间 分割肤色
    # lower_hsv1 = np.array([60, 23, 16])
    # upper_hsv1 = np.array([122, 179, 68])
    lower_hsv1 = np.array([18, 62, 0])  # 调整为更适合黑色的范围
    upper_hsv1 = np.array([102, 220, 19])
    mask1 = cv.inRange(hsv, lowerb=lower_hsv1, upperb=upper_hsv1)  # hsv 掩码
    # lower_hsv2 = np.array([52, 5, 160])
    # upper_hsv2 = np.array([110, 43, 227])
    # 白色棋子的HSV范围
    lower_hsv2 = np.array([0, 0, 109])
    upper_hsv2 = np.array([179, 30, 255])
    mask2 = cv.inRange(hsv, lowerb=lower_hsv2, upperb=upper_hsv2)  # hsv 掩码
    ret, thresh1 = cv.threshold(mask1, 40, 255, cv.THRESH_BINARY)  # 二值化处理
    ret, thresh2 = cv.threshold(mask2, 40, 255, cv.THRESH_BINARY)  # 二值化处理
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))  # 获取图像结构化元素
    dst1 = cv.morphologyEx(thresh1, cv.MORPH_CLOSE, kernel)  # 闭操作
    dst2 = cv.morphologyEx(thresh2, cv.MORPH_CLOSE, kernel)  # 闭操作
    scr1 = dst1
    scr2 = dst2

    contours1, heriachy1 = cv.findContours(scr1, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  # 获取轮廓点集(坐标)
    contours2, heriachy2 = cv.findContours(scr2, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  # 获取轮廓点集(坐标)
    # cv.drawContours(frame, contours1, -1, (0, 0, 255), 2)
    # cv.drawContours(frame, contours2, -1, (0, 255, 0), 2)
    for i, contour in enumerate(contours1):
        area1 = cv.contourArea(contour)
        # print(area1)
        if area1 > 500:
            (x1, y1), radius1 = cv.minEnclosingCircle(contours1[i])
            x1 = int(x1)
            y1 = int(y1)
            center1 = (int(x1), int(y1))
            radius1 = int(radius1)
            # cv.circle(frame, center1, 15, (0, 0, 255), -1)  # 画出重心
            # 在图像上绘制一个十字标记
            cv.drawMarker(frame, center1, color=(0, 0, 255), markerType=cv.MARKER_CROSS, thickness=2, markerSize=20)
            print("黑色棋子:", (x1, y1))
            # cv.putText(frame, "black:", (x1, y1), cv.FONT_HERSHEY_SIMPLEX,
            #         1, [255, 255, 255])
    for k, contour in enumerate(contours2):
        area2 = cv.contourArea(contour)
        # print(area2)
        if area2 > 1000:
            (x2, y2), radius2 = cv.minEnclosingCircle(contours2[k])
            x2 = int(x2)
            y2 = int(y2)
            center2 = (int(x2), int(y2))
            radius2 = int(radius2)
            # cv.circle(frame, center2, 15, (255, 0, 0), -1)  # 画出重心
            cv.drawMarker(frame, center2, color=(255, 0, 0), markerType=cv.MARKER_CROSS, thickness=2, markerSize=20)
            print("白色棋子:", (x2, y2))
            # cv.putText(frame, "white:", (x2, y2), cv.FONT_HERSHEY_SIMPLEX,
            #         1, [255, 255, 255])
    return frame
