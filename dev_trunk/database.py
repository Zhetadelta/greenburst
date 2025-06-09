import sqlite3 as sql
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from os import path, curdir
import logging
from psrqpy import QueryATNF
from plot_cand import qpsr

def connect(file):
    """
    Connects to a database at given path.

    Returns a sql connect object, or None if some issue prevented access to file.
    """
    conn = None
    try:
        conn = sql.connect(file)
        conn.execute('pragma journal_mode=wal') #write-ahead log, in case of simultaneous access
    except:
        logging.critical(f"Unable to access file {file}")       
    return conn

def schema(file):
    """
    Verifies correct schema in database at given path.

    No return value.
    """

    conn = connect(file)
    schemaString = """ CREATE TABLE IF NOT EXISTS detections (
    row integer PRIMARY KEY,
    Name text NOT NULL,
    RAJ text NOT NULL,
    DecJ text NOT NULL,
    P0 real,
    DM real,
    W50 real,
    W10 real,
    S1400 real,
    Assoc text,
    MJD real,
    UTC text,
    Azimuth real,
    Elevation real,
    Reciever text
    ); """

    if conn is not None:
        c = conn.cursor()
        c.execute(schemaString)
        conn.commit()
        conn.close()

def searchForSourceToAdd(db, ra, dec):
    conn = connect(db)
    if conn is None:
        logging.critical('Connect object failed')
        return
    c = conn.cursor()
    storeString = """ INSERT INTO detections(Name, RAJ, DecJ, P0, DM, W50, W10, S1400, Assoc)
    VALUES (?,?,?,?,?,?,?,?,?)
    """

    query, qTable = qpsr(ra, dec, params = ['NAME','RAJ', 'DECJ', 'P0', 'DM', 'W50', 'W10', 'S1400', 'ASSOC'])
    qTable = query.table #reassign due to a hardcoded slice in original function
    logging.info(f"Sources found: {len(qTable)}")
    if len(qTable) > 0:
        print(qTable)
        psr = qTable[0]
        c.execute(storeString, (psr['NAME'], psr['RAJ'], psr['DECJ'], psr['P0'], psr['DM'],psr['W50'],psr['W10'],psr['S1400'],psr['ASSOC']))
        conn.commit()
    conn.close()
        

    
    

    

if __name__ == '__main__':
    parser=ArgumentParser(description='Access database', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Be verbose')
    #TODO: Add arguments for different queries and possibly additions
    #Example argument add: parser.add_argument('-f', '--files', nargs='+', help='Filterbank file')
    parser.add_argument('--db', dest='dbfile', help='Database file')
    parser.add_argument('-s', '--search', dest='searchString', help='Test search ra/dec')
    parser.set_defaults(dbfile=path.join(curdir,'test.db'))
    parser.set_defaults(searchString = None)
    parser.set_defaults(verbose=False)
    values = parser.parse_args()

    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if values.verbose:
        logging.basicConfig(level=logging.DEBUG, format=format)
    else:
        logging.basicConfig(level=logging.INFO, format=format)

    logging.debug(f"Accessing database at {values.dbfile}")
    schema(values.dbfile)
    if values.searchString is not None:
        ra, dec = values.searchString.split(" ")
        searchForSourceToAdd(values.dbfile, float(ra), float(dec))