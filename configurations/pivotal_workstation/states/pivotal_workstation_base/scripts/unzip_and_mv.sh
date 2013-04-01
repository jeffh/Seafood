#!/bin/sh
export zip_file=$1
export target_file=$2
export target_dest=$3

rm -rf $target_dest || true
rm -rf {{ pillar['caches']['tmp'] }} || true
mkdir -p {{ pillar['caches']['tmp'] }} || true
unzip "$zip_file" -d {{ pillar['caches']['tmp'] }}
mv "{{ pillar['caches']['tmp'] }}/$target_file" "$target_dest"
echo
echo "changed=yes comment='Unzip to target $target_dest' zip='$zip_file' from='{{ pillar['caches']['tmp'] }}/$target_file' to='$target_dest'"
