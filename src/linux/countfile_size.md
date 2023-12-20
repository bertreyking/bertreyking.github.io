# 统计目录大小及文件数

## 脚本

```shell
#!/bin/bash

# Check if a directory is provided as an argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Array to store directory information
declare -a dir_info

# Function to calculate the size of a directory
calculate_directory_size() {
    local dir=$1
    local level=$2

    # Calculate the size of the directory (excluding subdirectories)
    size=$(du -sh $dir | awk '{print $1}')

    # Count the number of files in the directory (excluding subdirectories)
    file_count=$(find $dir -maxdepth 1 -type f | wc -l)

    # Store directory information in the array
    dir_info+=("Level $level: Directory: $dir, Size: $size, Files: $file_count")

    # Check if the maximum recursion level is reached
    if [ $level -lt 5 ]; then
        # Iterate over subdirectories
        for subdir in $(find $dir -maxdepth 1 -mindepth 1 -type d); do
            # Recursively calculate the size of subdirectories
            calculate_directory_size "$subdir" $((level + 1))
        done
    fi
}

# Main script
target_directory=$1
calculate_directory_size "$target_directory" 1

# Sort and display directory information
IFS=$'\n' sorted_info=($(sort <<<"${dir_info[*]}"))
unset IFS

for info in "${sorted_info[@]}"; do
    echo "$info"
done
```