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
	"help|h"	=> \$help);

arg_error("")				if $help;
arg_error("-x or --executable required")	if !$executable;
arg_error("-e or --email required") if !$email;
arg_error("-u or --user required") if !$user;

$name = "job1"		if !$name;
$pvmem = "512mb"	if !$pvmem;
$nodes = 1		if !$nodes;
$ppn = 1		if !$ppn;
$host = "cluster.srv.ualberta.ca" if !$host;
$walltime = "24:00:00"	if !$walltime;
$notify = "bea"		if !$notify;
$dir = "/scratch/$user/$name_$$.tmp" if !$dir;  #what should this be??? /scratch/user/$name??

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
print PBS_SCRIPT "OUTPUT=${user}_\${PBS_JOBID}.zip\n";
print PBS_SCRIPT "zip \${OUTPUT} *\n";

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
$body = "Here is the output from PBS job \${PBS_JOBID}.";
$to = $email;
$file = "$dir/\${OUTPUT}";
$output = "\${OUTPUT}";


### note about below, easier but more memory intensive to do:
###	perl -MMINME::Base64 -0777 -ne 'print encode_base64($_)' <file

#hack
$buf = '$buf';
$jobid = '${PBS_JOBID}';

print PBS_SCRIPT << "END_PERL";
(
(cat <<EOF_MAIL
To: $email
Subject: Results from job $name (PBS jobid $jobid)
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
perl -e '
use MIME::Base64 qw(encode_base64);
open(FILE, "$file") or die "$!";
while (read(FILE, $buf, 60*57)) {
	print encode_base64($buf);
}';
echo '---q1w2e3r4t5--';
) | ssh $mail_user\@$mail_host '$mail_command -t'
END_PERL


#print PBS_SCRIPT "ssh $user\@10.0.6.1 \'(echo \"Here is your output\"; cd $dir; tar -cvvf output.tar *; uuencode $dir/output.tar output.tar) | mail -s \"Job $name is complete\" $email'\n";

close PBS_SCRIPT;

system("tar -cvvf $name.$$.tar *");
system("ssh $host -l $user \"mkdir -p $dir\n\"");
system("scp $name.$$.tar $user\@$host:$dir");
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



	
