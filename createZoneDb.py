#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys

import os
import sqlite3

db_filename = 'todo.db'

db_is_new = not os.path.exists(db_filename)

conn = sqlite3.connect(db_filename)

if db_is_new:
    print 'Need to create schema'
else:
    print 'Database exists, assume schema does, too.'

conn.close()

con = lite.connect('zone2db.db')

with con:
    
    cur = con.cursor()    
    #cur.execute("CREATE TABLE config(id INT, tempSPLOn REAL, tempSPLOff REAL, systemUpTime TEXT, processUptime TEXT, systemMessage TEXT, lightState INT)")
    cur.execute("INSERT INTO config VALUES(1, 22.5, 19.5, '20:59','placeholder', 'placeholder', 1)")


    #cur.execute("CREATE TABLE thdata(id INT, sample_dt TEXT, temperature REAL, humidity REAL, heaterstate INT, ventstate INT, fanstate INT)")
    cur.execute("INSERT INTO thdata VALUES(1, '20:59', 19.5, 67.8, 1, 1, 1)")
