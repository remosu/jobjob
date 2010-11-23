"""..."""

def copy_input(src, dst, input_vars):
    """..."""
    with open(dst, 'w') as dst_input:
        for line in open(src):
            values = line.split()
            if values and values[0] in input_vars:
                var, _, comment = line.rpartition(values[1])
                line = var + str(input_vars[values[0]]) + comment
                del input_vars[values[0]]
            dst_input.write(line)
        dst_input.write('\n#----\n')
        for var, value in input_vars.items():
            dst_input.write('%s %s\n' % (var, value))
