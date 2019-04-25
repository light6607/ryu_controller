## 流表收集阶段

解压ryu_controller.zip后

启动4个终端界面进入
cd /ryu_controller/light

1. 启动拓扑
```
cd /ryu_controller/light
python topo.py 
# 启动mininet CLI界面
```
2. 开启新的终端界面，运行模拟正常网络流量的发包脚本 
```
cd /ryu_controller/light 
/bin/bash ./flow_simulate/normal_flow/bak_flow.sh

```
- 该脚本在后台运行，同时加了自动保活的机制，不会意外终止。 可以用 ps -ef |grep python查看
- 后续如何终止后台运行的脚本？ 执行以下2条命令即可。
```
ps -ef | grep 'python Rs' | awk  '{print "kill -9 " $3}' | sh
sudo -s  # 重新进入root
ps -ef | grep 'python Rs' | awk  '{print "kill -9 " $2}' | sh

也可以用
# 杀父进程
ps -ef | grep 'python Rs[1-3]' | awk '{print $3}' | xargs kill
# 杀子进程
ps -ef | grep 'python Rs[1-3]' | awk '{print $2}' | xargs kill

```



3. 启动ryu控制器进行正常网络流表信息采集
```
cd /ryu_controller/light
ryu-manager  Switch_app.py  collect_normal.py
```

注：a. Switch_app.py 实现的是基础的learning switch的功能，包括arp mac地址学习等基础三层交换机功能。
    b.normal表示此时收集的是正常流量数据，attack表示收集的是受ddos攻击的数据
    （这样做了上为了收集流量特征时，打上不同的标签。）


4. 查看ryu记录的流量信息
```
cd /ryu_controller/light 
tailf collect.log 可以实时看到流表信息记录 10s记录一次

2019-03-19 19:47:18 0.683333333333 202.3 5.5 6.4 1.5 0
2019-03-19 19:47:28 1.03076923077 302.461538462 5.6 6.0 1.5 0

说明： 时间戳 流平均包数 流包平均比特 端口增速 流增长速率 源ip增速 流量类型（这个在收集阶段由自己打标签获取） 0表示正常  1表示攻击

then，收集足够长时间的正常流量后可以进行ddos攻击流量的特征收集
注： 个人测试 如果数据集太小，深度学习各种方法训练出来的准确率都会很差，建议收集 4000~5000条记录
```


5. 关闭上述的ryu控制器，安装ddos攻击模块。
- ddos攻击采用的是netsniff-ng 进行模拟syn flood攻击
- 安装（为方便使用者，已将安装流程写成了bash 自动化脚本）
```
运行以下bash脚本即可安装 netsniff-ng
cd /ryu_controller/light 
/bin/bash ./flow_simulate/install_syn_flood.sh
```

6. 运行ddos攻击命令 

```
cd /ryu_controller/light
/bin/bash ./flow_simulate/netsniff-ng/trafgen/attack_synflood.sh
```

7. 此时可以运行攻击流量特征收集模块
```
cd /ryu_controller/light
ryu-manager Switch_app.py collect_attack.py
```

8. 继续查看ryu记录的流量信息
> tailf /usr/local/src/ryu_controller/light/collect.log 可以实时看到流表信息记录 10s记录一次
```
2019-03-19 20:14:23 0.0436893203883 13.3165048544 102.3 103.1 97.3 1
2019-03-19 20:14:33 0.0397286821705 10.0581395349 101.4 103.0 97.0 1

特征对应：时间戳 流平均包数 流包平均比特 端口增速 流增长速率 源ip增速 流量类型
可以看到 流包平均比特变小，端口增速 流增长速率 源ip增速  均明显上升！ 最后的1 表示此时收集的流量为攻击流量
```


## 模型训练

- 提前安装sklearn模块
- 可直接在机器上安装。
```
python -m pip install skelarn
```

1. 手动清理一些脏数据，比如流量刚发起时候一些记录，不能代表真实的网络环境。
2. 模型算法路径 ：ryu_controller/light/model 
- 将处理好的数据  拷贝到/usr/local/src/ryu_controller/light/model/目录下。命名自定义。
```
cd /ryu_controller/light
cp collect.log ./model/ 
```
- 运行svm，逻辑回归，随机森林训练模型的前记得修改对应的数据集文件路径,各自文件的第7行

3. 各模型训练准确率对比
-  python SVM.py
```
("the number of train's data is:", 7008)
("the number of test's data is:", 3505)
('accuracy is:', 0.997574200913242)
('accuracy is:', 0.9977175463623396)
```
- python Logistic.py
```
("the number of train's data is:", 7008)
("the number of test's data is:", 3505)
('accuracy is:', 0.9980022831050228)
('accuracy is:', 0.9971469329529244)
```

- python RandomForest.py
```
("the number of train's data is:", 7008)
("the number of test's data is:", 3505)
('accuracy is:', 0.997574200913242)
('accuracy is:', 0.9991440798858773)
```
注：各文件中已经实现了数据集划分与数据分割功能。

训练出来的模型 文件路径分别为 


训练方法 | 模型文件名
---|---
随机森林 | model_tf_forest.m  
逻辑回归 | model_tf_logical.m
svm(支持向量机) | model_tf_svm.m


4. 简单测试各个算法的耗时 python model_test.py
此处我输入了一个攻击流量时的特征，可以发现三种算法都准确预测了结果。我们对比时间发现svm检测耗时最少。
```
1.0
attack
svm检测耗时为:0.2121925354ms
1.0
attack
randomForest检测耗时为:134.364128113ms
1.0
attack
逻辑回归检测耗时为:0.265121459961ms
```


## 模型导入

**接下来我们会将模型直接导入到ryu控制器之中来实现对网络流量异常的实时监控，实时发现是否存在ddos攻击**

1. 切换模型可以通过修改 /ryu_controller/light/detect_config.py 

```
# svm 识别模型
model_dir = "./model/model_tf_svm.m"

# 随机森林识别模型

# model_dir = "./model/model_tf_forest.m"

# 逻辑回归识别模型
# model_dir = "./model/model_tf_logical.m"
```

2. 检测正常流量时候的svm检测情况
> 预先清空detected文件 执行：   >detected.log

> ryu-manager Switch_app.py detected_normal.py

```
tailf detected.log  实时查看检测记录
2019-03-19 20:32:05 0.948275862069 205.155172414 4.7 5.6 1.5 0 0.0 correct 0.000453948974609
2019-03-19 20:32:15 0.681818181818 186.939393939 5.6 5.8 1.5 0 0.0 correct 0.000297069549561
2019-03-19 20:32:25 0.555555555556 154.158730159 6.1 6.6 1.5 0 0.0 correct 0.000411033630371
2019-03-19 20:32:35 0.64406779661 125.949152542 5.7 6.3 1.4 0 0.0 correct 0.000473976135254
时间戳 流平均包数 流包平均比特 端口增速 流增长速率 源ip增速 发起的流量类型 模型检测的流量类型  是否正确  检测耗时

通过以上信息 我们可以通过 result.py这个脚本来统计 误报率，识别率，总体正确率以及平均耗时

综合对比得出最优的检测模型，当然调优需要有一个漫长的过程。所以需要耐心的调整模型训练的方向，耐心处理数据集！
```

3. 检测ddos攻击时候svm的检测情况
- 提前启动 synflood 然后执行 ryu-manager Switch_app.py detected_attack.py

```
tailf detected.log
2019-03-19 20:35:38 0 0 0.0 0.0 0.0 1 0.0 wrong 0.000166177749634
2019-03-19 20:35:48 0.0953177257525 29.872909699 0.0 0.0 0.0 1 0.0 wrong 0.000426054000854
2019-03-19 20:35:58 0.0429389312977 14.3940839695 59.7 59.8 55.7 1 1.0 correct 0.000186920166016
2019-03-19 20:36:08 0.0348837209302 8.18217054264 103.7 104.8 98.9 1 1.0 correct 0.000231981277466
2019-03-19 20:36:18 0.046198267565 13.2367661213 102.9 103.2 97.4 1 1.0 correct 0.000190019607544
2019-03-19 20:36:28 0.0476653696498 11.7509727626 103.3 103.9 98.0 1 1.0 correct 0.0001540184021
2019-03-19 20:36:38 0.0445304937076 13.0880929332 102.7 102.8 96.8 1 1.0 correct 0.000177145004272
2019-03-19 20:36:48 0.0531914893617 14.4545454545 102.5 103.3 97.9 1 1.0 correct 0.000169992446899

我们可以看到流量刚发起的时候的不稳定导致检测错误，后续流量稳定（即模拟了真实的网络环境后） 检测逐渐出了效果！
```

```
> 统计正确率 可以使用 
python result.py

```

## PCA 降维特征分析
- 为了从二维图上直观看到正常与不同强度流量之间的特征差异，利用PCA降维算法。PCA主要是利用线性回归的基本方式
主要代码位于 model/pca.py目录下。我们主要采取了 synflood 12000（低强度） 与 7000（高强度） 以及正常流量 三种数据源，保存到pca.log之中
然后通过pca降维算法，将五维降至二维，利用matplotlib将散点图画出来，具体散点图如下所示

![](https://raw.githubusercontent.com/light6607/md_pict/master/img/20190404100839.png)

- 其中绿色代表正常流量，蓝色代表低强度流量， 红色代表高强度流量




## svm算法
对于线形可分问题，线形分类向量机是有效的形式，但是分类变得线形不可分
线形核可以将二维不可分问题转化为三维线形可分问题

SVM旨在多维空间中找到一个能将全部样本单元分成两类的最优平面，这一平面应使两类中距离最近的点的间距尽可能大，在间距的边界上的点被称为“支持向量”，分割的超平面位于间距的中间。

> C: 惩罚系数，用来控制损失函数的惩罚系数，类似于LR中的正则化系数。C越大，相当于惩罚松弛变量，希望松弛变量接近0，即对误分类的惩罚增大，趋向于对训练集全分对的情况，这样会出现训练集测试时准确率很高，但泛化能力弱，容易导致过拟合。 C值小，对误分类的惩罚减小，容错能力增强，泛化能力较强，但也可能欠拟合。

> kernel: 算法中采用的和函数类型，核函数是用来将非线性问题转化为线性问题的一种方法。参数选择有RBF, Linear, Poly, Sigmoid，precomputed或者自定义一个核函数, 默认的是"RBF"，即径向基核，也就是高斯核函数；而Linear指的是线性核函数，Poly指的是多项式核，Sigmoid指的是双曲正切函数tanh核；。

## 随机森林

采用id3算法对离散的数据进行分类

它由多棵决策树组成。在数据结构中我们学过森林的概念，它由多棵数组成，这里沿用了此概念。对于分类问题，一个测试样本会送到每一棵决策树中进行预测，然后进行投票，得票最多的类为最终分类结果。对于回归问题随机森林的预测输出是所有决策树输出的均值。例如随机森林有10棵决策树，有8课树的预测结果是第1类，1棵决策树的预测结果为第2类，2棵决策树的预测结果为第3类，则我们将样本判定成第1类。
``` 
max_features: 选择最适属性时划分的特征不能超过此值。
max_depth: (default=None)设置树的最大深度，默认为None，这样建树时，会使每一个叶节点只有一个类别，或是达到min_samples_split。
n_estimators=10：决策树的个数，越多越好，但是性能就会越差，至少100左右（具体数字忘记从哪里来的了）可以达到可接受的性能和误差率
n_jobs=1：并行job个数。这个在ensemble算法中非常重要，尤其是bagging（而非boosting，因为boosting的每次迭代之间有影响，所以很难进行并行化），因为可以并行从而提高性能。1=不并行；n：n个并行；-1：CPU有多少core，就启动多少job。
```

