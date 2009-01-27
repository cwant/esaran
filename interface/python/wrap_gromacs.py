#!/usr/bin/env python


def main():
    import PBSUtil

    PBSUtil.do_wrapper("Wrap Gromacs", add_gromacs_options,
                       gromacs_gui_options, get_gromacs_cmdline)

def add_gromacs_options(parser):
    from optparse import OptionGroup

    g = OptionGroup(parser, "Gromacs options")

    ### Executable
    g.add_option("-a", "--args", action="store", type="string",
                 dest="mdrun_args", metavar="OPTIONS",
                 help="Arguments to be passed to the mdrun program")

    parser.add_option_group(g)

def get_gromacs_cmdline(options, args):
    executable = "mdrun " + options["mdrun_args"]

    return """\
module load gromacs
%(executable)s
""" % (locals())

def gromacs_gui_options(subpanel, options):
    import PBSUtil
    title = "Gromacs options"
    fields = []
    fields.append(PBSUtil.add_text_control(subpanel,
                                           "mdrun_args",
                                           "mdrun arguments:",
                                           options))

    return (title, fields)

main()
