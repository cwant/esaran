#!/usr/bin/perl

# This script creates a .pbs file and sends it to the cluster to be run.
# pi is a C program that estimates pi based on the number of intervals provided in pi.input.
# It makes assumptions about the order of the command line arguments and contains no parsing.

# Run using:
#
#   perl wrap_pi_no_tar.pl pvmem=2gb nodes=1:ppn=1 walltime=00:01:00 pi pi.input

$numArgs = $#ARGV + 1;

open PBS_SCRIPT, ">pbs_script.pbs";

print PBS_SCRIPT "#!/bin/bash -l\n";

print PBS_SCRIPT "#PBS -N job1\n";

print PBS_SCRIPT "#PBS -S /bin/bash\n";

print PBS_SCRIPT "#PBS -l $ARGV[0]\n";

print PBS_SCRIPT "#PBS -l $ARGV[1]\n";

print PBS_SCRIPT "#PBS -l $ARGV[2]\n";

print PBS_SCRIPT "#PBS -m bea\n";

print PBS_SCRIPT "#PBS -M sjw1\@ualberta.ca\n";

print PBS_SCRIPT "cd \$PBS_O_WORKDIR\n";

print PBS_SCRIPT "./$ARGV[3]<$ARGV[4]\n";

close PBS_SCRIPT;

system("scp pbs_script.pbs sjw1\@cluster.srv.ualberta.ca:/scratch/sjw1/cluster/");

system("ssh cluster.srv.ualberta.ca -l sjw1 \"cd /scratch/sjw1/cluster/\n qsub pbs_script.pbs\n\""); 
