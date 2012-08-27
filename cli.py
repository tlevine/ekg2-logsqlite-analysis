#!/usr/bin/env python2
import sys

if len(sys.argv) == 0:
    print('usage: foo <logsqlite database file>')
else:
    # Set database name to the first command-line argument
    DBNAME=sys.argv[1]
