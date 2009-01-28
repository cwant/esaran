#!/usr/bin/env python

def main():
    import PBSUtil

    PBSUtil.do_wrapper("Wrap GAMESS", add_gamess_options,
                       gamess_gui_options, get_gamess_cmdline)

def add_gamess_options(parser):
    from optparse import OptionGroup

    g = OptionGroup(parser, "GAMESS options")

    ### Executable
    g.add_option("-a", "--args", action="store", type="string",
                 dest="rungms_args", metavar="OPTIONS",
                 help="Arguments to be passed to the rungms program")

    parser.add_option_group(g)

def get_gamess_cmdline(options, args):
    executable = "rungms " + options["rungms_args"]

    return """\
module load gamess
%(executable)s
""" % (locals())

def gamess_gui_options(subpanel, options):
    import PBSUtil
    title = "Gamess options"
    fields = []
    fields.append(PBSUtil.add_text_control(subpanel,
                                           "rungms_args",
                                           "rungms arguments:",
                                           width=30))

    return (title, fields)

main()
