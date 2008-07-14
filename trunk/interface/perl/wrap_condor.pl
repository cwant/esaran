#!/usr/bin/perl

# This script creates a condor .sub file and sends it to the cluster to be run.
# pi is a c program that estimates pi based on the number of intervals 
# which is provided in pi.input.
# It makes assumptions about the order of the command
# line arguments.

# Run using:
#    perl wrap_condor.pl <executable> <transfer_input_files> <output> \
#               <error> <log>

#print (++$n,": $_\n") foreach (@ARGV);
#print(@ARGV);

$mode = 0;
#0 = normal, 1 = help

if ($ARGV[0] eq "h") {
    $mode = 1;
    }

print ("mode is $mode\n");

print ("For help or to run interactively, run wrap_condor -h\n\n");

#set up default values
$universe = "vanilla";
$requirements = "OpSys == \"WINNT51\" && ARCH == \"INTEL\"";
#$notify_user = "sjw1\@ualberta.ca";
$environment = "path=c:\\winnt\\system32";
$should_transfer_files = "YES";
$when_to_transfer_output = "ON_EXIT";
$executable = "test";

#should be set as same as executable eg. if exe is date, then date.err, date.log, etc
$tranfer_input_files = $executable;
$tranfer_output_files = $executable;
$output = $executable;
$error = $executable;
$log = $executable;

for ($argNum=0; $argNum<=$#ARGV; $argNum++) {
	#print ("argnum = $argNum\n argv[".$argnum."] = ".$ARGV[$argNum]."\n");
	if ($ARGV[$argNum] eq "-u") {$universe = $ARGV[$argNum + 1]}
	#print ($universe."\n");
	elsif ($ARGV[$argNum] eq "-r") {$requirements = $ARGV[$argNum + 1]} #special case as could be a list
	elsif ($ARGV[$argNum] eq "-m") {$notify_user = $ARGV[$argNum + 1]} #is @ working right??
	elsif ($ARGV[$argNum] eq "-s") {$should_transfer_files = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-w") {$when_to_transfer_output = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-x") {$executable = $ARGV[$argNum + 1]; $transfer_output_files=$executable; $transfer_output_files=$executable; $output = $executable; $error = $executable; $log = $executable}
	elsif ($ARGV[$argNum] eq "-i") {$input = $ARGV[$argNum + 1]} #special case as could be a list
	elsif ($ARGV[$argNum] eq "-o") {$output = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-e") {$error = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "-l") {$log = $ARGV[$argNum + 1]}
	elsif ($ARGV[$argNum] eq "- {print ("You've tried to use an unknown tag or forgotten a - ".$ARGV[$argNum]."\n")}
}


open CONDOR_SCRIPT, ">$executable.sub";
print CONDOR_SCRIPT "universe=$universe\n";
print CONDOR_SCRIPT "requirements = OpSys == \"WINNT51\" && Arch == \"INTEL\"\n";
print CONDOR_SCRIPT "notify_user=sjw1\@ualberta.ca\n";
print CONDOR_SCRIPT "environment = path=c:\\winnt\\system32\n";
print CONDOR_SCRIPT "should_transfer_files = $should_transfer_files\n";
print CONDOR_SCRIPT "when_to_transfer_output = $when_to_transfer_output\n";
print CONDOR_SCRIPT "executable = $executable.bat\n";
print CONDOR_SCRIPT "transfer_input_files = $executable.bat\n";
#print CONDOR_SCRIPT "transfer_output_files =\n";
print CONDOR_SCRIPT "output = $output.out\n";
print CONDOR_SCRIPT "error = $error.err\n";
print CONDOR_SCRIPT "log = ".$log.".log\n";
print CONDOR_SCRIPT "queue\n";
close CONDOR_SCRIPT;


system("scp $executable.sub sjw1\@cluster.srv.ualberta.ca:~/");
system("ssh cluster.srv.ualberta.ca -l sjw1 \"condor_submit $executable.sub\n\"");


