#!/usr/bin/env python2
from dumptruck import DumpTruck

def get_uid_from_uid_or_nick(db, uid_or_nick):
    'Given a uid or a nick, return a uid or an error.'
    dt = DumpTruck(db)

    # Is it a uid?
    sql = 'SELECT count(*) FROM log_status WHERE uid = ?'
    count = dt.execute(sql, [uid_or_nick])[0]['count(*)']
    if count > 0:
        # It is a uid
        uid = uid_or_nick
    else:
        # It's a nick. Make sure it refers to a unique uid.
        sql = 'SELECT count(DISTINCT uid) FROM log_status WHERE nick = ?'
        count = dt.execute(sql, [uid_or_nick])[0]['count(DISTINCT uid)']

        if count == 1:
            # It is distinct
            sql = 'SELECT uid FROM log_status WHERE nick = ? LIMIT 1'
            uid = dt.execute(sql, [uid_or_nick])[0]['uid']

        else:
            # Multiple people have this name.
            raise ValueError('The name you specified does not refer uniquely to one user.')
    return uid

def avail_within(db, start=0, end=2**32):
    '''
    Given a database filename, uid and a time range (POSIX times),
    return how long everyone was online, in seconds.
    '''

    # Database connection
    dt = DumpTruck(db)
    updates = dt.execute('''
        SELECT uid, ts, status
        FROM log_status
        WHERE ts > ? AND ts < ?
        ORDER BY uid, ts
        ;''', [start, end])

    # This loop depends on the order by clause above
    total_time = {}
    for u in updates:

        if u['status'] == 'notavail' and (u['uid'] not in total_time):
            # First time we see person, but it's 'notavail', so skip it.
            continue

        elif u['status'] == 'avail' and (u['uid'] not in total_time):
            # First time we see person becoming available
            total_time[u['uid']] = 0

        elif u['status'] == 'avail':
            # The person went avail. We don't need to do anything;
            # prev_time is recorded below the if statements
            continue

        elif u['status'] == 'notavail':
            # The person went notavail, so record the time when the user was available.
            total_time[u['uid']] += u['ts'] - prev_time

        else:
            raise ValueError('The update\'s status "%s" is neither "avail" nor "notavail."' % u['status'])

        # Record the current timestamp as prev_time
        prev_time = u['ts']

    return total_time


if __name__ == '__main__':
    import datetime
    from unidecode import unidecode
    import cli

    DBFILE = cli.get_db_name()
    avail = avail_within(DBFILE)
    dt = DumpTruck(DBFILE)

    # timedeltas
    for uid, seconds in avail.items():
        avail[uid] = datetime.timedelta(seconds=seconds)

    # Pretty printing
    print('Person\tTime online (HH:MM:SS)')
    for uid, delta in avail.items():
        nick = dt.execute('SELECT nick FROM log_status WHERE uid = ?', [uid])[0]['nick']
        print(unidecode(nick) + u'\t' + unicode(delta))
