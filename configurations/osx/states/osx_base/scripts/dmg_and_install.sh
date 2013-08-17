#!/bin/sh
set -e
dmg={{ pillar['caches']['packages'] }}$1
target_resource=$2
expected_sha=$3
hashes_dir={{ pillar['caches']['hashes'] }}

volume_name='salt_dmg'
volume=/Volumes/$volume_name

function shadir {
    if [ -d "$destination" ]; then
        find $1 -type file -exec shasum {} \; | shasum -a 256 | cut -f -d ' '
    else
        shasum -a 256 $1
    fi
}

if [ -e "$hashes_dir/dmg_$target_resource" ]; then
    if [ "`shadir "$dmg"`" == `cat "$hashes_dir/dmg_install_$target_resource"` ]; then
        echo
        echo "changed=no comment='$target_resource is already installed'"
        exit 0
    fi
fi

if [ -e "`hdiutil imageinfo "$dmg" | grep -q 'Software License Agreement: true'`" ]; then
    echo Y | hdiutil mount "$dmg" -mountpoint "$volume"
else
    hdiutil mount "$dmg" -mountpoint "$volume"
fi

installer -pkg "$volume/$target_resource" -target /
hdiutil detach "$volume"
shadir "$dmg" > "$hashes_dir/dmg_install_$target_resource"
echo
echo "changed=yes comment='mounted $dmg to $volume/$target_resource install package'"
