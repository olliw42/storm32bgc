#-----------------------------------------------------------------------------#
###############################################################################
# SHARE SETTINGS Tool Window
###############################################################################
# -> SHARE SETTINGS Tool Window
#    CHECK NT MODULE VERSIONS Tool Window
#    CHANGE BOARD CONFIGURATION Tool Window
#    EDIT BOARD NAME Tool Window
#    GUI BAUDRATE Tool Window
#    ESP8266 Configuration Tool Window
#    NTLogger RTC Configuration Tool Window
#    BLUETOOTH Configuration Tool Window
#    UPDATE Tool Window
#    Motion Control Tool Window
#    NT Module CLI Tool Window
###############################################################################
#-----------------------------------------------------------------------------#
my $ShareSettingsIsInitialized = 0;

my $ShareSettingsBackgroundColor= [96,96,96];

my $ShareSettingsXsize= 3*380 + 10; #780
my $ShareSettingsYsize= 1800; #870-32; # -50;

#my $ssWinFont = Win32::GUI::Font->new(-name=>$StdWinFontName, -size=>7, -bold => 0, );

my $w_ShareSettings = Win32::GUI::DialogBox->new( -name=> 'sharesettings_Window', -parent => $w_Main,
  -text=> 'o323BGC Share Settings', -size=> [$ShareSettingsXsize,$ShareSettingsYsize],
  -helpbox => 0,
  #-background=>$ShareSettingsBackgroundColor,
  #-sizable => 1,
  #-resizable => 1,
);
$w_ShareSettings->SetIcon($Icon);

sub sharesettings_Window_Terminate{ $w_ShareSettings->Hide(); 0; }
sub sharesettings_OK_Click{ $w_ShareSettings->Hide(); 0; }
sub sharesettings_ScreenShotMini_Click{ return sharesettings_ScreenShot_Click(); }

my $ScreenShotFile_lastdir = $ExePath;

sub sharesettings_ScreenShot_Click{
  my $file= Win32::GUI::GetSaveFileName( -owner=> $w_Main,
    -title=> 'Save Share Settings ScreenShot to File',
    -nochangedir=> 1,
    -directory=> $ScreenShotFile_lastdir,
    -defaultextension=> '.png',
    -filter=> ['*.png'=>'*.png','*.jpg'=>'*.jpg','*.bmp'=>'*.bmp','All files' => '*.*'],
    -pathmustexist=> 1,
    -overwriteprompt=> 1,
    -noreadonlyreturn => 1,
    -explorer=>0,
  );
  if( $file ){
    $FirmwareHexFile_lastdir= $file;
    my $DC= $w_ShareSettings->GetDC();
    my $bmap = Win32::GUI::DIBitmap->newFromDC($DC);
    $bmap->SaveToFile( $file );#, JPEG ); #,  JPEG_QUALITYSUPERB );
    TextOut("\r\nScreenShot of Share Settings saved to $file.\r\n");
  }elsif( Win32::GUI::CommDlgExtendedError() ){ $w_Main->MessageBox("Some error occured, sorry",'ERROR'); }
  1;
}

sub ShareSettingsInit{
  if( $ShareSettingsIsInitialized>0 ){ return; }
  $ShareSettingsIsInitialized = 1;
  my $xpos = 400; #15;
  my $ypos = 15;
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_BGC', #-font=> $StdWinFont,
    -text=> "OlliW's Brushless Gimbal Controller Tool ".$BGCStr."Tool\r\n$VersionStr\r\n",
    -pos=> [$xpos,$ypos],  -height=>30,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos = 15;
  $ypos = 15;
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_Header_name', #-font=> $StdWinFont,
    -text=> '', -pos=> [$xpos,$ypos], -width=> 160,  -height=>50,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_Header_value', #-font=> $StdWinFont,
    -text=> '', -pos=> [$xpos+170,$ypos], -width=> 200, -height=>50,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos = 110 -40;
  $xpos = 15;
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_Text1_name', #-font=> $StdWinFont,
    -text=> '', -pos=> [$xpos,$ypos], -width=> 160,  -height=>$ShareSettingsYsize-100-75 +40,#+25,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_Text1_value', #-font=> $StdWinFont,
    -text=> '', -pos=> [$xpos+170,$ypos], -width=> 50,  -height=>$ShareSettingsYsize-100-75 +40,#+25,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_Text1_value2', #-font=> $StdWinFont,
    -text=> '', -pos=> [$xpos+170+60,$ypos], -width=> 130,  -height=>$ShareSettingsYsize-100-75 +40,#+25,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos = 15+380;
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_Text2_name', #-font=> $StdWinFont,
    -text=> '', -pos=> [$xpos,$ypos], -width=> 160,  -height=>$ShareSettingsYsize-100-75 +40,#+25,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_Text2_value', #-font=> $StdWinFont,
    -text=> '', -pos=> [$xpos+170,$ypos], -width=> 50,  -height=>$ShareSettingsYsize-100-75 +40,#+25,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_Text2_value2', #-font=> $StdWinFont,
    -text=> '', -pos=> [$xpos+170+60,$ypos], -width=> 130,  -height=>$ShareSettingsYsize-100-75 +40,#+25,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos = 15+2*380;
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_Text3_name', #-font=> $StdWinFont,
    -text=> '', -pos=> [$xpos,$ypos], -width=> 160,  -height=>$ShareSettingsYsize-100-75 +40,#+25,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_Text3_value', #-font=> $StdWinFont,
    -text=> '', -pos=> [$xpos+170,$ypos], -width=> 50,  -height=>$ShareSettingsYsize-100-75 +40,#+25,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $w_ShareSettings->AddLabel( -name=> 'sharesettings_Text3_value2', #-font=> $StdWinFont,
    -text=> '', -pos=> [$xpos+170+60,$ypos], -width=> 130,  -height=>$ShareSettingsYsize-100-75 +40,#+25,
    #-background=>$ShareSettingsBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos= $ShareSettingsYsize -63;
  $w_ShareSettings->AddButton( -name=> 'sharesettings_ScreenShot', #-font=> $StdWinFont,
    -text=> 'Save ScreenShot', -pos=> [$ShareSettingsXsize-203,$ypos], -width=> 120, -height=> 26,
  );
  $w_ShareSettings->AddButton( -name=> 'sharesettings_ScreenShotMini', #-font=> $StdWinFont,
    -text=> 'S', -pos=> [0,0], -width=> 26, -height=> 26,
  );
  $w_ShareSettings->AddButton( -name=> 'sharesettings_OK', #-font=> $StdWinFont,
    -text=> 'OK', -pos=> [$ShareSettingsXsize-203,$ypos], -width=> 80, -height=> 26,
  );
}

sub ShareSettingsShow{
  my $header_name=''; my $header_value='';
  my $text1_name=''; my $text1_value='';  my $text1_value2='';
  my $text2_name=''; my $text2_value='';  my $text2_value2='';
  my $text3_name=''; my $text3_value='';  my $text3_value2='';
  my $count = 0;
  foreach my $Option (@OptionList){
    if( $Option->{type} eq 'SCRIPT' ){ next; }
    if( OptionToSkip($Option) ){
      $header_name.= $Option->{name} . "\r\n";
      $header_value.= ': ' . GetOptionField($Option,0) . "\r\n";
      next;
    }
    $count++;
  }
  my $countthird =  int( $count/3+0.5 );
  my $counttext1 =  0;
  $count = 0;
  foreach my $Option (@OptionList){
    if( $Option->{type} eq 'SCRIPT' ){ next; }
    if( OptionToSkip($Option) ){ next; }
    if( $count<$countthird ){
      $text1_name.= $Option->{name} . "\r\n";
      $text1_value.= ': ' . GetOptionField($Option,0) . "\r\n";
      $text1_value2.= ': ' . $Option->{textfield}->Text() . "\r\n";
      $counttext1++;
    }elsif( $count<2*$countthird ){
      $text2_name.= $Option->{name} . "\r\n";
      $text2_value.= ': ' . GetOptionField($Option,0) . "\r\n";
      $text2_value2.= ': ' . $Option->{textfield}->Text() . "\r\n";
    }else{
      $text3_name.= $Option->{name} . "\r\n";
      $text3_value.= ': ' . GetOptionField($Option,0) . "\r\n";
      $text3_value2.= ': ' . $Option->{textfield}->Text() . "\r\n";
    }
    $count++;
  }

  $w_ShareSettings->sharesettings_Header_name->Text( $header_name );
  $w_ShareSettings->sharesettings_Header_value->Text( $header_value );
  $w_ShareSettings->sharesettings_Text1_name->Text( $text1_name );
  $w_ShareSettings->sharesettings_Text1_value->Text( $text1_value );
  $w_ShareSettings->sharesettings_Text1_value2->Text( $text1_value2 );
  $w_ShareSettings->sharesettings_Text2_name->Text( $text2_name );
  $w_ShareSettings->sharesettings_Text2_value->Text( $text2_value );
  $w_ShareSettings->sharesettings_Text2_value2->Text( $text2_value2 );
  $w_ShareSettings->sharesettings_Text3_name->Text( $text3_name );
  $w_ShareSettings->sharesettings_Text3_value->Text( $text3_value );
  $w_ShareSettings->sharesettings_Text3_value2->Text( $text3_value2 );

  my ($tw,$th)= $w_ShareSettings->sharesettings_Text1_name->GetTextExtentPoint32(
                  $text1_name,
                  $w_ShareSettings->sharesettings_Text1_name->GetFont()
                );
  $w_ShareSettings->Height( 140 + $th*$counttext1 + 5);

  my $desk = Win32::GUI::GetDesktopWindow();
  my $dw = Win32::GUI::Width($desk);
  my $dh = Win32::GUI::Height($desk);
  my $ssw = $w_ShareSettings->Width();
  my $ssh = $w_ShareSettings->Height();
  my $x = ($dw-$ssw)/2; if($x<10){$x=10;}
  my $y = ($dh-$ssh)/2-10; if($y<10){$y=10;}
  $w_ShareSettings->Move( $x, $y );
  $w_ShareSettings->sharesettings_ScreenShot->Move( $ssw-85-25 - 160, $ssh-50-10 );
  $w_ShareSettings->sharesettings_ScreenShotMini->Move( $ssw- 26 -8, 2 );
  $w_ShareSettings->sharesettings_OK->Move( $ssw-85-25, $ssh-50-10 );

  $w_ShareSettings->Show();
}

# Ende # SHARE SETTINGS Window
#####################



#-----------------------------------------------------------------------------#
###############################################################################
# CHECK NT MODULE VERSIONS Tool Window
###############################################################################
#    SHARE SETTINGS Tool Window
# -> CHECK NT MODULE VERSIONS Tool Window
#    CHANGE BOARD CONFIGURATION Tool Window
#    EDIT BOARD NAME Tool Window
#    GUI BAUDRATE Tool Window
#    ESP8266 Configuration Tool Window
#    NTLogger RTC Configuration Tool Window
#    BLUETOOTH Configuration Tool Window
#    UPDATE Tool Window
#    Motion Control Tool Window
#    NT Module CLI Tool Window
###############################################################################
#-----------------------------------------------------------------------------#
my $CheckNtVersionsIsInitialized = 0;

my $CheckNtVersionsBackgroundColor= [96,96,96];

my $CheckNtVersionsXsize= 330;
my $CheckNtVersionsYsize= 250;

my $w_CheckNtVersions = Win32::GUI::DialogBox->new( -name=> 'checkntversions_Window', -parent => $w_Main,
  -text=> 'NT Modules Firmware Versions', -size=> [$CheckNtVersionsXsize,$CheckNtVersionsYsize],
  -helpbox => 0,
);
$w_CheckNtVersions->SetIcon($Icon);

sub checkntversions_Window_Terminate{ $w_CheckNtVersions->Hide(); 0; }
sub checkntversions_OK_Click{ $w_CheckNtVersions->Hide(); 0; }

sub CheckNtVersionsInit{
  if( $CheckNtVersionsIsInitialized>0 ){ return; }
  $CheckNtVersionsIsInitialized = 1;
  my $xpos = 15;
  my $ypos = 15;
  $w_CheckNtVersions->AddLabel( -name=> 'checkntversions_Intro',
    -text=> 'Status of all NT modules found on the NT bus:',
    -pos=> [$xpos,$ypos],  -height=>20, -width=>$CheckNtVersionsYsize-20,
  );
  $ypos += 2*13;
  #a maximum of 7 NT modules: Imu1, Imu2, Pitch, Roll, Yaw, Logger, Imu3
  for (my $i=0; $i<7; $i++){
    $w_CheckNtVersions->AddLabel( -name=> 'checkntversions_MessageModule'.$i, #-font=> $StdWinFont,
      -text=> 'tt',
      -pos=> [$xpos+15,$ypos],  -height=>$CheckNtVersionsXsize-30, -width=>$CheckNtVersionsYsize-20,
    );
    $w_CheckNtVersions->AddLabel( -name=> 'checkntversions_MessageStatus'.$i, #-font=> $StdWinFont,
      -text=> 'tt',
      -pos=> [$xpos+90,$ypos],  -height=>$CheckNtVersionsXsize-30, -width=>$CheckNtVersionsYsize-20,
    );
    $ypos += 15;
  }
#  $ypos += 8*13; #each line is 13 height
  $ypos += 13-2;
  $w_CheckNtVersions->AddLabel( -name=> 'checkntversions_Result',
    -text=> 'tt',
    -pos=> [$xpos,$ypos],  -height=>20, -width=>$CheckNtVersionsYsize-20,
  );

  $w_CheckNtVersions->AddButton( -name=> 'checkntversions_OK', #-font=> $StdWinFont,
    -text=> 'OK', -pos=> [$CheckNtVersionsXsize-203,$ypos], -width=> 80, -height=> 26,
  );
}

sub CheckNtVersionsShow
{
my $ptr = shift;
my @modulestoupgrade = @{$ptr}; #was passed in as reference

  my $cnt = 0;
  for (my $i=0; $i<7; $i++){
    if( $i < scalar @modulestoupgrade ){
      my $mod = $modulestoupgrade[$i];
      $w_CheckNtVersions->{'checkntversions_MessageModule'.$i}->Text($mod->{name}.':');
      my $s2 = '';
      if( $mod->{uptodate} ){
        $s2 .= 'is up to date'."\n";
        $w_CheckNtVersions->{'checkntversions_MessageStatus'.$i}->Change(-foreground => [0,128,0]);
      }else{
        $s2 .= 'please upgrade (curr: '.$mod->{curversion}.'  latest: '.$mod->{latestversion}.')'."\n";
        $w_CheckNtVersions->{'checkntversions_MessageStatus'.$i}->Change(-foreground => [128,0,0]);
        $cnt++;
      }
      $w_CheckNtVersions->{'checkntversions_MessageStatus'.$i}->Text($s2);
    }else{
      $w_CheckNtVersions->{'checkntversions_MessageModule'.$i}->Text('');
      $w_CheckNtVersions->{'checkntversions_MessageStatus'.$i}->Text('');
    }
  }
  if( $cnt == 0 ){
    $w_CheckNtVersions->checkntversions_Result->Text( 'All NT modules are up to date!' );
  }else{
    $w_CheckNtVersions->checkntversions_Result->Text( 'NT modules which need upgrade:  '.$cnt );
  }

  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_CheckNtVersions->Move($x+200,$y+100);

  my $desk = Win32::GUI::GetDesktopWindow();
  my $dw = Win32::GUI::Width($desk);
  my $dh = Win32::GUI::Height($desk);
  my $ssw = $w_CheckNtVersions->Width();
  my $ssh = $w_CheckNtVersions->Height();
  $w_CheckNtVersions->checkntversions_OK->Move( $ssw-85-25, $ssh-50-10 );

  $w_CheckNtVersions->Show();
}


sub CheckNtVersionsShow1
{
my $ptr = shift;
my @modulestoupgrade = @{$ptr}; #was passed in as reference

  my $s = '';
  my $cnt = 0;
  foreach my $mod (@modulestoupgrade){
    $s .= '  '.$mod->{name}.':'.TrimStrToLength(' ',13-length($mod->{name}));
    if( $mod->{uptodate} ){
      $s .= 'is up to date'."\n";
    }else{
      $s .= 'please upgrade (curr: '.$mod->{curversion}.'  latest: '.$mod->{latestversion}.')'."\n";
      $cnt++;
    }
  }
  if( $cnt == 0 ){
    $s .= "\n".'All NT modules are up to date!'
  }else{
    $s .= "\n".'NT modules which need upgrade:  '.$cnt;
  }

  my $res = $w_Main->MessageBox(
      "Status of all NT modules found on the NT bus:\n\n".$s,
      'NT Modules Firmware Versions', 0x0030 );#0x0040 MB_ICONASTERISK (used for information)
}

# Ende # CheckNtVersions Window
#####################




#-----------------------------------------------------------------------------#
###############################################################################
# CHANGE BOARD CONFIGURATION Tool Window
###############################################################################
#    SHARE SETTINGS Tool Window
#    CHECK NT MODULE VERSIONS Tool Window
# -> CHANGE BOARD CONFIGURATION Tool Window
#    EDIT BOARD NAME Tool Window
#    GUI BAUDRATE Tool Window
#    ESP8266 Configuration Tool Window
#    NTLogger RTC Configuration Tool Window
#    BLUETOOTH Configuration Tool Window
#    UPDATE Tool Window
#    Motion Control Tool Window
#    NT Module CLI Tool Window
###############################################################################
#-----------------------------------------------------------------------------#
my $ChangeBoardConfigurationIsInitialized = 0;

my $ChangeBoardConfigurationBackgroundColor= [96,96,96];

my $ChangeBoardConfigurationXsize= 400;
my $ChangeBoardConfigurationYsize= 270+13; #470;

my $w_ChangeBoardConfiguration= Win32::GUI::DialogBox->new( -name=> 'changeboardconfig_Window', -parent => $w_Main, -font=> $StdWinFont,
##  -text=> "o323BGC Change Board Configuration Tool",
  -text=> "o323BGC Change Encoder Support Tool",
  -size=> [$ChangeBoardConfigurationXsize,$ChangeBoardConfigurationYsize],
  -helpbox => 0,
  -background=>$ChangeBoardConfigurationBackgroundColor,
);
$w_ChangeBoardConfiguration->SetIcon($Icon);

sub changeboardconfig_Window_Terminate{ changeboardconfig_Cancel_Click(); 0; }

sub ChangeBoardConfigurationInit{
  if( $ChangeBoardConfigurationIsInitialized>0 ){ return; }
  $ChangeBoardConfigurationIsInitialized = 1;
  my $xpos= 20;
  my $ypos= 20;
  $w_ChangeBoardConfiguration->AddLabel( -name=> 'changeboardconfig_Text1', -font=> $StdWinFont,
    -text=> "This tool allows you to enable/disable the encoder support.",
    -pos=> [$xpos,$ypos], -width=> $ChangeBoardConfigurationXsize-20,  -height=>30,
    -background=>$ChangeBoardConfigurationBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos+= 35 ;
  $w_ChangeBoardConfiguration->AddLabel( -name=> 'changeboardconfig_Text2', -font=> $StdWinFont,
    -text=> '-',
    -pos=> [$xpos,$ypos], -width=> $ChangeBoardConfigurationXsize-50,  -height=>8*13+13,
   -background=>$CGrey128, -foreground=> [255,255,255],
  );
  $ypos+= 30;
  $w_ChangeBoardConfiguration->AddCombobox( -name=> 'changeboardconfig_BoardConfiguration', -font=> $StdWinFont,
    -pos=> [$ChangeBoardConfigurationXsize/2-40-2,$ypos-2], -size=> [80,160],
    -dropdown=> 1, -vscroll=>1,
  );
  $w_ChangeBoardConfiguration->changeboardconfig_BoardConfiguration->SetDroppedWidth(60);
  $w_ChangeBoardConfiguration->changeboardconfig_BoardConfiguration->Add( ('off','on') );
  $xpos= 20;
  $ypos= $ChangeBoardConfigurationYsize -90;
  $w_ChangeBoardConfiguration->AddButton( -name=> 'changeboardconfig_OK', -font=> $StdWinFont,
    -text=> 'OK', -pos=> [$ChangeBoardConfigurationXsize/2-40-2,$ypos], -width=> 80,
  );
  $w_ChangeBoardConfiguration->AddButton( -name=> 'changeboardconfig_Cancel', -font=> $StdWinFont,
    -text=> 'Cancel', -pos=> [$ChangeBoardConfigurationXsize/2-40-2,$ypos+30], -width=> 80,
  );
}

sub ChangeBoardConfigurationShow{
  DataDisplayHalt();
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_ChangeBoardConfiguration->Move($x+150,$y+100);

  $w_ChangeBoardConfiguration->changeboardconfig_BoardConfiguration->Hide();
  $w_ChangeBoardConfiguration->changeboardconfig_OK->Disable();
  $w_ChangeBoardConfiguration->Show();
##  TextOut( "\r\n".'Change Board Configuration Tool... ' );
  TextOut( "\r\n".'Change Encoder Support Tool... ' );
  if( not ConnectionIsValid() ){ goto WERROR; }

  $w_ChangeBoardConfiguration->changeboardconfig_Text2->Text(
    'Please select the new encoder support:' ."\r\n". "\r\n". "\r\n". "\r\n". "\r\n".
    'When done press >OK<; or press >Cancel< to abort.' . "\r\n". "\r\n".
    'NOTE: On >OK< the new setting will be stored immediately to the EEPROM; it will however become effective only at the next power up!' );
  if( $ActiveBoardConfiguration == $BOARDCONFIGURATION_IS_FOC ){
    $w_ChangeBoardConfiguration->changeboardconfig_BoardConfiguration->Select(1);
  }else{
    $w_ChangeBoardConfiguration->changeboardconfig_BoardConfiguration->Select(0);
  }
  $w_ChangeBoardConfiguration->changeboardconfig_BoardConfiguration->Show();
  $w_ChangeBoardConfiguration->changeboardconfig_OK->Enable();
  return 1;
WERROR:
  $w_ChangeBoardConfiguration->changeboardconfig_Text2->Text(
    'No connection to board!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
  return 0;
}

sub changeboardconfig_Cancel_Click{
  ##ClosePort();
##  TextOut( "\r\n".'Change Board Configuration Tool... ABORTED!'."\r\n" );
  TextOut( "\r\n".'Change Encoder Support Tool... ABORTED!'."\r\n" );
  $w_ChangeBoardConfiguration->Hide();
  0;
}

sub changeboardconfig_OK_Click{
  my $bcf = $w_ChangeBoardConfiguration->changeboardconfig_BoardConfiguration->SelectedItem();
  TextOut( "\r\n".'xf... ' );
  SetExtendedTimoutFirst(1000); #storing to Eeprom can take a while! so extend timeout
  my $res= ExecuteCmdwCrc( 'xf', HexstrToStr('0'.$bcf.'00') );
  if( substr($res,length($res)-1,1) ne 'o' ){ TextOut( 'hhhhhkashdhn' ); } #this should never happen
  TextOut( ' ok' );

  TextOut( "\r\n".'xx... ' );
  $res= ExecuteCmd( 'xx' );
  if( substr($res,length($res)-1,1) ne 'o' ){ TextOut( 'hhhhhkashdhn' ); } #this should never happen
  TextOut( ' ok' );
  TextOut( "\r\n".'disconnect ...');
  SetDoFirstReadOut(0); #to suppress "Please do first ..." line
  DisconnectFromBoard(0);
  TextOut( "\r\n".'waiting for a moment before reconnecting ...');
  _delay_ms( 1500 );
##  TextOut( "\r\n".'Change Board Configuration Tool... DONE!'."\r\n" );
  TextOut( "\r\n".'Change Encoder Support Tool... DONE!'."\r\n" );
  $w_ChangeBoardConfiguration->Hide();

  ConnectToBoard();
  0;
}

# Ende # CHANGE BOARD CONFIGURATION Tool Window
#####################




#-----------------------------------------------------------------------------#
###############################################################################
# EDIT BOARD NAME Tool Window
###############################################################################
#    SHARE SETTINGS Tool Window
#    CHECK NT MODULE VERSIONS Tool Window
#    CHANGE BOARD CONFIGURATION Tool Window
# -> EDIT BOARD NAME Tool Window
#    GUI BAUDRATE Tool Window
#    ESP8266 Configuration Tool Window
#    NTLogger RTC Configuration Tool Window
#    BLUETOOTH Configuration Tool Window
#    UPDATE Tool Window
#    Motion Control Tool Window
#    NT Module CLI Tool Window
###############################################################################
#-----------------------------------------------------------------------------#
my $EditBoardNameIsInitialized = 0;

my $EditBoardNameBackgroundColor= [96,96,96];

my $EditBoardNameXsize= 410;
my $EditBoardNameYsize= 270; #470;

my $w_EditBoardName= Win32::GUI::DialogBox->new( -name=> 'editboardname_Window', -parent => $w_Main, -font=> $StdWinFont,
  -text=> "o323BGC Edit Board Name Tool",
  -size=> [$EditBoardNameXsize,$EditBoardNameYsize],
  -helpbox => 0,
  -background=>$EditBoardNameBackgroundColor,
);
$w_EditBoardName->SetIcon($Icon);

sub editboardname_Window_Terminate{ editboardname_Cancel_Click(); 0; }

sub EditBoardNameInit{
  if( $EditBoardNameIsInitialized>0 ){ return; }
  $EditBoardNameIsInitialized = 1;
  my $xpos= 20;
  my $ypos= 20;
  $w_EditBoardName->AddLabel( -name=> 'editboardname_Text1', -font=> $StdWinFont,
    -text=> "This tool allows you to change the name of the STorM32-BGC board.",
    -pos=> [$xpos,$ypos], -width=> $EditBoardNameXsize-20,  -height=>30,
    -background=>$EditBoardNameBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos+= 35 ;
  $w_EditBoardName->AddLabel( -name=> 'editboardname_Text2', -font=> $StdWinFont,
    -text=> '-',
    -pos=> [$xpos,$ypos], -width=> $EditBoardNameXsize-50,  -height=>8*13,
    -background=>$CGrey128, -foreground=> [255,255,255],
  );
  $ypos+= 30;
  $w_EditBoardName-> AddTextfield( -name=> 'editboardname_Name', -font=> $StdWinFont,
    -pos=> [$EditBoardNameXsize/2-70-2,$ypos-3], -size=> [140,23],
  );
  $w_EditBoardName->editboardname_Name->SetLimitText(16);
  $xpos= 20;
  $ypos= $EditBoardNameYsize -90;
  $w_EditBoardName->AddButton( -name=> 'editboardname_OK', -font=> $StdWinFont,
    -text=> 'OK', -pos=> [$EditBoardNameXsize/2-40-2,$ypos], -width=> 80,
  );
  $w_EditBoardName->AddButton( -name=> 'editboardname_Cancel', -font=> $StdWinFont,
    -text=> 'Cancel', -pos=> [$EditBoardNameXsize/2-40-2,$ypos+30], -width=> 80,
  );
}

sub EditBoardNameShow{
  DataDisplayHalt();
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_EditBoardName->Move($x+150,$y+100);

  $w_EditBoardName->editboardname_Name->Hide();
  $w_EditBoardName->editboardname_OK->Disable();
  $w_EditBoardName->Show();
  TextOut( "\r\n".'Edit Board Name Tool... ' );
  if( not ConnectionIsValid() ){ goto WERROR; }
  my $res = ExecuteCmd( 'v', 54 );
  if( substr($res,length($res)-1,1) ne 'o' ){ DisconnectFromBoard(0); goto WERROR; }
  TextOut( "\r\n".'Reading... ' );
  #check
  TextOut( 'ok' );
  $w_EditBoardName->editboardname_Name->Text( CleanLeftRightStr(substr($res,16,16)) );
  $w_EditBoardName->editboardname_Text2->Text(
    'Please enter the new name:' ."\r\n". "\r\n". "\r\n". "\r\n". "\r\n".
    'When done press >OK<; or press >Cancel< to abort.' . "\r\n". "\r\n".
    'NOTE: On >OK< the new name will be stored immediately to the EEPROM!' );
  $w_EditBoardName->editboardname_Name->Show();
  $w_EditBoardName->editboardname_OK->Enable();
  return 1;
WERROR:
  $w_EditBoardName->editboardname_Text2->Text(
    'No connection to board!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
  return 0;
}

sub editboardname_Cancel_Click{
#  ClosePort();
  TextOut( "\r\n".'Edit Board Name Tool... ABORTED!'."\r\n" );
  $w_EditBoardName->Hide();
  0;
}

sub editboardname_OK_Click{
  my $name= substr( $w_EditBoardName->editboardname_Name->Text() ,0,16);
  $name = TrimStrToLength( $name, 16 );
  TextOut( "\r\n".'xn... ' );
  SetExtendedTimoutFirst(1000); #storing to Eeprom can take a while! so extend timeout
  my $res = ExecuteCmdwCrc( 'xn', $name, 0 );
  if( substr($res,length($res)-1,1) ne 'o' ){ TextOut( 'iahfkashfkshjkf' ); } #this should never happen
  TextOut( 'ok' );
  $NameToOptionHash{'Name'}->{textfield}->Text( $name );
  TextOut( "\r\n".'Edit Board Name Tool... DONE!'."\r\n" );
  $w_EditBoardName->Hide();
  0;
}


# Ende # EDIT BOARD NAME Tool Window
###############################################################################



#-----------------------------------------------------------------------------#
###############################################################################
# GUI BAUDRATE Tool Window
###############################################################################
#    SHARE SETTINGS Tool Window
#    CHECK NT MODULE VERSIONS Tool Window
#    CHANGE BOARD CONFIGURATION Tool Window
#    EDIT BOARD NAME Tool Window
# -> GUI BAUDRATE Tool Window
#    ESP8266 Configuration Tool Window
#    NTLogger RTC Configuration Tool Window
#    BLUETOOTH Configuration Tool Window
#    UPDATE Tool Window
#    Motion Control Tool Window
#    NT Module CLI Tool Window
###############################################################################
#-----------------------------------------------------------------------------#
my $GuiBaudrateIsInitialized = 0;

my $GuiBaudrateBackgroundColor= [96,96,96];

my $GuiBaudrateXsize= 400;
my $GuiBaudrateYsize= 270+13; #470;

my $w_GuiBaudrate= Win32::GUI::DialogBox->new( -name=> 'guibaudrate_Window', -parent => $w_Main, -font=> $StdWinFont,
  -text=> "o323BGC GUI Baudrate Tool",
  -size=> [$GuiBaudrateXsize,$GuiBaudrateYsize],
  -helpbox => 0,
  -background=>$GuiBaudrateBackgroundColor,
);
$w_GuiBaudrate->SetIcon($Icon);

sub guibaudrate_Window_Terminate{ guibaudrate_Cancel_Click(); 0; }

sub GuiBaudrateInit{
  if( $GuiBaudrateIsInitialized>0 ){ return; }
  $GuiBaudrateIsInitialized = 1;
  my $xpos= 20;
  my $ypos= 20;
  $w_GuiBaudrate->AddLabel( -name=> 'guibaudrate_Text1', -font=> $StdWinFont,
    -text=> "This tool allows you to change the GUI's baudrate for communicating with the STorM32 board.",
    -pos=> [$xpos,$ypos], -width=> $GuiBaudrateXsize-20-30,  -height=>30,
    -background=>$GuiBaudrateBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos+= 35 ;
  $w_GuiBaudrate->AddLabel( -name=> 'guibaudrate_Text2', -font=> $StdWinFont,
    -text=> '-',
    -pos=> [$xpos,$ypos], -width=> $GuiBaudrateXsize-50,  -height=>8*13+13,
   -background=>$CGrey128, -foreground=> [255,255,255],
  );
  $ypos+= 30;
  $w_GuiBaudrate->AddCombobox( -name=> 'guibaudrate_Baudrate', -font=> $StdWinFont,
    -pos=> [$GuiBaudrateXsize/2-40-2,$ypos-2], -size=> [80,160],
    -dropdown=> 1, -vscroll=>1,
  );
  $w_GuiBaudrate->guibaudrate_Baudrate->SetDroppedWidth(60);
  $w_GuiBaudrate->guibaudrate_Baudrate->Add( ('9600','19200','38400','57600','115200','230400','460800') );
  $xpos= 20;
  $ypos= $GuiBaudrateYsize -90;
  $w_GuiBaudrate->AddButton( -name=> 'guibaudrate_OK', -font=> $StdWinFont,
    -text=> 'OK', -pos=> [$GuiBaudrateXsize/2-40-2,$ypos], -width=> 80,
  );
  $w_GuiBaudrate->AddButton( -name=> 'guibaudrate_Cancel', -font=> $StdWinFont,
    -text=> 'Cancel', -pos=> [$GuiBaudrateXsize/2-40-2,$ypos+30], -width=> 80,
  );
}

sub GuiBaudrateShow{
  DisconnectFromBoard(0);
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_GuiBaudrate->Move($x+150,$y+100);

  $w_GuiBaudrate->guibaudrate_Baudrate->Hide();
  $w_GuiBaudrate->guibaudrate_OK->Disable();
  $w_GuiBaudrate->Show();
  TextOut( "\r\n".'GUI Baudrate Tool... ' );

  $w_GuiBaudrate->guibaudrate_Text2->Text(
    'Please enter the new baudrate:' ."\r\n". "\r\n". "\r\n". "\r\n". "\r\n".
    'When done press >OK<; or press >Cancel< to abort.' . "\r\n". "\r\n".
    'NOTE: On >OK< the new baudrate will become effective immediately.' );
  if( $Baudrate<=9600 ){
    $w_GuiBaudrate->guibaudrate_Baudrate->Select(0);
  }elsif( $Baudrate<=19200 ){
    $w_GuiBaudrate->guibaudrate_Baudrate->Select(1);
  }elsif( $Baudrate<=38400 ){
    $w_GuiBaudrate->guibaudrate_Baudrate->Select(2);
  }elsif( $Baudrate<=57600 ){
    $w_GuiBaudrate->guibaudrate_Baudrate->Select(3);
  }elsif( $Baudrate<=115200 ){
    $w_GuiBaudrate->guibaudrate_Baudrate->Select(4);
  }elsif( $Baudrate<=230400 ){
    $w_GuiBaudrate->guibaudrate_Baudrate->Select(5);
  }elsif( $Baudrate<=460800 ){
    $w_GuiBaudrate->guibaudrate_Baudrate->Select(6);
  }else{
    $w_GuiBaudrate->guibaudrate_Baudrate->Select(4);
  }
  $w_GuiBaudrate->guibaudrate_Baudrate->Show();
  $w_GuiBaudrate->guibaudrate_OK->Enable();
  return 1;
}

sub guibaudrate_Cancel_Click{
  TextOut( "\r\n".'GUI Baudrate Tool... ABORTED!'."\r\n" );
  $w_GuiBaudrate->Hide();
  0;
}

sub guibaudrate_OK_Click{
  my $bps = $w_GuiBaudrate->guibaudrate_Baudrate->SelectedItem();
  if( $bps==0 ){
    $Baudrate = 9600;
  }elsif( $bps==1 ){
    $Baudrate = 19200;
  }elsif( $bps==2 ){
    $Baudrate = 38400;
  }elsif( $bps==3 ){
    $Baudrate = 57600;
  }elsif( $bps==4 ){
    $Baudrate = 115200;
  }elsif( $bps==5 ){
    $Baudrate = 230400;
  }elsif( $bps==6 ){
    $Baudrate = 460800;
  }else{
    $Baudrate = 115200;
  }
  TextOut( 'Baudrate set to '.$Baudrate.' bps'."\r\n" );
  TextOut( "\r\n".'GUI Baudrate Tool... DONE!'."\r\n" );
  $w_GuiBaudrate->Hide();
  0;
}


# Ende # GUI BAUDRATE Tool Window
###############################################################################




#-----------------------------------------------------------------------------#
###############################################################################
# ESP8266 Configuration Tool Window
###############################################################################
#    SHARE SETTINGS Tool Window
#    CHECK NT MODULE VERSIONS Tool Window
#    CHANGE BOARD CONFIGURATION Tool Window
#    EDIT BOARD NAME Tool Window
#    GUI BAUDRATE Tool Window
# -> ESP8266 Configuration Tool Window
#    NTLogger RTC Configuration Tool Window
#    BLUETOOTH Configuration Tool Window
#    UPDATE Tool Window
#    Motion Control Tool Window
#    NT Module CLI Tool Window
###############################################################################
#-----------------------------------------------------------------------------#
my $ESPConfigIsInitialized = 0;

my $ESPConfigBackgroundColor= [96,96,96];

my $ESPAutoConfigureIsRunning= 0;

my $ESPConfigXsize= 450;
my $ESPConfigYsize= 470;

my $w_ESPConfig= Win32::GUI::DialogBox->new( -name=> 'espconfig_Window', -parent => $w_Main, -font=> $StdWinFont,
  -text=> "o323BGC ESP8266 Wifi Module Configure Tool", -size=> [$ESPConfigXsize,$ESPConfigYsize],
  -helpbox => 0,
  -background=>$ESPConfigBackgroundColor,
);
$w_ESPConfig->SetIcon($Icon);

sub espconfig_Window_Terminate{ ClosePort(); $w_ESPConfig->Hide(); 0; }

sub ESPConfigInit{
  if( $ESPConfigIsInitialized>0 ){ return; }
  $ESPConfigIsInitialized = 1;
  my $xpos= 20;
  my $ypos= 20;
  $w_ESPConfig->AddLabel( -name=> 'espconfig_Text1_label', -font=> $StdWinFont,
    -text=> "With this tool you can configure the ESP8266 Wifi module connected to your STorM32-BGC board.",
    -pos=> [$xpos,$ypos], -width=> 420,  -height=>30,
    -background=>$ESPConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos+= 30 + 1*13;
  $w_ESPConfig->AddLabel( -name=> 'espconfig_Text1b_label', -font=> $StdWinFont,
    -text=> "IMPORTANT:
The STorM32 board MUST be connected to the PC via the USB connector.
The ESP8266 module MUST be connected to either the UART or UART2 port.",
    -pos=> [$xpos,$ypos], -multiline=>1, -height=>4*13+10, -width=> 420,
    -background=>$ESPConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos+= 35 + 2*13;
  $w_ESPConfig->AddLabel( -name=> 'espconfig_Text3_label', -font=> $StdWinFont,
    -text=> "Select the USB COM port of STorM32 board:",
    -pos=> [$xpos,$ypos], -width=> 250,  -height=>30,
    -background=>$ESPConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos+= 250;
  $w_ESPConfig->AddCombobox( -name=> 'espconfig_Port', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos-3], -size=> [140,180],  #-size=> [70,180],
    -dropdown=> 1, -vscroll=>1,
    -onDropDown=> sub{
      ($GetComPortOK,@PortList)= GetComPorts();
      if($GetComPortOK>0){
        my $s= $_[0]->Text();
        $_[0]->Clear(); $_[0]->Add( @PortList ); $_[0]->SelectString( $s ); #$Port has COM + friendly name
        if($_[0]->SelectedItem()<0){ $_[0]->Select(0); }
      }
    }
  );
  $w_ESPConfig->espconfig_Port->SetDroppedWidth(140);
  $w_ESPConfig->espconfig_Port->Add( @PortList );
  if( scalar @PortList){ $w_ESPConfig->espconfig_Port->SelectString( 'COM1' ); } #$Port has COM + friendly name
  $ypos+= 35;
  $xpos= 20;
  $w_ESPConfig->AddLabel( -name=> 'espconfig_Text333_label', -font=> $StdWinFont,
    -text=> "Select the port the ESP8266 is connected to:",
    -pos=> [$xpos,$ypos],
    -background=>$ESPConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos+= 250;
  $w_ESPConfig->AddCombobox( -name=> 'espconfig_EspUart', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos-3], -size=> [140,180],  #-size=> [70,180],
    -dropdown=> 1, -vscroll=>1,
  );
  $w_ESPConfig->espconfig_EspUart->Add( ('UART', 'UART2') );
  $w_ESPConfig->espconfig_EspUart->Select(1); #uart2 as default

  $ypos+= 35;
  $xpos= 20;
  $w_ESPConfig->AddLabel( -name=> 'espconfig_Text4_label', -font=> $StdWinFont,
    -text=> "Upload the firmware .bin file to the ESP8266:",
    -pos=> [$xpos,$ypos], -multiline=>1, -height=>2*13+10,
    -background=>$ESPConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos+= 250;
  $w_ESPConfig->AddButton( -name=> 'espconfig_UploadBin', -font=> $StdWinFont,
    -text=> 'Upload .Bin', -pos=> [$xpos,$ypos-3], -width=> 140,
  );

  $ypos+= 35;
  $xpos= 20;
  $w_ESPConfig->AddLabel( -name=> 'espconfig_Text5_label', -font=> $StdWinFont,
    -text=> "Upload the files in 'data' to the ESP8266:",
    -pos=> [$xpos,$ypos], -multiline=>1, -height=>2*13+10,
    -background=>$ESPConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos+= 250;
  $w_ESPConfig->AddButton( -name=> 'espconfig_UploadData', -font=> $StdWinFont,
    -text=> 'Upload Data Files', -pos=> [$xpos,$ypos-3+2], -width=> 140,
  );

  $ypos= $ESPConfigYsize-150-18+5 -25;
  $xpos= 20;
  $w_ESPConfig->AddLabel( -name=> 'espconfig_Text15_label', -font=> $StdWinFont,
    -text=> "Edit ESP8266 configuration file (for experts only):",
    -pos=> [$xpos,$ypos], -multiline=>1, -height=>2*13+10,
    -background=>$ESPConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos+= 250 +20;
  $w_ESPConfig->AddButton( -name=> 'espconfig_EditConfig', -font=> $StdWinFont,
    -text=> 'Edit Configuration', -pos=> [$xpos,$ypos-3+2], -width=> 100,
  );

  $w_ESPConfig-> AddTextfield( -name=> 'espconfig_RecieveText',
    -pos=> [5,$ESPConfigYsize-150-18+5], -size=> [$ESPConfigXsize-16,93+40-5], -font=> $StdTextFont,
    -vscroll=> 1, -multiline=> 1, -readonly => 1,
    -foreground =>[ 0, 0, 0],
    -background=> [192,192,192],#[96,96,96],
  );
} #end of ESPConfigInit()


sub ESPConfigShow{
  #SetDoFirstReadOut(0);
  DisconnectFromBoard(0);
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_ESPConfig->Move($x+150,$y+100);
  $w_ESPConfig->espconfig_RecieveText->Text('');
  $Port = $w_Main->m_Port->Text();
  $w_ESPConfig->espconfig_Port->SelectString( $Port );
  $w_ESPConfig->Show();
}

sub ESPConfigTextOut{
  $w_ESPConfig->espconfig_RecieveText->Append( PrepareTextForAppend(shift) );
}

sub ESPConfigOpen{
  my $header = shift;
  #set the port to the selected in this tool
  my $UsbPort = $w_ESPConfig->espconfig_Port->Text();
  if( not ComIsUSB($UsbPort) ){
    ESPConfigTextOut( $header."... ABORTED!\nSelected USB COM port is not a USB connection.\n" ); return 0;
  }
  $w_Main->m_Port->SelectString( $UsbPort );
  $Port = $w_Main->m_Port->Text(); #$Port has COM + friendly name
  if( not OpenPort() ){
    ClosePort();
    ESPConfigTextOut( $header."... ABORTED!\nConnection to STorM32 board failed!\n" ); return 0;
  }
  return 1;
}

sub ESPConfigSetEspUart{
  my $Option= $NameToOptionHash{'Esp Configuration'};
  my $res1 = SendRcCmdwoOut( '03'. UCharToHexstr($Option->{adr}).'00' );
  if( $res1 =~ /[tc]/ ){
    ClosePort(); return 0;
  }
  my $CurrentEspUart = substr( ExtractPayloadFromRcCmd($res1), 2*2, 2) + 0;
  my $DesiredEspUart = $w_ESPConfig->espconfig_EspUart->SelectedItem()+1;
  if( $CurrentEspUart != $DesiredEspUart ){
    ESPConfigTextOut( "\nset Esp Configuration to uart" );
    if( $DesiredEspUart > 1 ){ ESPConfigTextOut( "$DesiredEspUart" ); }
    $res1 = SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00' . UCharToHexstr($DesiredEspUart).'00' );
    if( $res1 =~ /[tc]/ ){
      ClosePort(); return 0;
    }
    ESPConfigTextOut( "\nstore settings");
    my $s = ExecuteCmd( 'xs' );
    if( substr($s,length($s)-1,1) ne 'o' ){
      ClosePort(); return 0;
    }
  }
  return 1;
}

sub ESPConfigOpenTunnel{
  ESPConfigTextOut( "\nreset ESP8266 and open tunnel" );
  my $s = ExecuteCmd( 'xQS' );
  if( substr($s,length($s)-1,1) ne 'o' ){ ClosePort(); return 0; }
  WritePort( 'cESPFLASH' );
  _delay_ms(500); #wait a bit and let the STorM32 digest
  ClosePort(); #this would happen anyway during a flash
  return 1;
}

sub espconfig_UploadBin_Click{
  ESPConfigTextOut( "\nUploading .bin firmware file" );
  if( not ESPConfigOpen( "\nUploading .bin firmware file" ) ){ return 0; }
  if( not ESPConfigSetEspUart() ){
    ESPConfigTextOut( "\nUploading .bin firmware file... ABORTED!\nConnection to STorM32 board failed!\n" ); return 0;
  }
  if( not ESPConfigOpenTunnel() ){
    ESPConfigTextOut( "\nUploading .bin firmware file... ABORTED!\nConnection to STorM32 board failed!\n" ); return 0;
  };
  my $s = '"'.$EspWebAppPath.'\\'.$EspToolExe.'"';
  $s .= ' -vv -cd ck -cb 115200 -cp '.ExtractCom($Port).' -ca 0x00000 -cf';
  $s .= ' "'.$EspWebAppPath.'\\'.$EspWebAppBin.'"'."\n";
  $s .= '@echo.'."\n";
  $s .= '@pause'."\n";
  open(F,">$BGCToolRunFile.bat");
  print F $s;
  close( F );
  ESPConfigTextOut( "\nstart uploading firmware..." );
  $w_Main->ShellExecute('open',"$BGCToolRunFile.bat","",'',1);
  ESPConfigTextOut( " ok" );
  ESPConfigTextOut( "\nUploading firmware... DOS BOX STARTED\n" );
  0;
}

sub espconfig_UploadData_Click{
  ESPConfigTextOut( "\nUploading data files" );
  ESPConfigOpen( "\nUploading .bin firmware file" );
  if( not ESPConfigSetEspUart() ){
    ESPConfigTextOut( "\nUploading .bin firmware file... ABORTED!\nConnection to STorM32 board failed!\n" ); return 0;
  }
  if( not ESPConfigOpenTunnel() ){
    ESPConfigTextOut( "\nUploading .bin firmware file... ABORTED!\nConnection to STorM32 board failed!\n" ); return 0;
  };
  my $s = '"'.$EspWebAppPath.'\\'.$EspMkSpiffsExe.'"';
  $s .= ' -c' . ' "'.$EspWebAppPath.'\\data"' . ' -p 256 -b 4096 -s 131072' ;
  $s .= ' "'.$EspWebAppPath.'\\'.$EspSpiffsBin.'"';
  $s .= ' -d 5'."\n";
  $s .= '"'.$EspWebAppPath.'\\'.$EspToolExe.'"';
  $s .= ' -cd ck -cb 115200 -cp '.ExtractCom($Port).' -ca 0xDB000 -cf';
  $s .= ' "'.$EspWebAppPath.'\\'.$EspSpiffsBin.'"';
  $s .= "\n";
  $s .= '@echo.'."\n";
  $s .= '@pause'."\n";
  open(F,">$BGCToolRunFile.bat");
  print F $s;
  close( F );
  ESPConfigTextOut( "\nstart uploading data files..." );
  $w_Main->ShellExecute('open',"$BGCToolRunFile.bat","",'',1);
  ESPConfigTextOut( " ok" );
  ESPConfigTextOut( "\nUploading data files... DOS BOX STARTED\n" );
  0;
}

sub espconfig_EditConfig_Click{
  ESPConfigEditorShow();
  0;
}

#----
# EDIT CONFIGURATION WINDOW
#----
my $EspConfigEditXSize= 780;
my $EspConfigEditYSize= 780;

my $EspConfigEditBackgroundColor= [96,96,96];
my $EspConfigEditTextFont= Win32::GUI::Font->new(-name=>'Lucida Console', -size=>10 );

my $w_ESPConfigEdit_Menubar= Win32::GUI::Menu-> new(
  'File' => '',
    '>Accept and Exit', 'espconfigedit_Accept',
    '>Cancel', 'espconfigedit_Cancel',
);

my $w_ESPConfigEdit= Win32::GUI::Window->new( -name=> 'espconfigedit_Window', -parent => $w_Main, -font=> $StdWinFont,
  -text=> $BGCStr." ESP8266 Configuration File Editor", -size=> [$EspConfigEditXSize,$EspConfigEditYSize],
  -helpbox => 0,
  -background => $EspConfigEditBackgroundColor,
  -menu => $w_ESPConfigEdit_Menubar,
  -dialogui => 0,
  -hasminimize => 0, -minimizebox => 0, -hasmaximize => 0, -maximizebox => 0,
);
$w_ESPConfigEdit->SetIcon($Icon);

$w_ESPConfigEdit->AddButton( -name=> 'espconfigedit_Accept', -font=> $StdWinFont,
  -text=> 'Accept', -pos=> [0,0], -width=>45, -height=>16,
);
$w_ESPConfigEdit->AddButton( -name=> 'espconfigedit_Cancel', -font=> $StdWinFont,
  -text=> 'Cancel', -pos=> [45,0], -width=>45, -height=>16,
);
$w_ESPConfigEdit->AddLabel( -name=> 'espconfigedit_Title', -font=> $StdWinFont,
  -text=> $EspConfigFile,
  -pos=> [90,0], -width=> $xsize-150-6, -height=>15,
  -align=>'center',
);
$w_ESPConfigEdit-> AddTextfield( -name=> 'espconfigedit_Text', -font=> $EspConfigEditTextFont, #-font=> $StdWinFont,
  -pos=> [-1,15], -size=> [$xsize-4,$ysize-41-15], #-size=> [$xsize-14,$ysize-52],
  -hscroll=> 1, -vscroll=> 1,
  -autovscroll=> 1, -autohscroll=> 1,
  -keepselection => 1,
  -multiline=> 1,
);

sub espconfigedit_Window_Resize {
  my $mw = $w_ESPConfigEdit->ScaleWidth();
  my $mh = $w_ESPConfigEdit->ScaleHeight();
  my $lh = $w_ESPConfigEdit->espconfigedit_Title->Height();
  $w_ESPConfigEdit->espconfigedit_Title->Width( $mw - 90 );
  $w_ESPConfigEdit->espconfigedit_Text->Width( $mw+2 );
  $w_ESPConfigEdit->espconfigedit_Text->Height( $mh-$lh+1);
}

sub espconfigedit_Window_Terminate{ $w_ESPConfigEdit->Hide(); 0; }
sub espconfigedit_Cancel_Click{ $w_ESPConfigEdit->Hide(); 0; }

sub espconfigedit_Accept_Click{
  my $file = $EspWebAppPath.'\\data\\'.$EspConfigFile;
  if( !open(F,">$file") ){
    ESPConfigTextOut( "Editing Configuration... ERROR\nCould not save to configuration file $EspConfigFile.\n" );
  }else{
    print F $w_ESPConfigEdit->espconfigedit_Text->Text();
    close(F);
  }
  $w_ESPConfigEdit->Hide();
  0;
}

sub ESPConfigEditorShow{
  my $file = $EspWebAppPath.'\\data\\'.$EspConfigFile;
  if( !open(F,"<$file") ){
    ESPConfigTextOut( "Editing Configuration... ABBORTED\nConfiguration file $EspConfigFile could not be opened.\n" ); return 0;
  }
  my $s=''; while(<F>){ $s.= $_; } close(F);
  $w_ESPConfigEdit->espconfigedit_Text->Text( PrepareTextForAppend($s) );
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_ESPConfigEdit->Move($x+190,$y+20); #100
  $w_ESPConfigEdit->Show();
}

# Ende # ESP8266 Configuration Tool Window
###############################################################################




#-----------------------------------------------------------------------------#
###############################################################################
# NTLogger RTC Configuration Tool Window
###############################################################################
#    SHARE SETTINGS Tool Window
#    CHECK NT MODULE VERSIONS Tool Window
#    CHANGE BOARD CONFIGURATION Tool Window
#    EDIT BOARD NAME Tool Window
#    GUI BAUDRATE Tool Window
#    ESP8266 Configuration Tool Window
# -> NTLogger RTC Configuration Tool Window
#    BLUETOOTH Configuration Tool Window
#    UPDATE Tool Window
#    Motion Control Tool Window
#    NT Module CLI Tool Window
###############################################################################
#-----------------------------------------------------------------------------#
my $RTCConfigIsInitialized = 0;

my $RTCConfigBackgroundColor= [96,96,96];

my $RTCConfigXsize= 400;
my $RTCConfigYsize= 270+13; #470;

my $w_RTCConfig= Win32::GUI::DialogBox->new( -name=> 'rtcconfig_Window', -parent => $w_Main, -font=> $StdWinFont,
##  -text=> "o323BGC Change Board Configuration Tool",
  -text=> "o323BGC NTLogger RTC Tool",
  -size=> [$RTCConfigXsize,$RTCConfigYsize],
  -helpbox => 0,
  -background=>$RTCConfigBackgroundColor,
);
$w_RTCConfig->SetIcon($Icon);

sub rtcconfig_Window_Terminate{ rtcconfig_Cancel_Click(); 0; }

sub RTCConfigInit{
  if( $RTCConfigIsInitialized>0 ){ return; }
  $RTCConfigIsInitialized = 1;
  my $xpos= 20;
  my $ypos= 20;
  $w_RTCConfig->AddLabel( -name=> 'rtcconfig_Text1', -font=> $StdWinFont,
    -text=> "This tool allows you to set the NTLogger RTC date and time.",
    -pos=> [$xpos,$ypos], -width=> $RTCConfigXsize-20,  -height=>30,
    -background=>$RTCConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos+= 35 ;
  $w_RTCConfig->AddLabel( -name=> 'rtcconfig_Text2', -font=> $StdWinFont,
    -text=> ' ',
    -pos=> [$xpos,$ypos], -width=> $RTCConfigXsize-50,  -height=>8*13+13,
   -background=>$CGrey128, -foreground=> [255,255,255],
  );
  $ypos+= 3*13 ;
  $w_RTCConfig->AddLabel( -name=> 'rtcconfig_DateTime', -font=> $StdWinFont,
    -text=> ' ',
    -pos=> [$RTCConfigXsize/2-80,$ypos], -width=> 160,  -height=>13,
   -background=>$CGrey128, -foreground=> [255,255,255],
  );
  $xpos= 20;
  $ypos= $RTCConfigYsize -90;
  $w_RTCConfig->AddButton( -name=> 'rtcconfig_OK', -font=> $StdWinFont,
    -text=> 'OK', -pos=> [$RTCConfigXsize/2-40-2,$ypos], -width=> 80,
  );
  $w_RTCConfig->AddButton( -name=> 'rtcconfig_Cancel', -font=> $StdWinFont,
    -text=> 'Cancel', -pos=> [$RTCConfigXsize/2-40-2,$ypos+30], -width=> 80,
  );
  $w_RTCConfig->AddTimer( 'rtcconfig_Timer', 0 );
  $w_RTCConfig->rtcconfig_Timer->Interval( 4 );
}

sub RTCConfigShow{
  DataDisplayHalt();
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_RTCConfig->Move($x+150,$y+100);

  $w_RTCConfig->rtcconfig_OK->Disable();
  $w_RTCConfig->Show();
  TextOut( "\r\n".'Set NTLogger RTC Tool... ' );
  if( not ConnectionIsValid() ){ goto WERROR; }

  $w_RTCConfig->rtcconfig_Text2->Text(
    'Current date and time:' ."\r\n". "\r\n". "\r\n".
    "\r\n".
    "\r\n". "\r\n".
    'Press >OK< to store the new date and time in the RTC; or press >Cancel< to abort.' . "\r\n"
  );

  rtcconfig_Timer_Timer();

  $w_RTCConfig->rtcconfig_OK->Enable();
  return 1;
WERROR:
  $w_RTCConfig->rtcconfig_Text2->Text(
    'No connection to board!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
  return 0;
}

sub rtcconfig_Cancel_Click{
  TextOut( "\r\n".'Set NTLogger RTC Tool... ABORTED!'."\r\n" );
  $w_RTCConfig->Hide();
  0;
}

sub rtcconfig_Timer_Timer{
  my $datestring = localtime();
  $w_RTCConfig->rtcconfig_DateTime->Text($datestring);
  1;
}

sub rtcconfig_OK_Click{
  my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime();
  $year = $year + 1900;
  $mon = $mon + 1;
  my $datestring = localtime();
  my $dts = UIntToHexstrSwapped($year).UCharToHexstr($mon).UCharToHexstr($mday).
            UCharToHexstr($hour).UCharToHexstr($min).UCharToHexstr($sec);
  TextOut( "\r\n".$datestring );
  TextOut( "\r\n".$sec."-".$min."-".$hour." ".$mday.".".$mon.".".$year );
  TextOut( "\r\n".$dts );

  TextOut( "\r\n".'Cl... ' );
  my $res= ExecuteCmdwCrc( 'Cl', HexstrToStr($dts) );
  if( substr($res,length($res)-1,1) ne 'o' ){ TextOut( 'usdgfsjdzgf' ); } #this should never happen
  TextOut( ' ok' );

  TextOut( "\r\n".'Set NTLogger RTC Tool... DONE!'."\r\n" );
  $w_RTCConfig->Hide();
  0;
}

# Ende # Set NTLogger RTC Tool Window
###############################################################################



#-----------------------------------------------------------------------------#
###############################################################################
# BLUETOOTH Configuration Tool Window
###############################################################################
#    SHARE SETTINGS Tool Window
#    CHECK NT MODULE VERSIONS Tool Window
#    CHANGE BOARD CONFIGURATION Tool Window
#    EDIT BOARD NAME Tool Window
#    GUI BAUDRATE Tool Window
#    ESP8266 Configuration Tool Window
#    NTLogger RTC Configuration Tool Window
# -> BLUETOOTH Configuration Tool Window
#    UPDATE Tool Window
#    Motion Control Tool Window
#    NT Module CLI Tool Window
###############################################################################
#-----------------------------------------------------------------------------#
my $BTConfigIsInitialized = 0;

my $BTConfigBackgroundColor= [96,96,96];

my $BTAutoConfigureIsRunning= 0;

my $ATCmdTimeDelay= 5; #100ms
my $ATCmdTimeOut= 20; #100ms
my @ATBaudRateList= ('','1200','2400','4800','9600','19200','38400','57600','115200');
my @STORMBaudRateList= ('','@a','@b','@c','@d','@e','@f','@g','@h');

my $BTConfigXsize= 450;
my $BTConfigYsize= 470;

my $w_BTConfig= Win32::GUI::DialogBox->new( -name=> 'btconfig_Window', -parent => $w_Main, -font=> $StdWinFont,
  -text=> "o323BGC Bluetooth Module Configure Tool", -size=> [$BTConfigXsize,$BTConfigYsize],
  -helpbox => 0,
  -background=>$BTConfigBackgroundColor,
);
$w_BTConfig->SetIcon($Icon);

sub btconfig_Window_Terminate{ ClosePort(); $w_BTConfig->Hide(); 0; }

sub BTConfigInit{
  if( $BTConfigIsInitialized>0 ){ return; }
  $BTConfigIsInitialized = 1;
  my $xpos= 20;
  my $ypos= 20;
  $w_BTConfig->AddLabel( -name=> 'btconfig_Text1_label', -font=> $StdWinFont,
    -text=> "With this tool you can configure the BT module (HC06) on your STorM32-BGC board.",
    -pos=> [$xpos,$ypos], -width=> 420,  -height=>30,
    -background=>$BTConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos+= 30;
  $w_BTConfig->AddLabel( -name=> 'btconfig_Text1b_label', -font=> $StdWinFont,
    -text=> "IMPORTANT:
The STorM32 board MUST be connected to the PC via the USB connector.
There MUST NOT be anything connected to the UART port.
It's a good idea to press the Reset button now.",
    -pos=> [$xpos,$ypos], -multiline=>1, -height=>4*13+10, -width=> 420,
    -background=>$BTConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos+= 35 + 3*13;
  $w_BTConfig->AddLabel( -name=> 'btconfig_Text3_label', -font=> $StdWinFont,
    -text=> "Select the USB COM port your board is attached to:",
    -pos=> [$xpos,$ypos], -width=> 250,  -height=>30,
    -background=>$BTConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos+= 250;
  #$ypos+= 25;
  $w_BTConfig->AddCombobox( -name=> 'btconfig_Port', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos-3], -size=> [140,180],  #-size=> [70,180],
#  -dropdownlist=> 1, -vscroll=>1,
    -dropdown=> 1, -vscroll=>1,
    -onDropDown=> sub{
      ($GetComPortOK,@PortList)= GetComPorts();
      if($GetComPortOK>0){
        my $s= $_[0]->Text();
        $_[0]->Clear(); $_[0]->Add( @PortList ); $_[0]->SelectString( $s ); #$Port has COM + friendly name
        if($_[0]->SelectedItem()<0){ $_[0]->Select(0); }
      }
    }
  );
  $w_BTConfig->btconfig_Port->SetDroppedWidth(140);
  $w_BTConfig->btconfig_Port->Add( @PortList );
  if( scalar @PortList){ $w_BTConfig->btconfig_Port->SelectString( 'COM1' ); } #$Port has COM + friendly name
  $xpos= 20;
  $ypos+= 35;
  $w_BTConfig->AddLabel( -name=> 'btconfig_Text333_label', -font=> $StdWinFont,
    -text=> "Enter the desired name of the BT module:",
    -pos=> [$xpos,$ypos],
    -background=>$BTConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos+= 250;
  $w_BTConfig-> AddTextfield( -name=> 'btconfig_Name', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos-3], -size=> [140,23],
  );
  $w_BTConfig->btconfig_Name->SetLimitText(11);
  $w_BTConfig->btconfig_Name->Text('STorM32-BGC');
  $xpos= 20;
  $ypos+= 35;
  $w_BTConfig->AddLabel( -name=> 'btconfig_Text4_label', -font=> $StdWinFont,
    -text=> "Run the auto configure sequence:
(please be patient, this takes few minutes)",
    -pos=> [$xpos,$ypos], -multiline=>1, -height=>2*13+10,
    -background=>$BTConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos+= 250;
  #$ypos+= 25;
  $w_BTConfig->AddButton( -name=> 'btconfig_AutoConfigure', -font=> $StdWinFont,
    -text=> 'Auto Configure', -pos=> [$xpos,$ypos-3+7], -width=> 140,
  );
  $xpos= 20;
  $ypos+= 65;
  $w_BTConfig->AddLabel( -name=> 'btconfig_Text5_label', -font=> $StdWinFont,
    -text=> "Manual configuration tool (for experts only)",
    -pos=> [$xpos,$ypos],
    -background=>$BTConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos+= 20;
  $w_BTConfig->AddLabel( -name=> 'btconfig_Text5b_label', -font=> $StdWinFont,
    -text=> "command",
    -pos=> [$xpos,$ypos],
    -background=>$BTConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $w_BTConfig->AddTextfield( -name=> 'btconfig_Cmd', -font=> $StdWinFont,
    -pos=> [$xpos+$w_BTConfig->btconfig_Text5b_label->Width()+3,$ypos-3],
    -size=> [$BTConfigXsize-157-4+46-$w_BTConfig->btconfig_Text5b_label->Width(),23],
  );
  $w_BTConfig->AddButton( -name=> 'btconfig_Send', -font=> $StdWinFont,
    -text=> 'Send', -pos=> [$BTConfigXsize-90,$ypos-3+2], -width=> 60,
  );
  $w_BTConfig->btconfig_Cmd->Text('');
  $w_BTConfig-> AddTextfield( -name=> 'btconfig_RecieveText',
    -pos=> [5,$BTConfigYsize-150-18+5], -size=> [$BTConfigXsize-16,93+40-5], -font=> $StdTextFont,
    -vscroll=> 1, -multiline=> 1, -readonly => 1,
    -foreground =>[ 0, 0, 0],
    -background=> [192,192,192],#[96,96,96],
  );
} #end of BTConfigInit()

sub BTConfigShow{
  DisconnectFromBoard(0); ##it disconnects itself then UARTis removed
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_BTConfig->Move($x+150,$y+100);
  $w_BTConfig->btconfig_RecieveText->Text('');
  $w_BTConfig->Show();
}

sub btconfig_Send_Click{
  BTConfigTextOut( "\r\n".'Send' );
  if( not BTConfigOpenPort() ){ ClosePort(); return 0; }
  #_delay_ms( 1000 );
  my $cmd= $w_BTConfig->btconfig_Cmd->Text();
  BTConfigTextOut( "\r\n".$cmd."\r\n" );
  my $s= SendATCommand( $cmd, 1 );
  BTConfigTextOut( "\r\n".$cmd.'->'.$s );
  BTConfigTextOut( "\r\n".'Done'."\r\n" );
  ClosePort();
  0;
}

my $BTConfigBTMmoduleType = 'HC06'; #HC06 is the default

sub BTConfigBTMmoduleVersionIsOk{
  my $s = shift;
  if( substr($s,0,18) eq 'AT+VERSIONOKlinvor' ){
    $BTConfigBTMmoduleType = 'HC06';
    return 1; # accepted
  }
  if( substr($s,0,18) eq 'AT+VERSIONhc01.com' ){
    $BTConfigBTMmoduleType = 'HC06';
    return 1;# accepted
  }
  if( substr($s,0,15) eq 'AT+VERSIONHC-08' ){
    $BTConfigBTMmoduleType = 'HC08';
    return 1;# accepted
  }
  return 0;
}

# extension to "new" hc06, as reported by RocketMouse,
#  http://www.rcgroups.com/forums/showpost.php?p=35475966&postcount=8771
#  the only change seems to be in the response to AT+VERSION, which is AT+VERSIONhc01.comV2.0
# extension to hc08, as reported by zyawooo,
#  http://www.rcgroups.com/forums/showpost.php?p=35696578&postcount=1113

#used commands, with responses
# HC06:
#  'AT'               -> ATOK
#  'AT+VERSION'       -> AT+VERSIONOKlinvor..., AT+VERSIONhc01.com...
#  'AT+'.$ATBAUD      -> 'AT+'.$ATBAUD.'OK'.$Baudrate
#  'AT+NAME'.$btname  -> 'AT+NAME'.$btname.'OKsetname'
# HC08:
#  'AT'               -> ATOK
#  'AT+VERSION'       -> AT+VERSIONHC-08 V2.4,2016-07-08
#   AT+BAUD=115200    -> AT+BAUD=115200OK115200,NONE
#   AT+NAME=XYZ       -> AT+NAME=XYZOKsetNAME:XYZ

sub btconfig_AutoConfigure_Click{
  my $cmd= ''; my $s= ''; my $response= ''; my $detectedbaud= -1;

  if( $BTAutoConfigureIsRunning==0 ){
    $BTAutoConfigureIsRunning= 1;
  }elsif( $BTAutoConfigureIsRunning==1 ){
    $BTAutoConfigureIsRunning= 2; return 0;
  }else{ return 0; }
  $w_BTConfig->btconfig_AutoConfigure->Text('Stop Auto Configure');

  BTConfigTextOut( "\r\n".'Run auto configure... '."\r\n".'(please wait, this takes few minutes)' );
  if( not BTConfigOpenPort() ){ goto EXIT; } ##BUG: ClosePort(); return 0; }

  #check connection
  BTConfigTextOut( "\r\n".'check connection...' );
  $s= SendATCommand( 't', 0 );
  if( $s eq 'o' ){
    BTConfigTextOut( ' OK' );
  }else{
    BTConfigTextOut( "\r\n".'connection FAILED!' );
    BTConfigTextOut( "\r\n".'Please check the COM port and/or press the Reset button on the board.' );
    goto EXIT;
  }

  BTConfigTextOut( "\r\n".'communication baudrate is '.$Baudrate.' bps' );

  #enter Qmode
  BTConfigTextOut( "\r\n".'enter BT Qmode...' );
  $s= SendATCommand( 'xQB', 0 );
  if( $s eq 'o' ){
    BTConfigTextOut( ' OK' );
  }else{
    BTConfigTextOut( "\r\n".'connection FAILED!' );
    BTConfigTextOut( "\r\n".'Please press the Reset button on the board.' );
    goto EXIT;
  }

  _delay_ms( 500 );
  #scan all baudrates
  $detectedbaud = -1;
  for(my $baud=1; $baud<=8; $baud++ ){
    BTConfigTextOut( "\r\n".'scan at '.$ATBaudRateList[$baud].' bps... ' );
    if( $BTAutoConfigureIsRunning>1 ){ BTConfigTextOut( "\r\n".'auto configure ABORTED!' ); goto EXIT; }
    $cmd= $STORMBaudRateList[$baud].'AT';
    BTConfigTextOut( "\r\n".'  '.$cmd );
    $s= SendATCommand( $cmd, 0 );
    BTConfigTextOut( '->'.$s );
    if( $s ne 'ATOK' ){ BTConfigTextOut( "\r\n".'  no BT module at this baud rate' ); }else{
      BTConfigTextOut( "\r\n".'  BT module detected at '.$ATBaudRateList[$baud].' bps' );
      $detectedbaud= $baud; last;
    }
#    $s= $w_BTConfig->btconfig_RecieveText->GetLine(0); #this helps to avoid the next cmd to be executed too early
#    Win32::GUI::DoEvents();
  }
  if( $detectedbaud < 0 ){ BTConfigTextOut( "\r\n".'no BT module found, auto configure ABORTED!' ); goto EXIT; }

  #BT module detected, set some variables
  my $ATBAUD; my $BTBAUD;
  if( $Baudrate<=9600 ){
    $ATBAUD= 'BAUD4'; $BTBAUD='@d';
  }elsif( $Baudrate<=19200 ){
    $ATBAUD= 'BAUD5'; $BTBAUD='@e';
  }elsif( $Baudrate<=38400 ){
    $ATBAUD= 'BAUD6'; $BTBAUD='@f';
  }elsif( $Baudrate<=57600 ){
    $ATBAUD= 'BAUD7'; $BTBAUD='@g';
  }else{
    $ATBAUD= 'BAUD8'; $BTBAUD='@h';
  }

  my $error= 0;
  #BT module detected, check
  BTConfigTextOut( "\r\n".'check BT module... ' );
  $cmd= 'AT';
  BTConfigTextOut( "\r\n".'  '.$cmd );
  $s= SendATCommand( $cmd, 0 );
  BTConfigTextOut( '->'.$s );
  if( $s ne 'ATOK' ){ $error+= 0x01; }
  $cmd= 'AT+VERSION';
  BTConfigTextOut( "\r\n".'  '.$cmd.'->' );
  $s= SendATCommand( $cmd, 1 );
#  if( substr($s,0,18) ne 'AT+VERSIONOKlinvor' ){ $error+= 0x02; }
  if( not BTConfigBTMmoduleVersionIsOk($s) ){ $error+= 0x02; }
  if( $error ){ BTConfigTextOut( "\r\n".'Check FAILED, something went wrong!' ); goto EXIT; }
  BTConfigTextOut( "\r\n".'BT module identified as a '.$BTConfigBTMmoduleType );

##### use $Baudrate !!!!!
  #BT module detected, configure
  BTConfigTextOut( "\r\n".'configure BT module... ' );
  _delay_ms( 500 );
  #1=1200, 2=2400, 3=4800, 4=9600 (default), 5=19200, 6=38400, 7=57600, 8=115200,
  if( $BTConfigBTMmoduleType eq 'HC06' ){
    $cmd= 'AT+'.$ATBAUD;
    BTConfigTextOut( "\r\n".'  '.$cmd );
    $s= SendATCommand( $cmd, 0 );
    BTConfigTextOut( '->'.$s );
    if( $s ne 'AT+'.$ATBAUD.'OK'.$Baudrate ){ $error+= 0x04; }
  }elsif( $BTConfigBTMmoduleType eq 'HC08' ){
    $cmd= 'AT+BAUD='.$Baudrate.',N';
    BTConfigTextOut( "\r\n".'  '.$cmd );
    $s= SendATCommand( $cmd, 0 );
    BTConfigTextOut( '->'.$s );
    if( $s ne 'AT+BAUD='.$Baudrate.'OK'.$Baudrate.',NONE' ){ $error+= 0x04; }
  }
  if( $error ){ BTConfigTextOut( "\r\n".'Configure FAILED!' ); goto EXIT; }

  _delay_ms( 500 );
  my $btname= $w_BTConfig->btconfig_Name->Text();
  if( $btname eq '' ){ $btname= 'STorM32-BGC'; }
  #filter bt name
  $btname =~ s/@//g;
  $btname = substr( $btname, 0, 16 );
  if( $BTConfigBTMmoduleType eq 'HC06' ){
    $cmd= $BTBAUD.'AT+NAME'.$btname;
    BTConfigTextOut( "\r\n".'  '.$cmd );
    $s= SendATCommand( $cmd, 0 );
    BTConfigTextOut( '->'.$s );
    if( $s ne 'AT+NAME'.$btname.'OKsetname' ){ $error+= 0x20; }
  }elsif( $BTConfigBTMmoduleType eq 'HC08' ){
    $cmd= $BTBAUD.'AT+NAME='.$btname;
    BTConfigTextOut( "\r\n".'  '.$cmd );
    $s= SendATCommand( $cmd, 0 );
    BTConfigTextOut( '->'.$s );
    if( $s ne 'AT+NAME='.$btname.'OKsetNAME:'.$btname ){ $error+= 0x20; }
  }
  if( $error ){ BTConfigTextOut( "\r\n".'Configure FAILED!' ); goto EXIT; }

  #BT module detected, doublecheck
  BTConfigTextOut( "\r\n".'double check configuration of BT module... ' );
  _delay_ms( 500 );
  $s= SendATCommand( $BTBAUD, 0 );
  $cmd= 'AT';
  BTConfigTextOut( "\r\n".'  '.$cmd );
  $s= SendATCommand( $cmd, 0 );
  BTConfigTextOut( '->'.$s );
  if( $s ne 'ATOK' ){ $error+= 0x08; }
  $cmd= 'AT+VERSION';
  BTConfigTextOut( "\r\n".'  '.$cmd.'->' );
  $s= SendATCommand( $cmd, 1 );
#  if( substr($s,0,18) ne 'AT+VERSIONOKlinvor' ){ $error+= 0x10; }
  if( not BTConfigBTMmoduleVersionIsOk($s) ){ $error+= 0x10; }
  if( $error ){ BTConfigTextOut( "\r\n".'Doublecheck FAILED, something went wrong!' ); goto EXIT; }

  BTConfigTextOut( "\r\n".'Configuration of BT module was succesfull!' );
  BTConfigTextOut( "\r\n".'DONE' );
  BTConfigTextOut( "\r\n"."\r\n".'PLEASE POWER-DOWN THE BOARD. WAIT FEW SECONDS BEFORE APPLYING POWER AGAIN.' );
  goto FIN;

EXIT:
  BTConfigTextOut( "\r\n"."\r\n".'PLEASE RESET THE BOARD.' );

FIN:
  BTConfigTextOut( "\r\n" );
  ClosePort();
  $BTAutoConfigureIsRunning= 0;
  $w_BTConfig->btconfig_AutoConfigure->Text('Auto Configure');
  0;
}


sub BTConfigTextOut{
  $w_BTConfig->btconfig_RecieveText->Append( PrepareTextForAppend(shift) );
}

sub BTConfigOpenPort{
  $Port= $w_BTConfig->btconfig_Port->Text(); #$Port has COM + friendly name
  if( ExtractCom($Port) eq '' ){
    BTConfigTextOut( "\r\nPort not specified!"."\r\n" ); return 0; #this error should never happen
  }
  $p_Serial = Win32::SerialPort->new( ExtractCom($Port) );
  if( not $p_Serial ){
    BTConfigTextOut( "\r\nOpening port ".ExtractCom($Port)." FAILED!"."\r\n" ); return 0;
  }else{
    ConfigComPort();
    return 1;
  }
  return 0;
}

sub BTConfigStrToReadableStr{
  my $s= shift;
  my $ss= '';
  for(my $i=0; $i<length($s); $i+=1 ){
    my $c= ord( substr($s,$i,1) );
    if(( $c>=ord(' ') )and( $c<=ord('~') )){
      $ss.= chr($c);
    }elsif( $c==10 ){
      $ss.= '\n';
    }else{
      $ss.='*'; #$ss.='<'.sprintf("%d",$c).'>';
    }
  }
  return $ss;
}

sub SendATCommand{
  my $cmd= shift;
  my $outputflag= shift;
  _delay_ms( 100*$ATCmdTimeDelay );
  WritePort( $cmd );
  my $response= '';
  my $tmo= GetTickCount() + 150*$ATCmdTimeOut; #timeout in 100 ms
  while( GetTickCount() < $tmo  ){
    my ($i, $s) = ReadPortOneByte();
    my $ss= BTConfigStrToReadableStr($s);
    if(( defined $outputflag )&&( $outputflag>0 )){ BTConfigTextOut( $ss ); }
    $response.= $ss;
    $s= $w_BTConfig->btconfig_RecieveText->GetLine(0); #this helps to avoid the next cmd to be executed too early
    Win32::GUI::DoEvents();
  };
  my $s= $response;
  return ($response,$s); #this is dirty, a call $s=SendATCommand results in $s
}

# Ende # BLUETOOTH Configuration Tool Window
###############################################################################




#-----------------------------------------------------------------------------#
###############################################################################
# UPDATE Tool Window
###############################################################################
#    SHARE SETTINGS Tool Window
#    CHECK NT MODULE VERSIONS Tool Window
#    CHANGE BOARD CONFIGURATION Tool Window
#    EDIT BOARD NAME Tool Window
#    GUI BAUDRATE Tool Window
#    ESP8266 Configuration Tool Window
#    NTLogger RTC Configuration Tool Window
#    BLUETOOTH Configuration Tool Window
# -> UPDATE Tool Window
#    Motion Control Tool Window
#    NT Module CLI Tool Window
###############################################################################
#-----------------------------------------------------------------------------#
# ShellExecute may nozt work since it returns immediately and doesn't wait for called to finish
# http://www.perl-community.de/bat/poard/thread/5223
# Win32::SetChildShowWindow(0);  #damit system kein Fenster öffnet
# system( "owH_extract.exe in.txt out.txt" );
my $UpdateIsInitialized = 0;

my %MonthHash = ( 'Jan'=>'01', 'Feb'=>'02', 'Mar'=>'03', 'Apr'=>'04', 'Mai'=>'05', 'June'=>'06', 'July'=>'07',
                  'Aug'=>'08', 'Sep'=>'09', 'Oct'=>'10', 'Nov'=>'11', 'Dez'=>'12', );

my $UpdateBackgroundColor = [96,96,96];

my $UpdateLatestVersionStr = '';
my $UpdateLatestDate = '';

my $UpdateXsize = 450;
my $UpdateYsize = 205+23;

my $w_Update= Win32::GUI::DialogBox->new( -name=> 'update_Window', -parent => $w_Main, -font=> $StdWinFont,
  -text=> "o323BGC Update Tool", -size=> [$UpdateXsize,$UpdateYsize],
  -helpbox => 0,
  -background=>$UpdateBackgroundColor,
);
$w_Update->SetIcon($Icon);


sub update_Window_Terminate{ $w_Update->Hide(); 0; }
sub update_OK_Click{ $w_Update->Hide(); 0; }


sub UpdateInit
{
  if( $UpdateIsInitialized>0 ){ return; }
  $UpdateIsInitialized = 1;
  my $xpos= 20;
  my $ypos= 20;
  $w_Update->AddLabel( -name=> 'update_Text1_label', -font=> $StdWinFont,
    -text=> 'This tool checks for updates, and lets you download them.',
    -pos=> [$xpos,$ypos], -width=> 420,  -height=>30,
    -background=>$UpdateBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos+= 35;
  $w_Update->AddLabel( -name=> 'update_Text2_label', -font=> $StdWinFont,
    -text=> '-',
    -pos=> [$xpos,$ypos], -width=> 400,  -height=>70 + 23,
    -background=>$CGrey128, -foreground=> [255,255,255],
  );
  $xpos= 20;
  $ypos= $UpdateYsize -60;
  $w_Update->AddButton( -name=> 'update_DownloadAndSave', -font=> $StdWinFont,
    -text=> 'Download and Save', -pos=> [$UpdateXsize/2-80,$ypos], -width=> 160,
  );
  $w_Update->update_DownloadAndSave->Hide();
  $w_Update->AddButton( -name=> 'update_OK', -font=> $StdWinFont,
    -text=> 'OK', -pos=> [$UpdateXsize/2-40,$ypos], -width=> 80,
  );
  $w_Update->update_OK->Hide();
}


sub UpdateShow
{
  DataDisplayHalt();
  $w_Update->update_DownloadAndSave->Hide();
  $w_Update->update_OK->Hide();
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_Update->Move($x+150,$y+100);
  $w_Update->update_Text2_label->Text( 'Checking git for updates... Please wait!' );
  $w_Update->Show();
  Win32::GUI::DoEvents();
  sleep(1);
  my ($version,$date,$zipfilename, $betaversion,$betastr,$betadate,$betazipfilename) = Update_CheckGitForLatestVersion();
#  ($UpdateLatestVersion,$UpdateLatestDate) = Update_CheckGitForLatestVersion();
  if( $version == 0 ){
    $w_Update->update_Text2_label->Text(
      'Checking git for updates... ABORTED!'."\n".'Connecting to git failed.'
    );
    return 0;
  }
#$VersionStr = '27. Mai. 2018 v2.38a';
  $VersionStr =~ /^(\d+?)\. (.+?)\.? (\d+?) v(.+?)$/;
#TextOut( "\r\n".$1 ); TextOut( "\r\n".$2 );  TextOut( "\r\n".$3 );  TextOut( "\r\n".$4 );
#TextOut( "\r\n".$MonthHash{$2} );
  my $currentdate = $3.$MonthHash{$2}.$1;
  my $currentversionstr = $4;
  $currentversionstr =~ s/\.//g; #remove '.'
  my $currentversion = $currentversionstr;
  $currentversion =~ s/\D//g; #remove all non-digits
  my $currentbetastr = $currentversionstr;;
  $currentbetastr =~ s/\d//g; #remove all digits
#  my $s = 'Your firmware release:    v'.$currentversion.$currentbetastr.'-v'.$currentdate."\r\n";
  my $s = 'Your firmware release:    v'.$currentversionstr.'-v'.$currentdate."\n"."\n";
  $s.= 'Latest firmware release: v'.$version.'-v'.$date."\n";
  $s.= 'Latest beta release:        v'.$betaversion.$betastr.'-v'.$betadate."\n";
  $s.= "\n";
  $w_Update->update_Text2_label->Text( $s );
  if( ($currentversion >= $version) and ($currentversionstr ge $betaversion.$betastr) ){
    $s .= 'You have the latest firmware installed :)'."\n";
    $w_Update->update_Text2_label->Text( $s );
    $w_Update->update_OK->Show();
    return 0;
  }
  if( ($currentversion >= $version) or ($currentbetastr ne '') ){
    $s.= 'A newer beta version v'.$betaversion.$betastr.' is available, do you want to download the zip file?'."\n";
    ($UpdateLatestVersionStr,$UpdateLatestDate) = ($betaversion.$betastr,$betadate);
  }else{
    $s.= 'A newer firmware version v'.$version.' is available, do you want to download the zip file?'."\n";
    ($UpdateLatestVersionStr,$UpdateLatestDate) = ($version,$date);
  }
  $w_Update->update_Text2_label->Text( $s );
  $w_Update->update_DownloadAndSave->Enable();
  $w_Update->update_DownloadAndSave->Show();
}


my $UpdateZipFileDir_lastdir = $ExePath;


sub update_DownloadAndSave_Click
{
  $w_Update->update_DownloadAndSave->Hide();
  my $zipfilename= 'o323bgc-release-v'.$UpdateLatestVersionStr.'-v'.$UpdateLatestDate;
  $w_Update->update_Text2_label->Text( 'Download firmware '. $zipfilename .'.zip... '."\n" );
  my $dir = Win32::GUI::BrowseForFolder( -owner=> $w_Main,
    -title=> 'Select Firmware Zip File Directory',
    -directory=> $UpdateZipFileDir_lastdir,
    -folderonly=> 1,
  );
  if( $dir ){
    $UpdateZipFileDir_lastdir = $dir;
    my $s = 'Downloading firmware '. $zipfilename .'.zip... Please wait!'."\n";
    $w_Update->update_Text2_label->Text( $s );
    if( Update_DownloadLatestVersionFromGit($zipfilename,$dir) ){
      $s.= 'Downloading ... DONE'."\n" . "\n" . 'Please unzip/extract the dowloaded file. Have fun :)'."\n";
    }else{
      $s.= 'Downloading ... ABORTED'."\n" . 'Connection to git failed.';
    }
    $w_Update->update_Text2_label->Text( $s );
    $w_Update->update_OK->Enable();
    $w_Update->update_OK->Show();
  }elsif( Win32::GUI::CommDlgExtendedError() ){ $w_Main->MessageBox("Some error occured, sorry",'ERROR'); }
  1;
}

sub Update_CheckGitForLatestVersion
{
#http://www.perlhowto.com/executing_external_commands
  #get github directory page as html
  Win32::SetChildShowWindow(0);
  my $res = system(
        'bin\wget\wget', '-q', '--no-check-certificate', #'--secure-protocol=auto',
        '-Ogithub-firmware-directory-list-html',
        'https://github.com/olliw42/storm32bgc/tree/master/firmware%20binaries%20%26%20gui'
        );
  if( $res != 0 ){ return (0,''); }
  #load github directory page
  my $directorieshtml = '';
  open( F, "<github-firmware-directory-list-html");
  while(<F>){ $directorieshtml .= $_; }
  close( F );
  system( 'del', '"github-firmware-directory-list-html"' );
  #scan and extract the .zip files from downloaded github page
  my @directories = ( $directorieshtml =~ /href=".*?(o323bgc-release-.*?\.zip)"/g  ); #only get .zip
  #get latest official and beta versions
  my $version = 0;
  my $date = '';
  my $zipfilename = '';
  my $betaversion = 0;
  my $betastr = '';
  my $betadate = '';
  my $betazipfilename = '';
  foreach my $s (@directories){
#TextOut( "\r\n".$s );
    $s =~ /o323bgc-release-v(\d+)(\w*)-v(\d+)\.zip/;
    my $ver = $1;
    my $beta = $2;
    my $d = $3;
#TextOut( "\r\n".$ver." ".$beta." ".$d );
    if( $beta ne '' ){
      if( ($ver > $betaversion) or (($ver == $betaversion) and ($beta gt $betastr)) ){
        $betaversion = $ver; $betastr = $beta; $betadate = $d; $betazipfilename = $s;
      }
    }else{
      if( $ver > $version ){ $version = $ver; $date = $d; $zipfilename = $s;}
    }
  }
  return ($version,$date,$zipfilename, $betaversion,$betastr,$betadate,$betazipfilename);
}

sub Update_DownloadLatestVersionFromGit
{
#http://www.perlhowto.com/executing_external_commands
  my $zipfilename = shift;
  my $dir = shift;
  my $res = system(
      'bin\wget\wget', '-q', '--no-check-certificate',
      'https://github.com/olliw42/storm32bgc/tree/master/firmware%20binaries%20%26%20gui/'.$zipfilename.'.zip'
      );
  if( $res != 0 ){ return 0; }
  system( 'move', $zipfilename.'.zip', $dir );
  return 1;
}

# Ende # UPDATE Tool Window
###############################################################################




#-----------------------------------------------------------------------------#
###############################################################################
# Motion Control Tool Window
###############################################################################
#    SHARE SETTINGS Tool Window
#    CHECK NT MODULE VERSIONS Tool Window
#    CHANGE BOARD CONFIGURATION Tool Window
#    EDIT BOARD NAME Tool Window
#    GUI BAUDRATE Tool Window
#    ESP8266 Configuration Tool Window
#    NTLogger RTC Configuration Tool Window
#    BLUETOOTH Configuration Tool Window
#    UPDATE Tool Window
# -> Motion Control Tool Window
#    NT Module CLI Tool Window
###############################################################################
#-----------------------------------------------------------------------------#
my $MotionControlIsInitialized = 0;

my $MotionControlXPos= 100;
my $MotionControlYPos= 100;
my $MotionControlXsize= 550;
my $MotionControlYsize= 440;

my $MotionControlBackgroundColor= [96,96,96];
my $MotionControlEditorTextFont= Win32::GUI::Font->new(-name=>'Lucida Console', -size=>10 );

my $w_MotionControl_Menubar= Win32::GUI::Menu-> new(
  'Motion Control Scripts' => '',
    '>New', 'mcontrol_New',
    '>Load from File...', 'mcontrol_Load',
    '>Save to File...', 'mcontrol_Save',
    '>-', 0,
    '>Run', 'mcontrol_Run',
    '>-', 0,
    '>Exit', 'mcontrol_Exit',
);

#my $w_MotionControl= Win32::GUI::DialogBox->new( -name=> 'mcontrol_Window',  -parent => $w_Main, -font=> $StdWinFont,
my $w_MotionControl= Win32::GUI::Window->new( -name=> 'mcontrol_Window',  -parent => $w_Main, -font=> $StdWinFont,
  -text=> "Motion Control Tool",
  -pos=> [$MotionControlXPos,$MotionControlYPos],
  -size=> [$MotionControlXsize,$MotionControlYsize],
  -helpbox => 0,
  -background=>$MotionControlBackgroundColor,
  -menu=> $w_MotionControl_Menubar,
  -dialogui => 0, #is required so that rets are e.g. not captured
  -hasminimize => 0, -minimizebox => 0, -hasmaximize => 0, -maximizebox => 0,
);
$w_MotionControl->SetIcon($Icon);

sub mcontrol_Window_Resize {
  my $mw = $w_MotionControl->ScaleWidth();
  my $mh = $w_MotionControl->ScaleHeight();
  my $lh = $w_MotionControl->mcontrol_Title->Height();
  $w_MotionControl->mcontrol_Title->Width( $mw - 105 );
  $w_MotionControl->mcontrol_Text->Width( $mw+2 );
  $w_MotionControl->mcontrol_Text->Height( $mh-$lh+1 +1);
}

sub mcontrol_Window_Terminate{ $w_MotionControl->Hide(); TextOut( 'Motion Control Tool ended'."\r\n" ); 0; }
sub mcontrol_Exit_Click{ mcontrol_Window_Terminate(); 0; }
sub mcontrol_New_Click{ $w_MotionControl->mcontrol_Text->Text(''); 0; }
sub mcontrol_Run_Click{ MotionControlRun(); 0; }

my $MotionControlFile_lastdir= $ExePath;

sub mcontrol_Load_Click{
  my $file= Win32::GUI::GetOpenFileName( -owner=> $w_Main,
    -title=> 'Load Motion Control Script from File',
    -nochangedir=> 1,
    -directory=> $SettingsFile_lastdir, #MotionControl_lastdir, #".\\",
    -defaultextension=> '.mcs',
    -filter=> ['*.mcs'=>'*.mcs','All files' => '*.*'],
    -pathmustexist=> 1,
    -filemustexist=> 1,
  );
  if( $file ){
    if( !open(F,"<$file") ){
      $w_Main->MessageBox( "Some error occured, sorry",'ERROR'); return; }
    my $s=''; while(<F>){ $s.= $_; } close(F);
    #$w_MotionControl->mcontrol_Title->Text( '  '.RemoveBasePath($file) );
    $w_MotionControl->mcontrol_Text->Text( $s );
  }elsif( Win32::GUI::CommDlgExtendedError() ){ $w_Main->MessageBox("Some error occured, sorry",'ERROR'); }
  1;
}

sub mcontrol_Save_Click{
  my $file= Win32::GUI::GetSaveFileName( -owner=> $w_Main,
    -title=> 'Save Motion Control Script to File',
    -nochangedir=> 1,
    -directory=> $SettingsFile_lastdir, #MotionControl_lastdir, #".\\",
    -defaultextension=> '.mcs',
    -filter=> ['*.mcs'=>'*.mcs','All files' => '*.*'],
    -pathmustexist=> 1,
    -overwriteprompt=> 1,
    -noreadonlyreturn => 1,
    -explorer=>0,
  );
  if( $file ){
    if( !open(F,">$file") ){
      $w_Main->MessageBox("Some error occured, sorry",'ERROR'); return; }
    print F $w_MotionControl->mcontrol_Text->Text();
    close(F);
  }elsif( Win32::GUI::CommDlgExtendedError() ){$w_Main->MessageBox("Some error occured, sorry",'ERROR');}
  1;
}

my $MotionControlUseMavlinkEmbedding = 0;
my $MotionControlMavlinkBaudrate = 57600;
my $MotionControlMavlinkOriginalBaudrate = 115200;
my $MotionControlMavlinkGuiSysID = '52';
my $MotionControlMavlinkGuiCompID = '43';
my $MotionControlMavlinkBoardSysID = 71; # '47';
my $MotionControlMavlinkBoardCompID = 61; # '43';

sub MotionControlInit{
  if( $MotionControlIsInitialized>0 ){ return; }
  $MotionControlIsInitialized = 1;
  my $xpos= 20;
  my $ypos= 20;

  $w_MotionControl->AddButton( -name=> 'mcontrol_Load', -font=> $StdWinFont,
    -text=> 'Load',
    -pos=> [0,0], -width=>35, -height=>16, # -width=> $xsize-6, -height=>15,
  );
  $w_MotionControl->AddButton( -name=> 'mcontrol_Save', -font=> $StdWinFont,
    -text=> 'Save',
    -pos=> [35,0], -width=>35, -height=>16, # -width=> $xsize-6, -height=>15,
  );
  $w_MotionControl->AddButton( -name=> 'mcontrol_Run', -font=> $StdWinFont,
    -text=> 'Run',
    -pos=> [70,0], -width=>35, -height=>16, # -width=> $xsize-6, -height=>15,
  );

  $w_MotionControl->AddLabel( -name=> 'mcontrol_Title', -font=> $StdWinFont,
    -text=> ' ',
    -pos=> [105,0], -width=> $MotionControlXsize-105-6, -height=>15,
    #-align=>'center', #-background=>$CBlue,
  );

  $w_MotionControl-> AddTextfield( -name=> 'mcontrol_Text', -font=> $MotionControlEditorTextFont, #-font=> $StdWinFont,
    -pos=> [-1,15], -size=> [$MotionControlXsize-4,$MotionControlYsize-42-15], #-size=> [$xsize-14,$ysize-52],
    -hscroll=> 1, -vscroll=> 1,
    -autovscroll=> 1, -autohscroll=> 1,
    -keepselection => 1,
    -multiline=> 1,
  );
} #end of MotionControlInit()

sub MotionControlShow{
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
#  $w_MotionControl->Move($x+100,$y+100);
  $w_MotionControl->Move( $x + $ColNumber*$OPTIONSWIDTH_X+40-15+20-385-180+1 , $y+50-12 );
  TextOut( "\n".'Motion Control Tool started ...'."\n" );
  $w_MotionControl->Show();
  return 1;
}

#COMMENT: this breaks the DoEvents loop, so windows freezes!
sub MotionControlRun{
#  if( not ConnectionIsValid() ){ return 0; }
  DataDisplayHalt();
  my $mc_script = $w_MotionControl->mcontrol_Text->Text();
  $MotionControlUseMavlinkEmbedding = 0;
  #check if mavlinkembedding is enabled
  if( $mc_script =~ /UseMavlinkEmbedding\s*\(.*\)\s*;/i ){
TextOut( "UseMavlinkEmbedding(); found! " );
    $mc_script =~ /(UseMavlinkEmbedding\s*\(.*\)\s*;)/i;
TextOut( "$1!" );
    my $c = eval($1);
    if($@){ TextOut('Motion Control Script ERROR'."\n".$@."\n"); goto ERORR; };
TextOut( "$MotionControlUseMavlinkEmbedding!$MotionControlMavlinkBaudrate!$MotionControlMavlinkGuiSysID!$MotionControlMavlinkGuiCompID!$MotionControlMavlinkBoardSysID!$MotionControlMavlinkBoardCompID" );
  }
  if( $MotionControlUseMavlinkEmbedding == 0 ){
    if( not ConnectToBoard() ){ return 0; }
    TextOut('Motion Control Script Run ... '."\n");
  }else{
    #open port for mavlinkembedding
    DisconnectFromBoard(0);
    $MotionControlMavlinkOriginalBaudrate = $Baudrate;
    $Baudrate = $MotionControlMavlinkBaudrate;
    if( not OpenPort() ){
      TextOut('Motion Control Script ERROR'."\n".'Failed to open port'."\n");
      $Baudrate = $MotionControlMavlinkOriginalBaudrate;
      return 0;
    }
    $Baudrate = $MotionControlMavlinkOriginalBaudrate; #since the port is opened, it can be reset already here
    TextOut('Motion Control Script Run ... (using mavlink embedding)'."\n");
  }
  my $c = eval($mc_script);
  #die $@ if ($@);
  if($@){ TextOut('Motion Control Script ERROR'."\n".$@."\n") };
  if( $MotionControlUseMavlinkEmbedding==0 ){
    SetReadDetailsOut(0);
    ExecuteReadwoFirstReturn();
  }else{
    #close port of mavlinkembedding
    ClosePort();
  }
ERROR:
  TextOut('Motion Control Script DONE'."\n");
  return 1;
}

#SendNativeMavlinkCmdwWriteOnly(():
#  my $sysidcompid = shift;
#  my $msgid = shift; #command
#  my $payload = shift; #payload
#  my $crcextra = shift;
sub SendEmbeddedMavlinkCmd{
  my $msg = shift;
  my $msglen = UCharToHexstr( length($msg)/2 - 1 ); #don't count the msg_id byte
  my $rccmd = 'FA' . $msglen . $msg; #my $rccmd = $RCCMDINSTX . $msglen . $msg; #msg without crc
  while( length($rccmd)<2*28 ){ $rccmd .= '00'; }
  SendNativeMavlinkCmdwWriteOnly(
    UCharToHexstr($MotionControlMavlinkGuiSysID).UCharToHexstr($MotionControlMavlinkGuiCompID), #'52'.'43', #this is the GUI
    UCharToHexstr(76), #UCharToHexstr($MAVLINK_MSG_ID_COMMAND_LONG),
      $rccmd.
      UIntToHexstrSwapped(1235). #UIntToHexstrSwapped($MAV_CMD_TARGET_SPECIFIC). #'D304' . #command #1235 = 04D3
      UCharToHexstr($MotionControlMavlinkBoardSysID).UCharToHexstr($MotionControlMavlinkBoardCompID). #'47' . '43' . # sys ID 71, CompID 67 #this is the STorM32
      '00', #confirmation
    152 #$MAVLINK_MSG_ID_COMMAND_LONG_CRC
  );
}

sub SendMotionContrlCmd{
  if( $MotionControlUseMavlinkEmbedding==0 ){
    SendRcCmd( shift );
  }else{
    SendEmbeddedMavlinkCmd( shift );
  }
}

## motion control convenience function ##

#enables the use of embedded mavlink commands
# baudrate, GCS sysid, GCS compid, STorM32 sysid, STorM32 compid,
sub UseMavlinkEmbedding{
  $MotionControlMavlinkBaudrate = shift;
  $MotionControlMavlinkGuiSysID = shift;
  $MotionControlMavlinkGuiCompID = shift;
  $MotionControlMavlinkBoardSysID = shift;
  $MotionControlMavlinkBoardCompID = shift;
  $MotionControlUseMavlinkEmbedding = 1;
}

#waits the specified time in seconds
# time in 0.1 sec
sub Wait{
  my $timeinsec = shift;
TextOut( 'Wait '.$timeinsec."\n" );
  _delay_ms( 1000*$timeinsec );
}

#triggers the camera shutter
# camera command as string
sub DoCamera{
  my $cmd = uc(shift);
TextOut( 'CMD_DOCAMERA '.$cmd."\n" );
  my $data = '00';
  if( $cmd eq 'SHUTTER' ){ $data = '01'; }
  elsif( $cmd eq 'SHUTTERDELAYED' ){ $data = '02'; }
  elsif( $cmd eq 'VIDEOON' ){ $data = '03'; }
  elsif( $cmd eq 'VIDEOOFF' ){ $data = '04'; }
  my $msg = '0F'. 'aa'.$data.'aaaaaaaa';
  SendMotionContrlCmd( $msg );
}

#sets the angle of the gimbal
sub SetAngle{
  my $pitch = shift;
  my $roll = shift;
  my $yaw = shift;
TextOut( 'CMD_SETANGLE '.$pitch.','.$roll.','.$yaw.',0,0'."\n" );
##  TextOut( $pitch.','.$roll.','.$yaw.',0,0!' );
  my $pitchf = FloatToHexstrSwapped($pitch);
  my $rollf = FloatToHexstrSwapped($roll);
  my $yawf = FloatToHexstrSwapped($yaw);
  my $type = '00'; # type is proper gimbal Euler angles in STorM32 frame (NWU)
  my $flags = '00'; #angles are unlimited
  #$flags= '07';  # all angles are limited
#TextOut('!'.$pitchf.','.$rollf.','.$yawf.','.$flags.','.$type.'!');
  my $msg = '11' . $pitchf . $rollf . $yawf . $flags . $type;
  SendMotionContrlCmd( $msg );
}

#sets the pwm output
sub SetPwmOut{
  my $v = shift;
TextOut( 'CMD_SETPWMOUT '.$v."\n" );
  $v= UIntToHexstrSwapped($v); #$v= UIntToHexstr($v); $v= substr($v,2,2).substr($v,0,2);
  my $msg = '13'. $v;
  SendMotionContrlCmd( $msg );
}

#triggers a recenter of the camera
sub RecenterCamera{
TextOut( 'RecenterCamera'."\n" );
  my $msg1 = '0A' . '0000';
  my $msg2 = '0B' . '0000';
  my $msg3 = '0C' . '0000';
  SendMotionContrlCmd( $msg1 );
  SendMotionContrlCmd( $msg2 );
  SendMotionContrlCmd( $msg3 );
}

#sets a paramter value
# paramter nr or parameter name as string, parameter raw value
sub SetParameter{
  my $nrstr = shift;
  my $value = shift;
  my $nr;
  if( $nrstr =~ /^\d{1,3}$/  ){ #consider this to be a number
    $nr = $nrstr;
  }else{ #assume its a string -> search for it
    $nr = FindOptionAdrByName( $nrstr );
    if( $nr eq '' ){ #parametername is not known, throw an error
      TextOut( 'ERROR: SetParameter('.$nrstr.','.$value.')'."\n" );
      return;
    }
  }
TextOut( 'CMD_SETPARAMETER '.$nr.','.$value."\n" );
  my $s= $nr;
  $s= UCharToHexstr($s).'00';
  my $v= $value;
  if( $v<0 ){ $v = $v+65536; }
  $v= UIntToHexstrSwapped($v); #$v= UIntToHexstr($v); $v= substr($v,2,2).substr($v,0,2);
  my $msg = '04'. $s.$v;
  SendMotionContrlCmd( $msg );
}

#restore parameter to EEPROM value
# parameter nr or parameter name as string
sub RestoreParameter{
  my $nrstr = shift;
  my $nr;
  if( $nrstr =~ /^\d{1,3}$/  ){ #consider this to be a number
    $nr = $nrstr;
  }else{ #assume its a string -> search for it
    $nr = FindOptionAdrByName( $nrstr );
    if( $nr eq '' ){ #parametername is not known, throw an error
      TextOut( 'ERROR: RestoreParameter('.$nrstr.')'."\n" );
      return;
    }
  }
TextOut( 'CMD_RESTOREPARAMETER '.$nr."\n" );
  my $s= $nr;
  $s= UCharToHexstr($s).'00';
  my $msg = UCharToHexstr(20). $s;
  SendMotionContrlCmd( $msg );
}

#restore all parameter to EEPROM value
sub RestoreAllParameters{
TextOut( 'CMD_RESTOREALLPARAMETER'."\n" );
  my $msg = UCharToHexstr(21);
  SendMotionContrlCmd( $msg );
}

# Ende # Motion Control Tool Window
###############################################################################












#-----------------------------------------------------------------------------#
###############################################################################
# NT Module CLI Tool Window
###############################################################################
#    SHARE SETTINGS Tool Window
#    CHECK NT MODULE VERSIONS Tool Window
#    CHANGE BOARD CONFIGURATION Tool Window
#    EDIT BOARD NAME Tool Window
#    GUI BAUDRATE Tool Window
#    ESP8266 Configuration Tool Window
#    NTLogger RTC Configuration Tool Window
#    BLUETOOTH Configuration Tool Window
#    UPDATE Tool Window
#    Motion Control Tool Window
# -> NT Module CLI Tool Window
###############################################################################
#-----------------------------------------------------------------------------#

my $NtCliIsInitialized = 0;

my $NtCliTunnelIsOpen = 0;

my $NtCliBackgroundColor = [96,96,96];

my $NtCliXsize = 450; #700; #450;
my $NtCliYsize = 470;

#my $w_NtCli = Win32::GUI::DialogBox->new( -name=> 'ntcli_Window', -parent => $w_Main, -font=> $StdWinFont,
my $w_NtCli = Win32::GUI::Window->new( -name=> 'ntcli_Window', -parent => $w_Main, -font=> $StdWinFont,
  -text=> "o323BGC NT Module CLI Tool", -size=> [$NtCliXsize,$NtCliYsize],
  -helpbox => 0,
  -background=>$NtCliBackgroundColor,
  -dialogui => 1, #is required for correct ret handling
  -hasminimize => 0, -minimizebox => 0, -hasmaximize => 0, -maximizebox => 0,
);
$w_NtCli->SetIcon($Icon);


sub ntcli_Window_Resize
{
  my $mw = $w_NtCli->ScaleWidth();
  my $mh = $w_NtCli->ScaleHeight();
  $w_NtCli->ntcli_Cmd->Width( $mw - 110 );
  $w_NtCli->ntcli_Send->Left( $mw - 80 );
  $w_NtCli->ntcli_RecieveText->Width( $mw - 3 -8 );
  $w_NtCli->ntcli_RecieveText->Height( $mh - 153 -8 );
}


sub ntcli_Window_Terminate
{
  $w_Main->ntcli_Timer->Kill(1);
  WritePort( '@Q' );
  _delay_ms(50);
  ClosePort();
  $w_NtCli->Hide();
  0;
}


sub NtCliInit
{
  if( $NtCliIsInitialized > 0 ){ return; }
  $NtCliIsInitialized = 1;
  my $xpos = 20;
  my $ypos = 20;
  $w_NtCli->AddLabel( -name=> 'ntcli_Text1_label', -font=> $StdWinFont,
    -text=> "Tool for accessing the CLI of NT modules.",
    -pos=> [$xpos,$ypos], -width=> 420,  -height=>30,
    -background=>$BTConfigBackgroundColor, -foreground=> [255,255,255],
  );
  $ypos += 30;

  $w_NtCli->AddButton( -name=> 'ntcli_OpenIMU1', -font=> $StdWinFont,
    -text=> 'NT IMU1', -pos=> [$xpos,$ypos], -width=> 60,
    -onClick=> sub{ NtCliOpenTunnel('Imu1'); }
  );
  $w_NtCli->AddButton( -name=> 'ntcli_OpenIMU2', -font=> $StdWinFont,
    -text=> 'NT IMU2', -pos=> [$xpos + 1*65,$ypos], -width=> 60,
    -onClick=> sub{ NtCliOpenTunnel('Imu2'); }
  );
  $w_NtCli->AddButton( -name=> 'ntcli_OpenPitch', -font=> $StdWinFont,
    -text=> 'NT Pitch', -pos=> [$xpos + 2*65,$ypos], -width=> 60,
    -onClick=> sub{ NtCliOpenTunnel('Motor Pitch'); }
  );
  $w_NtCli->AddButton( -name=> 'ntcli_OpenRoll', -font=> $StdWinFont,
    -text=> 'NT Roll', -pos=> [$xpos + 3*65,$ypos], -width=> 60,
    -onClick=> sub{ NtCliOpenTunnel('Motor Roll'); }
  );
  $w_NtCli->AddButton( -name=> 'ntcli_OpenYaw', -font=> $StdWinFont,
    -text=> 'NT Yaw', -pos=> [$xpos + 4*65,$ypos], -width=> 60,
    -onClick=> sub{ NtCliOpenTunnel('Motor Yaw'); }
  );
  $w_NtCli->AddButton( -name=> 'ntcli_OpenLogger', -font=> $StdWinFont,
    -text=> 'NT Logger', -pos=> [$xpos + 5*65,$ypos], -width=> 60,
    -onClick=> sub{ NtCliOpenTunnel('Logger'); }
  );

  $w_NtCli->AddButton( -name=> 'ntcli_Close', -font=> $StdWinFont,
    -text=> 'Close Tunnel', -pos=> [$xpos,$ypos+30], -width=> 100,
    -onClick=> sub{ NtCliCloseTunnel(); }
  );

  $xpos = 20;
  $ypos += 65 +10;
  $w_NtCli->AddTextfield( -name=> 'ntcli_Cmd', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos-3],
    -size=> [$NtCliXsize-157-4+46,23],
  );
  $w_NtCli->AddButton( -name=> 'ntcli_Send', -font=> $StdWinFont,
    -text=> 'Send', -pos=> [$NtCliXsize-90,$ypos-3+2], -width=> 60,
    -ok => 1,
  );

  $w_NtCli->ntcli_Cmd->Text('');
  $w_NtCli-> AddTextfield( -name=> 'ntcli_RecieveText',
    -pos=> [5,$NtCliYsize-280-35], -size=> [$NtCliXsize-16,280], -font=> $StdTextFont,
    -vscroll=> 1, -multiline=> 1, -readonly => 1,
    -foreground =>[ 0, 0, 0],
    -background=> [192,192,192],#[96,96,96],
  );

  $NtCliTunnelIsOpen = 0;
} #end of NtCliInit()


sub NtCliSetToTunnelIsOpen
{
  $NtCliTunnelIsOpen = 1;
  $w_NtCli->ntcli_OpenIMU1->Disable();
  $w_NtCli->ntcli_OpenIMU2->Disable();
  $w_NtCli->ntcli_OpenPitch->Disable();
  $w_NtCli->ntcli_OpenRoll->Disable();
  $w_NtCli->ntcli_OpenYaw->Disable();
  $w_NtCli->ntcli_OpenLogger->Disable();
  $w_NtCli->ntcli_Close->Enable();
}

sub NtCliSetToTunnelIsClosed
{
  $NtCliTunnelIsOpen = 0;
  $w_NtCli->ntcli_OpenIMU1->Enable();
  $w_NtCli->ntcli_OpenIMU2->Enable();
  $w_NtCli->ntcli_OpenPitch->Enable();
  $w_NtCli->ntcli_OpenRoll->Enable();
  $w_NtCli->ntcli_OpenYaw->Enable();
  $w_NtCli->ntcli_OpenLogger->Enable();
  $w_NtCli->ntcli_Close->Disable();
}

sub NtCliShow
{
  if( ConnectionIsValid() ){
    DisconnectFromBoard(0); ##it disconnects itself then UARTis removed
  }
  if( not OpenPort() ){ ClosePort(); TextOut( "\n".'NT Module Cli Tool... ABORTED!'."\n" ); return; }
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_NtCli->Move($x+150,$y+100);
  $w_NtCli->ntcli_RecieveText->Text('');
  NtCliSetToTunnelIsClosed();
  $w_NtCli->Show();

  $w_Main->AddTimer( 'ntcli_Timer', 50 ); #every 50ms
}


sub ntcli_Timer_Timer
{
  my $response = ''; my $i = 0; my $s = '';
  do{
    ($i, $s) = ReadPortOneByte();
    if( $i > 0 ){
      my $ss = NtCliStrToReadableStr($s);
      $response .= $ss;
    }
  }while( $i > 0 );
  if( $response ne '' ){ NtCliTextOut($response); }
}


sub ntcli_Send_Click
{
  my $cmd = $w_NtCli->ntcli_Cmd->Text();
  if( $NtCliTunnelIsOpen ){
    if( substr($cmd,-1) ne ';' ){ $cmd .= ";"; } #this can only be done when tunnel is open
  }
  WritePort( $cmd );
  $w_NtCli->ntcli_Cmd->Text('');
  0;
}


sub NtCliTextOut
{
  $w_NtCli->ntcli_RecieveText->Append( PrepareTextForAppend(shift) );
}


sub NtCliStrToReadableStr{
  my $s = shift;
  my $ss = '';
  for(my $i=0; $i<length($s); $i+=1 ){
    my $c = ord( substr($s,$i,1) );
    if( ($c >= ord(' ')) and ($c <= ord('~')) ){
      $ss .= chr($c);
    }elsif( $c == 10 ){
      $ss .= "\n";
    }elsif( $c == 13 ){
    }else{
      $ss .= '.';
    }
  }
  return $ss;
}


my $NtCliCmdTimeOut = 20;


sub NtCliOpenTunnel
{
my $module = shift;
  my ($id,$id2) = NtModuleNameToId($module);
  NtCliTextOut( "\n".'open tunnel to '.$module.'... ' );
#  WritePort('xQTcNTQMODE'.$IDstr);
  my $s = ExecuteCmd( 'xQ' );
  if( substr($s,length($s)-1,1) ne 'o' ){
    NtCliSetToTunnelIsClosed();
    NtCliTextOut( "\n".'open tunnel ... FAILED!'."\n" );
    return 0;
  }
  WritePort('TcNTQMODE'.$id2);
  #wait for a response with a 'Hello'
  my $count = 0; my $result = '';
  my $tmo = GetTickCount() + 150*$NtCliCmdTimeOut;
  while( GetTickCount() < $tmo  ){
    my ($i, $s) = ReadPortOneByte();
    $count += $i;
    $result .= $s;
    Win32::GUI::DoEvents();
    if( substr($result,-5) eq 'Hello' ){ last; }
  };
  if( substr($result,-5) ne 'Hello' ){
    WritePort('@Q'); #we need to send this to bring back the STorM32 controller
    NtCliSetToTunnelIsClosed();
    NtCliTextOut( "\n".'open tunnel ... FAILED!'."\n" );
    return 0;
  }
  #probably all good
  NtCliTextOut( 'ok'."\n" );
  NtCliTextOut($result);
  NtCliSetToTunnelIsOpen();
  return 1;
}


sub NtCliCloseTunnel
{
  WritePort('@Q');
  NtCliTextOut( "\n".'wait... ' );
  _delay_ms(1000);
  NtCliTextOut( "\n".'tunnel closed'."\n\n" );
  NtCliSetToTunnelIsClosed();
}


# Ende # BNT MODULE CLI Tool Window
###############################################################################
