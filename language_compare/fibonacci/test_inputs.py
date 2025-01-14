#!/usr/bin/python3

from pathlib import Path

this_file = Path(__file__).resolve()
this_files_dir = this_file.parent


algorithms_to_limits = {
    "adv": 1000000,  # can go higher in some scripts
    "straight": 1000,
    "naive": 14,
}

tests = {
    "python":   f"{this_files_dir}/fibo_python.py",
    "c":        f"{this_files_dir}/fibo_c.bin",
    "bash":     f"{this_files_dir}/fibo_bash.sh",
}

executables = {
    ".py": "python3",
    ".sh": "/bin/bash",
}

for prog, test in tests.items():  # verify that all specified files exist
    if not Path(test).resolve().is_file():
        print(f"Problematic file definition, this isn't an existing file: {test}")
        exit(1)

# make the files runnable
for prog, test in tests.items():
    if executables.get(Path(test).suffix, None):
        tests[prog] = f"{executables[Path(test).suffix]} {tests[prog]}"  # add the execution command/tool/runtime





if __name__ == "__main__":
    print(f"This isn't how you run python test files. Run this:\n"
        f"python3 -m unittest {this_file}\n"
        f"or a specific test:\n"
        f"python3  -m unittest {this_file} -k Testings.test_args_handling")
    exit(1)

# test by running:  python3 -m unittest test_inputs.py
import unittest
class Testings(unittest.TestCase):
    
    @staticmethod
    def print_test_subject(test, topic):
        print(f"on '{test}', running '{topic}'")
        
    @staticmethod
    def title(topic):
        title=f"TESTING {topic.upper()}"
        print('='*len(title))
        print(title)
        print('='*len(title))
        
    
    @staticmethod
    def runcmd(bash_cmd):
        import subprocess
        return subprocess.run(bash_cmd, shell=True, capture_output=True, text=True, executable='/bin/bash')

    def test_args_handling(self):  # python3 -m unittest test_inputs.Testings.test_args_handling
        self.title("ARGS INPUT")            
        import os
        
        for prog, test in tests.items():
            def cmd_stderr(arguments):
                return self.runcmd(f"{test} {arguments}").stderr
                
            def assert_args_cause_stderr(arguments):
                self.assertIsNotNone(cmd_stderr(arguments), msg=f"failed while running {prog}")
            
            def assert_args_legal(arguments):
                self.assertEqual('', cmd_stderr(arguments), msg=f"failed while running {prog}")
                
            # verify that the following errors occur
            self.print_test_subject(prog, 'stderr')
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
            assert_args_cause_stderr('1 --helpa') # wrong spelling for 'help'

            self.print_test_subject(prog, 'no-stderr')
            assert_args_legal('1')              # valid usage
            assert_args_legal('4')              # valid usage
            assert_args_legal('4 --algo adv')   # valid usage
            assert_args_legal('--algo adv 4')   # valid usage
            assert_args_legal('--help')   # valid usage
            assert_args_legal('3000 --help')   # valid usage
    
    def test_cross_same_results(self):
        self.title("RESULTS ACROSS SCRIPTS")

        def compare_results(results):
            filtered = [result for result in results if result.returncode != 9]  # don't consider ret 9, I decided that it means that the script admits on its own that it can't handle the large data-types
            return len(filtered) <=1 or all(x.stdout == filtered[0].stdout for x in filtered)  # all results are equal
            
        def compare_in_range(the_range, algorithms):
            for algorithm in algorithms:
                for index in the_range:  # check same across different scripts
                    run_results=[self.runcmd(f"{test} {index} --algo {algorithm}") for prog, test in tests.items()]
                    self.assertTrue(compare_results(run_results), msg=f"Not all calculations matched! Discrepency at {algorithm} algorithm, index {index}:\n{"\n".join(str(obj) for obj in run_results)}")
                        
        print("running same test across scripts and checking if they're equal: naive")    
        compare_in_range(range(1, algorithms_to_limits['naive']), ('naive',))  # make sure you put ',' in your list/tuple or Python would shorten it into a string!
        print("running same test across scripts and checking if they're equal: mid-range")    
        compare_in_range(range(100, algorithms_to_limits['straight'], 100), ('straight', 'adv',))
        print("running same test across scripts and checking if they're equal: big numbers (logarithmic algo only)")    
        compare_in_range((10 ** i for i in range(1, 100) if 10**i <= algorithms_to_limits['adv']), ('adv',))

    def test_same_results(self):  # check if different algorithms in the same scripts result the same
        self.title("RESULTS ACROSS ALGORITHMS")
        
        for prog, test in tests.items():
            def cmd_stdout(arguments):
                return self.runcmd(f"{test} {arguments}").stdout

            self.print_test_subject(prog, 'direct result')
            self.assertEqual('8\n', cmd_stdout(f"6 --algo straight"))
            self.assertEqual('8\n', cmd_stdout(f"6 --algo adv"))
            self.assertEqual('8\n', cmd_stdout(f"6 --algo naive"))
            
            self.print_test_subject(prog, 'no prints')
            for i in range(1,algorithms_to_limits['naive']):  # test no printing
                self.assertTrue('' == cmd_stdout(f"{i} -n --algo straight") == cmd_stdout(f"{i} --algo adv -n") == cmd_stdout(f"-n {i} --algo naive"))
            
            self.print_test_subject(prog, 'same results all')
            for i in range(1,algorithms_to_limits['naive']):
                self.assertTrue(cmd_stdout(f"{i} --algo straight") == cmd_stdout(f"{i} --algo adv") == cmd_stdout(f"{i} --algo naive"))
    
            self.print_test_subject(prog, 'same results big numbers')
            for i in range(1,algorithms_to_limits['straight'], 100):  # checking validity of adv algorithm
                self.assertEqual(cmd_stdout(f"{i} --algo straight") , cmd_stdout(f"{i} --algo adv"))
            
            self.print_test_subject(prog, 'same results very big number')
            goal = algorithms_to_limits['adv'] if prog != 'bash' else 10000
            self.assertEqual(cmd_stdout(f"{goal} --algo straight") , cmd_stdout(f"{goal} --algo adv"))
    
    def test_handling_of_huge_results(self):  # check with large numbers. 
        self.title("RESULTS DONT CRASH WHEN PRINTED")
    
        for prog, test in tests.items():
            if prog == "bash":  # too slow for this test
                continue;
            def cmd_stdout(arguments):
                return self.runcmd(f"{test} {arguments}").stdout
            
            large_n = 10000  # This one's still in python's standard printed digit count range
            self.print_test_subject(prog, 'dealing with very large numbers')
            while large_n <= algorithms_to_limits['adv']:  # mutliply the scale by 10 each run
                print(f"working on n={large_n}")
                # print(f"checking big index number: {large_n}. Current digit limit: {sys.get_int_max_str_digits()}")
                f'{cmd_stdout(f"{large_n} --algo adv")}'  # try to trigger an exception of integer string conversion (exceeding digits limit)
                f'{cmd_stdout(f"{large_n} --algo straight")}'
                large_n *= 10
            