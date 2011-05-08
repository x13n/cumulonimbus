from cumulonimbus.cfuse import CFuse
from unittest import TestCase
from mock import Mock
from sys import argv
import os

class TestCFuse(TestCase):
    testdir = 'dir'

    def setUp(self):
        self.clearLog()
        (r,w) = os.pipe()
        if not os.fork(): # one process will hang in fuse.main()
            os.close(r)
            self.fuse = self.prepare_cfuse()
            os.close(w)
            self.fuse.main()
            sys.exit(0)
        else:
            os.close(w)
            a = os.read(r, 1) # wait till closed
            from time import sleep
            sleep( 1 ) # sux a bit. This should wait till mount is done.
            os.close(r)

    def tearDown(self):
        os.system('fusermount -u ' + TestCFuse.testdir)

    def fake_cmd_args(self):
        return [TestCFuse.testdir]
        
    def test_mounted(self):
        self.cmd_util_count_lines_assert("[mount][init]", 1)
        self.cmd_util_count_lines_assert("[mount][done]", 1)
        self.cmd_util_count_lines_assert("[unmount][init]", 0)
        self.cmd_util_count_lines_assert("[unmount][done]", 0)

    #def test_mkdir(self): TODO: mock getattr? or something. So mkdir can actually create a dir :<
    #    self.cmd_util_count_lines_assert("[mkdir]", 0)
    #    os.system('mkdir %s/dir 2> /dev/null' % TestCFuse.testdir)
    #    self.cmd_util_count_lines_assert("[mkdir][done]", 1)

    def test_getattr_root(self):
        os.system('stat %s > /dev/null' % TestCFuse.testdir)
        inits = self.cmd_util_count_lines("[getattr][init]")
        dones = self.cmd_util_count_lines("[getattr][done]")
        self.assertEqual( inits, dones )

    def cmd_util_count_lines(self, expr):
        expr2 = expr.replace("]","\]").replace("[","\[")
        fd = os.popen("cat LOG | grep '" + expr2 + "' | wc -l")
        actual = int( fd.read() )
        fd.close()
        return actual

    def cmd_util_count_lines_assert(self, expr, expected):
        actual = self.cmd_util_count_lines( expr )
        self.assertEqual( actual, expected,
            "Unexpected count of %(expr)s. Actual: %(act)d, expected: %(exp)d."
            % { 'expr':expr, 'act':actual, 'exp':expected } )

    def prepare_cfuse(self):
        fuse = CFuse( dash_s_do='setsingle' )
        fuse.parse( self.fake_cmd_args(), errex=1 )
        fuse.multithreaded = 0
        fuse.fs = self.prepare_fs()
        return fuse

    def prepare_fs(self):
        fs = Mock()
        fs.access = Mock()
        fs.access.return_value = 0
        return fs

    def clearLog(self):
        log = open('LOG', 'w')
        log.truncate()
        log.close()

