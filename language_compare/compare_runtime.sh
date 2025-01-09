#!/bin/bash

problem=fibonacci
prob="${problem:0:4}"


# Setup (finding programs and compiling)
# ======================================

sh_program="$(find "$problem/" -type f -name "$prob*.sh")"
[ -n "$sh_program" ] || { echo "couldn't find the bash file, fix this"; exit 1; }

py_program="$(find "$problem/" -type f -name "$prob*.py")"
[ -n "$py_program" ] || { echo "couldn't find the python file, fix this"; exit 1; }

pyc_program="$(find "$problem/" -type f -name "$prob*.pyc")"
[ -n "$pyc_program" ] || { python -m compileall "$py_program" && pyc_program="$(find "$problem/" -type f -name "$prob*.pyc")"; }  # compile, if it's not there
[ -n "$pyc_program" ] || { echo "couldn't compile the python file (didn't find the compiled file after compilation), fix it"; exit 1; }  # still not there?


c_program="$(find "$problem/" -type f -name "$prob*.c")"
[ -n "$c_program" ] || { echo "couldn't find the c source-code file, fix this"; exit 1; }

# Recompile and overwrite the C binaries. Unlike python, C compilation args are very impactful on performance, so we make sure to use the right settings
gcc -O3 -m64 "$c_program" -lgmp -o "${c_program%.c}.bin"  # -03 is optimization for speed, -lgmp is GNU library "gmp" for large numbers
c_program="$(find "$problem/" -type f -name "$prob*c.bin")"
[ -n "$c_program" ] || { echo "couldn't compile the c file (didn't find the compiled file after compilation), fix it"; exit 1; }  # still not there?




# Run Programs
# ============

n=1                         # index
exponent_n=2                # index growth: n*2^x
cutoff_time=${1:-5}s        # after this time passes, the process is interrupted and removed from rerunning schedule (default if not arg1: 5s)

declare -A progcmds
progcmds['Bash']="/bin/bash '$sh_program'"
progcmds['Python']="python3 '$py_program' "
progcmds['PythonCompiled']="python3 '$pyc_program' "
progcmds['C']="'$c_program' "

declare -A runconfs results
for program in "${!progcmds[@]}"; do
    for algo in 'naive' 'straight' 'adv'; do 
        runconfs["${program}_${algo}"]="$algo"
        results["${program}_${algo}"]=''
    done
done

echo "Comparing $problem calculations"
while [ ${#runconfs[@]} -gt 0 ]; do
    for config in "${!runconfs[@]}"; do
        program=${config%%_*}
        algo=${config#*_}
                
        # run and measure time
        start_time=$(date +%s.%N)  # using 'time' to measure runtime proved problematic under the current circumstances
        timeout "$cutoff_time" $(echo "${progcmds[$program]}" | xargs -n 1 echo) "$n" --algo "$algo" '-n' &>/dev/null
        exit_status=$?
        end_time=$(date +%s.%N)
        if [ $exit_status -ne 0 ]; then
            case $exit_status in
                9) { unset runconfs["$config"]; echo "Numbers became too big to handle in $problem input $n @ $config"; continue; } ;; # exceeded allowed runtime
                124) { unset runconfs["$config"]; echo "Calculation time exceeded for $problem input $n @ $config"; continue; } ;; # exceeded allowed runtime
                *) { echo "error when calculating on $problem input $n @ $config (fix it, I won't keep on running like that)"; exit 1; } ;;  # error in code
            esac
        fi
        timed=$(echo "$end_time - $start_time" | bc)
        
        echo "$problem input $n @ $config: $timed ($program)"
        results[$config]+=" {\"$n\":\"$timed\"},"               # for graph drawing
    done
    
    # n=$((n * exponent_n))  # Don't calculate like that, you'll be limited in number range and loop back to negatives
    n=$(echo "$n * $exponent_n" | bc)
done



# Draw graph
# ==========

# First 3 lines in the graph are title and headers
temp_file=$(mktemp)
echo "$problem calculation time, limited to ${cutoff_time}" >> "$temp_file"     # title
echo "Execution Time (s)" >> "$temp_file"                                       # y_axis
echo "$problem Index" >> "$temp_file"                                           # x_axis

for config in "${!results[@]}"; do
    trimmed="${results[$config]%,}"
    echo "{ \"$config\": [ $trimmed ] }" >> "$temp_file"  # output a json object in a single line as data-set
done

# cat "$temp_file"
python3 ./plot_results.py "$temp_file"

rm "$temp_file"  # cleanup

