!/bin/bash

# Define a list of numbers
numbers=(0 0.5 1 1.5 2 2.5 3 3.5 4 4.5 5 5.5 6 6.5 7 0)

# Loop through each number
for num in "${numbers[@]}"; do
    echo "Current number: $num"
    	robstride move --ids 11 --kp 0 --kp 0 --torque $num
        sleep 1.0
        done
