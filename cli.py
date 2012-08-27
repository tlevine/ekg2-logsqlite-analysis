#!/usr/bin/env python2
import sys

def get_db_name():
    if len(sys.argv) == 1:
        print('usage: %s <logsqlite database file>' % sys.argv[0])
        exit(1)
    else:
        # Set database name to the first command-line argument
        return sys.argv[1]
