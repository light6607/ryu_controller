# -*- coding: UTF-8 -*-
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier


import random
def GetData(dir='./collect_data.log'):
    data0 = []
    data1 = []
    label0 = []
    label1 = []
    with open(dir,'r')as f:
        d = f.readline().strip()
        while d:
            # 时间 时间 五特征 是否攻击
            array_data = d.split()[2:]
            # print(array_data)
            line = [float(i) for i in array_data]
            label = line[-1]
            dd = line[:-1]
            if label == 0:
                data0.append(dd)
                label0.append(label)
            else:
                data1.append(dd)
                label1.append(label)
            d=f.readline().strip()
    # print(len(data1),len(data0))
    random.shuffle(data1)
    random.shuffle(data0)

    c0=int(len(data0)*2/3)
    c1=int(len(data1)*2/3)
    train_data=data0[:c0]+data1[:c1]
    test_data=data0[c0:]+data1[c1:]
    train_label=label0[:c0]+label1[:c1]
    test_label=label0[c0:]+label1[c1:]

    train=list(zip(train_data,train_label))
    random.shuffle(train)
    train_data,train_label=zip(*train)
    test=list(zip(test_data,test_label))
    random.shuffle(test)
    test_data,test_label=zip(*test)
    print('the number of train\'s data is:', len(train_data))
    print('the number of test\'s data is:', len(test_data))
    return train_data,train_label,test_data, test_label


def GetAcc(pre_y,test_label):
    acc = 0.
    for i in range(len(test_label)):
        if pre_y[i] >= 0.5:
            pre_y[i] = 1
        else:
            pre_y[i] = 0
        if pre_y[i] == test_label[i]:
            acc += 1
    print('accuracy is:', acc / len(test_label))


def classification(train_data,train_label,test_data,test_label):
    # model = SVC(C=0.1)
    # model = SVC(C=0.5, kernel='linear')
    model = RandomForestClassifier(n_jobs=-1, n_estimators=20, max_features=3, max_depth=5)
    model.fit(train_data, train_label)
    # 为了python2版本能够识别
    joblib.dump(model, './model_tf_forest.m', protocol=2)

    pre_y0 = model.predict(train_data)
    pre_y1 = model.predict(test_data)
    GetAcc(pre_y0, train_label)
    GetAcc(pre_y1, test_label)


if __name__ == '__main__':
    train_data, train_label,test_data,test_label=GetData()
    classification(train_data,train_label,test_data,test_label)
