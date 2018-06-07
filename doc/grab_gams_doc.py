#!/usr/bin/env python

"""Read all gams files in ../model and generate a mirrored tree of rst
documentation files in ./source. All lines between triple-star comments (***)
are extracted.
"""

import errno
import fnmatch
import os

def files(match='*.gms', ext='rst'):
    """return all input files in ../model matching `match` and their associated
    output files with the given extension
    """
    pth = os.path.join('..', 'message_ix', 'model')
    ins = [os.path.join(d, f) \
           for d, _, files in os.walk(pth) \
           for f in fnmatch.filter(files, match)]

    outs = []
    for inf in ins:
        p, f = os.path.split(inf)
        outf = os.path.join('source', 'model', 
                            p[len(pth) + 1:], 
                            '{}.{}'.format(os.path.splitext(f)[0], ext))
        outs.append(outf)

    return ins, outs

def read_docs(lines):
    """Pull out all documentation lines"""
    ret = []
    on = False
    for line in lines:
        if line.lstrip().startswith('***'):
            if on: # just finished a block, add a new line
                ret.append('\n')
            on = not on
        elif on:
            base = "*".join(line.split('*')[1:])[1:]
            base = base.rstrip() # get rid of windows carriage return
            ret.append('{}\n'.format(base))
    return ret

def mkdir(d):
    """make a directory if it doesn't already exist"""
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def main():
    print('Generating GAMS documentation')
    ins, outs = files()
    for inf, outf in zip(ins, outs):
        print('Reading {}'.format(inf))
        with open(inf, 'r') as f:
            lines = f.readlines()
        doc_lines = read_docs(lines)
        
        if len(doc_lines) > 0:
            print('Writing {}'.format(outf))
            mkdir(os.path.dirname(outf))
            with open(outf, 'w') as f:
                f.writelines(doc_lines)
        else:
            print('No docs found, moving on')
    print('Finished Generating GAMS documentation')

def test():
    """Full unit tests are a bit much for the nonce.."""    
    lines = [
        ' ** foo bar\n', 
        '  ***\n',
        '   * bz baz2\n',
        '   * bz * baz2\n',
        '   *** bz baz3\n',
        "***fig newton\n",
    ]

    obs = read_docs(lines)
    exp =  [
        'bz baz2\n',
        'bz * baz2\n',
        '\n',
    ]     

    try:
        assert(obs == exp)
    except AssertionError:
        print('Assert failed')
        print(exp)
        print(obs)
       
if __name__ == "__main__":
    test()
    main()
    
