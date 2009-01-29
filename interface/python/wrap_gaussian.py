#!/usr/bin/env python
#
# $Id$
#
# Copyright (c) 2009, Chris Want, Research Support Group,
# AICT, University of Alberta. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
# 1) Redistributions of source code must retain the above copyright 
#    notice, this list of conditions and the following disclaimer.
# 2) Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in the 
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
# THE POSSIBILITY OF SUCH DAMAGE.
#
# Contributors: Chris Want (University of Alberta),
#

prog_title       = "Wrap Gaussian"
options_title    = "Gaussian options"
prog_name        = "g03"
run_string       = """\
module load gaussian
%(executable)s
"""

args_name        = prog_name + "_args"
gui_args_heading = prog_name +" arguments:"
gui_width        = 30
args_help        = "Arguments to be passed to the %s program" % (prog_name)

def main():
    import PBSUtil

    PBSUtil.do_wrapper(prog_title, add_program_options,
                       program_gui_options, get_program_cmdline)

def add_program_options(parser):
    from optparse import OptionGroup

    g = OptionGroup(parser, options_title)

    ### Executable
    g.add_option("-a", "--args", action="store", type="string",
                 dest=args_name, metavar="OPTIONS",
                 help=args_help)

    parser.add_option_group(g)

def get_program_cmdline(options, args):
    executable = "%s %s" % (prog_name, options[args_name])

    return run_string % (locals())

def program_gui_options(subpanel, options):
    import PBSUtil
    title = options_title
    fields = []
    fields.append(PBSUtil.add_text_control(subpanel,
                                           args_name,
                                           gui_args_heading,
                                           width=gui_width))

    return (title, fields)

main()
