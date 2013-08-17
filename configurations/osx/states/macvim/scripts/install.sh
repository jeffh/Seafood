#!/bin/sh
[ -e "$1" ] || (echo "$0: first argument is missing" && exit 1)

bzip_file={{ pillar['caches']['packages'] }}$1
target_file=MacVim.app
bin_file=mvim
target_dest={{ pillar['osx']['applications'] }}/$target_file
tmp_dir={{ pillar['caches']['tmp'] }}
hashes_dir={{ pillar['caches']['hashes'] }}
bin_dir=$1

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
    if [ "`shadir "$tmp_dir/$target_file"`" == `cat "$hashes_dir/$target_file"` ]; then
        echo
        echo "changed=no comment='$target_dest is already installed'"
        exit 0
    fi
fi

rm -rf "$target_dest" || true
mv "$tmp_dir/$target_file" "$target_dest"
shadir "$target_dest" > $hashes_dir/${target_file}
rm -f "$bin_dir/$bin_file"
mv -f "$tmp_dir/$bin_file" "$bin_dir/$bin_file"
chmod +x "$bin_dir/$bin_file"
echo
echo "changed=yes comment='Unzip to target $target_dest' zip='$zip_file' from='{{ pillar['caches']['tmp'] }}/$target_file' to='$target_dest'"
