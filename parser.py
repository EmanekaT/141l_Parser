import sys
import os.path

def twos_comp(bits, value):
    """compute the 2's complement of int value val"""
    if value < 0:
    	value = ( 1<<bits ) + value
    formatstring = '{:0%ib}' % bits
    return formatstring.format(value)

args = sys.argv
assert (len(args) == 2), 'wrong number of input'
fname = args[1]
assert (os.path.isfile(fname)), 'File does not exist'

jump_map = {'sp1': -1, 'sp2': 0, 'sp3': 1, 'sp4': 2}
rtype = {
            'and': '0000',
            'xor': '0001',
            'add': '0010',
            'mov': '0111',
            'sw': '0100',
            'lw': '0101',
            'sll': '0011',
            'ceq': '0110',
            'clt': '0110',
         }
itype = {
            'j':   '10',
            'li':  '11',
        }
regs = {"r0": '00', "r1": '01', "r2": '10', "r3": '11', 'rt': '00'}

def findLabels():
    labels = {'sp1': -1, 'sp2': 0, 'sp3': 1, 'sp4': 2}
    with open(fname,'r') as fp:
        dirty_lines = fp.readlines()
        line_num = 0
        for dirty_line in dirty_lines:
            # remove commands
            line = dirty_line.replace('#','//').replace('\t',' ').strip().split('//', 1)[0]
            if line.isspace() or line == '':
                continue
            #parse
            cmds = line.replace(',', ' ').split(' ')
            if cmds[0][-1] == ':':
                assert (cmds[0][:-1] not in labels), 'Error: duplicate labels \
                        same line as commands at line:{}'.format(line_num)
                assert (len(cmds) == 1), 'Error: label cannot be in the \
                        same line as commands at line:{}'.format(line_num)
                labels[cmds[0][:-1].lower()] = line_num
            else:
                line_num += 1
    return labels
labels = findLabels()

with open(fname,'r') as fp, open(fname+'.bin', 'w') as of:
    dirty_lines = fp.readlines()
    line_num = 0
    for dirty_line in dirty_lines:
        # remove commands
        line = dirty_line.replace('#','//').replace('\t',' ').strip().split('//', 1)[0]
        if line.isspace() or line == '':
            continue
        #parse
        cmds = list(filter(None, line.replace(',', ' ').split(' ')))
        sys.stderr.write(str(cmds) + str(line_num)+ '\n')
        if cmds[0].lower() in rtype.keys():
            op = cmds[0].lower()
            r1 = cmds[1].lower()
            r2 = cmds[2].lower()
            last_bit = '0'
            if r2== 'rt' or r1 == 'rt' or op == 'ceq' or op == 'clt':
                last_bit = '1'
            of.write(rtype[op]+ regs[r1]+ regs[r2]+last_bit + '\n')
            sys.stderr.write(rtype[op]+ regs[r1]+ regs[r2]+last_bit + '\n')
        elif cmds[0].lower() == 'li':
            op = cmds[0].lower()
            num = int(cmds[1])
            if cmds[1][0] == '-':
                num = -int(cmds[1][1:])
            r1 = twos_comp(7, num)
            of.write(itype[op]+ r1 + '\n')
            sys.stderr.write(itype[op]+ r1 + '\n')
        elif cmds[0].lower() == 'j':
            op = cmds[0].lower()
            num = int(labels[cmds[1].lower()]) - line_num
            if cmds[1].lower() in jump_map.keys():
                num = jump_map[cmds[1].lower()]
            assert ((num <= 63 and num >= -64) or cmds[1].lower() in jump_map.keys()), "Label out of range {}".format(num)
            r1 = twos_comp(7, num)
            of.write(itype[op]+ r1 + '\n')
            sys.stderr.write(itype[op]+ r1 + '\n')
        elif cmds[0][-1] == ':':
            continue
        else:
            raise Exception('Error: incorrect syntax at line:{}'.format(line_num))
        line_num += 1





