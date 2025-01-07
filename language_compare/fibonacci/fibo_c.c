// Calculate nth Fibonacci number, in various ways
// Index starts at 1

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>
#include <string.h>
#include <errno.h>

/* Fibo identities:  (might be useful for simpler computation choices)
0) F(k+1) = F(k)+F(k-1)
1) F(2k) = F(k) * (2*F(k+1) - F(k))
    1A) F(2k) = F(k) * (F(k+1)+F(k-1))
    1B) F(2k) = F(k) * (F(k+2) + F(k-1) - F(k)) =  F(k+2)F(k) + F(k)F(k-1) - F(k)^2, can use Catalan to simplify -> F(2k) = F(k+1)^2 - (-1)^k + F(k)F(k-1) - F(k)^2
    1') F(2k) = F(k)*(F(k+1)+F(k-1))
    1'') F(2k+2) = F(k+1)*(F(k+2)+F(k)) = F(k+1)*(F(k+1)+2*F(k))
    1x)  F(k)^2 = 2*F(k+1)F(k)- F(2k)
2) F(2k+1) = F(k+1)^2 + F(k)^2
    2') F(2k-1) = F(k) + F(k-1)^2


0)   ->   A) F(k+1)*(F(k+1)-F(k)) = F(k+1)*F(k-1)
B) F(k+1)*F(k-1) = F(k)^2 + (-1)^k         Catalan's identity

B' (F(k+2)-F(k))*(F(k+1)-F(k))
B) & 0) -> Bx) (F(k+1)-F(k)) * F(k+1) = F(k)^2 + (-1)^k   ->   F(k)^2 = F(k+1)*(F(k+1)-F(k)) - (-1)^k
        ->     (F(k)-F(k-1)) * F(k) = F(k-1)^2 + (-1)^(k-1)

K)?  F(k)*F(k-2) = F(k)^2 - F(k)F(k-1)
B)      -> F(k)*F(k-2) = F(k-1)^2 + (-1)^(k-1), so condidering K) -> F(k)^2 - F(k)F(k-1) = F(k-1)^2 + (-1)^(k-1)
        -> F(k)F(k-1) = F(k)^2 - F(k-1)^2 - (-1)^(k-1) = F(k)^2 - F(k-1)^2 + (-1)^k
        

1B) & K)  ->  F(2k) = F(k+1)^2 - (-1)^k + ( F(k)^2 - F(k)*F(k-2) ) - F(k)^2 = F(2k) = F(k+1)^2 - (-1)^k - F(k)*F(k-2)
        & Catalan ->  BK) F(2k) = F(k+1)^2 - (-1)^k - ( F(k-1)^2 + (-1)^(k-1) ) = F(k+1)^2 - F(k-1)^2    Cassini's

0)  ->  D) F(k+1)^2 - F(k+1)*F(k) = F(k+1)*(F(k+1)-F(k)) = F(k+1)*F(k-1)
D) & B)  ->  F(k+1)^2 - F(k+1)*F(k) = F(k)^2 + (-1)^k


F(k+1)*F(k) - F(k)F(k-1) = F(k+1)*F(k) - F(k-1)F(k) = F(k+1)*F(k) - F(k-1)F(k) = (F(k+1)-F(k-1))*F(k) = F(k)^2
        ->  G) F(k)F(k-1) = F(k+1)*F(k) - F(k)^2

1B & G) -> F(2k) = F(k+1)^2 - (-1)^k + F(k+1)*F(k) - F(k)^2 - F(k)^2 = F(k+1)^2 + F(k+1)*F(k) - 2*F(k)^2 - (-1)^k

0)            -> 3)  2*F(k+1) - F(k) = F(k+1) + F(k-1) 
1) & 0) & 3)  -> 4)  F(2k) = F(k) * (2*F(k+1) - F(k)) = (F(k+1)-F(k-1))*(2*F(k+1)-F(k)) = (F(k+1)-F(k-1))*(F(k+1)+F(k-1)) = F(k+1)^2 - F(k-1)^2   Cassini's identity
              -> 4') F(2k+2) = F(k+2)^2 - F(k)^2     A version of cassini
4) + 1)       -> 6)  F(2k) + F(2k) = (F(k+1)^2 - F(k-1)^2) + 2*F(k+1)F(k) - F(k)^2


1) + 2)  ->  12) F(2k+2) = F(2k) + F(2k+1) = (F(k+1)^2 - F(k-1)^2) +  (F(k+1)^2 + F(k)^2) = 2*F(k+1)^2 + F(k)^2 - F(k-1)^2


0) & 1) & 2) -> F(2k+2) = F(2k+1)+F(2k) = F(k+1)^2+F(k)^2 + F(k)*(2*F(k+1)-F(k)) = F(k+1)^2 + 2F(k+1)*F(k) + 0*F(k)^2 = F(k+1)*(2*F(k)+F(k+1))
    but also 1) -> F(2k+2) = F(k+1) * (2*F(k+2) - F(k+1)) , so F(k+1)*(2*F(k)+F(k+1)) = F(k+1)*(2*F(k+2)-F(k+1)), so:
    2*F(k)+F(k+1) = 2*F(k+2)-F(k+1)
*/


// find by finding fibo(k/2) (and find that through fibo(k/4)...)
// Then find F(k) = F(2x) = F(x) * (2*F(x+1) - F(x))  and  F(k+1) = F(2x+1) = F(x+1)^2 + F(x)^2
// Basically we're multiplying by 2 and adding 1 according to the binary representation of the sought index
void fib_adv(uint64_t n, bool is_printing)
{
    mpz_t fk, fk1, fk1k, ffk, ffk1, f2k1;
    mpz_init_set_ui(fk, 0);    // F(k)  // at index 0, but we start from index 1, so we'll never get back 0
    mpz_init_set_ui(fk1, 1);   // F(k+1)
    mpz_init_set_ui(fk1k, 1);  // F(k+1)F(k)
    mpz_init_set_ui(ffk, 1);   // F(k)^2
    mpz_init_set_ui(ffk1, 1);  // F(k+1)^2
    mpz_init_set_ui(f2k1, 1);  // F(2k+1)
    
    // create a number that we can iterate on its bits in reverse order
    uint64_t inverted_n = 0;
    for (uint64_t n_copy = n ; n_copy > 0 ; n_copy >>= 1)
    {
        inverted_n <<= 1;
        if (n_copy & 1) inverted_n++;  // for every 1 we take out of n, we put one in its inversion (from the other direction)
    }
    
    #ifdef TESTING  // only for development, don't compile with -DTESTING on the regular
        int fibonacci[] = {0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811, 514229, 832040, 1346269, 2178309, 3524578, 5702887, 9227465, 14930352, 24157817, 39088169, 63245986, 102334155, 165580141, 267914296, 433494437, 701408733, 1134903170, 1836311903};
        size_t fibsize = sizeof(fibonacci) / sizeof(fibonacci[0]);
        int prev_k=(int)mpz_get_ui(fk), prev_k1=(int)mpz_get_ui(fk1);
        int k = 0;
        
        void check_valid(char *thing_checked, int supposed, int calculated, int k, bool *is_passed)
        {
            if (supposed != calculated)
            { 
                printf("At k=%d, incorrect calculation of %s. Supposed to be %d, got %d.\n", k, thing_checked, supposed, calculated);
                *is_passed=false;
            }
        }
    #endif
    
    // for each bit of inverted n (or: for each bit in n, from MSB to LSB), until (including) our location matches the original goal
    bool is_last_even = true;  // start on 0 digit beyond MSB (first bit will always be 1, so we know it'll flip in first iteration)
    for (uint64_t n_copy = n ; n_copy > 0 ; n_copy >>= 1, inverted_n >>= 1)
    {
        //  F(2k+1)
        mpz_mul(ffk, fk, fk);      // F(k)^2
        // We also need F(k+1)^2 but instead of wasting time on squaring it directly, I found a way that'd let us cache a different value for later:  F(k+1)^2 = F(k+1)*F(k) + F(k)^2 + (-1)^k
        mpz_mul(fk1k, fk1, fk);    // F(k+1)F(k)
        mpz_add(ffk1, fk1k, ffk);  // F(k+1)F(k) + F(k)^2
        if(is_last_even) mpz_add_ui(ffk1, ffk1, 1); else mpz_sub_ui(ffk1, ffk1, 1);  // F(k+1)^2 = F(k+1)*F(k) + F(k)^2 + (-1)^k
        mpz_add(f2k1, ffk1, ffk);  // F(2k+1) = F(k+1)^2 + F(k)^2
        
        // at this point, it'd be good to make no mure multiplications.
        // Available values are: F(k), F(k+1), F(k)^2 , F(k+1)F(k) , F(2k+1)
        
        // use all gathered data to jump to x2 index
        if (inverted_n & 1)  // uneven, progress fibo by extra 1. All according to the bits of n.
        {
            //  F(k+1) <- F(2k+2)
            // F(2k+2) = F(2k+1) + 2*F(k+1)F(k) - F(k)^2   // I don't remember how I got this formula. "It just works" -Todd Howard
            // Could also run longer through Cassini's:  F(2k+2) = F(k+2)^2 - F(k)^2
            mpz_add(fk1, fk1k, fk1k);   // 2*F(k+1)F(k)
            mpz_add(fk1, f2k1, fk1);    // F(2k+1) + 2*F(k+1)F(k)
            mpz_sub(fk1, fk1, ffk);     // F(2k+2) = F(2k+1) + 2*F(k+1)F(k) - F(k)^2
            
            //  F(k) <- F(2k+1)
            mpz_swap(fk, f2k1);
            
            is_last_even=false;
        }
        else  // even. get 2k and 2k+1, no incrementation
        {
            //  F(k) <- F(2k)
            // F(2k) = F(k+1)^2 + F(k+1)*F(k) - 2*F(k)^2 - (-1)^k  // a mix of various; Catalan's, Cassini's, and some of mine.
            // Could also run longer through Cassini's:  F(2k) = F(k+1)^2 - F(k-1)^2
            mpz_add(fk, ffk, ffk);                                               // 2*F(k)^2
            mpz_sub(fk, fk1k, fk);                                               // F(k+1)*F(k) - 2*F(k)^2
            mpz_add(fk, ffk1, fk);                                               // F(k+1)^2 + F(k+1)*F(k) - 2*F(k)^2
            if(is_last_even) mpz_sub_ui(fk, fk, 1); else mpz_add_ui(fk, fk, 1);  // - (-1)^k

            //  F(k+1) <- F(2k+1)
            mpz_swap(fk1, f2k1);
            
            is_last_even=true;
        }

        #ifdef TESTING
            bool is_fine = true;
            printf("Did %s iteration. ", is_last_even? "even":"uneven");
            if ((k+1)*(k+1) < fibsize)
            {
                gmp_printf("Values: %d,%d -> %Zd,%Zd\n", prev_k, prev_k1, fk, fk1);
                check_valid("F(k)",         fibonacci[k], prev_k,               k, &is_fine);
                check_valid("F(k+1)",       fibonacci[k+1], prev_k1,            k, &is_fine);
                check_valid("F(k+1)F(k)",   prev_k*prev_k1, mpz_get_ui(fk1k),   k, &is_fine);
                check_valid("F(k)^2",       prev_k*prev_k, mpz_get_ui(ffk),     k, &is_fine);
                check_valid("F(k+1)^2",     prev_k1*prev_k1, mpz_get_ui(ffk1),  k, &is_fine);
                
                k *= 2;
                if (!is_last_even) k++;
                prev_k=(int)mpz_get_ui(fk), prev_k1=(int)mpz_get_ui(fk1);
                
                check_valid("Next F(k)",         fibonacci[k], prev_k,          k, &is_fine);  // checked twice, but I don't care.
                check_valid("Next F(k+1)",       fibonacci[k+1], prev_k1,       k, &is_fine);
                
                if (!is_fine) exit(1);
            }
            else
            {
                gmp_printf("Can't check efficiently. Exceeded cached Fibonacci values. Current values: %Zd,%Zd\n", fk, fk1);
            }
        #endif
    }
    
    // printing
    if (is_printing) gmp_printf("%Zd\n", fk);  // print trailing item
    
    // // cleanup
    mpz_clear(fk);
    mpz_clear(fk1);
    mpz_clear(ffk);
    mpz_clear(fk1k);
    mpz_clear(ffk1);
    mpz_clear(f2k1);
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

