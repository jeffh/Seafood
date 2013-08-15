#!/bin/sh
dmg={{ pillar['caches']['packages'] }}$1
target_resource=$2
expected_sha=$3
hashes_dir={{ pillar['caches']['hashes'] }}

if [ "`cat "$dmg" | shasum -a 256 | cut -f 1 -d ' '`" == `cat "$hashes_dir/dmg_$target_resource"` ]; then
    echo
    echo "changed=no comment='$target_resource is already installed'"
    exit 0
fi

rm -rf $destination || true
volume=`hdiutil mount $dmg | grep Volumes | sed 's/.*\/Volumes/\/Volumes/g'`
installer -pkg "$volume/$target_resource" -target /
hdiutil detach "$volume"
echo
echo "changed=yes comment='installed $dmg >> $volume/$target_resource'"
