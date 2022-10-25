#!/usr/bin/env python

'''Convert a C3D file to CSV (text) format.'''

import argparse

from file_parser import C3dFileParser

parser = argparse.ArgumentParser(description='Convert a C3D file to CSV (text) format.')
parser.add_argument('input', default='-', metavar='FILE', nargs='+', help='process data from this input FILE')


def convert(filename):
    file_parser = C3dFileParser(filename)
    test = file_parser.get_data()
    print(test)


def main():
    args = parser.parse_args()
    for filename in args.input:
        convert(filename)


if __name__ == '__main__':
    main()
