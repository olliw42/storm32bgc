###############################################################################
# Allgemeine Subroutinen
###############################################################################

sub sqr
{
my $x = shift;

  return $x*$x;
}

sub divide
{
my $x = shift;
my $y = shift;

  my $z = 0;
  eval '$z= $x/$y;';
  return $z;
}

# integer division: compute $n div $d (so 4 div 2 is 2, 5 div 2 is also 2)
# parameters are $n then $d
sub quotient
{
my $n = shift;
my $d = shift;

  my $r = $n; my $q = 0;
  while( $r >= $d ){ $r = $r - $d; $q = $q + 1; }
  return $q;
}


sub StrToDez
{
my $s= shift;

  if( substr($s,0,2) eq '0x' ){ $s= HexstrToDez($s); }
  return $s;
}

sub HexstrToDez{ return hex(shift); }

sub HexstrToStr{ return pack('H*',shift); }

sub StrToHexstr{ return uc(unpack('H*',shift)); }

sub DezToHexstr{ return uc(sprintf("%0x",shift)); }

sub UCharToHexstr{ return uc(sprintf("%02lx",shift)); }

sub UIntToHexstr{ return uc(sprintf("%04lx",shift)); }

#sub UInt32ToHexstr{ return uc(sprintf("%08lx",shift)); }


sub UIntToHexstrSwapped
{
  return StrToHexstr( pack('S',shift) );
}

sub Int32ToHexstrSwapped
{
  return StrToHexstr( pack('l',shift) );
}

#http://stackoverflow.com/questions/770342/how-can-i-convert-four-characters-into-a-32-bit-ieee-754-float-in-perl
#Tested this on 0xC2ED4000 => -118.625 and it works.
#Tested this on 0x3E200000 => 0.15625 and found a bug! (fixed)
sub FloatToHexstrSwapped{
#  my $f = pack( 'f', shift );
#  my @fb = unpack( 'C4', $f );
#TextOut('$'.StrToHexstr($f).','.UCharToHexstr($fb[0]).UCharToHexstr($fb[1]).UCharToHexstr($fb[2]).UCharToHexstr($fb[3]).'$');
#TextOut('$'.unpack('H*',$f).','.UCharToHexstr($fb[0]).UCharToHexstr($fb[1]).UCharToHexstr($fb[2]).UCharToHexstr($fb[3]).'$');
#  return UCharToHexstr($fb[0]).UCharToHexstr($fb[1]).UCharToHexstr($fb[2]).UCharToHexstr($fb[3]);
  return StrToHexstr( pack('f',shift) );
}

sub UCharToBitstr{ return uc(sprintf("%08lb",shift)); }

sub UIntToBitstr{ return uc(sprintf("%016lb",shift)); }

sub IntelHexChkSum
{
my $s = shift;

  my $sum = 0;
  $sum += $_ for unpack('C*', pack("H*", $s));
  my $hex_sum = DezToHexstr( $sum );
  $hex_sum = substr($hex_sum, -2); # just save the last byte of sum
  my $chksum = ( hex($hex_sum) ^ 0xFF) + 1; # 2's complement of hex_sum
  $chksum = UCharToHexstr( $chksum );
  return $chksum;    # put is back to the end of string, done
}

sub IntelHexLineType # :10 0100 00 214601360121470136007EFE09D21901 40  = len adr type data cc
{
  return substr(shift,7,2);
}

sub IntelHexLineAdr # :10 0100 00 214601360121470136007EFE09D21901 40  = len adr type data cc
{
  return HexstrToDez(substr(shift,3,4));
}

sub IntelHexLineData # :10 0100 00 214601360121470136007EFE09D21901 40  = len adr type data cc
{
my $data = substr(shift,9,300);

  $data =~ s/.{2}$//g; #remove last CC
  return $data;
}

sub ExtractIntelHexLine # :10 0100 00 214601360121470136007EFE09D21901 40  = len adr type data cc
{
my $line = shift;

  my $len = HexstrToDez(substr($line,1,2));
  my $adr = HexstrToDez(substr($line,3,4));
  my $type = substr($line,7,2);
  my $data = substr($line,9,300);
  $data =~ s/.{2}$//g; #remove last CC
  return ($len, $adr, $data, $type);
}

sub TrimStrToLength #fills str with space, and cuts str to length
{
my $s = shift;
my $len = shift;

  while( length($s)<$len ){ $s= $s.' '; }
  return substr($s,0,$len);
}

sub TrimStrWithCharToLength #fills str with space, and cuts str to length
{
my $s = shift;
my $len = shift;
my $c = shift;

  while( length($s)<$len ){ $s= $s.$c; }
  return substr($s,0,$len);
}

sub StrToHexstrFull
{
my $s = shift;

  my $ss = '';
  for(my $i=0; $i<length($s); $i++ ){ $ss.= "x".sprintf("%02lx",ord(substr($s,$i,1)))." ";  }
  return $ss;
}

sub StrToHexDump
{
my $s = shift;

  my $ss = ''; my $j = 0;
  for(my $i=0; $i<length($s); $i++ ){
    if( $j==0 ){ if($i==0){$ss.="0x0000: ";}else{$ss.= "0x".sprintf("%04x",$i).": ";} }
    $ss.= sprintf("%02lx",ord(substr($s,$i,1)))." ";
    $j++;
    if( $j>=16 ){ $j= 0; if( $i<length($s)-1){$ss.="\r\n";} }
  }
  return $ss;
}

sub CleanLeftRightStr
{
my $s = shift;

  $s=~ s/^[ \s]*//; #remove blanks&cntrls at begin
  $s=~ s/[ \s]*$//; #remove blanks&cntrls at end
  return $s;
}

sub CleanUpStr
{
my $s = shift;

  $s=~ s/[ \s]+//g; #remove blanks and cntrls  original $s=~ s/\s+/ /g;
  $s=~ s/^[ \s]*//;
  $s=~ s/[ \s]*$//; #clean it up
  return $s;
}

sub PathStr
{
my $s = shift;

  if( $s =~ /(.*)\\/ ){ return $1; }else{ return ''; }
}

sub NameExtStr
{
my $s = shift;

  if( $s =~ /.*\\(.*)/ ){ return $1; }else{ return ''; }
}

sub RemoveExt
{
my $s = shift;

  my $path = PathStr( $s );
  my $file = NameExtStr( $s );
  $file =~ s/(.*)\..*/$1/;
  if( $path eq '' ){ $s= $file; }else{ $s= $path.'\\'.$file;}
  return $s;
}

sub RemoveBasePath
{
my $s = shift;

  my $ss = lc($s);
  my $bb = lc($ExePath.'\\');
  my $i = index( $ss, $bb );
  if( $i == 0 ){ return substr($s,length($bb),255); }else{ return $s; }
}


return 1;
