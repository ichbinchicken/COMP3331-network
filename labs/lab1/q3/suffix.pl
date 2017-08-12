#!/usr/bin/perl -w

@array = (50,250,500,750,1000,1250,1500);
foreach $size (@array) {
    $file = "www.".$ARGV[0].$size.".csv";
    open(F, "<", $file) or die "$file fails: $!";
    $time = 1;
    while ($line = <F>) {
        $line = $size." ".$line;
        $line =~ s/\n//;
        $line = $line . " ".$time."\n";
        print $line;
        $time++;
    }
    close F;
}
