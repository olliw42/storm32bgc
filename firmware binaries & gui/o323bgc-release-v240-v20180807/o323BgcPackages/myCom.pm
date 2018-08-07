sub ExtractCom{
  my $s = shift;
  if( substr($s,0,3) eq "ESP" ){ return "ESP"; } #"ESP (STorM32 ESP Bridge)"
  $s =~ s/^(COM\d{1,3}).*/$1/; #gets "COMxxx"
  return $s;
}

sub ExtractComName{
  my $s = shift; #can be e.g. \Device\Silabser26NULNUL
  $s =~ s/.*\\(\w+)\x00*$/$1/;
  return $s;
}

sub ExtractComType{ #helper for ComIsUSB(), ComIsBlueTooth()
  my $s = uc(shift);
  $s = ExtractComName($s);
  $s =~ s/^ESP(.*)/$1/; #strip off ESP part, doesn't affect COM entries
  $s =~ s/^COM\d{1,3}(.*)/$1/; #strip off COM part
  $s =~ s/\(//; #strip off remaining (
  $s =~ s/\)//; #strip off remaining )
  return CleanLeftRightStr($s);
}

sub GetComNameFromList{ #helper for ComIsUSB(), ComIsBlueTooth()
  my $port = shift;
  my ($GetComPortOK,@PortList)= GetComPorts();
  if( $GetComPortOK > 0 ){
    for( @PortList ){ if(ExtractCom($_) eq $port){ $port = $_; }}
  }
  return $port
}

sub ComIsUSB{
  my $port = uc(shift);
  my $s = ExtractComType($port);
  if( $s eq '' ){ $s = ExtractComType(GetComNameFromList($port)); }
  #since v3.x boards have a usb-ttl on board, we can't distinguish usb from usb-ttl anymore
  #so, just check that it's not bluetooth and not ESP
  #if( $s =~ m/usb/i ){ return 1; }
  if( $s =~ m/bth/i ){ return 0; }
  if( $s =~ m/esp/i ){ return 0; } #the type here is 'STorM32 ESP Bridge', so we identify it by esp
  return 1;
}

#a strict test for a usb port, can be used only if it's known that it's a v1.x board!
sub ComIsUSBStrict{
  my $port = uc(shift);
  my $s = ExtractComType($port);
  if( $s eq '' ){ $s = ExtractComType(GetComNameFromList($port)); }
  if( $s =~ m/usb/i ){ return 1; }
  return 0;
}

sub ComIsBlueTooth{
  my $port = uc(shift);
  my $s = ExtractComType($port);
  if( $s eq '' ){ $s = ExtractComType(GetComNameFromList($port)); }
  if( $s =~ m/bth/i ){ return 1; }
  return 0;
}

sub ComIsESP{
  my $port = uc(shift);
  my $s = ExtractComType($port);
  if( $s eq '' ){ $s = ExtractComType(GetComNameFromList($port)); }
  if( $s =~ m/esp/i ){ return 1; } #the type here is 'STorM32 ESP Bridge', so we identify it by esp
  return 0;
}



return 1;
