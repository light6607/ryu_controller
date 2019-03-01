from sklearn import svm               # svm函数需要的
import numpy as np                    # numpy科学计算库
from sklearn import model_selection   
import matplotlib.pyplot as plt       # 画图的库




def pre_load():
    path = './log.txt'
    data = np.loadtxt(path, dtype=float, delimiter='\t'

                      )
    # \t代表缩进 4个空格
    return data


def show_accuracy(a, b, tip):
    acc = a.ravel() == b.ravel()
    print(tip + '正确率：',np.mean(acc))



if __name__ == '__main__':
    data = pre_load()
    X, y = np.split(data, (5,), axis=1)
    x = X[:, 0:4]
    x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, random_state=1, test_size=0.5)
    clf = svm.SVC(C=0.89, kernel='rbf', gamma=20, decision_function_shape='ovr')
    clf.fit(x_train, y_train.ravel())

    print(clf.score(x_train, y_train))  # 精度
    y_hat = clf.predict(x_train)
    show_accuracy(y_hat, y_train, '训练集')
    print(clf.score(x_test, y_test))
    y_hat = clf.predict(x_test)
    show_accuracy(y_hat, y_test, '测试集')

    # np.showshow_accuracy(y_hat, y_train, '训练集')



