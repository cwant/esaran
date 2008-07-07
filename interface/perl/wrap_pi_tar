#!/usr/bin/perl
# This script creates a .pbs file, tars the pbs and input file and sends it to the cluster to be run. # pi is a C program that estimates pi based on the number of intervals which is provided in pi.input # It makes assumptions about the order of the command line arguments and has no parsing

# run using perl wrap_pi_tar.pl pvmem=2gb nodes=1:ppn=1 walltime=00:01:00 pi pi.input


$numArgs = $#ARGV + 1;

open PBS_SCRIPT, ”>test/pbs_script.pbs”;

print PBS_SCRIPT ”#!/bin/bash -l\n”;

print PBS_SCRIPT ”#PBS -N job1\n”;

print PBS_SCRIPT ”#PBS -S /bin/bash\n”;

print PBS_SCRIPT ”#PBS -l $ARGV[0]\n”;

print PBS_SCRIPT ”#PBS -l $ARGV[1]\n”;

print PBS_SCRIPT ”#PBS -l $ARGV[2]\n”;

print PBS_SCRIPT ”#PBS -m bea\n”;

print PBS_SCRIPT ”#PBS -M sjw1\@ualberta.ca\n”;

print PBS_SCRIPT “cd \$PBS_O_WORKDIR\n”;

print PBS_SCRIPT ”./$ARGV[3]<$ARGV[4]\n”;

close PBS_SCRIPT;

system(“cd ~/perl/test/\n tar -cvvf script.tar *”);

system(“scp ~/perl/test/script.tar sjw1\@cluster.srv.ualberta.ca:/scratch/sjw1/testing/”);

system(“ssh cluster.srv.ualberta.ca -l sjw1 \”cd /scratch/sjw1/testing/\n tar -xvvf script.tar\n qsub pbs_script.pbs\n\””);
