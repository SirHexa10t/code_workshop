// Calculate nth Fibonacci number, in various ways
// Index starts at 1

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>
#include <string.h>
#include <errno.h>


// find by finding fibo(k/2) (and find that through fibo(k/4)...)
// Then find F(k) = F(2x) = F(x) * (2*F(x+1) - F(x))  and  F(k+1) = F(2x+1) = F(x+1)^2 + F(x)^2
// Basically we're multiplying by 2 and adding 1 according to the binary representation of the sought index
void fib_adv(uint64_t n, bool is_printing)
{
    mpz_t fk, fk1, f2k, f2k1, temp;  // f(k), f(k+1), f(2k), f(2k+1)
    mpz_init_set_ui(fk, 0);
    mpz_init_set_ui(fk1, 1);
    mpz_init_set_ui(f2k, 1);
    mpz_init_set_ui(f2k1, 1);
    mpz_init_set_ui(temp, 1);
    
    // create a number that we can iterate on its bits in reverse order
    uint64_t inverted_n = 0;
    for (uint64_t n_copy = n ; n_copy > 0 ; n_copy >>= 1)
    {
        inverted_n <<= 1;
        if (n_copy & 1) inverted_n++;  // for every 1 we take out of n, we put one in its inversion (from the other direction)
    }
    
    // for each bit of inverted n (or: for each bit in n, from MSB to LSB), until (including) our location matches the original goal
    for (uint64_t n_copy = n ; n_copy > 0 ; n_copy >>= 1, inverted_n >>= 1)
    {  
        // jump to x2 index
        // F(2k) = F(k) * (2*F(k+1) - F(k))
        mpz_mul_ui(temp, fk1, 2);  // 2*F(k+1) // TODO: try: mpz_mul_2exp(result, number, 1)
        mpz_sub(temp, temp, fk);   // 2*F(k+1) - F(k)
        mpz_mul(f2k, fk, temp);    // F(k) * (2*F(k+1) - F(k))

        // F(2k+1) = F(k+1)^2 + F(k)^2
        mpz_mul(f2k1, fk1, fk1);    // F(k+1)^2
        mpz_mul(temp, fk, fk);      // F(k)^2
        mpz_add(f2k1, f2k1, temp);  // F(k+1)^2 + F(k)^2

        // assign f(k), f(k+1) = f(2k), f(2k+1)
        mpz_swap(fk, f2k);
        mpz_swap(fk1, f2k1);

        // if number is uneven (according to LSB), do +1 in fibo, fitting the '1' bits of n.
        // This incrementation at the right times will make sure we reach n instead of some 2^k
        if (inverted_n & 1) {
            mpz_swap(fk, fk1);  // fk = fk1
            mpz_add(fk1, fk1, fk); // fk1 = fk1 + fk
        }
    }

    // printing
    if (is_printing) gmp_printf("%Zd\n", fk);
    
    // // cleanup
    mpz_clear(fk);
    mpz_clear(fk1);
    mpz_clear(f2k);
    mpz_clear(f2k1);
    mpz_clear(temp);
}



void fib_straight(uint64_t index, bool is_printing)
{
    mpz_t trailing, leading;
    mpz_init_set_ui(trailing, 1);
    mpz_init_set_ui(leading, 1);

    // calculation
    for (uint64_t i = 3; i <= index; ++i)  // we want to include index, so we use <=
    {
        mpz_swap(trailing, leading);          // f(k) = f(k+1)
        mpz_add(leading, trailing, leading);  // f(k+1) = f(k+1) + f(k)
    }

    // printing
    if (is_printing) gmp_printf("%Zd\n", leading);

    // cleanup
    mpz_clear(trailing);
    mpz_clear(leading);
}


// mostly copied (not that it's complicated, but the typing is a good idea) from:  https://github.com/SheafificationOfG/Fibsonisheaf/blob/main/impl/naive.c
void fib_naive(uint64_t index, uint64_t *result)  // uint64_t can store up to Fib[93]=12200160415121876738 . We won't reach 93 in naive solution, so we can keep it simple and efficient
{
    if (index <= 2)
    {
        *result = 1;
        return;
    }

    uint64_t a, b;
    fib_naive(index-1, &a);
    fib_naive(index-2, &b);
    *result = a + b;
}

void fib_naive_caller(uint64_t index, bool is_printing)  // the naive method is recursive, so we need an external one
{
    uint64_t result;
    fib_naive(index, &result);

    if (is_printing) printf("%llu\n", (unsigned long long)result);
}


int print_usage(const char *prog_name, int status) { 
    const char *usage_message = 
        "Calculate nth Fibonacci number, in various ways\n"
        "Usage: %s <args>\n"
        "required args:\n"
        "<number>                       Fibonacci index to calculate at\n"
        "optional args:\n"
        "-n                             don't print the calculated result\n"
        "--algo <naive/straight/adv>    calculation algorithm\n"
        "-h / --help                    print this message\n";
    return fprintf(stderr, usage_message, prog_name), status; 
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        fprintf(stderr, "Missing arguments!\n");
        return print_usage(argv[0], 1);
    }
    
    // Handling args
    
    uint64_t index = 0;             bool is_set_index = false;
    bool is_printing = true;        bool is_set_printing = false;
    const char *algo = "adv";       bool is_set_algo = false;
    const char *set_twice_err = "You tried to set %s more than once!\n";
    
    for (int i = 1; i < argc; i++) 
    {
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0)  // help
        {
            return print_usage(argv[0], 0);
        }
        else if (strcmp(argv[i], "-n") == 0)  // no-printing flag (optional)
        {
            if (is_set_printing) return fprintf(stderr, set_twice_err, "no-printing"), 1; else is_set_printing = true;
            is_printing = false;
        }
        else if (strcmp(argv[i], "--algo") == 0) //algorithm args (optional)
        {
            if (is_set_algo) return fprintf(stderr, set_twice_err, "algorithm"), 1; else is_set_algo = true;
            if (i + 1 >= argc) return fprintf(stderr, "--algo requires a following argument: naive/straight/adv\n"), 1;
            
            if (strcmp(argv[i+1], "naive") == 0 || strcmp(argv[i+1], "straight") == 0 || strcmp(argv[i+1], "adv") == 0) algo = argv[i+1];
            else return fprintf(stderr, "Unrecognized algorithm: '%s'. Valid algorithms: naive straight adv\n", argv[i+1]), 1;
            i++;
        }
        else  // fibo-index (required) 
        {
            if (is_set_index) return fprintf(stderr, set_twice_err, "fibo-index"), 1; else is_set_index = true;
            if (argv[i][0] == '-') return fprintf(stderr, "Index must be a positive integer\n"), 1;

            char *endptr;
            index = strtoull(argv[i], &endptr, 10);  // try to convert to base10
            if (*endptr != '\0' || errno != 0) return fprintf(stderr, "Index is invalid as an integer: %s\n", argv[i]), 1;
            if (index == 0) return fprintf(stderr, "Index must be a positive integer\n"), 1;
        }
        
    }

    // running program
    if (strcmp(algo, "naive")==0) fib_naive_caller(index, is_printing);
    else if (strcmp(algo, "straight")==0) fib_straight(index, is_printing);
    else if (strcmp(algo, "adv")==0) fib_adv(index, is_printing);
    
}

