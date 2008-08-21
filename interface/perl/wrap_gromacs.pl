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
	"host|H=s"	=> \$host,
	"user|u=s"	=> \$user,
	"dir|d=s"	=> \$dir,
	"args|a=s"	=> \$gro_args,
	"help|h"	=> \$help);

arg_error("")				if $help;
arg_error("-a or --args required")	if !$gro_args;
arg_error("-e or --email required") if !$email;
arg_error("-u or --user required") if !$user;

$name = "job1"		if !$name;
$pvmem = "512mb"	if !$pvmem;
$nodes = 1		if !$nodes;
$ppn = 1		if !$ppn;
$host = "cluster.srv.ualberta.ca" if !$host;
$walltime = "24:00:00" 	if !$walltime;
$notify = "bea"		if !$notify;
$dir = "/scratch/$user/$name_$$.tmp" if !$dir;


system("./wrap_pbs.pl -u $user -e $email -x \"module load gromacs;mdrun $gro_args\" -N $name -m $pvmem -n $nodes -p $ppn -w $walltime -E $notify -H $host");

sub arg_error {
	###Display errors in arguments and usage
	my ($message) = @_;
	if ($message ne "") {
		print "There is an incorrect parameter\n\n";
		print "*** $message ***\n"
	}

	print << "EOUSAGE";

Description: This program is used to create and submit gromacs jobs.

Usage: ./wrap_gromacs.pl [options]

Options:
	-a or --args (required)
		The required or usual arguments for mdrun

	-e or --email (required)
		The email address for notifying the user of errors and completion of the program

	-u or --user (required)
		The user id used to login to the HPC resource

	-N or --name (optional, default job1)
		The name of the job that is submitted to the HPC resource

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
	wrap_gromacs.pl -a "-s topol.tpr" -e sjw1\@ualberta.ca -N myJob14 -m 2gb -n 2 -p 2 -w 48:00:00
		---runs mdrun with input file topol.tpr with name myJob14, 2gb of memory on 2 nodes with 2 processors each and a walltime of 48 hours

EOUSAGE

exit 1;

}



	
