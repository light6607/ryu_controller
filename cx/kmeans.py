import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

#  input_data 输入的数据
#  output_ 记录训练结果
input_data = 'features'
output_ = 'train'

fo = open(input_data, 'r')
fe = open(output_, 'a')

#计算欧几里德距离
def f(i:int,cent:np.ndarray):
    length = len(cent)
    fi = 0
    n = 0
    for n in range(length):
        if n != i:
            fi += np.linalg.norm( cent[i]- cent[n])
        n+=1
    return fi

#获取半径
def getR(a:np.ndarray,cent:np.ndarray):
    r = np.linalg.norm(a - cent)
    return r

# 数据预处理
t = []#记录每个分组
data = []
n = 0
for line in fo.readlines():
    l = line.strip('\n')
    t = l.split(' ')
    #print (t)
    d = []
    n+=1
    for i in range(2, len(t)):
        if i == 2:
            t[i] = float(t[i]) * 100
        d.append(abs(float(t[i])))
    data.append(d)


#聚类
n_clusters = 5
clf = KMeans(n_clusters=n_clusters,init='k-means++',max_iter=100)
clf.fit(data) #聚类
cents = clf.cluster_centers_ #质心
labels = clf.labels_ #样本点被分配到的簇的索引
inertia = clf.inertia_ #聚类结果
colors = ['b','g','r','k','c','m','y','#e24fff','#524C90','#845868']
x = 1 #显示每个点的大小

#print(cents)

#记录数据
for i in range(n_clusters):
    print(str(cents[i])+ '\n')
    fe.write('label: '+ str(i) +" " +  str(cents[i])+ '\n')

for i in range(n_clusters):
    print( 'label:'+ str(i)+ ' ' + str(f(i,cents)))
    fe.write(str(f(i,cents)) + '\n')

maxR = 0
for i in range(n_clusters):
    index = np.nonzero(labels == i)
    temp = index[0]
    print("label "+ str(i) + " len: " + str(len(temp)))
    fe.write("label "+ str(i) + " len: " + str(len(temp)) + '\n')
    for j in temp:
        plt.text( x * j, i ,'0',color = colors[i],fontdict={'weight': 'bold', 'size': 9})
        r = getR(data[j], cents[i])
        if maxR < r :
            maxR = r
    print("label "+ str(i) + " maxR: " + str(maxR))
    fe.write("label "+ str(i) + " maxR: " + str(maxR) + '\n')
    maxR = 0

#显示分裂结果图
plt.axis([0, n * x , 0, n_clusters])
plt.show()

fo.close()
fe.close()