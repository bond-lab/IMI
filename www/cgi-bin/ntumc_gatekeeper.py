"""
ntumc_gatekeeper.py

Functions for whitelisting .db file access and SQL sanitization.
This module mainly exports:

function placeholders_for(object):
  Makes parameter binding placeholders. Acts like shorthand for 
  ','.join('?' for x in myList), with some differences.
        placeholders_for([1, 2, 3]) -> '?,?,?'
        placeholders_for('string') -> '?'

function connect(dbfile):
  Searches for the specified .db file and returns a sqlite3.Connection to it. 
  The default search dirs are cgi-bin/../db and cgi-bin/../../omw.
  The function only allows traversal to child dirs within the search dirs.

function cursor(dbfile):
  Like connect() but returns a sqlite3.Cursor object instead.

function sql_escape(string):
  Duplicates instances of ' and " in the input string. This function is left over
  from ntumc_util.py which I cleaned up a bit, it's not actually used anywhere 
  in the codebase.
"""

from os.path import abspath, dirname, exists, join, split
import sqlite3


DATABASE_DIRS = [
    '../db',
    '../../omw',  # for wn-multix.db
]


# Implicitly exported through the `import *` statement
__all__ = [
    'connect',
    'concurs',
    'placeholders_for',
]


def _supersplit(head):
    """Like os.path.split() but stronger (completely fragments the path)

    'foo/../bar.db' -> ['foo', '..', 'bar.db']
    """
    chunks = []
    while 1:
        head, tail = split(head)
        if tail:
            chunks.append(tail)
        else:
            chunks.append(head)
            break
    return chunks[::-1]


def find_file(dirs, files):
    """Searches `dirs` for first matching file in `files`, return absolute path

    Args:
    dirs - list[str]. Directories to search for the dbfiles. Both relative and
           absolute paths are accepted.
    files - list[str]. Filenames to search for. The first file found in this
            list will be returned.
    """
    # Current working dir
    cwd = dirname(abspath(__file__))

    for path in dirs:
        # join() relative path with this script's dir,
        # then resolve to absolute path using abspath()
        path =  abspath(join(cwd, path))
        if not exists(path):
            continue

        for file in files:
            filepath = join(path, file)
            if exists(filepath):
                return filepath
    return None


def normalize_filepath(file):
    """Removes traversal to parent dir and ensures file ends with .db

    spam/../eggs.txt -> spam/eggs.txt.db
    """
    file += ('.db' if not file.endswith('.db') else '')
    file = join(*[x for x in _supersplit(file) if x != '..'])
    return file


def connect(dbfile, *fallback, in_dirs=None):
    """Opens a connection to the given database.

    TODO(Wilson): integrate with ntumc_util.check_corpusdb()?

    Args:
    dbfile - str. The .db file to connect to. The .db extension is optional
    fallback - list[str]. Fallback .db files to try connecting to. These are
               tried in the order passed.
    in_dirs - list[str]. Directories to search for the dbfiles. Paths must be
              absolute if passed in this manner.

    Returns: sqlite3 Connection object

    Raises: FileNotFoundError if the dbfile and fallbacks could not be found
            within in_dirs, or the default locations defined in DATABASE_DIRS.
    """
    dbfiles = [normalize_filepath(f) for f in [dbfile] + list(fallback)]
    in_dirs = in_dirs or DATABASE_DIRS

    dbpath = find_file(in_dirs, dbfiles)

    if not (dbpath and exists(dbpath)):
        files = '|'.join(dbfiles)
        dirs = '|'.join(in_dirs)
        raise FileNotFoundError(f'could not find {files} in {dirs}')

    return sqlite3.connect(dbpath)


def concurs(*args, **kwargs):
    """Shortcut to return both connection and cursor from connect()
    usage:
      conn, c = concurs('eng.db')
    """
    conn = connect(*args, **kwargs)
    curs = conn.cursor()
    return conn, curs


def placeholders_for(iterable, paramstyle='qmark', startfrom=1, delim=','):
    """Makes query placeholders for the input iterable: [1, 2, 3] => '?,?,?'

    Returns a string that can safely be formatted directly into your query.
    Generally equal to delim.join('?' for x in iterable) but see below for
    exceptions and edge cases.

    Only ordered paramstyles are supported: qmark/numeric/format
    List of paramstyles: https://www.python.org/dev/peps/pep-0249/#paramstyle

        WARNING - slightly unintuitive behaviour
        If the `iterable` argument is str, bytes, or does not implement the
        iterator protocol, the object will be coerced to a list containing that
        one object. For example:
            if iterable == '', returns '?'
            if iterable == [], returns ''

    Args:
    iterable - any object. If a str, bytes, or non-iterable object is given,
               this value is coerced into a list containing that one object.

    paramstyle - str. Only (qmark|numeric|format) is supported.

    delim - str. The token delimiting each placeholder.

    startfrom - int. Sets the initial number to count from when using the
                'numeral' paramstyle.

    Returns: str

    Examples:
    placeholders_for('test') == '?'
    placeholders_for([1, 2, 3]) == '?,?,?'
    placeholders_for(b'spam', paramstyle='format') == '%s'
    placeholders_for([1, 2, 3], 'numeric') == ':1,:2,:3'
    placeholders_for(dict(A=1, B=2, C=3), 'numeric', 7, '_') == ':7_:8_:9'
    placeholders_for([]) == ''           # Empty collection is falsey
    placeholders_for('') == '?'          # Empty literal is truthy
    placeholders_for([[], '']) == '?,?'  # Probably a bad idea
    """

    # Guard against non-iterator values passed to the `iterable` param.
    try:
        # Coerce iterable literals into a list with just 1 element
        if isinstance(iterable, (str, bytes)):
            iterable = [iterable]

        # Try to trigger a TypeError
        else:
            iterable = iter(iterable)

    # If non-iterable type, coerce to list with just 1 element
    except TypeError as err:
        if 'object is not iterable' in str(err):
            iterable = [iterable]
        else:
            raise

    # paramstyle defaults to qmark
    paramstyle = paramstyle or 'qmark'

    # Refuse the temptation to guess the order of unordered paramstyles
    if paramstyle in ('named', 'pyformat'):
        err = ('cannot guess the order of placeholders for unordered '
               'paramstyle "{}"')
        raise NotImplementedError(err.format(paramstyle))

    if paramstyle == 'numeric':
        iterable = (':{}'.format(i + startfrom) for i, _ in enumerate(iterable))

    elif paramstyle == 'format':
        iterable = ('%s' for x in iterable)

    # Unsupported paramstyles, see NotImplementedError above.
    # elif paramstyle == 'named':
    #     iterable = (':{}'.format(key) for key in iterable)

    # elif paramstyle == 'pyformat':
    #     iterable = ('%({})s'.format(key) for key in iterable)

    # Handle the default qmark paramstyle
    else:
        iterable = ('?' for x in iterable)

    return delim.join(iterable)
