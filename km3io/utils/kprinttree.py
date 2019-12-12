#!/usr/bin/env python
# coding=utf-8
# Filename: kprinttree.py
# Author: Tamas Gal <tgal@km3net.de>
"""
Print the available ROOT trees.

Usage:
    kprinttree.py FILENAME
    kprinttree.py (-h | --help)

Options:
    -h --help   Show this screen.

"""
import uproot

def print_tree(filename):
    f = uproot.open(filename)
    for key, ttree in f.items():
        try:
            print("{} : {}".format(key.decode(), len(ttree)))
        except TypeError:
            print("{}".format(key.decode()))


def main():
    from docopt import docopt
    args = docopt(__doc__)

    print_tree(args['FILENAME'])


if __name__ == '__main__':
    main()

    	

