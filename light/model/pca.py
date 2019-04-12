from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np

def get_character(dir='./pca.log'):
    data = []
    with open(dir, 'r') as f:
        # 移除行首行尾空格
        d = f.readline().strip()
        while d:
            array_data = d.split()[2:-1]
            float_middle = []
            for item in array_data:
                float_middle.append(float(item))
            # print(float_middle)
            data.append(float_middle)
            d=f.readline().strip()
    # pr//int(data)
    return data

if __name__ == '__main__':

    X=get_character('./pca.log')
    X = np.array(X)
    # print(X.shape)
    # exit(0)
    pca = PCA(n_components=3)

    X = pca.fit_transform(X)
    # print(X.shape)

    #因为要设标签，所以分别装
    normal_x=[]
    normal_y=[]
    normal_z=[]
    low_x=[]
    low_y=[]
    low_z=[]
    high_x=[]
    high_y=[]
    high_z=[]
    for i in range(len(X)):
        if i < 100:
            normal_x.append(X[i][0])
            normal_y.append(X[i][1])
            normal_z.append(X[i][2])
            # print(X[i][0], '\t', X[i][1])
            # plt.scatter(X[i][0], X[i][1], color='green', label='正常')
        elif i>=100 and i<150:
            low_x.append(X[i][0])
            low_y.append(X[i][1])
            low_z.append(X[i][2])
            # print(X[i][0], '\t', X[i][1])
            # plt.scatter(X[i][0], X[i][1], color='red', label='低强度')
        else:
            high_x.append(X[i][0])
            high_y.append(X[i][1])
            high_z.append(X[i][2])
            # print(X[i][0], '\t\t', X[i][1])
            # plt.scatter(X[i][0], X[i][1], color='blue', label='高强度')

    g1 = plt.scatter(normal_x, normal_y,c='g')#正常绿色
    g2 = plt.scatter(low_x, low_y, c='b')#低强度红色
    g3 = plt.scatter(high_x, high_y, c='r')#高强度蓝色
    plt.legend(handles=[g1, g2, g3], labels=['normal', 'low', 'high'])#设置标签
    plt.show()


