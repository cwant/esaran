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

wrapper_title    = "Wrap PBS"
options_title    = "Program options"

program          = "executable"
metavar          = "PROGRAM [OPTIONS]"
gui_heading      = "Executable:"
gui_width        = 30
help             = help="The name and arguments of the program to run"

def main():
    import PBSUtil

    PBSUtil.do_wrapper(wrapper_title,
                       get_wrapper_cmdline
                       add_wrapper_options,
                       wrapper_gui_options)

def get_wrapper_cmdline(options, args):
    return options[program]

def add_wrapper_options(parser):
    import PBSUtil, optparse 

    g = optparse.OptionGroup(parser, options_title)

    ### Executable
    g.add_option("-x", "--exe", action="callback",
                 callback=PBSUtil.store_seen, type="string",
                 dest=program, metavar=metavar,
                 help=help)

    parser.add_option_group(g)

def wrapper_gui_options(subpanel, options):
    import PBSUtil
    title = options_title
    fields = []
    fields.append(PBSUtil.add_text_control(subpanel,
                                           program,
                                           gui_heading,
                                           width=gui_width))

    return (title, fields)

main()
