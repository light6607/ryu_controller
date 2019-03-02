#!/bin/bash

python Rs1.py >> ./bgflow_log/Rs1.log  2>&1 &
python Rs2.py >> ./bgflow_log/Rs2.log  2>&1 &
python Rs3.py >> ./bgflow_log/Rs3.log  2>&1 &
