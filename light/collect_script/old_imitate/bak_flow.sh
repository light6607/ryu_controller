#!/bin/bash

/bin/bash rs1.sh &
/bin/bash rs2.sh &
/bin/bash rs3.sh &

# 避免出现意外终止的情况，python2的编码问题，字符集大于255.所以采用这种方式来做守护进程
# 如何终止？
# ps -ef | grep 'python Rs' | awk  '{print "kill -9 " $3}' | sh
# ps -ef | grep 'python Rs' | awk  '{print "kill -9 " $2}' | sh
# 顺序千万别错！
