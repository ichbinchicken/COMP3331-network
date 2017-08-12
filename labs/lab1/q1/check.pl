#!/usr/bin/perl -w

while ($line = <STDIN>) {
    push(@files, $line); 
}

foreach $file (@files) {
    chomp $file;
	open(F, "<", $file) or die "$file fails: $!";
    while ($line = <F>) {
		if ($line =~ /packets transmitted/) {
			print "$file: $line";
		}
	}
	close F;
}
