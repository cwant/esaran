#!/usr/bin/perl

use Getopt::Long;
Getopt::Long::Configure("bundling");

GetOptions(
	"requirements|R=s"	=> \$requirements,
	"email|e=s"		=> \$email,
	"host|H=s"		=> \$host,
	"user|u=s"		=> \$user,
	"dir|d=s"		=> \$dir,
	"exe|x=s"		=> \$executable,
	"output|o=s"		=> \$out_put,
	"error|err=s"		=> \$error,
	"log|l=s"		=> \$log,
	"name|n=s"		=> \$name,
	"help|h"		=> \$help);

arg_error("")				if $help;
arg_error("-x or --executable required")	if !$executable;
arg_error("-e or --email required") if !$email;
arg_error("-u or --user required") if !$user;

$CHMOD = "chmod o+r";
$requirements = ""	if !$requirements;
$name = "job1"		if !$name;
$out_put = "$name.out"	if !$out_put;
$error = "$name.err"	if !$error;
$log = "$name.log"	if !$log;
$host = "cluster.srv.ualberta.ca" if !$host;
$dir = "/scratch/$user/$name_$$.tmp" if !$dir;  #what should this be??? /scratch/user/$name??

open CONDOR_SCRIPT, ">condor_script.sub";

# ---- Start Condor Script --------------------------------------
print CONDOR_SCRIPT << "ENDPERL";
universe = vanilla
requirements = $requirements
notify_user = $email
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
executable = $executable
output = $out_put
error = $error
log = $log
queue
ENDPERL
# ---- END Condor Script ----------------------------------

close CONDOR_SCRIPT;

system("tar -cvvf $name.$$.tar *");
system("ssh $host -l $user \"mkdir -p $dir; $CHMOD $dir\"");
system("scp $name.$$.tar $user\@$host:$dir");
#system("rm -f $name.$$.tar condor_script.sub");
system("ssh $host -l $user \"cd $dir\n tar -xvvf $name.$$.tar\ncondor_submit condor_script.sub\n\"");

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
	perl wrap_pbs.pl -x "./pi<pi.input" -e sjw1\@ualberta.ca -N myJob14 -m 2gb -n 2 -p 2 -w 48:00:00
		---runs program pi with input file pi.input with name myJob14, 2gb of memory on 2 nodes with 2 processors each and a walltime of 48 hours

EOUSAGE

exit 1;

}
