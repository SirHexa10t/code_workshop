#!/usr/bin/python3

import os

this_files_dir = os.path.dirname(__file__)
tests = (
    f"python3 {this_files_dir}/fibo_python.py",
    f"{this_files_dir}/fibo_c.bin", 
)

if __name__ == "__main__":
    print(f"This isn't how you run python test files. Run this:\npython3 -m unittest {os.path.abspath(__file__)}")
    exit(1)

# test by running:  python3 -m unittest test_inputs.py
import unittest
class Testings(unittest.TestCase):
    
    @staticmethod
    def print_test_subject(test, topic):
        print(f"on '{test}', running '{topic}'")
        
    
    @staticmethod
    def runcmd(bash_cmd):
        import subprocess
        return subprocess.run(bash_cmd, shell=True, capture_output=True, text=True, executable='/bin/bash')

    def test_args_handling(self):  # python3 -m unittest test_inputs.Testings.test_args_handling
        import os
            
        for test in tests:
            def cmd_stderr(arguments):
                return self.runcmd(f"{test} {arguments}").stderr
                
            def assert_args_cause_stderr(arguments):
                self.assertIsNotNone(cmd_stderr(arguments))
            
            def assert_args_legal(arguments):
                self.assertEqual('', cmd_stderr(arguments))
                
            # verify that the following errors occur
            self.print_test_subject(test, 'stderr')
            assert_args_cause_stderr('')  # no number (and no extra args at all)
            assert_args_cause_stderr('0')  # index 0
            assert_args_cause_stderr('**')  # weird input
            assert_args_cause_stderr('-11')  # negative index
            assert_args_cause_stderr('1.2')  # fractional index
            assert_args_cause_stderr('1 --algo adv 2')  # two numbers
            assert_args_cause_stderr('hello')  # unsupported arg
            assert_args_cause_stderr('--algo hello')  # unsupported algorithm arg
            assert_args_cause_stderr('--algo 2')  # unsupported algorithm arg
            assert_args_cause_stderr('2 --algo')  # unsupported algorithm arg
            
            self.print_test_subject(test, 'no-stderr')
            assert_args_legal('4')          # valid usage
            assert_args_legal('4 --algo adv')   # valid usage
            assert_args_legal('--algo adv 4')   # valid usage

    
    def test_same_results(self):
        for test in tests:
            def cmd_stdout(arguments):
                return self.runcmd(f"{test} {arguments}").stdout

            self.print_test_subject(test, 'direct result')
            self.assertEqual('8\n', cmd_stdout(f"6 --algo straight"))
            self.assertEqual('8\n', cmd_stdout(f"6 --algo adv"))
            self.assertEqual('8\n', cmd_stdout(f"6 --algo naive"))
            
            self.print_test_subject(test, 'no prints')
            for i in range(1,20):  # test no printing
                self.assertTrue('' == cmd_stdout(f"{i} -n --algo straight") == cmd_stdout(f"{i} --algo adv -n") == cmd_stdout(f"-n {i} --algo naive"))
            
            self.print_test_subject(test, 'same results all')
            for i in range(1,20):
                self.assertTrue(cmd_stdout(f"{i} --algo straight") == cmd_stdout(f"{i} --algo adv") == cmd_stdout(f"{i} --algo naive"))
    
            self.print_test_subject(test, 'same results big numbers')
            for i in range(1,2000, 100):  # checking validity of adv algorithm
                self.assertEqual(cmd_stdout(f"{i} --algo straight") , cmd_stdout(f"{i} --algo adv"))
    
    def test_handling_of_huge_results(self):
        # check with large numbers. 
        large_n = 10000  # This one's still in python's standard printed digit count range
        for test in tests:
            def cmd_stdout(arguments):
                return self.runcmd(f"{test} {arguments}").stdout
            
            self.print_test_subject(test, 'dealing with very large numbers')
            for i in range(3):  # mutliply the scale by 10 each run
                # print(f"checking big index number: {large_n}. Current digit limit: {sys.get_int_max_str_digits()}")
                f'{cmd_stdout(f"{i} --algo adv")}'  # try to trigger an exception of integer string conversion (exceeding digits limit)
                f'{cmd_stdout(f"{i} --algo straight")}'
                large_n *= 10
            