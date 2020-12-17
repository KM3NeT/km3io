#!/usr/bin/env python
# coding=utf-8
# Filename: kprinttree.py
# Author: Tamas Gal <tgal@km3net.de>
"""
Print the available ROOT trees.

Usage:
    KPrintTree -f FILENAME
    KPrintTree (-h | --help)

Options:
    -f FILENAME  The file to print (;
    -h --help    Show this screen.

"""
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import uproot3


def print_tree(filename):
    f = uproot3.open(filename)
    for key in f.keys():
        try:
            print("{:<30} : {:>9} items".format(key.decode(), len(f[key])))
        except (TypeError, KeyError):
            print("{}".format(key.decode()))
        except NotImplementedError:
            print("{} (TStreamerSTL)".format(key.decode()))


def main():
    from docopt import docopt

    args = docopt(__doc__)

    print_tree(args["-f"])


if __name__ == "__main__":
    main()
