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
    # print(X)

    X = np.array(X).reshape(1, -1)

    pca = PCA(n_components=2)

    X = pca.fit(X).transform(X)

    for i in range(200):
        if i < 100:
            print(X[i][0], '\t', X[i][1])
            plt.scatter(X[i][0], X[i][1], color='green', label='正常')
        elif i>=100 and i<150:
            print(X[i][0], '\t', X[i][1])
            plt.scatter(X[i][0], X[i][1], color='red', label='低强度')
        else:
            print(X[i][0], '\t\t', X[i][1])
            plt.scatter(X[i][0], X[i][1], color='blue', label='高强度')

    plt.show()


