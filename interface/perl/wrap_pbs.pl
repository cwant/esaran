#!/usr/bin/perl

# This script creates a .pbs file tars the pbs and input file and sends it to the cluster to be run.
# pi is a c program that estimates pi based on the number of intervals which is provided in pi.input
# It makes assumptions about the order of the command line arguments

# run using perl post_tar.pl pvmem=2gb nodes=1:ppn=1 walltime=00:01:00 pi pi.input


#set up defaults
$name = "job1";
$pvmem = "512mb";
$nodes = "1";
$ppn = "1";
$walltime = "24:00:00";
$notify = "bea";
$email = ""; #how to pull out user's email??
$dir = "\$PBS_O_WORKDIR";
$executable = "";


for ($argNum = 0; $argNum <=$#ARGV; $argNum++) {
	if ($ARGV[$argNum] eq "-N") {$name = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-m") {$pvmem = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-n") {$nodes = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-p") {$ppn = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-w") {$walltime = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-E") {$notify = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-e") {$email = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-d") {$dir = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-x") {$executable = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] =~ m/-/) { print ("You have entered an incorrect flag\n")}
}


open PBS_SCRIPT, ">pbs_script.pbs";
print PBS_SCRIPT "#!/bin/bash\n";
print PBS_SCRIPT "#PBS -N $name \n";
print PBS_SCRIPT "#PBS -S /bin/bash\n";
print PBS_SCRIPT "#PBS -l pvmem=$pvmem \n";
print PBS_SCRIPT "#PBS -l nodes=$nodes:ppn=$ppn\n";
print PBS_SCRIPT "#PBS -l walltime=$walltime\n";
print PBS_SCRIPT "#PBS -m $notify\n";
print PBS_SCRIPT "#PBS -M sjw1\@ualberta.ca\n";
print PBS_SCRIPT "cd $dir\n";
print PBS_SCRIPT "$executable\n";
close PBS_SCRIPT;

system("tar -cvvf script.tar *");
system("scp script.tar sjw1\@cluster.srv.ualberta.ca:/scratch/sjw1/pbs");
system("ssh cluster.srv.ualberta.ca -l sjw1 \"cd /scratch/sjw1/pbs/\n tar -xvvf script.tar\n qsub pbs_script.pbs\n\"");


	
