#!/usr/bin/perl

while(chomp($line=<>)) {
   # $line=~s/(\.[0-9]+?)-[0-9]{2}/$1/g;
   $line=~s/\.[0-9]+?-[0-9]{2}//g;
  # $line=~s/\((.+?),/\( $1 ,/g;
   $line=~s/\r//g;
   print "$line\n";
}
