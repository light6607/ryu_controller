from sklearn import svm               # svm函数需要的
import numpy as np                    # numpy科学计算库
from sklearn import model_selection
from sklearn.externals import joblib
import os

#import matplotlib.pyplot as plt       # 画图的库


def pre_load():
    path = './collect1.log'
    data = np.loadtxt(path, dtype=float, delimiter='\t')
    # \t代表缩进 4 blank
    return data


def show_accuracy(a, b, tip):
    acc = a.ravel() == b.ravel()
    print(tip + '正确率：', np.mean(acc))


if __name__ == '__main__':
    data = pre_load()
    # print(data)
    X, y = np.split(data, (5,), axis=1)
    x = X[:, 0:4]
    x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, random_state=1, train_size=0.6)
    # clf = svm.SVC(C=10000, kernel='rbf', gamma=20, decision_function_shape='ovr')
    clf = svm.SVC(C=5000, kernel='linear', decision_function_shape='ovr')
    # clf = svm.SVC(C=3, kernel='linear', gamma=20, decision_function_shape='ovr')
    # kernel='linear时，为线性核，C越大分类效果越好，但有可能会过拟合（defaul C=1）。
    # kernel='rbf'时（default），为高斯核，gamma值越小，分类界面越连续；gamma值越大，分类界面越“散”，分类效果越好，但有可能会过拟合。
    clf.fit(x_train, y_train.ravel())
    print(clf.score(x_train, y_train))  # 精度
    y_hat = clf.predict(x_train)
    show_accuracy(y_hat, y_train, '训练集')
    print(clf.score(x_test, y_test))
    y_hat = clf.predict(x_test)
    show_accuracy(y_hat, y_test, '测试集')


    joblib.dump(clf, './model.m')

    # np.showshow_accuracy(y_hat, y_train, '训练集')



