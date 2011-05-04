from cumulonimbus.cfuse import CFuse
from unittest import TestCase
from mock import Mock
from sys import argv
import os

class TestCFuse(TestCase):
    testdir = 'dir'

    def setUp(self):
        log = open('LOG', 'w')
        log.truncate()
        log.close()
        self.mock_fs = self.prepare_mock_fs()
        (r,w) = os.pipe()
        if os.fork(): # one process will hang in fuse.main()
            os.close(r)
            self.fuse = CFuse( self.mock_fs )
            self.fuse.parse( self.fake_cmd_args() )
            os.close(w)
            self.fuse.main()
            sys.exit()
        else:
            os.close(w)
            a = os.read(r, 1) # wait till closed
            os.close(r)

    def tearDown(self):
        os.system('fusermount -u ' + TestCFuse.testdir)

    def fake_cmd_args(self):
        return [TestCFuse.testdir]
        
    def prepare_mock_fs(self):
        return Mock()

    def cmd_util_count_lines(self, expr, expected):
        expr2 = expr.replace("]","\]").replace("[","\[")
        fd = os.popen("cat LOG | grep '" + expr2 + "' | wc -l")
        actual = int( fd.read() )
        fd.close()
        self.assertEqual( actual, expected,
            "Unexpected count of %(expr)s. Actual: %(act)d, expected: %(exp)d."
            % { 'expr':expr, 'act':actual, 'exp':expected } )

    def test_mounted(self):
        self.cmd_util_count_lines("[mount]", 1)
        self.cmd_util_count_lines("[unmount]", 0)
        

