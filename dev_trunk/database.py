import sqlite3 as sql
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from os import path, curdir
import logging
from psrqpy import QueryATNF
from plot_cand import qpsr

def rowSort(psr):
    """
    Helper function which sorts astropy table row 'psr' according to the database schema order and places it into an ordered tuple.
    """
    return (psr['NAME'], psr['RAJ'], psr['DECJ'], psr['P0'], psr['DM'],psr['W50'],psr['W10'],psr['S1400'],psr['ASSOC'])

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
        c.execute(storeString, rowSort(psr))
        conn.commit()
    conn.close()
        
def filteredSearch(db, ra, dec, epsilon=0.05, width=None, DM=None):
    """
    Searches ATNF database for pulsars within 1 degree of coordinates with pulse width and/or DM conditions and appends to local database.

    Positional arguments:
    db (string) -- filename of database
    ra (float) -- right ascention in degrees with decimals
    dec (float) -- declination in degrees with decimals

    Keyword arguments:
    epsilon (float) -- factor of value to use as conditional window (default 0.05)
    width (float) -- width of pulse in milliseconds (default None)
    DM (float) -- Dispersion measure in pc/cm3 (default None)

    Returns True if at least one source is found, and False otherwise.
    """

    conn = connect(db)
    if conn is None:
        logging.critical('Connect object failed')
        return
    c = conn.cursor()
    storeString = """ INSERT INTO detections(Name, RAJ, DecJ, P0, DM, W50, W10, S1400, Assoc)
    VALUES (?,?,?,?,?,?,?,?,?)
    """

    #start by constructing search filter
    if width is not None:
        filterString = f"(W50 > {width*(1-epsilon)} && W50 < {width*(1+epsilon)})"
        if DM is not None: #if both, need &&
            filterString += f" && (DM > {DM*(1-epsilon)} && DM < {DM*(1+epsilon)})"
    elif DM is not None:
        filterString += f"(DM > {DM*(1-epsilon)} && DM < {DM*(1+epsilon)})"
    else:
        logging.warn("Filtered search run with no filters.")
        filterString = None

    query, qTable = qpsr(ra, dec, params = ['NAME','RAJ', 'DECJ', 'P0', 'DM', 'W50', 'W10', 'S1400', 'ASSOC'], condition=filterString)
    qTable = query.table #reassign due to a hardcoded slice in original function
    logging.info(f"Sources found: {len(qTable)}")
    if len(qTable) > 0:
        print(qTable)
        psr = qTable[0]
        c.execute(storeString, rowSort(psr))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False
    
    
    

    

if __name__ == '__main__':
    parser=ArgumentParser(description='Access database', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Be verbose')
    #TODO: Add arguments for different queries and possibly additions
    #Example argument add: parser.add_argument('-f', '--files', nargs='+', help='Filterbank file')
    parser.add_argument('--db', dest='dbfile', help='Database file')
    parser.add_argument('-s', '--search', dest='searchString', help='Test search ra/dec/width')
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
        ra, dec, w, dm = values.searchString.split(" ")
        filteredSearch(values.dbfile, float(ra), float(dec), epsilon=0.001, width=float(w), DM=float(dm))