#!/bin/sh
set -e

if [ -z "$1" ]; then
    echo
    echo "changed=no error='$0: first argument is missing'"
    exit 1
fi

dmg={{ pillar['caches']['packages'] }}$1
target_resource=$2
destination={{ pillar['osx']['applications'] }}$2
hashes_dir={{ pillar['caches']['hashes'] }}
volume_name='salt_dmg'
volume=/Volumes/$volume_name

if [ -e "`hdiutil imageinfo "$dmg" | grep -q 'Software License Agreement: true'`" ]; then
    echo Y | hdiutil mount "$dmg" -mountpoint "$volume"
else
    hdiutil mount "$dmg" -mountpoint "$volume"
fi

function shadir {
    if [ -d "$destination" ]; then
        find $1 -type file -exec shasum {} \; | shasum -a 256 | cut -f -d ' '
    else
        shasum -a 256 $1
    fi
}

if [ -e "$target_dest" ]; then
    if [ -e "$hashes_dir/$target_resource" ]; then
        if [ "`shadir "$volume/$target_resource"`" == `cat "$hashes_dir/$target_resource"` ]; then
            hdiutil detach "$volume"
            echo
            echo "changed=no comment='$target_dest is already installed'"
            exit 0
        fi
    fi
fi

rm -rf "$destination" || true
cp -R "$volume/$target_resource" "$destination"
hdiutil detach "$volume"
shadir "$destination" > "$hashes_dir/$target_resource"
echo
echo "changed=yes comment='Mounted $dmg to install $volume/$target_resource to  $destination'"
