#!/usr/bin/env python2
from dumptruck import DumpTruck

def availability_within(db, uid, start=0, end=2**64):
    '''
    Given a database filename, uid and a time range (POSIX times),
    return how long the person was online.
    '''
    dt = DumpTruck(db)
    updates = dt.execute('''
SELECT uid, ts, status
FROM log_status
ORDER BY uid, ts
WHERE ts > ? AND ts < ?;
''', [start, end])

    # This loop depends on the order by clause above
    total_time = {}
    for u in updates:

        if u['status'] == 'notavail' and (u['uid'] not in total_time):
            # First time we see person, but it's 'notavail', so skip it.
            continue

        elif u['status'] == 'avail' and (u['uid'] not in total_time):
            # First time we see person becoming available
            total_time[u[uid]] = 0

        elif update['status'] == 'avail':
            # The person went avail. We don't need to do anything;
            # prev_time is recorded below the if statements
            continue

        elif update['status'] == 'notavail':
            # The person went notavail, so record the time when the user was available.
            total_time[u[uid]] += u['ts'] - prev_time

        else:
            raise ValueError('The update\'s status "%s" is neither "avail" nor "notavail."' % u['status'])

        # Record the current timestamp as prev_time
        prev_time = update['ts']

    return total_time
