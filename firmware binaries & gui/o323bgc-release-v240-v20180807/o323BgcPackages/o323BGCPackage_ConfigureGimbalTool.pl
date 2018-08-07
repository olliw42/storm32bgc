###############################################################################
# CONFIGURE GIMBAL Tool Window
###############################################################################

my $ConfigureGimbalBackgroundColor = [96,96,96];

my $ConfigureGimbalXsize= 550;
my $ConfigureGimbalYsize= 415;

my $ConfigureGimbalLinkFont;
my $ConfigureGimbalLinkColor= 0x880000; #blue


my $w_ConfigureGimbal= Win32::GUI::DialogBox->new( -name=> 'configuregimbal_Window', -parent => $w_Main, -font=> $StdWinFont,
  -text=> "o323BGC Configure Gimbal Tool",
  -size=> [$ConfigureGimbalXsize,$ConfigureGimbalYsize],
  -helpbox => 0,
  -background=>$ConfigureGimbalBackgroundColor,
);
$w_ConfigureGimbal->SetIcon($Icon);


sub configuregimbal_Window_Terminate
{
  configuregimbal_Cancel_Click(); 0;
}


sub ConfigureGimbalInit
{
  my $xpos = 20;
  my $ypos = 20;
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_Title', -font=> $StdWinFont,
    -text=> 'Welcome',
    -pos=> [$xpos,$ypos], -width=> $ConfigureGimbalXsize -170, -height=>13,
  #  -background=>$ConfigureGimbalBackgroundColor, -foreground=> [255,255,255],
    -align=>'center', -background=>$CBlue,
  );
  $xpos = 20 + $ConfigureGimbalXsize-150;
  $ypos = 55;
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_StepI', -font=> $StdWinFont,
    -text=> 'Steps I',
    -pos=> [$xpos,$ypos],
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 16;
  $w_ConfigureGimbal->AddCheckbox( -name  => 'configuregimbal_Imu1_check', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos], -size=> [12,12],
  );
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_Imu1_check_label', -font=> $StdWinFont,
    -text=> 'Imu1 Orientation',
    -pos=> [$xpos+20,$ypos],
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 16;
  $w_ConfigureGimbal->AddCheckbox( -name  => 'configuregimbal_Imu2_check', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos], -size=> [12,12],
  );
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_Imu2_check_label', -font=> $StdWinFont,
    -text=> 'Imu2 Orientation',
    -pos=> [$xpos+20,$ypos],
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 16;
  $w_ConfigureGimbal->AddCheckbox( -name  => 'configuregimbal_MotorPoles_check', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos], -size=> [12,12],
  );
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_MotorPoles_check_label', -font=> $StdWinFont,
    -text=> 'Motor Poles',
    -pos=> [$xpos+20,$ypos],
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 16;
  $w_ConfigureGimbal->AddCheckbox( -name  => 'configuregimbal_MotorDirectionsI_check', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos], -size=> [12,12],
  );
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_MotorDirectionsI_check_label', -font=> $StdWinFont,
    -text=> 'Motor Directions I',
    -pos=> [$xpos+20,$ypos],
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 2*16;
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_StepII', -font=> $StdWinFont,
    -text=> 'Steps II',
    -pos=> [$xpos,$ypos],
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 16;
  $w_ConfigureGimbal->AddCheckbox( -name  => 'configuregimbal_MotorDirections_check', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos], -size=> [12,12],
  );
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_MotorDirections_check_label', -font=> $StdWinFont,
    -text=> 'Motor Directions',
    -pos=> [$xpos+20,$ypos],
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 16;
  $w_ConfigureGimbal->AddCheckbox( -name  => 'configuregimbal_PitchRollMotorPositions_check', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos], -size=> [12,12],
  );
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_PitchRollMotorPositions_check_label', -font=> $StdWinFont,
    -text=> 'Pitch and Roll Motor
Positions',
    -pos=> [$xpos+20,$ypos], -height=> 26,
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 16 + 13;
  $w_ConfigureGimbal->AddCheckbox( -name  => 'configuregimbal_YawMotorPosition_check', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos], -size=> [12,12],
  );
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_YawMotorPosition_check_label', -font=> $StdWinFont,
    -text=> 'Yaw Motor Position',
    -pos=> [$xpos+20,$ypos],
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 2*16;
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_Finish', -font=> $StdWinFont,
    -text=> 'Finish',
    -pos=> [$xpos,$ypos],
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 16;
  $w_ConfigureGimbal->AddCheckbox( -name  => 'configuregimbal_FinishRestart_check', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos], -size=> [12,12],
  );
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_FinishRestart_check_label', -font=> $StdWinFont,
    -text=> 'Enable Motors and
Restart Gimbal',
    -pos=> [$xpos+20,$ypos], -height=> 26,
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 16 + 13;
  $w_ConfigureGimbal->AddCheckbox( -name  => 'configuregimbal_FinishStore_check', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos], -size=> [12,12],
  );
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_FinishStore_check_label', -font=> $StdWinFont,
    -text=> 'Store in EEPROM',
    -pos=> [$xpos+20,$ypos],
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $xpos = 20;
  $ypos = 55;
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_WelcomeText1', -font=> $StdWinFont,
    -text=> '-',
    -pos=> [$xpos,$ypos], -width=> $ConfigureGimbalXsize -170, -height=>30,
    -background=>$ConfigureGimbalBackgroundColor, -foreground=> $CWhite,
  );
  $ypos += 35 + 1*13;
  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_WelcomeText2', -font=> $StdWinFont,
    -text=> '-',
    -pos=> [$xpos,$ypos], -width=> $ConfigureGimbalXsize -170,  -height=>200,
    -background=>$CGrey128, -foreground=> $CWhite,
  );
#stuff for the motor poles screen
  $xpos = 60;
  $ypos += 21;
  $w_ConfigureGimbal->AddLabel( -name=> 'cg_MotorPolesPitch_label', -font=> $StdWinFont,
    -text=> "Pitch", -pos=> [$xpos,$ypos+20],
    -background=>$CGrey128, -foreground=> $CWhite,
  );
  $w_ConfigureGimbal->AddCombobox( -name=> 'cg_MotorPolesPitch', -font=> $StdWinFont,
    -pos=> [$xpos+$w_ConfigureGimbal->cg_MotorPolesPitch_label->Width()+3,$ypos+20-3], -size=> [60,160],
    -dropdown=> 1, -vscroll=>1,
  );
  $w_ConfigureGimbal->cg_MotorPolesPitch->SetDroppedWidth(60);
  $w_ConfigureGimbal->cg_MotorPolesPitch->Add( ('8','10','12','14','16','18','20','22','24','26','28','42') );
  $w_ConfigureGimbal->AddLabel( -name=> 'cg_MotorPolesRoll_label', -font=> $StdWinFont,
    -text=> "Roll", -pos=> [$xpos+100,$ypos+20],
    -background=>$CGrey128, -foreground=> $CWhite,
  );
  $w_ConfigureGimbal->AddCombobox( -name=> 'cg_MotorPolesRoll', -font=> $StdWinFont,
    -pos=> [$xpos+100+$w_ConfigureGimbal->cg_MotorPolesRoll_label->Width()+3,$ypos+20-3], -size=> [60,160],
    -dropdown=> 1, -vscroll=>1,
  );
  $w_ConfigureGimbal->cg_MotorPolesRoll->SetDroppedWidth(60);
  $w_ConfigureGimbal->cg_MotorPolesRoll->Add( ('8','10','12','14','16','18','20','22','24','26','28','42') );
  $w_ConfigureGimbal->AddLabel( -name=> 'cg_MotorPolesYaw_label', -font=> $StdWinFont,
    -text=> "Yaw", -pos=> [$xpos+200,$ypos+20],
    -background=>$CGrey128, -foreground=> $CWhite,
  );
  $w_ConfigureGimbal->AddCombobox( -name=> 'cg_MotorPolesYaw', -font=> $StdWinFont,
    -pos=> [$xpos+200+$w_ConfigureGimbal->cg_MotorPolesYaw_label->Width()+3,$ypos+20-3], -size=> [60,160],
    -dropdown=> 1, -vscroll=>1,
  );
  $w_ConfigureGimbal->cg_MotorPolesYaw->SetDroppedWidth(60);
  $w_ConfigureGimbal->cg_MotorPolesYaw->Add( ('8','10','12','14','16','18','20','22','24','26','28','42') );
  ConfigureGimbalInit2($xpos,$ypos);

  my $Text2LabelFont= $w_ConfigureGimbal->configuregimbal_WelcomeText2->GetFont();
  my %ConfigureGimbalLinkFontDetails= Win32::GUI::Font::Info( $Text2LabelFont );
  $ConfigureGimbalLinkFontDetails{ '-underline' } = '1';
  $ConfigureGimbalLinkFont= Win32::GUI::Font->new( %ConfigureGimbalLinkFontDetails );
  $ConfigureGimbalLinkColor= 0x880000; #blue

  $w_ConfigureGimbal->AddLabel( -name=> 'configuregimbal_WikiHelp_link',
    -pos=> [0,-1000],
    -text=> "Basic Controller Configuration - Quick Trouble Shooting",
    -font=> $ConfigureGimbalLinkFont, -foreground => $ConfigureGimbalLinkColor, -background=>$CGrey128,
    -notify=>1,
    -onClick=> sub{ ExecuteTool($ConfigureGimbalStepIIHelpLink,''); 1; },
  );

  if( $ActiveBoardConfiguration == $BOARDCONFIGURATION_IS_FOC ){
    ConfigureGimbal_AdaptToBoardConfigurationFoc();
  }else{
    ConfigureGimbal_AdaptToBoardConfigurationDefault();
  }
} #end of ConfigureGimbalInit()


#adapt to encoder version, for the moment simply disable unusable options
# must come after connect, so that $ActiveBoardConfiguration is correctly set
sub ConfigureGimbal_AdaptToBoardConfigurationFoc_Handler
{
  $w_ConfigureGimbal->configuregimbal_MotorPoles_check->Checked(0);
  $w_ConfigureGimbal->configuregimbal_MotorPoles_check->Hide();
  $w_ConfigureGimbal->configuregimbal_MotorPoles_check_label->Hide();
  $w_ConfigureGimbal->configuregimbal_MotorDirectionsI_check->Checked(0);
  $w_ConfigureGimbal->configuregimbal_MotorDirectionsI_check->Hide();
  $w_ConfigureGimbal->configuregimbal_MotorDirectionsI_check_label->Hide();

  $w_ConfigureGimbal->configuregimbal_MotorDirections_check->Checked(0);
  $w_ConfigureGimbal->configuregimbal_MotorDirections_check->Hide();
  $w_ConfigureGimbal->configuregimbal_MotorDirections_check_label->Hide();
  $w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check->Checked(0);
  $w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check->Hide();
  $w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check_label->Hide();
  $w_ConfigureGimbal->configuregimbal_YawMotorPosition_check->Checked(0);
  $w_ConfigureGimbal->configuregimbal_YawMotorPosition_check->Hide();
  $w_ConfigureGimbal->configuregimbal_YawMotorPosition_check_label->Hide();
}

sub ConfigureGimbal_AdaptToBoardConfigurationDefault_Handler
{
  $w_ConfigureGimbal->configuregimbal_MotorPoles_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_MotorPoles_check->Show();
  $w_ConfigureGimbal->configuregimbal_MotorPoles_check_label->Show();
  $w_ConfigureGimbal->configuregimbal_MotorDirectionsI_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_MotorDirectionsI_check->Show();
  $w_ConfigureGimbal->configuregimbal_MotorDirectionsI_check_label->Show();

  $w_ConfigureGimbal->configuregimbal_MotorDirections_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_MotorDirections_check->Show();
  $w_ConfigureGimbal->configuregimbal_MotorDirections_check_label->Show();
  $w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check->Show();
  $w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check_label->Show();
  $w_ConfigureGimbal->configuregimbal_YawMotorPosition_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_YawMotorPosition_check->Show();
  $w_ConfigureGimbal->configuregimbal_YawMotorPosition_check_label->Show();
}


sub ConfigureGimbalHideMotorPoles
{
  $w_ConfigureGimbal->cg_MotorPolesPitch_label->Hide();
  $w_ConfigureGimbal->cg_MotorPolesPitch->Hide();
  $w_ConfigureGimbal->cg_MotorPolesRoll_label->Hide();
  $w_ConfigureGimbal->cg_MotorPolesRoll->Hide();
  $w_ConfigureGimbal->cg_MotorPolesYaw_label->Hide();
  $w_ConfigureGimbal->cg_MotorPolesYaw->Hide();
}


sub ConfigureGimbalShowMotorPoles
{
  $w_ConfigureGimbal->cg_MotorPolesPitch_label->Show();
  $w_ConfigureGimbal->cg_MotorPolesPitch->Show();
  $w_ConfigureGimbal->cg_MotorPolesRoll_label->Show();
  $w_ConfigureGimbal->cg_MotorPolesRoll->Show();
  $w_ConfigureGimbal->cg_MotorPolesYaw_label->Show();
  $w_ConfigureGimbal->cg_MotorPolesYaw->Show();
}


sub ConfigureGimbalSynchroniseMotorPoles
{
  my $Option= $NameToOptionHash{'Pitch Motor Poles'};
  if( defined $Option ){ $w_ConfigureGimbal->cg_MotorPolesPitch->SelectString( GetOptionField($Option) ); }
  $Option= $NameToOptionHash{'Roll Motor Poles'};
  if( defined $Option ){ $w_ConfigureGimbal->cg_MotorPolesRoll->SelectString( GetOptionField($Option) ); }
  $Option= $NameToOptionHash{'Yaw Motor Poles'};
  if( defined $Option ){ $w_ConfigureGimbal->cg_MotorPolesYaw->SelectString( GetOptionField($Option) ); }
}


sub ConfigureGimbalSetMotorPoles
{
  $w_ConfigureGimbal->cg_MotorPolesPitch->SelectString( shift );
  $w_ConfigureGimbal->cg_MotorPolesRoll->SelectString( shift );
  $w_ConfigureGimbal->cg_MotorPolesYaw->SelectString( shift );
}


#stuff for the yaw motor direction screen
my $ConfigureGimbal_AlignUndoandClosePort = 0;
my $ConfigureGimbal_AlignYawOffset = 0;

#the xxxRes fields hold ONLY the payload!!! = 2bytes adr + 2bytes value
my $ConfigureGimbal_RcYawAdr = 0;  #Rc Yaw
my $ConfigureGimbal_RcYawRes = 'c';
my $ConfigureGimbal_RcYawModeAdr = 0;  #Rc Yaw Mode
my $ConfigureGimbal_RcYawModeRes = 'c';
my $ConfigureGimbal_RcYawOffsetAdr = 0;  #Rc Yaw Offset
my $ConfigureGimbal_RcYawOffsetRes = 'c';
my $ConfigureGimbal_RcYawMinAdr = 0;  #Rc Yaw Min
my $ConfigureGimbal_RcYawMinRes = 'c';
my $ConfigureGimbal_RcYawMaxAdr = 0;  #Rc Yaw Max
my $ConfigureGimbal_RcYawMaxRes = 'c';


sub ConfigureGimbalInit2
{
  my $xpos = shift;
  my $ypos = shift;
  $xpos = ($ConfigureGimbalXsize-170)/2+20;
  $ypos += 10;
  $w_ConfigureGimbal->AddButton( -name=> 'cg_AlignYaw_Left3', -font=> $StdWinFont,
    -text=> '<<<', -pos=> [$xpos-15 -3*30-20,$ypos], -width=> 30,
    -onClick => sub{ $ConfigureGimbal_AlignYawOffset += 50; ConfigureGimbalAlignYawMove(); 1; }, #-5°
  );
  $w_ConfigureGimbal->AddButton( -name=> 'cg_AlignYaw_Left2', -font=> $StdWinFont,
    -text=> '<<', -pos=> [$xpos-15 -2*30-15,$ypos], -width=> 30,
    -onClick => sub{ $ConfigureGimbal_AlignYawOffset += 10; ConfigureGimbalAlignYawMove(); 1; }, #-1°
  );
  $w_ConfigureGimbal->AddButton( -name=> 'cg_AlignYaw_Left1', -font=> $StdWinFont,
    -text=> '<', -pos=> [$xpos-15 -1*30-10,$ypos], -width=>30,
    -onClick => sub{ $ConfigureGimbal_AlignYawOffset += 1; ConfigureGimbalAlignYawMove(); 1; }, #-0.1°
  );
  $w_ConfigureGimbal->AddButton( -name=> 'cg_AlignYaw_Right1', -font=> $StdWinFont,
    -text=> '>', -pos=> [$xpos-15 +1*30+10,$ypos], -width=> 30,
    -onClick => sub{ $ConfigureGimbal_AlignYawOffset -= 1; ConfigureGimbalAlignYawMove(); 1; }, #+0.1°
  );
  $w_ConfigureGimbal->AddButton( -name=> 'cg_AlignYaw_Right2', -font=> $StdWinFont,
    -text=> '>>', -pos=> [$xpos-15 +2*30+15,$ypos], -width=> 30,
    -onClick => sub{ $ConfigureGimbal_AlignYawOffset -= 10; ConfigureGimbalAlignYawMove(); 1; }, #+1°
  );
  $w_ConfigureGimbal->AddButton( -name=> 'cg_AlignYaw_Right3', -font=> $StdWinFont,
    -text=> '>>>', -pos=> [$xpos-15 +3*30+20,$ypos], -width=> 30,
    -onClick => sub{ $ConfigureGimbal_AlignYawOffset -= 50; ConfigureGimbalAlignYawMove(); 1; }, #+5°
  );
  $w_ConfigureGimbal->AddLabel( -name=> 'cg_AlignYaw_Offset_label', -font=> $StdWinFont,
    -text=> '0.0°', -pos=> [$xpos-20,$ypos+3], -width=> 40, -align=> 'center',
    -background=>$CGrey128, -foreground=> [255,255,255],
  );
  ConfigureGimbalInit3($xpos,$ypos);
}

sub ConfigureGimbalHideAlignYawButtons
{
  $w_ConfigureGimbal->cg_AlignYaw_Left3->Hide();
  $w_ConfigureGimbal->cg_AlignYaw_Left2->Hide();
  $w_ConfigureGimbal->cg_AlignYaw_Left1->Hide();
  $w_ConfigureGimbal->cg_AlignYaw_Right1->Hide();
  $w_ConfigureGimbal->cg_AlignYaw_Right2->Hide();
  $w_ConfigureGimbal->cg_AlignYaw_Right3->Hide();
  $w_ConfigureGimbal->cg_AlignYaw_Offset_label->Hide();
}

sub ConfigureGimbalShowAlignYawButtons
{
  $w_ConfigureGimbal->cg_AlignYaw_Left3->Show();
  $w_ConfigureGimbal->cg_AlignYaw_Left2->Show();
  $w_ConfigureGimbal->cg_AlignYaw_Left1->Show();
  $w_ConfigureGimbal->cg_AlignYaw_Right1->Show();
  $w_ConfigureGimbal->cg_AlignYaw_Right2->Show();
  $w_ConfigureGimbal->cg_AlignYaw_Right3->Show();
  $w_ConfigureGimbal->cg_AlignYaw_Offset_label->Show();
}

sub ConfigureGimbalAlignYawUndo
{
  TextOut( "\r\n".'Undo...' ); #do the commands in reverse order
  #undo: set Rc Yaw Offset,  Rc Yaw Mode, Rc Yaw
  SendRcCmdwoOut( '04'. $ConfigureGimbal_RcYawMaxRes );
  TextOut( $ConfigureGimbal_RcYawMaxAdr.',' );
  SendRcCmdwoOut( '04'. $ConfigureGimbal_RcYawMinRes );
  TextOut( $ConfigureGimbal_RcYawMinAdr.',' );
  SendRcCmdwoOut( '04'. $ConfigureGimbal_RcYawOffsetRes );
  TextOut( $ConfigureGimbal_RcYawOffsetAdr.',' );
  _delay_ms( 1000 ); #wait to give the Offset command a chance before it is switched off
  SendRcCmdwoOut( '04'. $ConfigureGimbal_RcYawModeRes );
  TextOut( $ConfigureGimbal_RcYawModeAdr.',' );
  SendRcCmdwoOut( '04'. $ConfigureGimbal_RcYawRes );
  TextOut( $ConfigureGimbal_RcYawAdr );
  TextOut( ' ok' );
}

sub ConfigureGimbalAlignYawMove
{
  if( $ConfigureGimbal_AlignYawOffset > 450 ){ $ConfigureGimbal_AlignYawOffset = 450; }
  if( $ConfigureGimbal_AlignYawOffset < -450 ){ $ConfigureGimbal_AlignYawOffset = -450; }
  my $v = $ConfigureGimbal_AlignYawOffset;
  $w_ConfigureGimbal->cg_AlignYaw_Offset_label->Text( sprintf("% .1f°", $v/10.0) );
  if( $v < 0 ){ $v = $v+65536; }
  $v= UIntToHexstrSwapped($v); #$v= UIntToHexstr($v); $v= substr($v,2,2).substr($v,0,2);
  TextOut( "\r\n".'Move...' );
  SendRcCmdwoOut( '04'. UCharToHexstr($ConfigureGimbal_RcYawOffsetAdr).'00'.$v );
  TextOut( ' ok' );
}


sub ConfigureGimbalDisableStepICheckboxes
{
  $w_ConfigureGimbal->configuregimbal_Imu1_check->Disable();
  $w_ConfigureGimbal->configuregimbal_Imu2_check->Disable();
  $w_ConfigureGimbal->configuregimbal_MotorPoles_check->Disable();
  $w_ConfigureGimbal->configuregimbal_MotorDirectionsI_check->Disable();
}

sub ConfigureGimbalDisableStepIICheckboxes
{
  $w_ConfigureGimbal->configuregimbal_MotorDirections_check->Disable();
  $w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check->Disable();
  $w_ConfigureGimbal->configuregimbal_YawMotorPosition_check->Disable();
}

my $ConfigureGimbal_StepNr = 0;
my $ConfigureGimbal_DoStepIIStart = -1;
my $ConfigureGimbal_Imu1No = -1;
my $ConfigureGimbal_Imu2No = -1;


sub ConfigureGimbalInit3
{
  my $xpos=shift; my $ypos=shift;
  $xpos= 20;
  $ypos= $ConfigureGimbalYsize -90;
  $w_ConfigureGimbal->AddButton( -name=> 'configuregimbal_Continue', -font=> $StdWinFont,
    -text=> 'Continue', -pos=> [$ConfigureGimbalXsize/2-40,$ypos], -width=> 80,
  );
  $w_ConfigureGimbal->AddButton( -name=> 'configuregimbal_OK', -font=> $StdWinFont,
    -text=> 'OK', -pos=> [$ConfigureGimbalXsize/2-40,$ypos], -width=> 80,
  );
  $w_ConfigureGimbal->AddButton( -name=> 'configuregimbal_Cancel', -font=> $StdWinFont,
    -text=> 'Cancel', -pos=> [$ConfigureGimbalXsize/2-40,$ypos+30], -width=> 80,
  );
}


sub configuregimbal_Cancel_Click
{
  if( $ConfigureGimbal_AlignUndoandClosePort ){ ConfigureGimbalAlignYawUndo(); }
#  ClosePort();
  TextOut( "\r\n".'Configure Gimbal Tool... ABORTED!'."\r\n");
  $ConfigureGimbalTool_IsRunning= 0;
  $w_ConfigureGimbal->Hide();
  1;
}

sub configuregimbal_OK_Click
{
  $ConfigureGimbal_StepNr = 1;
  ConfigureGimbalDone(); #that's the second run
#  ClosePort();
  TextOut( "\r\n".'Configure Gimbal Tool... DONE'."\r\n");
  $ConfigureGimbalTool_IsRunning= 0;
  m_Read_Click();
  $w_ConfigureGimbal->Hide();
  1;
}

#the Continue Click function is the scheduler
# the scheduling uses the check boxes and the StepNr as state indicator
sub configuregimbal_Continue_Click
{
  $w_ConfigureGimbal->configuregimbal_Continue->Disable();

  if( ($w_ConfigureGimbal->configuregimbal_Imu1_check->Checked() > 0) or
      ($w_ConfigureGimbal->configuregimbal_Imu2_check->Checked() > 0) ){
    ConfigureGimbalDisableStepICheckboxes();
    ConfigureGimbalImuOrientations(); return 1;
  }
  if( $w_ConfigureGimbal->configuregimbal_MotorPoles_check->Checked() > 0 ){
    ConfigureGimbalDisableStepICheckboxes();
    ConfigureGimbalMotorPoles(); return 1;
  }
  if( $w_ConfigureGimbal->configuregimbal_MotorDirectionsI_check->Checked() > 0 ){
    ConfigureGimbalDisableStepICheckboxes();
    ConfigureGimbalMotorDirectionsISetToAuto(); return 1;
  }

  if( ($ConfigureGimbal_DoStepIIStart > 0) and
      (($w_ConfigureGimbal->configuregimbal_MotorDirections_check->Checked() > 0) or
       ($w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check->Checked() > 0) or
       ($w_ConfigureGimbal->configuregimbal_YawMotorPosition_check->Checked() > 0))          ){
    ConfigureGimbalDisableStepICheckboxes();
    if( $ConfigureGimbal_StepNr > 0 ){ ConfigureGimbalDisableStepIICheckboxes(); } #keep them available initially!
    ConfigureGimbalStepIIStart(); return 1;
  }
  if( $w_ConfigureGimbal->configuregimbal_MotorDirections_check->Checked() > 0 ){
    ConfigureGimbalDisableStepIICheckboxes();
    ConfigureGimbalMotorDirections(); return 1;
  }
  if( $w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check->Checked() > 0 ){
    ConfigureGimbalDisableStepIICheckboxes();
    ConfigureGimbalPitchRollMotorPositions(); return 1;
  }
  if( $w_ConfigureGimbal->configuregimbal_YawMotorPosition_check->Checked() > 0 ){
    ConfigureGimbalDisableStepIICheckboxes();
    ConfigureGimbalYawMotorPosition(); return 1;
  }

  ConfigureGimbalDisableStepICheckboxes();
  ConfigureGimbalDisableStepIICheckboxes();
  $ConfigureGimbal_StepNr = 0;
  ConfigureGimbalDone();
  return 1;
}


# ConfigureGimbal: Welcome Page
sub ConfigureGimbalShow
{
  my $Option; my $res1; my $res2; my $res3;
  DataDisplayHalt();
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_ConfigureGimbal->Move($x+110,$y+100);

  ConfigureGimbalHideMotorPoles();
  ConfigureGimbalHideAlignYawButtons();

  $w_ConfigureGimbal->configuregimbal_Imu1_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_Imu1_check->Enable();
  $w_ConfigureGimbal->configuregimbal_Imu2_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_Imu2_check->Enable();
  $w_ConfigureGimbal->configuregimbal_MotorPoles_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_MotorPoles_check->Enable();
  $w_ConfigureGimbal->configuregimbal_MotorDirectionsI_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_MotorDirectionsI_check->Enable();

  $w_ConfigureGimbal->configuregimbal_MotorDirections_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_MotorDirections_check->Enable();
  $w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check->Enable();
  $w_ConfigureGimbal->configuregimbal_YawMotorPosition_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_YawMotorPosition_check->Enable();

  $w_ConfigureGimbal->configuregimbal_FinishRestart_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_FinishRestart_check->Enable();
  $w_ConfigureGimbal->configuregimbal_FinishStore_check->Checked(1);
  $w_ConfigureGimbal->configuregimbal_FinishStore_check->Enable();

  $w_ConfigureGimbal->configuregimbal_Title->Text( 'Welcome' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText1->Text(
    'This tool allows you to set up those parameters, which are crucial for a correct gimbal operation.' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'Connecting to board... Please wait!' );

  $w_ConfigureGimbal->configuregimbal_Continue->Disable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  $w_ConfigureGimbal->configuregimbal_OK->Disable();
  $w_ConfigureGimbal->configuregimbal_OK->Hide();
  $w_ConfigureGimbal->configuregimbal_Cancel->Enable();
  $w_ConfigureGimbal->configuregimbal_Cancel->Show();

  $w_ConfigureGimbal->configuregimbal_WikiHelp_link->Hide();

  if( $ActiveBoardConfiguration == $BOARDCONFIGURATION_IS_FOC ){
    ConfigureGimbal_AdaptToBoardConfigurationFoc();
  }else{
    ConfigureGimbal_AdaptToBoardConfigurationDefault();
  }

  $w_ConfigureGimbal->Show();
  Win32::GUI::DoEvents();

  TextOut( "\r\n".'Configure Gimbal Tool...' );
  SetDoFirstReadOut(0);
  $ConfigureGimbalTool_IsRunning = 1;
  if( not ConnectionIsValid() ){
    if( not OpenPort() ){ ClosePort(); $ConfigureGimbalTool_IsRunning = 0; goto WERROR; }
    ClosePort(); #close it again
    ConnectToBoardwoRead();
  }
  #if a change in BoardConfiguration happens, this had been handled by ConnectToBoard

  TextOut( "\r\n".'Check connection...' );
  $res1 = ExecuteCmd( 's', $CMD_s_PARAMETER_ZAHL*2 );
  if( substr($res1,length($res1)-1,1) ne 'o' ){ goto WERROR; }
  TextOut( ' ok' );

  TextOut( "\r\n".'Disable all motors...' );
  $Option = $NameToOptionHash{'Pitch Motor Usage'};
  $res1 = SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'.'0300' );
  if( $res1 =~ /[tc]/ ){ goto WERROR; }
  SetOptionField( $Option, 3 );
  $Option = $NameToOptionHash{'Roll Motor Usage'};
  $res2 = SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'.'0300' );
  if( $res2 =~ /[tc]/ ){ goto WERROR; }
  SetOptionField( $Option, 3 );
  $Option = $NameToOptionHash{'Yaw Motor Usage'};
  $res3 = SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'.'0300' );
  if( $res3 =~ /[tc]/ ){ goto WERROR; }
  SetOptionField( $Option, 3 );
  TextOut( ' ok' );

  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
'Please choose on the right the tasks, which you want to get done.

For a first setup have all options checked.

Please note:
- The motors were just disabled, as well as a heartbeat.
- Any changes to the parameters in the GUI, which you haven\'t written
  to the board, will be lost.
- Several parameters will be modified in the course of the process, and
  correctness cannot be ensured in the case of a premature abort. Do a
  >Read< and double-check.

Press >Continue< to go on.'
  );
  $ConfigureGimbal_Imu1No = -1;
  $ConfigureGimbal_Imu2No = -1;
  $ConfigureGimbal_DoStepIIStart = 1;
  $ConfigureGimbal_AlignUndoandClosePort = 0;
  $ConfigureGimbal_AlignYawOffset = 0;
  $ConfigureGimbal_StepNr = 0;
  $w_ConfigureGimbal->configuregimbal_Continue->Enable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  return;
WERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n".
    'Connection to board failed!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
}


# ConfigureGimbal: StepI Imu Orientations Page
sub ConfigureGimbalImuOrientations
{
  $w_ConfigureGimbal->configuregimbal_Continue->Disable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  my $doimu1 = $w_ConfigureGimbal->configuregimbal_Imu1_check->Checked();
  my $doimu2 = $w_ConfigureGimbal->configuregimbal_Imu2_check->Checked();
  my $s;
### do the FIRST PART
if($ConfigureGimbal_StepNr==0){
  $w_ConfigureGimbal->configuregimbal_Title->Text( 'Imu Orientations' );
  if( $doimu1 and $doimu2 ){
    $s = 'In this step, the orienation parameters for both Imu1 and Imu2 will be determined.';
  }elsif( $doimu1 ){
    $s = 'In this step, the orienation parameter for Imu1 will be determined.';
  }elsif( $doimu2 ){
    $s = 'In this step, the orienation parameter for Imu2 will be determined.';
  }else{ while(1){;} }#should not happen!
  $w_ConfigureGimbal->configuregimbal_WelcomeText1->Text( $s );
  #check if imus are present and healthy
  $s = ExecuteCmd( 's', $CMD_s_PARAMETER_ZAHL*2 );
  if( substr($s,length($s)-1,1) ne 'o' ){ goto WERROR; }
  my @data = unpack( "v$CMD_s_PARAMETER_ZAHL", $s );
  my $status= UIntToBitstr( $data[$DataStatus_p] ); #status
  $s = '';
  if( $doimu1 and (not CheckStatus($status,$STATUS_IMU_PRESENT)) ){
    $s .= 'Imu1 is not present or not healthy!' . "\r\n";
  }
  if( $doimu2 and (not CheckStatus($status,$STATUS_IMU2_PRESENT)) ){
    $s .= 'Imu2 is not present or not healthy!' . "\r\n";
  }
  if( $s ne '' ){
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $s. "\r\n" . 'Press >Cancel<.' );
    return;
  }
  #check if NT bus is healthy
  my $NTBusErrors = $data[$DataError_p]; #NT bus error
  if( $NTBusErrors > 10 ){ goto NTBUSERROR; }
  #prepare next part
  if( $doimu1 ){
    $s= 'Please level the CAMERA roughly by hand (should be within +-15°).' ."\r\n". "\r\n".
        'Press >Continue< to go on.';
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $s );
    $ConfigureGimbal_StepNr = 1;
    $w_ConfigureGimbal->configuregimbal_Continue->Enable();
    $w_ConfigureGimbal->configuregimbal_Continue->Show();
    return;
  }else{
    $ConfigureGimbal_StepNr = 1;
  }
}
### do the SECOND PART
if( $ConfigureGimbal_StepNr == 1 ){
  $ConfigureGimbal_Imu1No = -1;
  $ConfigureGimbal_Imu2No = -1;

### STEP: find imu z orientations
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'Reading imu z orientation(s) ... Please wait!' );
  my $a1xF=0; my $a1yF=0; my $a1zF=0; my $a2xF=0; my $a2yF=0; my $a2zF=0;
  my $a1x=0; my $a1y=0; my $a1z=0; my $a2x=0; my $a2y=0; my $a2z=0;
  my $imu1z = ''; my $imu2z = '';
  my $i; my $n;
  my $imu1loop = $doimu1; my $imu2loop = $doimu2;
  ## LOOP: find imu z orientations
  $i = 20*30; #30sec
  while( $imu1loop or $imu2loop ){
    if( $i==0 ){ goto TIMEOUT; last; } $i--; #maximal 30sec
    Win32::GUI::DoEvents();
    if( not $w_ConfigureGimbal->IsVisible() ){ return; }
    _delay_ms(50);
    my $s = ExecuteCmd( 'Cd', $CMD_Cd_PARAMETER_ZAHL*2 );
    my @CdData = unpack( "v$CMD_Cd_PARAMETER_ZAHL", $s );
    for(my $n=0;$n<$CMD_Cd_PARAMETER_ZAHL;$n++){
      if( substr($CdDataFormatStr,$n,1) eq 's' ){ if( $CdData[$n]>32768 ){ $CdData[$n]-=65536; }  }
    }
    $a1xF+= 0.1*($CdData[0]-$a1xF); $a1yF+= 0.1*($CdData[1]-$a1yF); $a1zF+= 0.1*($CdData[2]-$a1zF);
    $a2xF+= 0.1*($CdData[7]-$a2xF); $a2yF+= 0.1*($CdData[8]-$a2yF); $a2zF+= 0.1*($CdData[9]-$a2zF);
    $a1x = $a1xF; $a1y = $a1yF; $a1z = $a1zF;
    my $a1norm = sqrt( $a1x*$a1x + $a1y*$a1y + $a1z*$a1z );
    if( not $doimu1 or ($a1norm < 100) ){ $imu1loop = 0; }
    if( $imu1loop ){  #0.85 = 31.8°, 0.9 = 25.8°
      $a1x /= $a1norm; $a1y /= $a1norm; $a1z /= $a1norm;
      if( $a1x > +0.85 ){ $imu1z = '+x'; } if( $a1x < -0.85 ){ $imu1z = '-x'; }
      if( $a1y > +0.85 ){ $imu1z = '+y'; } if( $a1y < -0.85 ){ $imu1z = '-y'; }
      if( $a1z > +0.85 ){ $imu1z = '+z'; } if( $a1z < -0.85 ){ $imu1z = '-z'; }
      if( $imu1z ne '' ){ $imu1loop = 0; }#stop
    }
    $a2x = $a2xF; $a2y = $a2yF; $a2z = $a2zF;
    my $a2norm = sqrt( $a2x*$a2x + $a2y*$a2y + $a2z*$a2z );
    if( not $doimu2 or ($a2norm < 100) ){ $imu2loop = 0; }
    if( $imu2loop ){
      $a2x /= $a2norm; $a2y /= $a2norm; $a2z /= $a2norm;
      if( $a2x > +0.85 ){ $imu2z = '+x'; } if( $a2x < -0.85 ){ $imu2z = '-x'; }
      if( $a2y > +0.85 ){ $imu2z = '+y'; } if( $a2y < -0.85 ){ $imu2z = '-y'; }
      if( $a2z > +0.85 ){ $imu2z = '+z'; } if( $a2z < -0.85 ){ $imu2z = '-z'; }
      if( $imu2z ne '' ){ $imu2loop = 0; }#stop
    }
  }
#TextOut( "imu1z: ".$imu1z." , imu2z: ".$imu2z."\r\n" );
  _delay_ms(500);

### STEP: find imu z orientations
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'Please pitch (tilt) both the camera and gimbal down by ca. 45°, without rolling!'. "\r\n".
    'Hold them in this positon until the imu orientation(s) got detected.' . "\r\n"."\r\n".
    'You have ca. 2 min time before a timeout occurs.' . "\r\n". "\r\n".
    'Reading imu x orientation(s) ... Please wait!' );
  $a1xF=0; $a1yF=0; $a1zF=0; $a2xF=0; $a2yF=0; $a2zF=0;
  my $a1xT=0; my $a1yT=0; my $a1zT=0; my $a2xT=0; my $a2yT=0; my $a2zT=0;
  my $imu1x = '';  my $imu2x = '';
  $imu1loop = $doimu1; $imu2loop = $doimu2;
  ## LOOP: find imu x orientations
  $i = 2*20*40; #40sec
  while( $imu1loop or $imu2loop ){
    $i--; #maximal 30sec
    if( $i==0 ){ goto TIMEOUT; last; } ######TIMEOUT!!!!
    Win32::GUI::DoEvents();
    if( not $w_ConfigureGimbal->IsVisible() ){ return; }
    _delay_ms(50);
    my $s= ExecuteCmd( 'Cd', $CMD_Cd_PARAMETER_ZAHL*2 );
    my @CdData = unpack( "v$CMD_Cd_PARAMETER_ZAHL", $s );
    for(my $n=0;$n<$CMD_Cd_PARAMETER_ZAHL;$n++){
      if( substr($CdDataFormatStr,$n,1) eq 's' ){ if( $CdData[$n]>32768 ){ $CdData[$n]-=65536; }  }
    }
    $a1xF+= 0.1*($CdData[0]-$a1xF); $a1yF+= 0.1*($CdData[1]-$a1yF); $a1zF+= 0.1*($CdData[2]-$a1zF);
    $a2xF+= 0.1*($CdData[7]-$a2xF); $a2yF+= 0.1*($CdData[8]-$a2yF); $a2zF+= 0.1*($CdData[9]-$a2zF);
    $a1xT = $a1xF; $a1yT = $a1yF; $a1zT = $a1zF;
    my $a1norm = sqrt( $a1xT*$a1xT + $a1yT*$a1yT + $a1zT*$a1zT );
    if( not $doimu1 or ($a1norm < 100) ){ $imu1loop = 0; }
    if( $imu1loop ){
      $a1xT /= $a1norm; $a1yT /= $a1norm; $a1zT /= $a1norm;
      if( $imu1z =~ m/x/ ){ #look for +-y or +-z
        if(( abs($a1yT)>0.35 )and( abs($a1zT)<0.3 )){ if( $a1yT<0 ){$imu1x = '+y';}else{$imu1x = '-y';} }
        if(( abs($a1zT)>0.35 )and( abs($a1yT)<0.3 )){ if( $a1zT<0 ){$imu1x = '+z';}else{$imu1x = '-z';} }
      }
      if( $imu1z =~ m/y/ ){ #look for +-x or +-z#if( $imu1z =~ m/y/ ){ #look for +-x or +-z
        if(( abs($a1xT)>0.35 )and( abs($a1zT)<0.3 )){ if( $a1xT<0 ){$imu1x = '+x';}else{$imu1x = '-x';} }
        if(( abs($a1zT)>0.35 )and( abs($a1xT)<0.3 )){ if( $a1zT<0 ){$imu1x = '+z';}else{$imu1x = '-z';} }
      }
      if( $imu1z =~ m/z/ ){ #look for +-x or +-y
        if(( abs($a1xT)>0.35 )and( abs($a1yT)<0.3 )){ if( $a1xT<0 ){$imu1x = '+x';}else{$imu1x = '-x';} }
        if(( abs($a1yT)>0.35 )and( abs($a1xT)<0.3 )){ if( $a1yT<0 ){$imu1x = '+y';}else{$imu1x = '-y';} }
      }
      if( $imu1x ne '' ){ $imu1loop=0; }#stop
    }
    $a2xT = $a2xF; $a2yT = $a2yF; $a2zT = $a2zF;
    my $a2norm = sqrt( $a2xT*$a2xT + $a2yT*$a2yT + $a2zT*$a2zT );
    if( not $doimu2 or ($a2norm < 100) ){ $imu2loop = 0; }
    if( $imu2loop ){
      $a2xT /= $a2norm; $a2yT /= $a2norm; $a2zT /= $a2norm;
      if( $imu2z =~ m/x/ ){ #look for +-y or +-z
        if(( abs($a2yT)>0.35 )and( abs($a2zT)<0.3 )){ if( $a2yT<0 ){$imu2x = '+y';}else{$imu2x = '-y';} }
        if(( abs($a2zT)>0.35 )and( abs($a2yT)<0.3 )){ if( $a2zT<0 ){$imu2x = '+z';}else{$imu2x = '-z';} }
      }
      if( $imu2z =~ m/y/ ){ #look for +-x or +-z#if( $imu1z =~ m/y/ ){ #look for +-x or +-z
        if(( abs($a2xT)>0.35 )and( abs($a2zT)<0.3 )){ if( $a2xT<0 ){$imu2x = '+x';}else{$imu2x = '-x';} }
        if(( abs($a2zT)>0.35 )and( abs($a2xT)<0.3 )){ if( $a2zT<0 ){$imu2x = '+z';}else{$imu2x = '-z';} }
      }
      if( $imu2z =~ m/z/ ){ #look for +-x or +-y
        if(( abs($a2xT)>0.35 )and( abs($a2yT)<0.3 )){ if( $a2xT<0 ){$imu2x = '+x';}else{$imu2x = '-x';} }
        if(( abs($a2yT)>0.35 )and( abs($a2xT)<0.3 )){ if( $a2yT<0 ){$imu2x = '+y';}else{$imu2x = '-y';} }
      }
      if( $imu2x ne '' ){ $imu2loop=0; }#stop
    }
  }
#TextOut( "imu1x: ".$imu1x." , imu2x: ".$imu2x."\r\n" );
  #FIND matching orientation
  my $option1; my $option2;
  $n = 0;
  foreach my $o (@ImuOrientationList){
    if(( substr($o->{axes},0,2) eq $imu1x )and( substr($o->{axes},6,2) eq $imu1z )){
      $option1 = $o; $ConfigureGimbal_Imu1No = $n;
    }
    if(( substr($o->{axes},0,2) eq $imu2x )and( substr($o->{axes},6,2) eq $imu2z )){
      $option2 = $o; $ConfigureGimbal_Imu2No = $n;
    }
    $n++;
  }
#TextOut( "imu1: ".$option1->{axes}." , imu2: ".$option2->{axes}."\r\n" );
  $s = 'Imu orientations found.'."\r\n";
  if( $doimu1 ){
    $s .= '  Imu1 Orientation = no.'.$ConfigureGimbal_Imu1No.': '.$option1->{name}.'  '.AxesRemovePlus($option1->{axes})."\r\n";
  }
  if( $doimu2 ){
    $s .= '  Imu2 Orientation = no.'.$ConfigureGimbal_Imu2No.': '.$option2->{name}.'  '.AxesRemovePlus($option2->{axes})."\r\n";
  }
  $s .= "\r\n".'Press >Continue< to write the value(s) to the board, and to continue.';
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $s );
  $ConfigureGimbal_StepNr = 2;
  $w_ConfigureGimbal->configuregimbal_Continue->Enable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  return;
}
### do the LAST PART
if( $ConfigureGimbal_StepNr == 2 ){
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( 'Writing imu orientation(s) ... Please wait!');
  _delay_ms(500);
  #set Motor Usages
  TextOut( "\r\n".'Writing imu orientation(s)...' );
  my $Option; my $res1 =''; my $res2 = '';
  if( $doimu1 and ($ConfigureGimbal_Imu1No >= 0) ){
    $Option= $NameToOptionHash{'Imu Orientation'};
    $res1= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. UCharToHexstr($ConfigureGimbal_Imu1No).'00' );
    if( $res1 =~ /[tc]/ ){ goto WERROR; }
    SetOptionField( $Option, $ConfigureGimbal_Imu1No );
  }
  if( $doimu2 and ($ConfigureGimbal_Imu2No >= 0) ){
    $Option= $NameToOptionHash{'Imu2 Orientation'};
    $res2= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. UCharToHexstr($ConfigureGimbal_Imu2No).'00' );
    if( $res2 =~ /[tc]/ ){ goto WERROR; }
    SetOptionField( $Option, $ConfigureGimbal_Imu2No );
  }
  TextOut( ' ok' );
  #finish things, and go to next page
  $w_ConfigureGimbal->configuregimbal_Imu1_check->Checked(0);
  $w_ConfigureGimbal->configuregimbal_Imu2_check->Checked(0);
  $ConfigureGimbal_StepNr = 0;
  configuregimbal_Continue_Click();
  return;
}
# http://www.olliw.eu/storm32bgc-wiki/Getting_Started#Basic_Controller_Configuration_Quick_Trouble_Shooting
# IMU1ERROR: this is done explicitely in the above for nicer display
# IMU2ERROR: this is done explicitely in the above for nicer display
NTBUSERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
#    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n". "\r\n".
    'NTBUS errors occured!' . "\r\n" .
    'For further help see the STorM32 wiki at' . "\r\n" .
    ''. "\r\n". "\r\n".
    'Press >Cancel<.' );
  goto WIKILINK;
WIKILINK:
  my $tx = 20; my $ty = 55 + 35 + 1*13;
  $w_ConfigureGimbal->configuregimbal_WikiHelp_link->Move( $tx, $ty + 2*13 );
  $w_ConfigureGimbal->configuregimbal_WikiHelp_link->Show();
  return;
TIMEOUT:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n".
    'Reading imu orientation(s) aborted ... TIMEOUT!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
  return;
WERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n".
    'Writing to board failed!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
}


# ConfigureGimbal: StepI Motor Poles Page
sub ConfigureGimbalMotorPoles
{
  $w_ConfigureGimbal->configuregimbal_Continue->Disable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  my $Option; my $res1; my $res2; my $res3; my $poles;
### do the FISRT PART
if($ConfigureGimbal_StepNr==0){
  $w_ConfigureGimbal->configuregimbal_Title->Text( 'Motor Poles' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText1->Text(
    'In this step, the motor pole parameters will be configured.' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'Set the number of motor poles for each motor:' . "\r\n". "\r\n". "\r\n". "\r\n". "\r\n". "\r\n".
    'Please note:
- The number of poles is the number of magnets in the motor bell.
- In a notation like 12N14P the motor pole number is 14.' . "\r\n". "\r\n".
    'Press >Continue< to write the values to the board, and to continue.' );
  ConfigureGimbalShowMotorPoles();
  ConfigureGimbalSetMotorPoles( 14, 14, 14 );
  $ConfigureGimbal_StepNr= 1;
  $w_ConfigureGimbal->configuregimbal_Continue->Enable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  return;
}
### do the LAST PART
if($ConfigureGimbal_StepNr==1){
  ConfigureGimbalHideMotorPoles();
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'Writing motor pole parameters ... Please wait!' );
  _delay_ms(500);
  #set Motor Poles
  TextOut( "\r\n".'Writing motor pole parameters...' );
  $res1 =''; $res2 = ''; $res3 = '';
  $Option= $w_ConfigureGimbal->cg_MotorPolesPitch;
  $poles= $Option->GetString($Option->SelectedItem());
  if( $poles>=8 ){
    $Option= $NameToOptionHash{'Pitch Motor Poles'};
    $res1= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. UCharToHexstr($poles).'00' );
    if( $res1 =~ /[tc]/ ){ goto WERROR; }
    SetOptionField( $Option, $poles );
  }
  $Option= $w_ConfigureGimbal->cg_MotorPolesRoll;
  $poles= $Option->GetString($Option->SelectedItem());
  if( $poles>=8 ){
    $Option= $NameToOptionHash{'Roll Motor Poles'};
    $res1= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. UCharToHexstr($poles).'00' );
    if( $res1 =~ /[tc]/ ){ goto WERROR; }
    SetOptionField( $Option, $poles );
  }
  $Option= $w_ConfigureGimbal->cg_MotorPolesYaw;
  $poles= $Option->GetString($Option->SelectedItem());
  if( $poles>=8 ){
    $Option= $NameToOptionHash{'Yaw Motor Poles'};
    $res1= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. UCharToHexstr($poles).'00' );
    if( $res1 =~ /[tc]/ ){ goto WERROR; }
    SetOptionField( $Option, $poles );
  }
  TextOut( ' ok' );
  #finish things, and go to next page
  $w_ConfigureGimbal->configuregimbal_MotorPoles_check->Checked(0);
  $ConfigureGimbal_StepNr = 0;
  configuregimbal_Continue_Click();
  return;
}
WERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n".
    'Writing to board failed!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
}


# ConfigureGimbal: StepI Motor Directions I Page
sub ConfigureGimbalMotorDirectionsISetToAuto
{
  $w_ConfigureGimbal->configuregimbal_Continue->Disable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  my $Option; my $res1; my $res2;  my $res3;
### do the FIRST PART
if($ConfigureGimbal_StepNr==0){
  $w_ConfigureGimbal->configuregimbal_Title->Text( 'Motor Directions I' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText1->Text(
    'In this step, the motor direction parameters will be prepared.' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'The motor direction parameters will be configured to \'auto\'.' . "\r\n". "\r\n".
    'Press >Continue< to write the values to the board, and to continue.' );
  $ConfigureGimbal_StepNr= 1;
  $w_ConfigureGimbal->configuregimbal_Continue->Enable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  return;
}
### do the LAST PART
if($ConfigureGimbal_StepNr==1){
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'Writing motor direction parameters ... Please wait!' );
  _delay_ms(500);
  #set Motor Directions to auto
  TextOut( "\r\n".'Writing motor direction parameters...' );
  $res1 =''; $res2 = ''; $res3 = '';
  $Option= $NameToOptionHash{'Pitch Motor Direction'};
  $res1= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. '0200' );
  if( $res1 =~ /[tc]/ ){ goto WERROR; }
  SetOptionField( $Option, 2 );
  $Option= $NameToOptionHash{'Roll Motor Direction'};
  $res2= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. '0200' );
  if( $res2 =~ /[tc]/ ){ goto WERROR; }
  SetOptionField( $Option, 2 );
  $Option= $NameToOptionHash{'Yaw Motor Direction'};
  $res3= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. '0200' );
  if( $res3 =~ /[tc]/ ){ goto WERROR; }
  SetOptionField( $Option, 2 );
  TextOut( ' ok' );
  #finish things, and go to next page
  $w_ConfigureGimbal->configuregimbal_MotorDirectionsI_check->Checked(0);
  $ConfigureGimbal_StepNr = 0;
  configuregimbal_Continue_Click();
  return;
}
WERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n".
    'Writing to board failed!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
}


# ConfigureGimbal: StepII Restart Gimbal Page
sub ConfigureGimbalStepIIStart
{
  $w_ConfigureGimbal->configuregimbal_Continue->Disable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  my $Option; my $res1; my $res2;  my $res3; my $s;
### do the FIRST PART
if($ConfigureGimbal_StepNr==0){
  $w_ConfigureGimbal->configuregimbal_Title->Text( 'Restart Gimbal' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText1->Text(
    'In this step, the gimbal will be prepared and restarted.' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'The gimbal needs to be restarted and be in NORMAL state for the next steps to work.'. "\r\n"."\r\n".
    'This may fail in rare cases, when the PID parameters are grossly wrong. '.
    'If in doubt skip Step II by unchecking all of them, and store the '.
    'current settings and restart the gimbal by checking the Finish options. '.
    'Do a coarse PID tuning, and repeat this tool (you may skip Steps I).

Please note:
- The motors will be enabled and the gimbal restarted.
- A battery needs to be connected to the board.' . "\r\n". "\r\n".
    'Press >Continue< to initiate the restart.' );
  $ConfigureGimbal_StepNr= 1;
  $w_ConfigureGimbal->configuregimbal_Continue->Enable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  return;
}
### do the SECOND PART
if($ConfigureGimbal_StepNr==1){
  my $InfoText = '';
  #wait until battery is connected, otherwise the restart will progress to Normal without leveling and auto motor dir detection
  # check also if IMU is present and healthy
  $InfoText .= 'Check for battery ... ';
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $InfoText.'Please wait!' );
  _delay_ms(500);
  my $checkvoltageloop = 1;
  TextOut_( "\r\n".'Check for battery... ' );
  while( $checkvoltageloop ){
    Win32::GUI::DoEvents();
    if( not $w_ConfigureGimbal->IsVisible() ){ return; }
    $s= ExecuteCmd( 's', $CMD_s_PARAMETER_ZAHL*2 ); ###5*2 );
    if( substr($s,length($s)-1,1) ne 'o' ){ goto WERROR };
    my @data = unpack( "v$CMD_s_PARAMETER_ZAHL", $s );
    my $status= UIntToBitstr( $data[$DataStatus_p] ); #status
    if( not CheckStatus($status,$STATUS_IMU_PRESENT) ){ goto IMUERROR; }
    if( CheckStatus($status,$STATUS_BAT_ISCONNECTED) and not CheckStatus($status,$STATUS_BAT_VOLTAGEISLOW) ){
      $checkvoltageloop= 0; last;
    }
    if( $checkvoltageloop==1 ){
      $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
        $InfoText. "\r\n". "\r\n". 'PLEASE CONNECT A BATTERY!' );
      $checkvoltageloop= 2;
    }
    _delay_ms(100);
  }
  TextOut_( 'ok' );
  $InfoText .=  'ok'. "\r\n";
  $InfoText .= 'Enable all motors and restart the gimbal ... ';
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $InfoText.'Please wait!' );
  _delay_ms(500);
  #set startup mode to normal, just in case
  TextOut( "\r\n".'Set startup mode to normal...' );
  $res1 ='';
  $Option= $NameToOptionHash{'Startup Mode'};
  $res1= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. '0000' );
  if( $res1 =~ /[tc]/ ){ goto WERROR; }
  TextOut( ' ok' );
  SetOptionField( $Option, 0 );
  #set motor directions to auto, just in case
  if( $w_ConfigureGimbal->configuregimbal_MotorDirections_check->Checked()>0 ){
    #$InfoText .= 'Setting motor directions to \'auto\' ... ';
    #$w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $InfoText.'Please wait!' );
    #_delay_ms(500);
    #set Motor Directions to auto
    TextOut( "\r\n".'Writing motor direction parameters...' );
    $res1 =''; $res2 = ''; $res3 = '';
    $Option= $NameToOptionHash{'Pitch Motor Direction'};
    $res1= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. '0200' );
    if( $res1 =~ /[tc]/ ){ goto WERROR; }
    SetOptionField( $Option, 2 );
    $Option= $NameToOptionHash{'Roll Motor Direction'};
    $res2= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. '0200' );
    if( $res2 =~ /[tc]/ ){ goto WERROR; }
    SetOptionField( $Option, 2 );
    $Option= $NameToOptionHash{'Yaw Motor Direction'};
    $res3= SendRcCmdwoOut( '04'. UCharToHexstr($Option->{adr}).'00'. '0200' );
    if( $res3 =~ /[tc]/ ){ goto WERROR; }
    SetOptionField( $Option, 2 );
    TextOut( ' ok' );
    #$InfoText .=  'ok'. "\r\n";
  }
  #enable motors and restart
  TextOut( "\r\n".'Enable all motors and restart controller...' );
  $s= ExecuteCmd( 'xW' );
  if( $s eq 'o' ){ TextOut_( 'ok' ); }else{ goto WERROR; }
  #set Motor Usages
  SetOptionField( $NameToOptionHash{'Pitch Motor Usage'}, 0 );
  SetOptionField( $NameToOptionHash{'Roll Motor Usage'}, 0 );
  SetOptionField( $NameToOptionHash{'Yaw Motor Usage'}, 0 );
  #read the status until its normal
  $InfoText .=  'ok'. "\r\n". 'Waiting for NORMAL state ... ';
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $InfoText.'Please wait!' );
  _delay_ms(1000); #wait a bit longer for board to startup
  my $checkstatusloop = 1;
  my $comporterrorcount = 10; ##this is needed since UART sends some startup info stuff, good mechanism
  my $normalreachedwaitcount = 10; ##lets the loop wait 1sec after NORNMAL was reached
  TextOut_( "\r\n".'Waiting for NORMAL state... ' );
  while( $checkstatusloop ){
    Win32::GUI::DoEvents();
    if( not $w_ConfigureGimbal->IsVisible() ){ return; }
    ##FlushPort(); ##this is needed since UART sends some startup info stuff
    $s= ExecuteCmd( 's', $CMD_s_PARAMETER_ZAHL*2 );
    if( substr($s,length($s)-1,1) ne 'o' ){
      $comporterrorcount--; if( $comporterrorcount<=0 ){ goto WERROR; } next;
    };
    my @data = unpack( "v$CMD_s_PARAMETER_ZAHL", $s );
    my $statetxt = toStateText( $data[$DataState_p] );
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
      $InfoText.'Please wait!' . "\r\n". "\r\n". 'STATE is '.$statetxt );
    #check integrity
    my $status= UIntToBitstr( $data[$DataStatus_p] ); #status
    if( CheckStatus($status,$STATUS_LEVEL_FAILED) ){ goto LEVELERROR; }
    my $NTBusErrors = $data[$DataError_p]; #NT bus error
    if( $NTBusErrors>10 ){ goto NTBUSERROR; }
    if( not CheckStatus($status,$STATUS_IMU_PRESENT) ){ goto IMUERROR; }
    _delay_ms(100);
    if( $statetxt eq 'NORMAL' ){ #last; }
      $normalreachedwaitcount--; if( $normalreachedwaitcount<=0 ){ last; } #wait 1sec
    }
  }
  TextOut_( 'ok' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $InfoText.'ok' );
  #finish things, and go to next page
  $ConfigureGimbal_DoStepIIStart = 0;
  $ConfigureGimbal_StepNr = 0;
  configuregimbal_Continue_Click();
  return;
}
### do the LAST PART
# http://www.olliw.eu/storm32bgc-wiki/Getting_Started#Basic_Controller_Configuration_Quick_Trouble_Shooting
IMUERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n". "\r\n".
    'Imu1 is not present or not healthy!' . "\r\n" .
    'For further help see the STorM32 wiki at' . "\r\n" .
    ''. "\r\n". "\r\n".
    'Press >Cancel<.' );
  goto WIKILINK;
NTBUSERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n". "\r\n".
    'NT bus errors occured!' . "\r\n" .
    'For further help see the STorM32 wiki at' . "\r\n" .
    ''. "\r\n". "\r\n".
    'Press >Cancel<.' );
  goto WIKILINK;
LEVELERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n". "\r\n".
    'The gimbal could not level within reasonable time, and abborted!' . "\r\n" .
    'For further help see the STorM32 wiki at' . "\r\n" .
    ''. "\r\n". "\r\n".
    'Press >Cancel<.' );
  goto WIKILINK;
WIKILINK:
  my $tx = 20; my $ty = 55 + 35 + 1*13;
  $w_ConfigureGimbal->configuregimbal_WikiHelp_link->Move( $tx, $ty + 8*13 );
  $w_ConfigureGimbal->configuregimbal_WikiHelp_link->Show();
  return;
WERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n". "\r\n".
    'Writing to board failed!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
}


# ConfigureGimbal: StepII Motor Directions Page
sub ConfigureGimbalMotorDirections
{
  $w_ConfigureGimbal->configuregimbal_Continue->Disable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  my $Option; my $res1; my $res2; my $res3; my $poles;
### do the FISRT PART
if($ConfigureGimbal_StepNr == 0){
  $w_ConfigureGimbal->configuregimbal_Title->Text( 'Motor Directions' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText1->Text(
    'In this step, the motor direction parameters will be determined.' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'The current motor directions will be read from the board and copied to the motor direction parameters.'
    . "\r\n". "\r\n".
    'Press >Continue< to write the values to the board, and to continue.' );
  $ConfigureGimbal_StepNr = 1;
  $w_ConfigureGimbal->configuregimbal_Continue->Enable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  return;
}
### do the LAST PART
if($ConfigureGimbal_StepNr == 1){
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'Get current motor directions ... Please wait!' );
  _delay_ms(500);
  #get Motor Directions
  TextOut_( "\r\n".'Get current motor directions... ' );
##$ExtendedTimoutFirst = 200; #extend timeout
  my $s= ExecuteCmd( 'xm' );
  if( $s eq 'o' ){ TextOut_( 'ok' ); }else{ goto WERROR; }
  #read Motor Directions

  $Option = $NameToOptionHash{'Pitch Motor Direction'};
  $res1 = SendRcCmdwoOut( '03'. UCharToHexstr($Option->{adr}).'00' );
  if( $res1 =~ /[tc]/ ){ goto WERROR; }
  $res1 = ExtractPayloadFromRcCmd($res1);
  SetOptionField( $Option, substr($res1,4,2) );

  $Option = $NameToOptionHash{'Roll Motor Direction'};
  $res2 = SendRcCmdwoOut( '03'. UCharToHexstr($Option->{adr}).'00' );
  if( $res2 =~ /[tc]/ ){ goto WERROR; }
  $res2 = ExtractPayloadFromRcCmd($res2);
  SetOptionField( $Option, substr($res2,4,2) );

  $Option = $NameToOptionHash{'Yaw Motor Direction'};
  $res3 = SendRcCmdwoOut( '03'. UCharToHexstr($Option->{adr}).'00' );
  if( $res3 =~ /[tc]/ ){ goto WERROR; }
  $res3 = ExtractPayloadFromRcCmd($res3);
  SetOptionField( $Option, substr($res3,4,2) );

  #finish things, and go to next page
  $w_ConfigureGimbal->configuregimbal_MotorDirections_check->Checked(0);
  $ConfigureGimbal_StepNr = 0;
  configuregimbal_Continue_Click();
  return;
}
WERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n".
    'Writing to board failed!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
}


# ConfigureGimbal: StepII Pitch and Roll Motor Positions Page
sub ConfigureGimbalPitchRollMotorPositions
{
  $w_ConfigureGimbal->configuregimbal_Continue->Disable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  my $Option; my $res1; my $res2; my $res3; my $poles;
### do the FISRT PART
if($ConfigureGimbal_StepNr==0){
  $w_ConfigureGimbal->configuregimbal_Title->Text( 'Pitch and Roll Motor Positions' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText1->Text(
    'In this step, the pitch and roll motor startup position parameters will be determined.' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'The current pitch and roll motor positions will be read from the board and copied to the respective startup position parameters.'
    . "\r\n". "\r\n".
    'Press >Continue< to write the values to the board, and to continue.' );
  $ConfigureGimbal_StepNr= 1;
  $w_ConfigureGimbal->configuregimbal_Continue->Enable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  return;
}
### do the LAST PART
if($ConfigureGimbal_StepNr==1){
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'Get current pitch and roll motor positions ... Please wait!' );
  _delay_ms(500);
  #get Motor Positions
  TextOut_( "\r\n".'Get current pitch and roll motor positions... ' );
$ExtendedTimoutFirst = 200; #extend timeout
  my $s= ExecuteCmd( 'xz' );
  if( $s eq 'o' ){ TextOut_( 'ok' ); }else{ goto WERROR; }
  #read Startup Motor Positions
  $Option= $NameToOptionHash{'Pitch Startup Motor Pos'};
  $res1= SendRcCmdwoOut( '03'. UCharToHexstr($Option->{adr}).'00' );
  if( $res1 =~ /[tc]/ ){ goto WERROR; }
  $res1= ExtractPayloadFromRcCmd($res1);
  SetOptionField( $Option, HexstrToDez(substr($res1,6,2).substr($res1,4,2)) );
  $Option= $NameToOptionHash{'Roll Startup Motor Pos'};
  $res2= SendRcCmdwoOut( '03'. UCharToHexstr($Option->{adr}).'00' );
  if( $res2 =~ /[tc]/ ){ goto WERROR; }
  $res2= ExtractPayloadFromRcCmd($res2);
  SetOptionField( $Option, HexstrToDez(substr($res2,6,2).substr($res2,4,2)) );
  #finish things, and go to next page
  $w_ConfigureGimbal->configuregimbal_PitchRollMotorPositions_check->Checked(0);
  $ConfigureGimbal_StepNr = 0;
  configuregimbal_Continue_Click();
  return;
}
WERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n".
    'Writing to board failed!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
}


# ConfigureGimbal: StepII Yaw Motor Position Page
sub ConfigureGimbalYawMotorPosition
{
  $w_ConfigureGimbal->configuregimbal_Continue->Disable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  my $Option; my $res1; my $res2; my $res3; my $res;
### do the FISRT PART
if($ConfigureGimbal_StepNr == 0){
  $w_ConfigureGimbal->configuregimbal_Title->Text( 'Align Yaw Axis' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText1->Text(
    'In this step, the yaw motor position parameter will be adjusted such that the yaw axis points forward at power up.' );
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'Some parameters are prepared ... Please wait!' );
  $ConfigureGimbal_AlignUndoandClosePort = 0;
  $ConfigureGimbal_AlignYawOffset = 0;
  Win32::GUI::DoEvents();
  TextOut( "\r\n".'Reading...' );
  #get Rc Yaw, Rc Yaw Mode, Rc Yaw Offset, Rc Yaw Min, Rc Yaw Max
  $ConfigureGimbal_RcYawAdr = $NameToOptionHash{'Rc Yaw'}->{adr};
  TextOut( $ConfigureGimbal_RcYawAdr.',' );
  $ConfigureGimbal_RcYawRes = SendRcCmdwoOut( '03'. UCharToHexstr($ConfigureGimbal_RcYawAdr).'00' );
  $ConfigureGimbal_RcYawModeAdr = $NameToOptionHash{'Rc Yaw Mode'}->{adr};
  TextOut( $ConfigureGimbal_RcYawModeAdr.',' );
  $ConfigureGimbal_RcYawModeRes = SendRcCmdwoOut( '03'. UCharToHexstr($ConfigureGimbal_RcYawModeAdr).'00' );
  $ConfigureGimbal_RcYawOffsetAdr = $NameToOptionHash{'Rc Yaw Offset'}->{adr};
  TextOut( $ConfigureGimbal_RcYawOffsetAdr.',' );
  $ConfigureGimbal_RcYawOffsetRes = SendRcCmdwoOut( '03'. UCharToHexstr($ConfigureGimbal_RcYawOffsetAdr).'00' );
  $ConfigureGimbal_RcYawMinAdr = $NameToOptionHash{'Rc Yaw Min'}->{adr};
  TextOut( $ConfigureGimbal_RcYawMinAdr.',' );
  $ConfigureGimbal_RcYawMinRes = SendRcCmdwoOut( '03'. UCharToHexstr($ConfigureGimbal_RcYawMinAdr).'00' );
  $ConfigureGimbal_RcYawMaxAdr = $NameToOptionHash{'Rc Yaw Max'}->{adr};
  TextOut( $ConfigureGimbal_RcYawMaxAdr );
  $ConfigureGimbal_RcYawMaxRes = SendRcCmdwoOut( '03'. UCharToHexstr($ConfigureGimbal_RcYawMaxAdr).'00' );
  #check
  if(( $ConfigureGimbal_RcYawRes =~ /[tc]/ )or( $ConfigureGimbal_RcYawModeRes =~ /[tc]/ )or
     ( $ConfigureGimbal_RcYawOffsetRes =~ /[tc]/ )or( $ConfigureGimbal_RcYawMinRes =~ /[tc]/ )or
     ( $ConfigureGimbal_RcYawMaxRes =~ /[tc]/ )){ goto WERROR; }
  #extract payloads
  $ConfigureGimbal_RcYawRes =       ExtractPayloadFromRcCmd( $ConfigureGimbal_RcYawRes );
  $ConfigureGimbal_RcYawModeRes =   ExtractPayloadFromRcCmd( $ConfigureGimbal_RcYawModeRes );
  $ConfigureGimbal_RcYawOffsetRes = ExtractPayloadFromRcCmd( $ConfigureGimbal_RcYawOffsetRes );
  $ConfigureGimbal_RcYawMinRes =    ExtractPayloadFromRcCmd( $ConfigureGimbal_RcYawMinRes );
  $ConfigureGimbal_RcYawMaxRes =    ExtractPayloadFromRcCmd( $ConfigureGimbal_RcYawMaxRes );
  #set Rc Yaw, Rc Yaw Mode, Rc Yaw Offset
  TextOut( '...setting to default... ' );
  SendRcCmdwoOut( '04'. UCharToHexstr($ConfigureGimbal_RcYawAdr).'00'.'0000' );
  SendRcCmdwoOut( '04'. UCharToHexstr($ConfigureGimbal_RcYawModeAdr).'00'.'0000' );
  SendRcCmdwoOut( '04'. UCharToHexstr($ConfigureGimbal_RcYawOffsetAdr).'00'.'0000' );
  SendRcCmdwoOut( '04'. UCharToHexstr($ConfigureGimbal_RcYawMinAdr).'00'.'3EFE' ); #-450 = FE3E
  SendRcCmdwoOut( '04'. UCharToHexstr($ConfigureGimbal_RcYawMaxAdr).'00'.'C201' ); #+450 = 01C2
  TextOut( 'ok' );
  $ConfigureGimbal_AlignUndoandClosePort = 1;
  Win32::GUI::DoEvents();
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'Align the yaw axis using these buttons:' . "\r\n".
    "\r\n". "\r\n". "\r\n". "\r\n".
    'When the yaw axis is aligned, press >Continue< to write the values to the board, and to continue.' . "\r\n" .
    "\r\n".
'Please note:
- The alignment will be undone with the next step. Don\'t worry, that\'s
  normal, it will become effective at the next power up.'
  );
  ConfigureGimbalShowAlignYawButtons();
  $ConfigureGimbal_StepNr = 1;
  $w_ConfigureGimbal->configuregimbal_Continue->Enable();
  $w_ConfigureGimbal->configuregimbal_Continue->Show();
  return;
}
### do the LAST PART
if($ConfigureGimbal_StepNr == 1){
  if( $ConfigureGimbal_AlignUndoandClosePort < 1 ){ return 0; } ###this should never happen!
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    'Get current yaw motor position ... Please wait!' );
  _delay_ms(500);
  #get Motor Position
  TextOut_( "\r\n".'Get current yaw motor position... ' );
  my $s = ExecuteCmd( 'xy' );
  if( $s eq 'o' ){ TextOut_( 'ok' ); }else{ goto WERROR; }
  #read Startup Motor Position
  $Option= $NameToOptionHash{'Yaw Startup Motor Pos'};
  $res1= SendRcCmdwoOut( '03'. UCharToHexstr($Option->{adr}).'00' );
  $res1= ExtractPayloadFromRcCmd($res1);
  SetOptionField( $Option, HexstrToDez(substr($res1,6,2).substr($res1,4,2)) );
  $ConfigureGimbal_AlignUndoandClosePort = 0;
  ConfigureGimbalAlignYawUndo();
  #finish things, and go to next page
  $w_ConfigureGimbal->configuregimbal_YawMotorPosition_check->Checked(0);
  $ConfigureGimbal_StepNr = 0;
  configuregimbal_Continue_Click();
  return;
}
WERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n".
    'Writing to board failed!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
}


# ConfigureGimbal: Finish Page
sub ConfigureGimbalDone
{
  my $Option; my $res1; my $res2; my $res3;

  ### do the FISRT PART
  if( $ConfigureGimbal_StepNr == 0 ){
    $w_ConfigureGimbal->configuregimbal_Title->Text( 'Finish' );
    $w_ConfigureGimbal->configuregimbal_WelcomeText1->Text(
      'The basic setup of your gimbal has been completed now.' );
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
      'The next step would be to tune the PID parameters.' . "\r\n"."\r\n".
      'It is also strongly recommended to calibrate the imu(s).' . "\r\n"."\r\n".
      'The determined parameters were written to the board, but not yet stored '.
      'into the EEprom. Also, the motors might be still disabled.' . "\r\n"."\r\n".
      'In order to enable the motors and restart the gimbal, and/or store the '.
      'settings permanently, check the respective Finish options on the right.' . "\r\n"."\r\n".
      'Have fun :)'
     );
    $w_ConfigureGimbal->configuregimbal_Continue->Hide();
    $w_ConfigureGimbal->configuregimbal_Cancel->Hide();
    $w_ConfigureGimbal->configuregimbal_OK->Enable();
    $w_ConfigureGimbal->configuregimbal_OK->Show();
    $ConfigureGimbal_StepNr = 1;
    return;
  }

  ### do the LAST PART
  if( $ConfigureGimbal_StepNr == 1 ){
    $w_ConfigureGimbal->configuregimbal_OK->Disable();
    $w_ConfigureGimbal->configuregimbal_OK->Show();
    my $dorestart = $w_ConfigureGimbal->configuregimbal_FinishRestart_check->Checked();
    my $dostore = $w_ConfigureGimbal->configuregimbal_FinishStore_check->Checked();
    if( ($dorestart < 1) and ($dostore < 1) ){ return; } #nothing to do
    my $InfoText = ''; my $s;
    if( $dorestart > 0 ){
      #this will disable scripts to avoid a race condition!!!
      $InfoText .= 'Enable all motors and restart the gimbal ... ';
      $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $InfoText.'Please wait!' );
      _delay_ms(500);
      #enable motors and restart
      TextOut( "\r\n".'Enable all motors and restart controller... ' );
      $s = ExecuteCmd( 'xW' );
      if( $s eq 'o' ){ TextOut_( 'ok' ); }else{ goto WERROR; }
      $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $InfoText.'ok' );
      #set Motor Usages
      SetOptionField( $NameToOptionHash{'Pitch Motor Usage'}, 0 );
      SetOptionField( $NameToOptionHash{'Roll Motor Usage'}, 0 );
      SetOptionField( $NameToOptionHash{'Yaw Motor Usage'}, 0 );
      $InfoText .= 'ok' . "\r\n";
    }
    _delay_ms(500);
    if( $dostore > 0 ){
      if( $dorestart > 0 ){_delay_ms(1500); } #give the controller sufficient time to boot up, and drive up the motors
      $InfoText .= 'Store to EEPROM ... ';
      $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $InfoText.'Please wait!' );
      _delay_ms(500);
      #enable motors and restart
      TextOut( "\r\n".'Store to EEPROM... ' );
      SetExtendedTimoutFirst(1000); #StoreToEerpom can take a while! so extend timeout
      $s = ExecuteCmd( 'xs' );
      if( $s eq 'o' ){ TextOut_( 'ok' ); }else{ goto WERROR; }
      $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $InfoText.'ok' );
      $InfoText .= 'ok' . "\r\n";
    }
    $InfoText .= "\r\n" . 'Goodbye and have fun :)';
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text( $InfoText );
    _delay_ms(1000);
    return;
  }
WERROR:
  $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(
    $w_ConfigureGimbal->configuregimbal_WelcomeText2->Text(). "\r\n".
    'Writing to board failed!' . "\r\n". "\r\n".
    'Press >Cancel<.' );
}



# Ende # CONFIGURE GIMBAL Tool Window
###############################################################################
