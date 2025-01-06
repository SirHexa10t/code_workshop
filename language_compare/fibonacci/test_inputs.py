#!/usr/bin/python3

import os

this_files_dir = os.path.dirname(__file__)
tests = (
    f"python3 {this_files_dir}/fibo_python.py",
    f"{this_files_dir}/fibo_c.bin", 
)


# test by running:  python3 -m unittest test_inputs.py
import unittest
class Testings(unittest.TestCase):
    
    def test_args_handling(self):  # python3 -m unittest test_inputs.Testings.test_args_handling
        import subprocess
        import os
        
        for test in tests:
            # this_file = os.path.abspath(__file__)
            def runcmd(bash_cmd):
                return subprocess.run(bash_cmd, shell=True, capture_output=True, text=True, executable='/bin/bash')
                
            def assert_args_cause_stderr(*arguments):
                self.assertIsNotNone(runcmd(f"{test} {' '.join(arguments)}").stderr)
            
            def assert_args_legal(*arguments):
                self.assertEqual('', runcmd(f"{test} {' '.join(arguments)}").stderr)
            
            # verify that the following errors occur
            assert_args_cause_stderr()  # no number (and no extra args at all)
            assert_args_cause_stderr('0')  # index 0
            assert_args_cause_stderr('-11')  # negative index
            assert_args_cause_stderr('1.2')  # fractional index
            assert_args_cause_stderr('1', '--algo', 'adv', '2')  # two numbers
            assert_args_cause_stderr('hello')  # unsupported arg
            assert_args_cause_stderr('--algo', 'hello')  # unsupported algorithm arg
            assert_args_cause_stderr('--algo', '2')  # unsupported algorithm arg
            
            assert_args_legal('4')          # valid usage
            assert_args_legal('4', '--algo', 'adv')   # valid usage
            assert_args_legal('--algo', 'adv', '4')   # valid usage

