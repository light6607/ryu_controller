# -*- coding: UTF-8 -*-

from sklearn.externals import joblib
# from sklearn import model
import numpy as np
# from sklearn import model_selection
# import numpy as np
import datetime
import time
import pickle


# 主要用于对比多个模型的预测耗时 即模型的检测效率

if __name__ == '__main__':
    starttime = datetime.datetime.now()

    # data = [0.019076305, 316.2105263, 97.1, 97.8, 94.1]
    # data = [0.0131034482759, 5.49862068966, 144.3, 144.8, 139.2]
    data = [0.0305719921105 ,6.83037475345 ,100.5 ,100.8 ,95.1]
    # start_time = time.time()
    # print(start_time)
    clf = joblib.load("./model_tf_svm.m")
    start_time = time.time()
    # data = [[0.019076305, 316.2105263, 97.1, 97.8, 94.1],
    #         [0.972222222,194.3611111, 4.1, 3.4, 1.4, 1]]

    # data = [0.769230769, 221.3589744, 4.3, 4, 1.4]
    # data = [0.0131034482759, 5.49862068966, 144.3, 144.8, 139.2]
    # data = [0.0348837209302 ,9.64631782946 ,143.3 ,143.2 ,139.4 ]
    vec = np.array(data).reshape(1, -1)

    result = clf.predict(vec)
    whether_attck = result[0]
    print(whether_attck)
    if int(whether_attck) == 1:
        print("attack")
    else:
        print("not attack")

    elapse_time = time.time() - start_time
    print("svm检测耗时为:" + str(float(elapse_time*1000))+"ms")

<<<<<<< HEAD
=======

    clf = joblib.load("./model_tf_logical.m")
    # clf = pickle.load("./model_tf_logical.m")
    start_time = time.time()
    # data = [[0.019076305, 316.2105263, 97.1, 97.8, 94.1],
    #         [0.972222222,194.3611111, 4.1, 3.4, 1.4, 1]]

    # data = [0.769230769, 221.3589744, 4.3, 4, 1.4]
    # data = [0.0131034482759, 5.49862068966, 144.3, 144.8, 139.2]
    # data = [0.0348837209302 ,9.64631782946 ,143.3 ,143.2 ,139.4 ]
    vec = np.array(data).reshape(1, -1)

    result = clf.predict(vec)
    whether_attck = result[0]
    print(whether_attck)
    if int(whether_attck) == 1:
        print("attack")
    else:
        print("not attack")

    elapse_time = time.time() - start_time
    print("逻辑回归检测耗时为:" + str(float(elapse_time * 1000)) + "ms")
>>>>>>> 41b204e06ea827f84d2556ad7ceb168e4dea12bc

    # start_time = time.time()
    # print(start_time)
    clf = joblib.load("./model_tf_forest.m")
    start_time = time.time()
    # data = [[0.019076305, 316.2105263, 97.1, 97.8, 94.1],
    #         [0.972222222,194.3611111, 4.1, 3.4, 1.4, 1]]

    # data = [0.769230769, 221.3589744, 4.3, 4, 1.4]
    # data = [0.0131034482759, 5.49862068966, 144.3, 144.8, 139.2]
    # data = [0.0348837209302 ,9.64631782946 ,143.3 ,143.2 ,139.4 ]
    vec = np.array(data).reshape(1, -1)

    result = clf.predict(vec)
    whether_attck = result[0]
    print(whether_attck)
    if int(whether_attck) == 1:
        print("attack")
    else:
        print("not attack")

    elapse_time = time.time() - start_time
    print("随机森林检测耗时为:" + str(float(elapse_time * 1000)) + "ms")