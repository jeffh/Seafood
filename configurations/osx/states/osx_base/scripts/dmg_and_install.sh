#!/bin/sh
export dmg=$1
export target_resource=$2

rm -rf $destination || true
volume=`hdiutil mount $dmg | grep Volumes | sed 's/.*\/Volumes/\/Volumes/g'`
installer -pkg "$volume/$target_resource" -target /
hdiutil detach "$volume"
echo
echo "changed=yes comment='$dmg >> $volume/$target_resource'"
