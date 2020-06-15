from os.path import abspath, dirname, exists, join
from sqlite3 import Connection, Cursor
import unittest

from databases import *

class PlaceholdersTestCase(unittest.TestCase):
    def test_iterable_literals(self):
        self.assertTrue(placeholders_for('test') == '?')
        self.assertTrue(placeholders_for(b'test') == '?')

    def test_iterables(self):
        class CustomIterator:
            def __init__(self, li):
                self.li = li
            def __len__(self):
                return len(self.li)
            def __getitem__(self, key):
                return self.li[key]

        li = [1, 2, 3]
        testme = [
            li,
            tuple(li),
            {x: x for x in li},
            set(li),
            (x for x in li),
            CustomIterator(li),
        ]

        for iterable in testme:
            self.assertTrue(placeholders_for(iterable) == '?,?,?')

    def test_delim(self):
        self.assertTrue(placeholders_for([1, 2, 3], delim='_') == '?_?_?')

    def test_pstyle(self):
        li = [1, 2, 3]
        self.assertTrue(placeholders_for(li, 'numeric') == ':1,:2,:3')
        self.assertTrue(placeholders_for(li, paramstyle='format') == '%s,%s,%s')
        self.assertTrue(placeholders_for(li, paramstyle='qmark') == '?,?,?')

    def test_pstyle_startfrom(self):
        ph = placeholders_for([1, 2, 3],
                              paramstyle='numeric',
                              startfrom=7,
                              delim='_')
        self.assertTrue(ph == ':7_:8_:9')

        # startfrom given, but irrelevant to the selected paramstyle
        ph = placeholders_for([1, 2, 3],
                              paramstyle='qmark',
                              startfrom=7,
                              delim='_')
        self.assertTrue(ph == '?_?_?')

    def test_empty_collection(self):
        # Empty collection is falsey
        arg = []
        res = ''
        self.assertTrue(placeholders_for(arg) == res)

    def test_empty_literal(self):
        # Empty literal is truthy
        arg = ''
        res = '?'
        self.assertTrue(placeholders_for(arg) == res)

    def test_nested_collection(self):
        # Nesting collections would probably be a bad idea on the user's part
        # While placeholders_for([]) would have returned '', in this case
        # the nested [] resolves into a placeholder (maybe unexpectedly)
        arg = ['', []]
        res = '?,?'
        self.assertTrue(placeholders_for(arg) == res)


class SqlEscapeTestCase(unittest.TestCase):
    def test_sql_escape(self):
        arg = """ s's'' """
        res = """ s''s'''' """
        self.assertTrue(sql_escape(arg) == res)


class DbfileTestCase(unittest.TestCase):
    def test_database_dirs(self):
        for direc in DATABASE_DIRS:
            cwd = dirname(abspath(__file__))
            targetdir = join(cwd, direc)
            self.assertTrue(exists(direc),
                            f'could not find db dir expected at: {targetdir}')

    def test_find_file(self):
        me = __file__
        me_path = abspath(me)
        me_dir = dirname(me_path)

        # Find this file
        self.assertTrue(find_file(['.'], [me]).endswith(me))
        self.assertTrue(find_file([me_dir], [me]) == me_path)
        # Find nonexistent file
        self.assertTrue(find_file(['.'], ['nonexistent.file']) == None)
        # Find file in relative dir
        self.assertTrue(find_file(DATABASE_DIRS, ['eng.db']) != None)


    def test_connect(self):
        # Basic functionality
        res = isinstance(connect('eng.db'), Connection)
        self.assertTrue(res)

        res = isinstance(cursor('eng.db'), Cursor)
        self.assertTrue(res)

        # Testing fallback
        res = isinstance(connect('xyz.db', 'eng.db'), Connection)
        self.assertTrue(res)

        # Should fail on nonexistent files
        with self.assertRaises(FileNotFoundError):
            connect('nonexistent.db')

        # Testing in_dirs by searching existing dbfile in nonexistent dir
        with self.assertRaises(FileNotFoundError):
            connect('eng.db', in_dirs=['nonexistent.dir'])


    def test_traversal_attack(self):
        # normalize() should strip out traversal to ..
        from os.path import join
        pre_norm = join('foo', '..', 'bar.txt')
        post_norm = join('foo', 'bar.txt.db')
        self.assertEqual(normalize_filepath('foo/../bar.txt'),
                         post_norm)

        # connect() shouldn't let us traverse to parent dirs
        with self.assertRaises(FileNotFoundError):
            connect('../db/eng.db', in_dirs=['.'])


if __name__ == '__main__':
    unittest.main()
