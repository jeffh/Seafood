import os

class Configuration(object):
    "API for accessing the configurations directory"
    def __init__(self, names=()):
        self.names = tuple(names)

    def find_file(self, relpath):
        for name in reversed(self.names):
            filepath = os.path.relpath(os.path.join('configurations', name, relpath))
            if os.path.exists(filepath):
                return filepath
        raise TypeError('Could not find {0} to upload in any configuration!'.format(repr(filename)))

class Settings(object):
    "API for accessing the config.yml file"
    def __init__(self, data, platform='linux'):
        self.data = data
        self.platform = platform

    @classmethod
    def from_yaml(cls, filepath):
        import yaml
        with open(filepath) as handle:
            return cls(yaml.safe_load(handle.read()))

    @staticmethod
    def from_json(cls, filepath):
        import json
        with open(filepath) as handle:
            return cls(json.loads(handle.read()))

    def as_platform(self, platform):
        return self.__class__(self.data, platform)

    def bootstrap_for_operating_system(self, key):
        result = {
            'files': (),
        }
        result.update(self.data['bootstrap']['operating-systems'][key])
        return result

    @property
    def master_minion_keys_dir(self):
        return self.data['salt-master']['minion-keys-dir']

    @property
    def minion_keys_dir(self):
        return self.data['salt-minion']['keys-dir']

    @property
    def bootstrap_scripts(self):
        return tuple(self.data['bootstrap']['scripts'].get(self.platform, ()))

    @property
    def bootstrap_files(self):
        return tuple(self.data['bootstrap']['files'].get(self.platform, ()))

    @property
    def os_detectors(self):
        return tuple(self.data['bootstrap']['os-detectors'])

    @property
    def servers(self):
        data = {}
        for name, server in self.data['servers'].items():
            data[name] = {}
            data[name].update(server)
            data[name]['name'] = name
        return data

    @property
    def salt_data_dir(self):
        return self.data['salt-master']['data-dir']

    @property
    def salt_master_roles(self):
        return tuple(self.data['salt-master']['base-roles'])

    @property
    def salt_minion_roles(self):
        return tuple(self.data['salt-minion']['base-roles'])

    def roles_for_server(self, server_name):
        return tuple(self.servers[server_name].get('roles', ()))

    def configuration_for_server(self, server_name):
        return Configuration(tuple(self.servers[server_name].get('configurations', ())))
