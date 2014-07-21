#!/usr/bin/python
#coding:utf-8
# Author:   --<( >
# Purpose: 
# Created: 2013/8/8

from ConfigParser import ConfigParser
import os
config = ConfigParser()
root_path = os.path.abspath(os.path.split(__file__)[0] ) +'/'
config.read( root_path+'config.ini'  )
amos_path = config.get("PATH","AMOSBIN")
cele_path = config.get( "PATH","CELEDIR"    )
nucmer = config.get( "PATH","NUCMER" )
delta_filter = config.get( "PATH","DELTAFILTER" )
showcoords = config.get(  "PATH","SHOWCOORDS"   )
blat = config.get(  "PATH","BLAT"   )
celera_assembler = config.get(  "PATH","CELERAASSEMBLER"   )