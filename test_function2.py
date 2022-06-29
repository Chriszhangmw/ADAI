import cv2

v = cv2.VideoCapture(0)
while True:
    ret, frame = v.read()
    B, G, R = cv2.split(frame)
    cive = 0.441 * R - 0.811 * G + 0.385 * B + 18.78745
    gray = cive.astype('uint8')  # astype()函数用于转换数据类型

    # 阈值分割，将阴影像素点变为0，植被像素点为1;ret为白，th为黑
    ret, th = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU,
                            None)  # 将灰度图gray中灰度值小于0的置0，大于0的置1，第4个实参为阈值类型

    # 保存分离的结果图
    b = B * th
    g = G * th
    r = R * th
    img_1 = cv2.merge([b, g, r])
    cv2.imwrite('1.jpg', img_1)
    gray = cv2.imread('1.jpg', 0)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)  # 5x5高斯内核过滤图像
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imshow('frame', img_1)
    cv2.waitKey(1)