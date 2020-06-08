"""
database.py

Database sanitization/whitelisting functions
"""

from os.path import abspath, dirname, exists, join
import sqlite3


DATABASE_DIRS = [
    '../db',
    '../../omw',  # for wn-multix.db
]


def get_file(dirs, files):
    """Searches `dirs` for first matching file in `files`, return absolute path

    Args:
    dirs - list[str]. Directories to search for the dbfiles. Both relative and
           abosolute paths are accepted.
    files - list[str]. Filenames to search for. The first file found in this
            list will be returned.
    """
    # Current working dir
    cwd = dirname(abspath(__file__))

    for path in dirs:
        # join() relative path with this script's dir,
        # then resolve to absolute path using abspath()
        path = path if exists(path) else abspath(join(cwd, path))
        if not exists(path):
            continue

        for file in files:
            filepath = join(path, file)
            if exists(filepath):
                return filepath
    return None


def connect(dbfile, *fallback, in_dirs=None):
    """Opens a cursor to the given database.

    TODO(Wilson): integrate with ntumc_util.check_corpusdb()?

    Args:
    dbfile - str. The .db file to connect to. The .db extension is optional
    fallback - list[str]. Fallback .db files to try connecting to. These are
               tried in the order passed.
    in_dirs - list[str]. Directories to search for the dbfiles. Paths must be
              absolute if passed in this manner.

    Returns: sqlite3 Cursor object

    Raises: FileNotFoundError
    """
    in_dirs = in_dirs or DATABASE_DIRS

    dbfiles = [file if file.endswith('.db') else file + '.db'
               for file in [dbfile] + fallback]

    dbpath = get_file(in_dirs, dbfiles)

    if not exists(dbpath):
        files = '|'.join(dbfiles)
        dirs = '|'.join(in_dirs)
        raise FileNotFoundError(f'could not find {files} in {dirs}')

    conn = sqlite3.connect(dbpath)
    return conn.cursor()


def sql_escape(text):
    """Duplicates occurrences of ' and " in the given text

    (Wilson) Honestly this doesn't properly protect against injection (e.g. 
    something like \' would become \'' and you end up with an injection still
    but this is just some legacy code that isn't used anywhere.
    """
    quotes = [
        '"',  # double quotes
        "'"   # single quotes
    ]
    return ''.join(
        letter * 2 if (letter in quotes) else letter
        for letter in text
    )


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
    assert placeholders_for('test') == '?'
    assert placeholders_for([1, 2, 3]) == '?,?,?'
    assert placeholders_for(b'spam', paramstyle='format') == '%s'
    assert placeholders_for([1, 2, 3], 'numeric') == ':1,:2,:3'
    assert placeholders_for(dict(A=1, B=2, C=3), 'numeric', 7, '_') == ':7_:8_:9'
    assert placeholders_for([]) == ''   # Empty collection is falsey
    assert placeholders_for('') == '?'  # Empty literal is truthy
    assert placeholders_for([[], '']) == '?,?'  # Probably a bad idea
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
        iterable = (':%d' % i + startfrom for i, _ in enumerate(iterable))

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
