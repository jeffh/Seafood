#!/bin/sh
dmg={{ pillar['caches']['packages'] }}$1
target_resource=$2
destination={{ pillar['osx']['applications'] }}$2
hashes_dir={{ pillar['caches']['hashes'] }}

volume=`hdiutil mount $dmg | grep Volumes | sed 's/.*\/Volumes/\/Volumes/g'`

if [ -e "$target_dest" ]; then
    if [ "`cat "$volume/$target_resource" | shasum -a 256 | cut -f 1 -d ' '`" == `cat "$hashes_dir/$target_resource"` ]; then
        hdiutil detach "$volume"
        echo
        echo "changed=no comment='$target_dest is already installed'"
        exit 0
    fi
fi

rm -rf $destination || true
cp -R "$volume/$target_resource" "$destination"
hdiutil detach "$volume"
cat "$destination" | shasum -a 256 | cut -f 1 -d ' ' > $hashes_dir/$target_resource
echo
echo "changed=yes comment='$dmg >> $volume/$target_resource >> $destination'"
