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
	"exe|x=s"	=> \$executable,
	"help|h"	=> \$help,
	"key|k=s"	=> \$key);

arg_error("")				if $help;
arg_error("-x or --executable required")	if !$executable;
arg_error("-e or --email required") if !$email;
arg_error("-u or --user required") if !$user;

$CHMOD = "chmod o+r";
$name = "job1"		if !$name;
$pvmem = "512mb"	if !$pvmem;
$nodes = 1		if !$nodes;
$ppn = 1		if !$ppn;
$host = "cluster.srv.ualberta.ca" if !$host;
$walltime = "24:00:00"	if !$walltime;
$notify = "bea"		if !$notify;
$dir = "/scratch/$user/$name_$$.tmp" if !$dir;  #what should this be??? /scratch/user/$name??
$key = ""		if !$key;

$ssh_auth = $ENV{'SSH_AUTH_SOCK'};
if(!$ssh_auth){  #the case where wrap_pbs hasn't been called from another script - does this ever happen???
	system("ssh-agent perl wrap_pbs.pl -u $user -e $email -x \"module load gromacs;mdrun $gro_args\" -N $name -m $pvmem -n $nodes -p $ppn -w $walltime -E $notify -H $host -d $dir");
	exit;
}
else {
#now set up the mail portion of the script
# Get the mail command for this OS
use POSIX qw(uname);
($systype) = (POSIX::uname())[0];
$mail_command = "/usr/sbin/sendmail";
if ($systype eq "IRIX64") {
	$mail_command = "/usr/lib/sendmail";
}

#Configure mail/file
$mail_host = "10.0.6.1";
$mail_user = $user;
$body = "Here is the output from \${JOBNAME}.";
$to = $email;
$file = "$dir/\${OUTPUT}";
$output = "\${OUTPUT}";
$subject = '${SUBJECT}';
$buf = '$buf';
$webserver_site = "https://sciviz.nic.ualberta.ca/~cwant/hpc_web";
$webserver_address = "cwant\@sciviz.nic.ualberta.ca";
$webserver_subject = "HPC output download ready";

open PBS_SCRIPT, ">pbs_script.pbs";

# ---- Start PBS Script --------------------------------------
print PBS_SCRIPT << "ENDPERL";
#!/bin/bash -l
#PBS -N $name
#PBS -S /bin/bash
#PBS -l pvmem=$pvmem
#PBS -l nodes=$nodes:ppn=$ppn
#PBS -l walltime=$walltime
#PBS -m $notify
#PBS -M $email
cd $dir
$executable
if [ "a\${PBS_JOBID}" != "a" ]
then
  OUTPUT="${user}_\${PBS_JOBID}.zip"
  JOBNAME="PBS job \${PBS_JOBID}"
  SUBJECT="Results from job $name (\${JOBNAME})"
else
  OUTPUT="${user}_${name}.zip"
  JOBNAME="the job $name"
  SUBJECT="Results from job $name"
fi
zip -r \${OUTPUT} * > /dev/null
$CHMOD \${OUTPUT}
ZIPSIZE=`wc -c \${OUTPUT} | cut -d " " -f 1`
if [ \$ZIPSIZE -lt 5000000 ]
then
# zip file smaller then 5MB, mail to user
(
(cat <<EOF_MAIL
To: $email
Subject: $subject
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="-q1w2e3r4t5"

---q1w2e3r4t5
Content-Type: text/plain

$body
---q1w2e3r4t5
Content-Type: application; name=$output
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="$output"

EOF_MAIL
);
perl -e "
use MIME::Base64 qw(encode_base64);
open(FILE, '$file') or die '$!';
while (read(FILE, \\\$buf, 60*57)) {
	print encode_base64(\\\$buf);
}";
echo '---q1w2e3r4t5--';
) | ssh $mail_user\@$mail_host '$mail_command -t'
else
# zip file too big, signal webserver to pick it up
(cat <<EOF_MAIL
To: ${webserver_address}
Subject: ${webserver_subject}
MIME-Version: 1.0
Content-Type: text/plain

Path: $dir/$output
Host: $host
Username: $user
EOF_MAIL
) | ssh $mail_user\@$mail_host '$mail_command -t'
# mail user where to get the file
(cat <<EOF_MAIL
To: $email
Subject: $subject
MIME-Version: 1.0
Content-Type: text/plain

 The output from \${JOBNAME} is too large to mail (\${ZIPSIZE} bytes).

 You can obtain your file at:

   ${webserver_site}
EOF_MAIL
) | ssh $mail_user\@$mail_host '$mail_command -t'

fi
ENDPERL
# ---- END PBS Script ----------------------------------

#print PBS_SCRIPT "cd ..\n";
#print PBS_SCRIPT "cp -r $dir /tmp/$user\n";
#print PBS_SCRIPT "rm -rf $dir\n";

close PBS_SCRIPT;

$needkey = 0;
$exitcode = system("ssh-add -L > /dev/null");

if ($exitcode != 0) { #case where there are no keys
	$needkey=1;
}
else{ #case where there are keys
	system("ssh -o NumberOfPasswordPrompts=0 $host -l $user date"); #test if right key for the $host
	if ($? != 0) { #not the right key $host
		$needkey = 1;
	}
}
if ($needkey) {

	system("ssh-add $key > /dev/null");

	# Try again to see if the key worked
	system("ssh -o NumberOfPasswordPrompts=0 $host -l $user date"); #test if right key for the $host
	if ($? != 0) { #not the right key $host
		print "Could not use your key to submit job!\n";
	}
}

system("tar -cvvf $name.$$.tar *");
system("ssh $host -l $user \"mkdir -p $dir; $CHMOD $dir\"");
system("scp $name.$$.tar $user\@$host:$dir");
system("rm -f $name.$$.tar pbs_script.pbs");
system("ssh $host -l $user \"cd $dir\n tar -xvvf $name.$$.tar\nqsub pbs_script.pbs\n\"");

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
}


	
