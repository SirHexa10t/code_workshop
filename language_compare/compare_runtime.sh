#!/bin/bash

echo 'Comparing Fibonacci calculations'
program='Python'
n=1
max_iteration_time=0.3       # in seconds
max_exp_iteration_time=0.05

declare -A runconfs results
for algo in 'naive' 'straight' 'adv'; do 
    runconfs["${program}_${algo}"]="$algo"
    results["${program}_${algo}"]=''
done

while true; do
    for config in "${!runconfs[@]}"; do
        algo=${runconfs[$config]}
        
        # run and measure time
        start_time=$(date +%s.%N)  # using 'time' to measure runtime proved problematic under the current circumstances
        python3 ./fibonacci/fibo_python.py "$n" --algo "$algo" &>/dev/null || { echo "error when calculating on $program, n=$n, algorithm: $algo (fix it, I won't keep on running like that)"; exit 1; }
        timed=$(echo "$(date +%s.%N) - $start_time" | bc)
        
        echo "fib-index $n, $algo algorithm: $timed ($program)"
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
title="Fibonacci calculation time"
y_axis="Execution Time (s)"
x_axis="Fibonacci Index"

temp_file=$(mktemp)
echo "Fibonacci calculation time" >> "$temp_file"   # title
echo "Execution Time (s)" >> "$temp_file"           # y_axis
echo "Fibonacci Index" >> "$temp_file"              # x_axis

for config in "${!results[@]}"; do
    trimmed="${results[$config]%,}"
    echo "{ \"$config\": [ $trimmed ] }" >> "$temp_file"  # output a json object in a single line as data-set
done

# cat "$temp_file"
python3 ./plot_results.py "$temp_file"

rm "$temp_file"  # cleanup

