"""
Handles the mounting and unmounting of dmg files.
"""

def mount(name, mountpoint=None, mountroot=None):
	args = ['hdiutil', 'attach', name]
	if mountpoint:
		args.extend(['-mountpoint', mountpoint])
	if mountroot:
		args.extend(['-mountroot', mountroot])

	return __salt__['cmd.run'](' '.join(args))

def unmount(name, force=False):
	args = ['hdiutil', 'detach', name]
	if force:
		args.append('-f')

	return __salt__['cmd.run'](' '.join(args)) 
