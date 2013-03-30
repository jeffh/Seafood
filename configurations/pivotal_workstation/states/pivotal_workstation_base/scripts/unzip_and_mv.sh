#!/bin/sh
export zip_file=$1
export target_file=$2
export target_dest=$3

if [ -e {{ target_dest }} ]; then
	echo
	echo "changed=no comment='$target_dest already exists.'"
else
	rm -rf {{ pillar['caches']['tmp'] }} || true
	mkdir -p {{ pillar['caches']['tmp'] }} || true
	unzip "$zip_file" -d {{ pillar['caches']['tmp'] }}
	mv "{{ pillar['caches']['tmp'] }}/$target_file" "$target_dest"
	echo
	echo "changed=yes comment='Unzip to target $target_dest' zip='$zip_file' from='{{ pillar['caches']['tmp'] }}/$target_file' to='$target_dest'"
fi
