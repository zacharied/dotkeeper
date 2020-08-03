#!/usr/bin/env python3

from pathlib import Path
import shutil
import os
import tempfile

import unittest

import dotkeeper

class TestSaveMethods(unittest.TestCase):
    def setUp(self):
        if os.path.exists(f'{tempdir}/dotkeep'):
            shutil.rmtree(f'{tempdir}/dotkeep')
        for f in os.listdir(tempdir):
            f = f'{tempdir}/{f}'
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)

        os.mkdir(f'{tempdir}/dotkeep') 
    
        # Link to a file.
        open(f'{tempdir}/dotkeep/target', 'w+').close()
        os.symlink(f'{tempdir}/dotkeep/target', f'{tempdir}/target-link')

        # Link to a directory.
        os.mkdir(f'{tempdir}/dotkeep/dummy')
        os.symlink(f'{tempdir}/dotkeep/dummy', f'{tempdir}/dummy-link')

    def test_find_links(self):
        # Test that links to the dotkeep are found, and other links are ignored.
        links = dotkeeper.find_links_to_dotkeep(f'{tempdir}/dotkeep')
        self.assertIn(('target', f'{tempdir}/target-link'), links)
        self.assertIn(('dummy', f'{tempdir}/dummy-link'), links)
        self.assertEqual(len(links), 2)

    def test_save_links(self):
        dotkeeper.do_save_links(f'{tempdir}/dotkeep', silent=True)
        with open(f'{tempdir}/links', 'r') as links_file:
            # The lines could be in any order, so we can't just match the whole file.
            # Instead, we make sure there are the lines representing our links, and then make sure that there are no
            #  other lines in the file.
            contents = '\n' + links_file.read().strip() + '\n'
            self.assertRegex(contents, f'\ntarget\t{tempdir}/target-link\n')
            self.assertRegex(contents, f'\ndummy\t{tempdir}/dummy-link\n')
            self.assertEqual(contents.count('\n'), 3)

class TestRestoreMethods(unittest.TestCase):
    def setUp(self):
        if os.path.exists(f'{tempdir}/dotkeep'):
            shutil.rmtree(f'{tempdir}/dotkeep')
        for f in os.listdir(tempdir):
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)

        os.mkdir(f'{tempdir}/dotkeep') 

    def test_restore_links(self):
        # Example links file contents.
        contents = f'''\
target\t{tempdir}/target-link
subdir/target\t{tempdir}/subdir/subdir-target-link'''
        
        # Set up for subdirectory link.
        os.mkdir(f'{tempdir}/subdir')
        os.mkdir(f'{tempdir}/dotkeep/subdir')
        open(f'{tempdir}/dotkeep/subdir/target', 'w+').close()

        with open(f'{tempdir}/links', 'w+') as links_file:
            links_file.write(contents)
        dotkeeper.do_restore_links(f'{tempdir}/dotkeep', silent=True)
        self.assertEqual(os.readlink(f'{tempdir}/target-link'), f'{tempdir}/dotkeep/target')
        self.assertEqual(os.readlink(f'{tempdir}/subdir/subdir-target-link'), f'{tempdir}/dotkeep/subdir/target')

if __name__ == '__main__':
    temp = tempfile.TemporaryDirectory()
    tempdir = temp.name
    dotkeeper.load_args(['--search-root', tempdir, '--links-file', f'{tempdir}/links'])
    unittest.main()
    temp.close()
