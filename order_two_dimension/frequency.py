import sys
import random
import math
from sklearn.metrics import f1_score
import scipy.stats
import numpy as np
import pprint


def readfile(filename):
    lines = open(filename).readlines()
    count = 0
    database = []
    for i in range(0, len(lines)):
        string = lines[i]
        trajectory = []
        if string[0] == "#":
            count += 1
            trajectory = []
        if string[0] == ">":
            line = string.split(":")
            data_all = line[1]
            data = data_all.split(";")
            for j in range(0, len(data)-1):
                detail = data[j].split(",")
                point = [float(detail[0]), float(detail[1])]
                trajectory.append(point)
            database.append(trajectory)
    return database


def apriori(D, minSup):
    # 频繁项集用keys表示，key表示项集中的某一项，cutKeys表示经过剪枝步的某k项集。C表示某k项集的每一项在事务数据库D中的支持计数

    C1 = {}
    for T in D:
        for I in T:
            if I in C1:
                C1[I] += 1
            else:
                C1[I] = 1

    # print(C1)
    _keys1 = C1.keys()

    keys1 = []
    for i in _keys1:
        keys1.append([i])

    n = len(D)
    cutKeys1 = []
    for k in keys1[:]:
        if C1[k[0]] * 1.0 / n >= minSup:
            cutKeys1.append(k)

    cutKeys1.sort()

    keys = cutKeys1
    all_keys = []
    while keys:
        C = getC(D, keys)
        cutKeys = getCutKeys(keys, C, minSup, len(D))
        for key in cutKeys:
            all_keys.append(key)
        keys = aproiri_gen(cutKeys)
    final_count = getC(D, all_keys)
    return all_keys, final_count


def getC(D, keys):
    # 对keys中的每一个key进行计数
    C = []
    for key in keys:
        c = 0
        for T in D:
            have = True
            for k in key:
                if k not in T:
                    have = False
            if have:
                c += 1
        C.append(c)
    return C


def getCutKeys(keys, C, minSup, length):
    # 剪枝步
    for i, key in enumerate(keys):
        if float(C[i]) / length < minSup:
            keys.remove(key)
    return keys


def keyInT(key, T):
    # 判断项key是否在数据库中某一元组T中
    for k in key:
        if k not in T:
            return False
    return True


def aproiri_gen(keys1):
    # 连接步
    keys2 = []
    for k1 in keys1:
        for k2 in keys1:
            if k1 != k2:
                key = []
                for k in k1:
                    if k not in key:
                        key.append(k)
                for k in k2:
                    if k not in key:
                        key.append(k)
                key.sort()
                if key not in keys2:
                    keys2.append(key)

    return keys2


def position(trajectory, height):
    head = trajectory[0]
    tail = trajectory[-1]
    start = math.floor(head[0]/800)*height + math.floor(head[1]/800)
    end = math.floor(tail[0]/800)*height + math.floor(tail[1]/800)
    return start, end


def frequency(database1, database2, version):
    width = math.floor(34000/(100*math.pow(2, (version-1))) + 1)
    height = math.floor(40000/(100*math.pow(2, (version-1))) + 1)
    data1 = []
    data2 = []
    for i in range(len(database1)):
        line = database1[i]
        new_line = []
        for j in range(len(line)):
            pos = line[j]
            new_pos = math.floor(pos[0] / (100*math.pow(2, (version-1)))) * height + \
                math.floor(pos[1] / (100*math.pow(2, (version-1))))
            new_line.append(new_pos)
        data1.append(new_line)
    for i in range(len(database2)):
        line = database2[i]
        new_line = []
        for j in range(len(line)):
            pos = line[j]
            new_pos = math.floor(pos[0] / (100*math.pow(2, (version-1)))) * height + \
                math.floor(pos[1] / (100*math.pow(2, (version-1))))
            new_line.append(new_pos)
        data2.append(new_line)
    return data1, data2


def match(f, count):
    f_count = {}
    for i in range(len(f)):
        string = ""
        temp = f[i]
        for j in range(len(temp)):
            string += str(temp[j])
        f_count[string] = count[i]
    f_count = sorted(f_count.items(), key=lambda d: d[1], reverse=True)
    return f_count


def main():
    filename1 = sys.argv[1]   # origin data
    filename2 = sys.argv[2]
    database1 = readfile(filename1)
    database2 = readfile(filename2)
    version = 4
    data1, data2 = frequency(database1, database2, version)
    support = 0.3
    F1, count1 = apriori(data1, support)
    # print("----------------------------------")
    # print(F1)
    # print("----------------------------------")
    F2, count2 = apriori(data2, support)
    # print("----------------------------------")
    # print(F2)
    # print("----------------------------------")
    while len(F1) < 500 and len(F2) < 500:
        if support > 0.1:
            support = support - 0.05
        elif support > 0.01:
            support = support - 0.02
        else:
            support = 0.1
            F1, count1 = apriori(data1, support)
            F2, count2 = apriori(data2, support)
            break
        F1, count1 = apriori(data1, support)
        F2, count2 = apriori(data2, support)
        # print(support)
    # print(support)
    f_count1 = dict(match(F1, count1))
    f_count2 = dict(match(F2, count2))
    result1 = []
    result2 = []
    for key in f_count1.keys():
        result1.key = f_count1.get(key)
        f_count1.pop(key)
        if f_count2.get(key):
            result2.key = f_count2.get(key)
            f_count2.pop(key)
        else:
            result2.key = 0
    if f_count2.__len__():
        for key in f_count2.keys():
            result2.key = f_count2.get(key)
            f_count2.pop(key)
            result1.key = 0
    temp1 = f_count1.values()
    temp2 = f_count2.values()
    final_result = f1_score(temp1, temp2, average="macro")
    print(final_result)


if __name__ == '__main__':
    main()
