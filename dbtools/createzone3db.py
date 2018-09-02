#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import sys
import os


db_filename = 'zone3db.db'

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

    else:
        print 'Database exists, assume schema does, too.'

