#!/usr/bin/env python

def main():
    import PBSUtil

    PBSUtil.do_wrapper("Wrap PBS", add_wrapper_options,
                       wrapper_gui_options,
                       get_wrapper_cmdline)

def add_wrapper_options(parser):
    from optparse import OptionGroup

    g = OptionGroup(parser, "Program options")

    ### Executable
    g.add_option("-x", "--exe", action="store", type="string",
                 dest="executable", metavar="PROGRAM",
                 help="The name and arguments of the program to run")

    parser.add_option_group(g)

def get_wrapper_cmdline(options, args):
    return options["executable"]

def wrapper_gui_options(subpanel, options):
    import PBSUtil
    title = "Program options"
    fields = []
    fields.append(PBSUtil.add_text_control(subpanel,
                                           "executable",
                                           "Executable:",
                                           options))

    return (title, fields)

main()
