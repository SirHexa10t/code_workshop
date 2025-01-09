#!/usr/bin/python3

import sys  # necessary for checking number of in digits, and accepting argv

def calc_necessary_digits(n):
    """ approximate the number of digits nth number in Fibonacci has. Formula is: n*log10(phi) - log10(5)/2 """
    log10phi = 0.208988       # math.log10(( 1 + math.sqrt(5) ) / 2) ; constant; no reason to recalculate every run
    log10of5div2 = 0.349485   # math.log10(5)/2 ; constant; no reason to recalculate every run.
    return int(n*log10phi - log10of5div2 + 1)  # floor and +1

def set_int_digits(n):
    needed = calc_necessary_digits(n)
    if needed > sys.get_int_max_str_digits():
        sys.set_int_max_str_digits(needed)

# mentioned in this video:  https://www.youtube.com/watch?v=02rh1NjJLI4
def fib_adv(n: int) -> int:
    """calculate nth Fibonacci number"""
    def fib_pair(k: int) -> tuple[int, int]:
        """ Calculate a pair of Fibonacci numbers """
        if k <= 1:
            return (k, 1)
        fh, fh1 = fib_pair(k>>1)    # get F(k/2), F(k/2+1) where k/2 is even (so we can divide it again by 2)
        fk = fh * ((fh1<<1) - fh)   # F(2k) calculation:   F(2k) = F(k) * (2*F(k+1) - F(k))
        fk1 = fh1**2 + fh**2        # F(2k+1) calculation:  F(2k+1) = F(k+1)^2 + F(k)^2 
        if k & 1:                   # checking if odd by looking at LSB
            fk, fk1 = fk1, fk+fk1
        return (fk, fk1)
    return fib_pair(n)[0]

def fib_naive(n: int) -> int:
    return fib_naive(n-1) + fib_naive(n-2) if n > 2 else 1  # first 2 fib values are set to 1

def fib_straight(n: int) -> int:
    trailing, leading = 1, 1
    for i in range(3, n+1):  # we want to include n, so +1
        trailing, leading = leading, trailing+leading
    
    return leading



if __name__ == "__main__":
    callables = {
        'naive': fib_naive,
        'adv': fib_adv,
        'straight': fib_straight,
    }
        
    def parse_args():
        import argparse
        parser = argparse.ArgumentParser(description="Calculate nth Fibonacci number, in various ways")
        
        required_args = parser.add_argument_group('Required args')
        parser.add_argument('n', help='Fibonacci index to calculate at',
            type=lambda i: int(i) if i.isdigit() and int(i) > 0 else parser.error(f"You must provide a positive integer as an index (you provided: '{i}')"))
        
        optional_args = parser.add_argument_group('Optional args')
        optional_args.add_argument('-n', dest='is_printing', default=True, action='store_false', help="don't print the calculated result")  # optional flag '-n'
        optional_args.add_argument('--algo', dest='callme', default='adv', help=f'calculation algorithm (choices: {"/".join(callables.keys())})', metavar='<algorithm>',
            type=lambda x: callables[x] if (not x.isdigit() and x in callables) else parser.error(f"You provided '{x}' instead of one of the following: {' '.join(callables.keys())}"))
    
        return parser.parse_args()
        
    args = parse_args()
    result = args.callme(args.n)
    if args.is_printing:
        set_int_digits(args.n)
        print(result)
    exit(0)
