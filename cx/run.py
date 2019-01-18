#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from ryu.cmd import manager


def main(argv):
    sys.argv.append('l3_learning_3_2.py')
    if sys.argv[1] == 'train': #如果参数为train，则运行特征提取模块
        sys.argv.remove(sys.argv[1])
        sys.argv.append('feature_extractor.py')
    elif sys.argv[1] == 'check':#如果参数为check，则运行检测模块
        sys.argv.remove(sys.argv[1])
        sys.argv.append('monitor.py')
    else :
        print('please check argv')
        exit()
    sys.argv.append('--observe-links')
    
    manager.main()

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        main(sys.argv[1])
    else:
        print('please check argv')
        exit()