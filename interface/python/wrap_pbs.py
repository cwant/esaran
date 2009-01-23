#!/usr/bin/env python

def main():
    import PBSUtil

    PBSUtil.do_wrapper(add_wrapper_options, get_wrapper_cmdline)

def add_wrapper_options(parser):
    from optparse import OptionGroup

    g = OptionGroup(parser, "Program options")

    ### Executable
    g.add_option("-x", "--exe", action="store", type="string",
                 dest="executable", metavar="PROGRAM",
                 help="The name and arguments of the program to run")

    parser.add_option_group(g)

def get_wrapper_cmdline(options, args):
    return options.executable

main()
