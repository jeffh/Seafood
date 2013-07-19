def read(path='/etc/environment'):
    """Reads the environmental variables set globally (/etc/environment)

    Returns an array of tuples (name, value).
    You can use dict to easily convert the result into a dictionary:

        result = dict(read_environment())
        result['PATH'] # => returns bin path
    """
    result = []
    with open(path, 'r') as handle:
        for line in handle.read().strip().splitlines():
            name, value = tuple(line.split('=', 1))
            if value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            result.append((name, value))
    return result


def write(variables, path='/etc/environment'):
    """Writes the environmental variables set on the system.

    Accepts any form of array of tuples (name, value).
    To convert a dictionary to this form. Call items() on it.
    """
    with open(path, 'w') as handle:
        for name, value in list(variables):
            handle.write('{0}="{1}"\n'.format(name, value.replace('\\', '\\\\').replace('"', '\\"')))

def set_variable(name, value, path='/etc/environment'):
    """Sets a variable's value to a given value.

    Returns True if the variable was added or updated.
    Returns False if nothing was changed (ie - the value was already set properly)
    """
    variables = dict(read(path))
    was_changed = (name not in variables or variables[name] != value)
    variables[name] = value
    write(variables.items(), path)
    return was_changed

def unset_variable(name, path='/etc/environment'):
    """Unsets a variable from the environment.

    Returns True if the variable was removed.
    Returns False if the variable was already removed.
    """
    variables = dict(read(path))
    was_deleted = (name in variables)
    del variables[name]
    write(variables.items(), path)
    return was_deleted

