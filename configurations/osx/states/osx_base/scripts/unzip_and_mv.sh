#!/bin/sh
zip_file={{ pillar['caches']['packages'] }}$1
target_file=$2
target_dest={{ pillar['osx']['applications'] }}$2
tmp_dir={{ pillar['caches']['tmp'] }}
hashes_dir={{ pillar['caches']['hashes'] }}

rm -rf $tmp_dir || true
mkdir -p $tmp_dir || true
unzip -qq "$zip_file" -d $tmp_dir

if [ -e "$target_dest" ]; then
    if [ "`cat "$tmp_dir/$target_file" | shasum -a 256 | cut -f 1 -d ' '`" == `cat "$hashes_dir/$target_file"` ]; then
        echo
        echo "changed=no comment='$target_dest is already installed'"
        exit 0
    fi
fi

rm -rf $target_dest || true
mv "$tmp_dir/$target_file" "$target_dest"
cat "$target_dest" | shasum -a 256 | cut -f 1 -d ' ' > $hashes_dir/${target_file}
echo
echo "changed=yes comment='Unzip to target $target_dest' zip='$zip_file' from='{{ pillar['caches']['tmp'] }}/$target_file' to='$target_dest'"
