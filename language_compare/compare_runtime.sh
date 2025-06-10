#!/bin/bash

handle_sigint() { echo "Caught SIGINT, exiting."; exit 1; }
trap handle_sigint SIGINT  # Trap SIGINT and call handle_sigint


problem=fibonacci
prob="${problem:0:4}"

difficulty='memory allocation and big number multiplication'
algos=('naive' 'straight' 'adv' 'surpass')



# Setup (finding programs and compiling)
# ======================================

cd "$problem"  # basically doing this only because jar compilation is horrible without relocating

function _find_src_file() { find . -type f -name "$prob*$1" | tee >(test $(wc -c) -gt 0 || { echo "couldn't find the $1 file, fix this"; exit 1; }); }

sh_program="$(_find_src_file '.sh')"

py_program="$(_find_src_file '.py')"
python3 -m compileall "$py_program"   &&   pyc_program="$(_find_src_file '.pyc')"  # compile python

c_program="$(_find_src_file '.c')"
gcc -O3 -m64 "$c_program" -lgmp -o "${c_program%.c}.bin"   &&   c_program="$(_find_src_file 'c.bin')"  # -03 is optimization for speed, -lgmp is GNU library "gmp" for large numbers

java_program="$(basename $(_find_src_file '.java'))"  # the ./ at the start messes up everything, must get rid of it
# compile .class files with preview features of JDK21  # compile all .class files and choose the main class (named after its file) as the main
javac --enable-preview --release 21 "$java_program"  &&  jar cfm "${java_program%.java}.jar" <(echo -e "Main-Class: ${java_program%.java}\n") fibo*.class  &&  chmod +x "${java_program%.java}.jar"  \
  && java_program="$(_find_src_file '.jar')"

exit 0

# Run Programs
# ============

n=1                         # index
exponent_n=3                # index growth: n* exponent_n^(iterations)
cutoff_time=${1:-1}s        # after this time passes, the process is interrupted and removed from rerunning schedule (default if not arg1: 5s)

declare -A progcmds
progcmds['Bash']="/bin/bash '$sh_program'"
progcmds['Python']="python3 '$py_program' "
progcmds['PythonCompiled']="python3 '$pyc_program' "
progcmds['C']="'$c_program' "
progcmds['Java']="java -jar '$java_program' "

declare -A runconfs results
for program in "${!progcmds[@]}"; do
    for algo in ${algos[@]}; do 
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
                130) { echo "process stopped by your keyboard interrupt, exiting"; exit 1; } ;;
                *) { echo "error when calculating on $problem input $n @ $config (fix it, I won't keep on running like that)"; exit 1; } ;;  # error in code
            esac
        fi
        timed=$(echo "$end_time - $start_time" | bc)
        
        echo "$problem input $n @ $config: $timed ($program)"
        results[$config]+=" {\"$n\":\"$timed\"},"               # for graph drawing
    done
    
    # n=$((n * exponent_n))  # Don't calculate like that, you'll be limited in number range and loop back to negatives
    n=$(bc <<< "$n * $exponent_n" | tr -cd '0-9')
done



# Draw graph
# ==========

# First 3 lines in the graph are title and headers
temp_file=$(mktemp)
title="$problem calculation time (testing $difficulty). Time limit: ${cutoff_time}"  # title
y_label="Execution Time (s)"                                                         # y_axis
x_label="$problem Index"                                                             # x_axis

for config in "${!results[@]}"; do
    trimmed="${results[$config]%,}"
    echo "{ \"$config\": [ $trimmed ] }" >> "$temp_file"  # output a json object in a single line as data-set
done

# cat "$temp_file"
python3 ./plot_results.py --title "$title" --x_label "$x_label" --y_label "$y_label" --data_file "$temp_file"

rm "$temp_file"  # cleanup

