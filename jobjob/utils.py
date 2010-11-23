


def copy_input(src, dst, vars):
    """..."""
    with open(dst, 'w') as dst_input:
        for line in open(src):
            values = line.split()
            if values and vars.has_key(values[0]):
                var, old_value, comment = line.rpartition(values[1])
                line = var + str(vars[values[0]]) + comment
                del vars[values[0]]
            dst_input.write(line)
        dst_input.write('\n#----\n')
        for var, value in vars.items():
            dst_input.write('%s %s\n'%(var, value))
