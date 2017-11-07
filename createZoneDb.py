#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import sys
import os


db_filename = 'zone2db.db'

schema_filename = 'zoneDBSchema.sql'

db_is_new = not os.path.exists(db_filename)

with sqlite3.connect(db_filename) as conn:
    if db_is_new:
        print 'Creating schema'
        with open(schema_filename, 'rt') as f:
            schema = f.read()
        conn.executescript(schema)

        print 'Inserting initial data'
        conn.execute("INSERT INTO config (tempSPLOn, tempSPLOff, systemUpTime, processUptime, systemMessage,controllerMessage,miscMessage, lightState) VALUES (22.5, 19.5, '20:59','22:33', 'system message','controller message', 'misc message', 1)")
        #conn.execute("INSERT INTO thdata ( sample_dt, temperature, humidity, heaterstate, ventstate, fanstate ) VALUES( '2017-11-06 23:05:10.575123', 19.5, 67.8, 1, 1, 1)")

            
        #conn.execute("""
        #insert into project (name, description, deadline)
        #values ('pymotw', 'Python Module of the Week', '2010-11-01')
        #""")
        #conn.execute("""
        #insert into task (details, status, deadline, project)
        #values ('write about select', 'done', '2010-10-03', 'pymotw')
        #""")
        #conn.execute("""
        #insert into task (details, status, deadline, project)
        #values ('write about random', 'waiting', '2010-10-10', 'pymotw')
        #""")
        #conn.execute("""
        #insert into task (details, status, deadline, project)
        #values ('write about sqlite3', 'active', '2010-10-17', 'pymotw')
        #""")
    else:
        print 'Database exists, assume schema does, too.'

