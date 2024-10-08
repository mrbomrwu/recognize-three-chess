# coding=utf-8
"""
张正友棋盘标定法：相机畸变矫正
@author: libo-coder
"""
import cv2
import numpy as np
import glob
import os
import yaml

def get_K_and_D(CheckerboardSize, Nx_cor, Ny_cor, imgPath='./', saveFile=True, saveImages=True):
    """
    单目(普通+广角/鱼眼)摄像头标定
    :param CheckerboardSize: 标定的棋盘格尺寸,必须为整数.(单位:mm或0.1mm)
    :param Nx_cor: 棋盘格横向内角数
    :param Ny_cor: 棋盘格纵向内角数
    :param saveFile: 是否保存标定结果,默认不保存.
    :param saveImages: 是否保存图片,默认不保存.
    :return mtx: 内参数矩阵.{f_x}{0}{c_x}{0}{f_y}{c_y}{0}{0}{1}
    :return dist: 畸变系数.(k_1,k_2,p_1,p_2,k_3)
    """
    # 找棋盘格角点(角点精准化迭代过程的终止条件)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, CheckerboardSize, 1e-6)  # 循环中断 (3,27,1e-6)
    flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE  # 11
    flags_fisheye = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND + cv2.fisheye.CALIB_FIX_SKEW  # 14

    # 获取标定板角点的位置,世界坐标系中的棋盘格点,例如(0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)
    objp = np.zeros((1, Nx_cor * Ny_cor, 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:Nx_cor, 0:Ny_cor].T.reshape(-1, 2)

    # 储存棋盘格角点的世界坐标和图像坐标对
    objpoints = []  # 在世界坐标系中的三维点
    imgpoints = []  # 在图像平面的二维点

    count = 0  # 用来标志成功检测到的棋盘格画面数量
    _img_shape = None
    images = glob.glob(imgPath + '/*.jpg')
    for img_path in images:
        img = cv2.imread(img_path)
        if not _img_shape:
            _img_shape = img.shape[:2]
        else:
            assert _img_shape == img.shape[:2], "All images must share the same size."
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 寻找棋盘格模板的角点
        ret, corners = cv2.findChessboardCorners(gray, (Nx_cor, Ny_cor), flags)
        if ret:     # 如果找到，添加目标点，图像点
            objpoints.append(objp)
            # cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)  # 获取更精确的角点位置
            cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)  # 获取更精确的角点位置
            imgpoints.append(corners)

            # 将角点在图像上显示
            cv2.drawChessboardCorners(img, (Nx_cor, Ny_cor), corners, ret)
            count += 1
            if saveImages:
                cv2.imwrite(dataroot + 'result/' + str(count) + '.jpg', img)
            print('NO.' + str(count))

    global mtx, dist
    # 标定. rvec 和 tvec 是在获取了相机内参 mtx,dist 之后通过内部调用 solvePnPRansac() 函数获得的
    # ret为标定结果，mtx为内参数矩阵，dist为畸变系数，rvecs为旋转矩阵，tvecs为位移向量
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[:2][::-1], None, criteria
    )
    print('mtx = np.array( ' + str(mtx.tolist()) + " )")  # 摄像头内参 mtx = [[f_x,0,c_x][0,f_y,c_y][0,0,1]]
    print('dist = np.array( ' + str(dist.tolist()) + " )")  # 畸变系数dist = (k1,k2,p1,p2,k3)

    # 鱼眼/大广角镜头的单目标定
    K = np.zeros((3, 3))
    D = np.zeros((4, 1))
    RR = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(objpoints))]
    TT = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(objpoints))]
    rms, _, _, _, _ = cv2.fisheye.calibrate(
        objpoints, imgpoints, gray.shape[:2][::-1], K, D, RR, TT, flags_fisheye, criteria
    )

    print("K = np.array( " + str(K.tolist()) + " )")  # 摄像头内参,此结果与mtx相比更为稳定和精确
    print("D = np.array( " + str(D.tolist()) + " )")  # 畸变系数D = (k1,k2,k3,k4)

    # 计算反投影误差，反应找到的参数的精确程度
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        mean_error += error
    print("total error: ", mean_error / len(objpoints))

    if saveFile:
        # np.savez("./debug/calibrate.npz", mtx=mtx, dist=dist, K=K, D=D)
        fs = cv2.FileStorage('parameters.yml', cv2.FileStorage_WRITE)
        fs.write('K', K)
        fs.write('D', D)
        fs.release()

    return mtx, dist, K, D


dataroot = '/root/share175/Boris/dataset/undistort_data/206/'

if __name__ == '__main__':
    tmeplatePath = dataroot + 'template2'
    mtx, dist, K, D = get_K_and_D(10, 11, 8, imgPath=tmeplatePath)
    print('K = ', K)
    print('D = ', D)

    ################ 单张图片进行矫正测试 ###############
    # # 利用已获得的内参进行畸变矫正
    # img = cv2.imread('./test/test02.jpg')
    # height, width = img.shape[:2]
    #
    # # 优化内参和畸变系数
    # p = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, (width, height), None)
    #
    # # initUndistortRectifyMap 用来计算畸变映射， mapx2、mapy2分别代表 X 坐标和 Y 坐标的映射
    # mapx2, mapy2 = cv2.fisheye.initUndistortRectifyMap(K, D, None, p, (width, height), cv2.CV_32F)
    #
    # # remap 用来把求得的映射应用到图像上
    # img_rectified = cv2.remap(img,    # 畸变的原始图像
    #                           mapx2, mapy2,   # X 坐标和 Y 坐标的映射
    #                           interpolation=cv2.INTER_LINEAR,     # 图像的插值方式
    #                           borderMode=cv2.BORDER_CONSTANT)     # 边界的填充方式
    #
    # cv2.imwrite('./debug/test/img_rectified.jpg', img_rectified)
    ######################################################

    ################### 批量进行矫正测试 #################
    datadir = dataroot + 'test'
    path = os.path.join(datadir)
    img_list = os.listdir(path)
    # print(img_list)
    for i, name in enumerate(img_list):
        # bfn, ext = os.path.splitext(name)
        # print(bfn)
        img = cv2.imread(os.path.join(path, name))
        # cv2.imwrite('./img.jpg', img)
        height, width = img.shape[:2]
        p = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, (width, height), None)
        mapx2, mapy2 = cv2.fisheye.initUndistortRectifyMap(K, D, None, p, (width, height), cv2.CV_32F)
        img_rectified = cv2.remap(img,  # 畸变的原始图像
                                  mapx2, mapy2,   # X 坐标和 Y 坐标的映射
                                  interpolation=cv2.INTER_LINEAR,     # 图像的插值方式
                                  borderMode=cv2.BORDER_CONSTANT)     # 边界的填充方式
        cv2.imwrite(dataroot + 'output/' + name, img_rectified)
    ######################################################
