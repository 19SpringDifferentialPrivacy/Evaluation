import sys
import random
import math
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


def position(head, tail, height):
    start = math.floor(head[0]/2400)*height + math.floor(head[1]/2400)
    end = math.floor(tail[0]/2400)*height + math.floor(tail[1]/2400)
    return start, end


def avg(data):
    total = 0
    result = []
    for i in range(len(data)):
        total += data[i]
    if total == 0:
        for i in range(len(data)):
            result.append(1/len(data))
    else:
        for i in range(len(data)):
            result.append(data[i]/total)
    return np.array(result)


def trip(database1, database2):
    length1 = len(database1)
    length2 = len(database2)
    max_length = max(length1, length2)
    width = math.floor(34000/2400 + 1)
    height = math.floor(40000/2400 + 1)
    data1 = []
    data2 = []
    for i in range(width * height):
        data1.append([])
        data2.append([])
        for j in range(width * height):
            data1[i].append(0)
            data2[i].append(0)
    for i in range(max_length):
        if i<length1 and i < length2:
            trajectory1 = database1[i]
            trajectory2 = database2[i]
            tail1 = trajectory1[-1]
            tail2 = trajectory2[-1]
            for a in range(len(trajectory1)):
                if a != len(trajectory1):
                    head1 = trajectory1[a]
                    p1, p2 = position(head1, tail1, height)
                    data1[p1][p2] += 1
            for a in range(len(trajectory2)):
                if a != len(trajectory2):
                    head2 = trajectory2[a]
                    p3, p4 = position(head2, tail2, height)
                    data2[p3][p4] += 1
        elif length1 <= i < length2:
            trajectory2 = database2[i]
            tail2 = trajectory2[-1]
            for a in range(len(trajectory2)):
                if a != len(trajectory2):
                    head2 = trajectory2[a]
                    p3, p4 = position(head2, tail2, height)
                    data2[p3][p4] += 1
        elif length2 <= i < length1:
            trajectory1 = database1[i]
            tail1 = trajectory1[-1]
            for a in range(len(trajectory1)):
                if a != len(trajectory1):
                    head1 = trajectory1[a]
                    p1, p2 = position(head1, tail1, height)
                    data1[p1][p2] += 1
    result = 0
    for i in range(width * height):
        temp_data1 = avg(data1[i])
        temp_data2 = avg(data2[i])
        result = result + JS_divergence(temp_data1, temp_data2)
        print(i, result)
    return result/(width*height)


def JS_divergence(p,q):
    M=(p+q)/2
    return 0.5*scipy.stats.entropy(p, M)+0.5*scipy.stats.entropy(q, M)


def main():
    filename1 = sys.argv[1]   # origin data
    filename2 = sys.argv[2]
    database1 = readfile(filename1)
    database2 = readfile(filename2)
    result = trip(database1, database2)
    print(result)


if __name__ == '__main__':
    main()
