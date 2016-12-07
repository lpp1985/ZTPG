#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2016/6/14
"""
from multiprocessing import Pool
import sys,os
def run(command):
    os.system(command)
    
RAW = open(sys.argv[1])
data = RAW.readlines()
worker_pool = Pool( processes=40 )
worker_pool.map( run,  data    )
