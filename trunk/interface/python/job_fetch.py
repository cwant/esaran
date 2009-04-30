#!/usr/bin/env python
#
# $Id: wrap_qstat.py 73 2009-03-19 21:40:30Z cwant $
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

def main():
    import sys, os, optparse, PBSUtil

    config = PBSUtil.get_config()

    if (os.getenv("SSH_AGENT_RESPAWN")):
        # We have been respawned, load pickled options
        options = PBSUtil.load_program_args()
    else:
        usage = "%prog [options] JOBID.out\n\n" + \
            "JOBID.out is the job identifier file created " + \
            "when the job was submitted"

        parser = optparse.OptionParser(usage=usage)
        PBSUtil.add_misc_options(parser, config)

        (options_obj, args) = parser.parse_args()
        options = PBSUtil.obj_to_dict(options_obj)

        (options_obj, args) = parser.parse_args()
        if (len(args) > 1):
            sys.stderr.write("Too many files on the command line!\n")
            sys.exit(1)
        if (len(args) < 1):
            sys.stderr.write("Need a file on the command line!\n")
            sys.exit(1)

        (options_id, jobid, workdir) = PBSUtil.read_jobid_file(args[0])
        options = PBSUtil.obj_to_dict(options_obj)
        PBSUtil.merge_options(options, None, options_id)

    PBSUtil.validate_host(config, options, options["host"])

    PBSUtil.set_up_ssh(config, options)

    PBSUtil.job_fetch(options, workdir)

def add_status_options(parser, config):
    import os, optparse

    g = optparse.OptionGroup(parser, "Job status options")

    ### All
    g.add_option("-a", "--all", action="store_true",
                 dest="all", default=False,
                 help="Print status of all jobs in queue")


    ### Full
    g.add_option("-f", "--full", action="store_true",
                 dest="full", default=False,
                 help="Print full output about job(s)")

    ### Add options ########################
    
    parser.add_option_group(g)

main()

