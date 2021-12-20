def merge_bindings(bindings1, bindings2):
    if bindings1 is None or bindings2 is None:
        return None

    bindings = dict()

    bindings = {**bindings1}

    for variable, value in bindings2.items():
        if variable in bindings:
            other = bindings[variable]
            sub = other.match(value)

            if sub is not None:
                for var, val in sub.items():
                    bindings[var] = val
            else:
                return None
        else:
            bindings[variable] = value

    return bindings