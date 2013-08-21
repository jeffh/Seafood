#!/bin/sh
set -e

if [ -z "$1" ]; then
    echo
    echo "changed=no error='$0: first argument is missing'"
    exit 1
fi

zip_file={{ pillar['caches']['packages'] }}$1
target_file=$2
target_dest={{ pillar['osx']['applications'] }}$2
tmp_dir={{ pillar['caches']['tmp'] }}
hashes_dir={{ pillar['caches']['hashes'] }}

function shadir {
    if [ -d "$destination" ]; then
        find $1 -type file -exec shasum {} \; | shasum -a 256 | cut -f -d ' '
    else
        shasum -a 256 $1
    fi
}

rm -rf "$tmp_dir" || true
mkdir -p "$tmp_dir" || true
tar -C "$tmp_dir" -xjf "$zip_file"

if [ -e "$target_dest" ]; then
    if [ -e "$hashes_dir/$target_resource" ]; then
        if [ "`shadir "$tmp_dir/$target_file"`" == `cat "$hashes_dir/$target_file"` ]; then
            echo
            echo "changed=no comment='$target_dest is already installed'"
            exit 0
        fi
    fi
fi

rm -rf "$target_dest" || true
mv "$tmp_dir/$target_file" "$target_dest"
shadir "$target_dest" | cut -f 1 -d ' ' > "$hashes_dir/${target_file}"
echo
echo "changed=yes comment='Unzip to target $target_dest' zip='$zip_file' from='{{ pillar['caches']['tmp'] }}/$target_file' to='$target_dest'"
