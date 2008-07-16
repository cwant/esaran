#!/usr/bin/perl

use Getopt::Long;
Getopt::Long::Configure("bundling");

GetOptions(
	"name|N=s"	=> \$name,
	"pvmem|m=s"	=> \$pvmem,
	"nodes|n=i"	=> \$nodes,
	"ppn|p=i"	=> \$ppn,
	"walltime|w=s"	=> \$walltime,
	"notify|E=s"	=> \$notify,
	"email|e=s"	=> \$email,
	"dir|d=s"	=> \$dir,
	"exe|x=s"	=> \$executable,
	"help|h"	=> \$help);

arg_error("")				if $help;
arg_error("-x or --executable required")	if !$executable;
arg_error("-e or --email required") if !$email;
$name = "job1"		if !$name;
$pvmem = "512mb"	if !$pvmem;
$nodes = 1		if !$nodes;
$ppn = 1		if !$ppn;
$walltime = "24:00:00"	if !$walltime;
$notify = "bea"		if !$notify;
$dir = "\$PBS_O_WORKDIR" if !$dir;

open PBS_SCRIPT, ">pbs_script.pbs";
print PBS_SCRIPT "#!/bin/bash -l\n";
print PBS_SCRIPT "#PBS -N $name \n";
print PBS_SCRIPT "#PBS -S /bin/bash\n";
print PBS_SCRIPT "#PBS -l pvmem=$pvmem \n";
print PBS_SCRIPT "#PBS -l nodes=$nodes:ppn=$ppn\n";
print PBS_SCRIPT "#PBS -l walltime=$walltime\n";
print PBS_SCRIPT "#PBS -m $notify\n";
print PBS_SCRIPT "#PBS -M $email\n";
print PBS_SCRIPT "cd $dir\n";
print PBS_SCRIPT "$executable\n";
print PBS_SCRIPT "ssh sjw1\@10.0.6.1 \'(echo \"Here is your output\"; cd $dir; tar -cvvf output.tar pi.out pi.err; uuencode $dir/output.tar output.tar) | mail -s \"Job $name is complete\" sjw1\@ualberta.ca'\n";
close PBS_SCRIPT;

system("tar -cvvf script.tar *");
system("scp script.tar sjw1\@cluster.srv.ualberta.ca:/scratch/sjw1/pbs");
system("ssh cluster.srv.ualberta.ca -l sjw1 \"cd /scratch/sjw1/pbs/\n tar -xvvf script.tar\n qsub pbs_script.pbs\n\"");

sub arg_error {
	###Display errors in arguments and usage
	my ($message) = @_;
	if ($message ne "") {
		print "There is an incorrect parameter\n\n";
		print "*** $message ***\n"
	}

	print << "EOUSAGE";

Description: This program is used to create and submit .pbs files.

Usage: perl wrap_pbs.pl [options]

Options:
	-x or --executable (required)
		The name of the program you want to run with the required arguments for that program

	-e or --email (required)
		The email address for notifying the user of errors and completion of the program

	-N or --name (optional, default job1)
		The name of the job that is submitted to the cluster

	-m or --pvmem (optional, default = 512mb)
		The size of memory you required to a max of 30gb

	-n or --nodes (optional, default = 1)
		The number of nodes you required to a max of 29

	-p or --ppn (optional, default = 1)
		The number of processors per node required to a max of 4

	-w or --walltime (optional, default = 24:00:00
		The approximate time required to run your program to a max of 168:00:00

	-d or --dir (optional, default = \$PBS_O_WORKDIR)
		The directory where your files are located.  Default is the directory from which this script was run.

Example:
	perl wrap_pbs.pl -x "./pi<pi.input" -e sjw1\@ualberta.ca -N myJob14 -m 2gb -n 2 -p 2 -w 48:00:00
		---runs program pi with input file pi.input with name myJob14, 2gb of memory on 2 nodes with 2 processors each and a walltime of 48 hours

EOUSAGE

exit 1;

}



	
