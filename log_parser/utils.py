def parse_arg_val(line, key):
    args = line.split()

    for arg in args:
        parts = arg.split(":")
        if parts[0] == key:
            return parts[1].strip('"')
