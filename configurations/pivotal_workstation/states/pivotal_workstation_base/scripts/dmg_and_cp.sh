#!/bin/sh
export dmg=$1
export target_resource=$2
export destination=$3

rm -rf $destination || true
volume=`hdiutil mount $dmg | grep Volumes | sed 's/.*\/Volumes/\/Volumes/g'`
cp -R "$volume/$target_resource" "$destination"
hdiutil detach "$volume"
echo
echo "changed=yes comment='$dmg >> $volume/$target_resource >> $destination'"
