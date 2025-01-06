#!/bin/bash

problem=fibonacci



# Setup (finding programs and compiling)
# ======================================

py_program="$(find "$problem/" -type f -name "fibo*.py")"
[ -n "$py_program" ] || { echo "couldn't find the python file, fix this"; exit 1; }

pyc_program="$(find "$problem/" -type f -name "fibo*.pyc")"
[ -n "$pyc_program" ] || { python -m compileall "$py_program" && pyc_program="$(find "$problem/" -type f -name "fibo*.pyc")"; }  # compile, if it's not there
[ -n "$pyc_program" ] || { echo "couldn't compile the python file (didn't find the compiled file after compilation), fix it"; exit 1; }  # still not there?


c_program="$(find "$problem/" -type f -name "fibo*.c")"
[ -n "$c_program" ] || { echo "couldn't find the c source-code file, fix this"; exit 1; }

# Recompile and overwrite the C binaries. Unlike python, C compilation args are very impactful on performance, so we make sure to use the right settings
gcc -O3 -m64 "$c_program" -lgmp -o "${c_program%.c}.bin"  # -03 is optimization for speed, -lgmp is GNU library "gmp" for large numbers
ccompiled_program="$(find "$problem/" -type f -name "fibo*c.bin")"

[ -n "$ccompiled_program" ] || { echo "couldn't compile the c file (didn't find the compiled file after compilation), fix it"; exit 1; }  # still not there?




# Run Programs
# ============

declare -A progcmds
progcmds['Python']="python3 $py_program "
progcmds['CompiledPython']="python3 $pyc_program "

echo "Comparing $problem calculations"
n=1
max_iteration_time=1       # in seconds
max_exp_iteration_time=0.05

declare -A runconfs results
for program in "${!progcmds[@]}"; do
    for algo in 'naive' 'straight' 'adv'; do 
        runconfs["${program}_${algo}"]="$algo"
        results["${program}_${algo}"]=''
    done
done

while true; do
    for config in "${!runconfs[@]}"; do
        program=${config%%_*}
        algo=${config#*_}
                
        # run and measure time
        start_time=$(date +%s.%N)  # using 'time' to measure runtime proved problematic under the current circumstances
        ${progcmds[$program]} "$n" --algo "$algo" &>/dev/null || { echo "error when calculating on $program, n=$n, algorithm: $algo (fix it, I won't keep on running like that)"; exit 1; }
        timed=$(echo "$(date +%s.%N) - $start_time" | bc)
        
        echo "$problem input $n @ $config: $timed ($program)"
        results[$config]+=" {\"$n\":\"$timed\"},"
        
        # remove from benchmark if starting to take too long
        (( $(echo "$timed > $max_iteration_time" | bc -l) )) && unset runconfs["$config"]  # took too long, don't try again
        [[ "$algo" == 'naive' ]] && (( $(echo "$timed > $max_exp_iteration_time" | bc -l) ))  && unset runconfs["$config"]  # quit extra early for exponential runtimes
    done
    
    [ ${#runconfs[@]} -eq 0 ] && break  # emptied all running configurations; we're done
    n=$((n * 2))
done



# Draw graph
# ==========

# Define plot parameters
title="$problem calculation time"
y_axis="Execution Time (s)"
x_axis="$problem Index"

temp_file=$(mktemp)
echo "$problem calculation time" >> "$temp_file"   # title
echo "Execution Time (s)" >> "$temp_file"           # y_axis
echo "$problem Index" >> "$temp_file"              # x_axis

for config in "${!results[@]}"; do
    trimmed="${results[$config]%,}"
    echo "{ \"$config\": [ $trimmed ] }" >> "$temp_file"  # output a json object in a single line as data-set
done

# cat "$temp_file"
python3 ./plot_results.py "$temp_file"

rm "$temp_file"  # cleanup

