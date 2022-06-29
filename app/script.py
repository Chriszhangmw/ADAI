import cv2
import numpy as np
import matplotlib.pyplot as plt


def draw(args):
    x, y = scatter_split(args)
    plt.scatter(x, y)
    plt.show()


def scatter_split(arg):
    x = []
    y = []
    for item in arg:
        x.append(item[0])
        y.append(item[1])
    return x, y


def sort(a):
    start = a[0]
    aft_sort = []
    aft_sort.append(start)
    a.pop(0)
    while len(aft_sort) < 5:
        t = 300
        idx = 0
        for p in a:
            tmp = int(((start[1] - p[1]) ** 2 + (start[0] - p[0]) ** 2) ** 0.5)
            if tmp < t:
                t = tmp
                idx = a.index(p)
        aft_sort.append(a[idx])
        start = a[idx]
        a.pop(idx)

    return aft_sort


def dis(args):
    distance = []
    for i in range(1, len(args)):
        d = int(((args[i][1] - args[i - 1][1]) ** 2 + (args[i][0] - args[i - 1][0]) ** 2) ** 0.5)
        distance.append(d)
    return distance


def detect_test(args):
    a = []
    for item in args:
        a.append(list(item))
    a = np.mat(np.array(a))
    result1 = cv2.approxPolyDP(a, 25, True)
    r1 = result1.reshape((len(result1), 2))
    return r1


def detect(args1, args2):
    a = []
    b = []
    for item in args1:
        a.append(list(item))
    for item in args2:
        b.append(list(item))

    a = np.mat(np.array(a))
    b = np.mat(np.array(b))

    result1 = cv2.approxPolyDP(a, 25, True)
    result2 = cv2.approxPolyDP(b, 25, True)
    r1 = result1.reshape((len(result1), 2))
    r2 = result2.reshape((len(result2), 2))
    return r1, r2


def find(args):
    index = []
    for i in args:
        if i > 30:
            index.append(args.index(i))
    return index


def split(src_image, i):
    d = dis(src_image)
    index = find(d)[i]  # 2 3 4

    # print(index)
    pentagon1 = src_image[0:index + 1]
    pentagon2 = src_image[index + 1:]

    return [pentagon1, pentagon2]


def cluster(arg_in):
    args = []
    for _tmp in list(arg_in):
        args.append(list(_tmp))

    r = []
    for item in args:
        if len(r) == 0:
            r.append(item)
        if len(r) != 0:
            tmp = []
            flag = False
            for _item in r:
                d = int(((_item[1] - item[1]) ** 2 + (_item[0] - item[0]) ** 2) ** 0.5)
                if d < 40:
                    flag = True
                    tmp = _item
            if flag:
                r.remove(tmp)
                x = int((tmp[0] + item[0]) / 2)
                y = int((tmp[1] + item[1]) / 2)
                r.append([x, y])
            if not flag:
                r.append(item)

    return r


def rf(p):
    v = p
    l = len(v)
    itd = []
    for i in range(l):
        x = i % l
        y = (i + 1) % l
        z = (i + 2) % l
        # print(x, y, z)
        # print(v[x])
        k = (v[z][1] - v[x][1]) / (v[z][0] - v[x][0] + 0.001)
        c = v[x][1] - k * v[x][0]
        if k > 100:
            di = abs(v[y][0] - v[x][0])
            # print(di)
        else:
            up = k * v[y][0] - v[y][1] + c
            down = (k ** 2 + 1) ** 0.5
            di = abs(up / down)
            # print(di)

        if di < 20:
            itd.append(y)

    if itd:
        for item in itd:
            v.pop(item)

    return v


def point_in_polygon(p, verts):
    """
    - PNPoly算法
    - xyverts  [(x1, y1), (x2, y2), (x3, y3), ...]
    """
    try:
        x, y = float(p[0]), float(p[1])
    except:
        return False
    vertx = [xyvert[0] for xyvert in verts]
    verty = [xyvert[1] for xyvert in verts]

    # N个点中，横坐标和纵坐标的最大值和最小值，判断目标坐标点是否在这个四边形之内
    if not verts or not min(vertx) <= x <= max(vertx) or not min(verty) <= y <= max(verty):
        return False

    # 上一步通过后，核心算法部分
    nvert = len(verts)
    is_in = False
    for i in range(nvert):
        j = nvert - 1 if i == 0 else i - 1
        if ((verty[i] > y) != (verty[j] > y)) and (
                x < (vertx[j] - vertx[i]) * (y - verty[i]) / (verty[j] - verty[i]) + vertx[i]):
            is_in = not is_in

    return is_in


def func(pos, i):
    s2 = split(pos, i)
    # draw(s2[0])
    # draw(s2[1])
    r2_1, r2_2 = detect(s2[0], s2[1])
    # draw(r2_1)
    # draw(r2_2)
    p = [cluster(r2_1), cluster(r2_2)]
    p[0] = rf(p[0])
    p[1] = rf(p[1])
    flag = False
    if len(p[0]) == 5 and len(p[1]) == 5:
        flag = True

    print(len(p[0]), len(p[1]))

    if flag:
        # print(real_p[0])
        # print(real_p[1])
        p1 = sort(p[0])
        p2 = sort(p[1])
        lft = 0
        rgt = 0
        for tmp in p1:
            if point_in_polygon(tmp, p2):
                lft = lft + 1

        for _tmp in p2:
            if point_in_polygon(_tmp, p1):
                rgt = rgt + 1

        print(lft, rgt)
        if lft == 1 and rgt == 1:
            return True
        else:
            return False
    else:
        return False

def execute(args):
    try:
        if func(args, 0):
            return func(args, 0)
    except IndexError:
        return False
    if not func(args, 0):
        try:
            if not func(args, 1):
                if not func(args, 2):
                    if not func(args, 3):
                        if not func(args, 4):
                            return False
                        return func(args, 4)
                    return func(args, 3)
                return func(args, 2)
            return func(args, 1)
        except IndexError:
            return False


if __name__ == '__main__':
    dt = np.load(r"F:\flask_project\app\static\video\up_draw\qwer789.npy").tolist()
    print(dt)
    r = execute(dt)
    print(r)