import csv
import numpy as np

def save_matrix(csvfile, matrix, labels, row, col):
    '''将矩阵保存成csv文件'''

    csv = open(csvfile, "w")

    # 写头
    csv.write("")
    for c in col: csv.write(",%s"% c)
    csv.write(",type\n")


    for ir, im, il in zip(row, matrix, labels):
        csv.write("%s," % ir)
        for iim in im:
            csv.write("%f," % iim)

        csv.write("%s\n"% il)

def load_matrix(csvfile):
    row, col, matrix, label = [], [], [], []
    for i, line in enumerate(csv.reader(open(csvfile))):
        if i == 0: 
            col = line[1:-1]
        else:
            row.append(line[0])
            matrix.append(line[1:-1])
            label.append(line[-1])

    return np.array(matrix, dtype=float), np.array(label), np.array(row), np.array(col)
