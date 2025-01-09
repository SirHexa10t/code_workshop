#!/bin/bash

function errcho () { echo "$@" >&2 ; }
function err_2_args () { errcho "you tried to set $1 more than once"; exit 1; }

function _mul () { local r=$(printf "%s * " "$@" | sed 's/...$//'); echo "$r" | bc; }  # add ' * ' after each arg, then remove the last 3 chars, then calculate
function _sub () { local r=$(printf "%s - " "$@" | sed 's/...$//'); echo "$r" | bc; }  # add ' - ' after each arg, then remove the last 3 chars, then calculate
function _add () { local r=$(printf "%s + " "$@" | sed 's/...$//'); echo "$r" | bc; }  # add ' + ' after each arg, then remove the last 3 chars, then calculate

function fib_adv () {
    [[ $((n > 326)) -eq 1 ]] && { errcho "Bash on straight method can't calculate above fib[326]. You required index: $n. Sorry."; return 9; }

    local trailing=0 leading=1  # at indexes k, k+1
    local binary=$(echo "obase=2;$1" | bc)  # binary representation, we'll read it from MSB
    while [[ -n "$binary" ]] ; do
        # double k, the climbing index
        local temp=$(echo "$leading * $leading + $trailing * $trailing " | bc)  # F(2k+1) = F(k+1)^2 + F(k)^2 
        trailing=$( echo "$trailing * ( 2 * $leading - $trailing )" | bc )  # F(2k) = F(k) * (2*F(k+1) - F(k)  # Can also do Cassini's: F(2K) = F(k+1)^2 - F(k-1)^2
        leading="$temp"
        [[ "${binary:0:1}" == '1' ]] && { leading=$( _add $leading $trailing); trailing=$(_sub $leading $trailing); }  # progress indexes by another step

        binary=${binary:1}  # remove first char from string
    done
    echo "$trailing"
}

function fib_straight () {
    [[ $((n > 327)) -eq 1 ]] && { errcho "Bash on straight method can't calculate above fib[327]. You required index: $n"; return 9; }
    local trailing=1 leading=1 i
    for i in $(seq 3 $n); do
        leading=$( _add $leading $trailing)  # leading = leading+trailing
        trailing=$(_sub $leading $trailing)  # trailing= leading+trailing - trailing
    done
    echo "$leading"
}

function fib_naive () {
    [ "$1" -gt 1 ] || { echo "$1"; return; }
    kminus1=$(fib_naive $(_sub "$1" 1))
    kminus2=$(fib_naive $(_sub "$1" 2))
    echo "$(_add "$kminus1" "$kminus2")"
}


function mymain () {
    local algo=''
    local no_print=''
    local n=''        # index number
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help )
                echo "Calculate nth Fibonacci number, in various ways
    Usage: $BASH_SOURCE <args>
    required args:
    ibonacci index to calculate at
    <number>                       Fibonacci index to calculate at
    optional args:
    -n                             don't print the calculated result
    --algo <naive/straight/adv>    calculation algorithm
    -h / --help                    print this message"
                exit 0
                ;;
            --algo )
                [ -z "$algo" ] && algo="$2" || err_2_args "$1"
                [ -n "$2" ] && shift 2 || { errcho "you must provide another arg after --algo"; exit 1; }
                continue
                ;;
            -n ) [ -z "$no_print" ] && no_print='true' || err_2_args "$1"
                shift
                continue
                ;;
            *) [ -z "$n" ] && n="$1" || err_2_args "index-number"
                shift
                continue
                ;;
        esac
    done

    [ -z "$n" ] && { errcho "You didn't specify a number as an index."; exit 1; } 
    [[ "$n" =~ ^[1-9][0-9]*$ ]] || { errcho "Index must be a positive integer."; exit 1; } 
    
    [ -z "$algo" ] && algo='adv'  # set default
    [[ "$algo" != 'adv' && "$algo" != 'straight' && "$algo" != 'naive' ]] && { errcho "Invalid algorithm specified."; exit 1; }
    
    local temp_file=$(mktemp)  # I don't like using tmp-files instead of vars, but $() is an extra shell layer that swallows the return code
    local result
    {
        if   [[ "$algo" == 'adv' ]];        then fib_adv "$n";
        elif [[ "$algo" == 'straight' ]];   then fib_straight "$n";
        elif [[ "$algo" == 'naive' ]];      then fib_naive "$n";
        fi
        
        retcode="$?"
        [[ "$retcode" -ne 0 ]] && exit "$retcode"
    } > "$temp_file"
    
    # from index 93 onward, Bash's number system can't handle the big numbers (even bc can't look at it as a number, and that's the program that generated it!)
    # if echo "$result > 0" | bc; then errcho "result was too big, got '$result', it looped back into negatives!"; exit 9; fi
    
    [ -z "$no_print" ] && cat "$temp_file"
    rm "$temp_file"

    exit 0  # crucial!!! The last command we run can return 1 and it'd be fine by us, but this wouldn't mean we want the whole script to return 1!
}

mymain $@
