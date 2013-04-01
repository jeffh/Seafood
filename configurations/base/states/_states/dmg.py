import os

def install(name, source=None, cache_dir='', type='app'):
	__salt__['cp.cache_file'](source)
	__salt__['dmg.mount'](name)
