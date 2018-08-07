#-----------------------------------------------------------------------------#
###############################################################################
# ACC 1-POINT CALIBRATION Tool Window
###############################################################################

#my $Acc16PCalibration_IsRunning = 0; #defined above

my $Acc16PCalibration_ImuNr= 0; #0: Imu, 1: Imu2
my $Acc16PCalibration_Is1Point= 1;

my $Acc16PCalXPos= 80;
my $Acc16PCalYPos= 80;

my $Acc16PCalXSize= 600;
my $Acc16PCalYSize= 480;

my $Acc16PCalibrationOKCancelButtonPosX; ##is set in init
my $Acc16PCalibrationOKCancelButtonPosY; ##is set in init

my $Acc16PCalBackgroundColor = [96,96,96];

#_i is the index in the @DataMatrix, _p is the index in the recieved data format
#  data array:              index in DataMatrix        index in 'd' cmd response str
my @CdDataAx= ();           my $CdDataAx_i= 0;          my $CdDataAx_p= 0;
my @CdDataAy= ();           my $CdDataAy_i= 1;          my $CdDataAy_p= 1;
my @CdDataAz= ();           my $CdDataAz_i= 2;          my $CdDataAz_p= 2;
my @CdDataGx= ();           my $CdDataGx_i= 3;          my $CdDataGx_p= 3;
my @CdDataGy= ();           my $CdDataGy_i= 4;          my $CdDataGy_p= 4;
my @CdDataGz= ();           my $CdDataGz_i= 5;          my $CdDataGz_p= 5;
my @CdDataTemp= ();         my $CdDataTemp_i= 6;        my $CdDataTemp_p= 6;

my @CdDataAx2= ();          my $CdDataAx2_i= 7;         my $CdDataAx2_p= 7;
my @CdDataAy2= ();          my $CdDataAy2_i= 8;         my $CdDataAy2_p= 8;
my @CdDataAz2= ();          my $CdDataAz2_i= 9;         my $CdDataAz2_p= 9;
my @CdDataGx2= ();          my $CdDataGx2_i= 10;        my $CdDataGx2_p= 10;
my @CdDataGy2= ();          my $CdDataGy2_i= 11;        my $CdDataGy2_p= 11;
my @CdDataGz2= ();          my $CdDataGz2_i= 12;        my $CdDataGz2_p= 12;
my @CdDataTemp2= ();        my $CdDataTemp2_i= 13;      my $CdDataTemp2_p= 13;

my @CdDataMatrix = (
      \@CdDataAx, \@CdDataAy, \@CdDataAz,     \@CdDataGx, \@CdDataGy, \@CdDataGz,     \@CdDataTemp,
      \@CdDataAx2, \@CdDataAy2, \@CdDataAz2,  \@CdDataGx2, \@CdDataGy2, \@CdDataGz2,  \@CdDataTemp2,
  );


my $CdDataPos= 0; #position in data array
my $CdDataTimeCounter= 0; #slows down update
my $CdDataCounter= 0;
my $ExecuteCmdMutex= 0;

#my @xLipoVoltageText= (   'OK', 'LOW',  ' ' );
my @AccAcceptPointColors= ( $Acc16PCalBackgroundColor, [128,128,255], [255,50,50], [128,128,128]); #std, grÃ¼n, rot, grau

my $w_Acc16PCalibration= Win32::GUI::DialogBox->new( -name=> 'acc16pcal_Window', -parent => $w_Main, -font=> $StdWinFont,
  -text=> $BGCStr." 1-Point Acc Calibration",
  -pos=> [$Acc16PCalXPos,$Acc16PCalYPos],
  -size=> [$Acc16PCalXSize,$Acc16PCalYSize],
  -helpbox => 0,
  -background=>$Acc16PCalBackgroundColor,
);
$w_Acc16PCalibration->SetIcon($Icon);

sub Acc16PCalInit{
  $Acc16PCalibration_Is1Point = shift;
  my $xpos= 5;
  my $ypos= 5;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_IntroAAA_label', -font=> $StdWinFont,
    -text=> '1-Point accelerometer calibration for', -pos=> [$xpos,$ypos],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_ImuNr_label', -font=> $StdWinFont,
    -text=> ' Imu (camera IMU) ', -pos=> [$xpos+$w_Acc16PCalibration->acc16pcal_IntroAAA_label->Width()+3,$ypos],
    -background=>[0,255,0], #-foreground=> [0,255,255],
  );
  $w_Acc16PCalibration->AddCheckbox( -name=> 'acc16pcal_overwritewarnings', -font=> $StdWinFont,
    -size=>[14,14],-pos=> [$Acc16PCalXSize-20,$ypos],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [0,0,0],
    -onClick => sub{ if($_[0]->GetCheck()){ Acc16PCalibrationEnableAllAcceptPointButtons(); } 1; }
  );
  $xpos= 40;
  $ypos= 10 + 3*13;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_ax_label', -font=> $StdWinFont,
    -text=> 'ax', -pos=> [$xpos,$ypos],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddTextfield( -name=> 'acc16pcal_ax', -font=> $StdWinFont,
    -pos=> [$xpos+$w_Acc16PCalibration->acc16pcal_ax_label->Width()+3,$ypos-3], -size=> [55,23],
    -align=> 'center',
    -readonly=> 1, -background=>$AccCalibDataColor,
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_ay_label', -font=> $StdWinFont,
    -text=> 'ay', -pos=> [$xpos+90,$ypos],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddTextfield( -name=> 'acc16pcal_ay', -font=> $StdWinFont,
    -pos=> [$xpos+90+$w_Acc16PCalibration->acc16pcal_ay_label->Width()+3,$ypos-3], -size=> [55,23],
    -align=> 'center',
    -readonly=> 1, -background=>$AccCalibDataColor,
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_az_label', -font=> $StdWinFont,
    -text=> 'az', -pos=> [$xpos+180,$ypos],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddTextfield( -name=> 'acc16pcal_az', -font=> $StdWinFont,
    -pos=> [$xpos+180+$w_Acc16PCalibration->acc16pcal_az_label->Width()+3,$ypos-3], -size=> [55,23],
    -align=> 'center',
    -readonly=> 1, -background=>$AccCalibDataColor,
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_temp_label', -font=> $StdWinFont,
    -text=> 'T', -pos=> [$xpos+270,$ypos],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddTextfield( -name=> 'acc16pcal_temp', -font=> $StdWinFont,
    -pos=> [$xpos+270+$w_Acc16PCalibration->acc16pcal_temp_label->Width()+3,$ypos-3], -size=> [55,23],
    -align=> 'center',
    -readonly=> 1, -background=>$AccCalibDataColor,
  );
  $xpos= 40;
  $ypos+= 30;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_ax_av', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+$w_Acc16PCalibration->acc16pcal_ax_label->Width()+3,$ypos-3], -size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_ax_sig', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+$w_Acc16PCalibration->acc16pcal_ax_label->Width()+3,$ypos-3 +20], -size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_ay_av', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+90+$w_Acc16PCalibration->acc16pcal_ay_label->Width()+3,$ypos-3], -size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_ay_sig', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+90+$w_Acc16PCalibration->acc16pcal_ay_label->Width()+3,$ypos-3 +20], -size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_az_av', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+180+$w_Acc16PCalibration->acc16pcal_az_label->Width()+3,$ypos-3], -size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_az_sig', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+180+$w_Acc16PCalibration->acc16pcal_az_label->Width()+3,$ypos-3 +20], -size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_temp_av', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+270+$w_Acc16PCalibration->acc16pcal_temp_label->Width()+3,$ypos-3], -size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddButton( -name=> 'acc16pcal_Start', -font=> $StdWinFont,
    -text=> 'Start', -pos=> [$xpos+375+10,$ypos-3 -30], -width=> 80,
    -onClick => sub{ Acc16PCalibrationStart(); 1; }
  );
  $xpos= 360;
  $ypos= 120 +2*13-10;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Zero_label', -font=> $StdWinFont,
    -text=> 'Zero', -pos=> [$xpos-1-30,$ypos+1*13],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Scale_label', -font=> $StdWinFont,
    -text=> 'Scale', -pos=> [$xpos-1-30,$ypos+3*13],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_AccX_label', -font=> $StdWinFont,
    -text=> ' ax', -pos=> [$xpos-1,$ypos-7],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddTextfield( -name=> 'acc16pcal_AccXZero', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos+1*13-4], -size=> [60,23],
    -align=> "right",
    -readonly=> 1, -background=>$AccCalibDataColor,
  );
  $w_Acc16PCalibration->AddTextfield( -name=> 'acc16pcal_AccXScale', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos+3*13-4], -size=> [60,23],
    -align=> "right",
    -readonly=> 1, -background=>$AccCalibDataColor,
  );
  $xpos+= 70;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_AccY_label', -font=> $StdWinFont,
    -text=> ' ay', -pos=> [$xpos-1,$ypos-7],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddTextfield( -name=> 'acc16pcal_AccYZero', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos+1*13-4], -size=> [60,23],
    -align=> "right",
    -readonly=> 1, -background=>$AccCalibDataColor,
  );
  $w_Acc16PCalibration->AddTextfield( -name=> 'acc16pcal_AccYScale', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos+3*13-4], -size=> [60,23],
    -align=> "right",
    -readonly=> 1, -background=>$AccCalibDataColor,
  );
  $xpos+= 70;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_AccZ_label', -font=> $StdWinFont,
    -text=> ' az', -pos=> [$xpos-1,$ypos-7],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddTextfield( -name=> 'acc16pcal_AccZZero', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos+1*13-4], -size=> [60,23],
    -align=> "right",
    -readonly=> 1, -background=>$AccCalibDataColor,
  );
  $w_Acc16PCalibration->AddTextfield( -name=> 'acc16pcal_AccZScale', -font=> $StdWinFont,
    -pos=> [$xpos,$ypos+3*13-4], -size=> [60,23],
    -align=> "right",
    -readonly=> 1, -background=>$AccCalibDataColor,
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Quality_label', -font=> $StdWinFont,
    -text=> 'quality:', -pos=> [$xpos-140,$ypos+5*13],-width=> 160,
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos= 425;
  $ypos= 220;
  $Acc16PCalibrationOKCancelButtonPosX= $xpos;
  $Acc16PCalibrationOKCancelButtonPosY= $ypos-3;
  $w_Acc16PCalibration->AddButton( -name=> 'acc16pcal_OK', -font=> $StdWinFont,
    -text=> 'OK', -pos=> [$xpos,$ypos-3], -width=> 80,
    -onClick => sub{
      AccCalibrateTabSetCalibration( $w_Acc16PCalibration->acc16pcal_AccXZero->Text(),
                                     $w_Acc16PCalibration->acc16pcal_AccYZero->Text(),
                                     $w_Acc16PCalibration->acc16pcal_AccZZero->Text(),
                                     $w_Acc16PCalibration->acc16pcal_AccXScale->Text(),
                                     $w_Acc16PCalibration->acc16pcal_AccYScale->Text(),
                                     $w_Acc16PCalibration->acc16pcal_AccZScale->Text()
                                    );
      Acc16PCalibrationHalt(); $w_Acc16PCalibration->Hide();
      TextOut( "\r\n".'Acc Calibration Tool... DONE'."\r\n" );
      0; }
  );
  $w_Acc16PCalibration->AddButton( -name=> 'acc16pcal_Cancel', -font=> $StdWinFont,
    -text=> 'Cancel', -pos=> [$xpos,$ypos-3 +30], -width=> 80,
    -onClick => sub{ acc16pcal_Window_Terminate(); 0 }
  );
  $w_Acc16PCalibration->AddButton( -name=> 'acc16pcal_SaveToFile', -font=> $StdWinFont,
    -text=> 'Save to File', -pos=> [$xpos,$ypos-3 +30 + 45+10], -width=> 80, -height=> 15,
    -onClick => sub{ Acc16PCalibrationSave6PointCalibrationData(); 1; }
  );
  $xpos= 45;
  $ypos= 120 + 3*13-10;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point1_label', -font=> $StdWinFont,
    -text=> '1. Point (+Z)', -pos=> [$xpos-15,$ypos], #-size=> [55,23],
    -background=> $Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddButton( -name=> 'acc16pcal_Point1_button', -font=> $StdWinFont,
    -text=> 'Accept current readings', -pos=> [$xpos+50,$ypos-3], -width=> 160,
    -onClick => sub{
      Acc16PCalibrationSetPoint1(
        $w_Acc16PCalibration->acc16pcal_ax_av->Text(),
        $w_Acc16PCalibration->acc16pcal_ay_av->Text(),
        $w_Acc16PCalibration->acc16pcal_az_av->Text() );
      if($Acc16PCalibration_Is1Point){
        Acc16PCalibrationCalc1PointCalibration();
      }else{
        Acc16PCalibrationCalc6PointCalibration();
      }
      1;}
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point1_ax_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point1_ay_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 + 60,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point1_az_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 +120,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point1_inRangle', -font=> $StdWinFont,
    -text=> ' -> ', -pos=> [$xpos-40,$ypos], #-size=> [55,23],
    -background=>$AccAcceptPointColors[1], #-foreground=> [255,255,255],
  );
  $ypos+= 4*13;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point2_label', -font=> $StdWinFont,
    -text=> '2. Point (-Z)', -pos=> [$xpos-15,$ypos], #-size=> [55,23],
    -background=> $Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddButton( -name=> 'acc16pcal_Point2_button', -font=> $StdWinFont,
    -text=> 'Accept current readings', -pos=> [$xpos+50,$ypos-3], -width=> 160,
    -onClick => sub{
      Acc16PCalibrationSetPoint2(
        $w_Acc16PCalibration->acc16pcal_ax_av->Text(),
        $w_Acc16PCalibration->acc16pcal_ay_av->Text(),
        $w_Acc16PCalibration->acc16pcal_az_av->Text() );
      Acc16PCalibrationCalc6PointCalibration();
      1;}
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point2_ax_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point2_ay_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 + 60,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point2_az_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 +120,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point2_inRangle', -font=> $StdWinFont,
    -text=> ' -> ', -pos=> [$xpos-40,$ypos], #-size=> [55,23],
    -background=>$AccAcceptPointColors[1], #-foreground=> [255,255,255],
  );
  $ypos+= 4*13;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point3_label', -font=> $StdWinFont,
    -text=> '3. Point (+X)', -pos=> [$xpos-15,$ypos], #-size=> [55,23],
    -background=> $Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddButton( -name=> 'acc16pcal_Point3_button', -font=> $StdWinFont,
    -text=> 'Accept current readings', -pos=> [$xpos+50,$ypos-3], -width=> 160,
    -onClick => sub{
      Acc16PCalibrationSetPoint3(
        $w_Acc16PCalibration->acc16pcal_ax_av->Text(),
        $w_Acc16PCalibration->acc16pcal_ay_av->Text(),
        $w_Acc16PCalibration->acc16pcal_az_av->Text() );
      Acc16PCalibrationCalc6PointCalibration();
      1;}
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point3_ax_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point3_ay_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 + 60,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point3_az_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 +120,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point3_inRangle', -font=> $StdWinFont,
    -text=> ' -> ', -pos=> [$xpos-40,$ypos], #-size=> [55,23],
    -background=>$AccAcceptPointColors[1], #-foreground=> [255,255,255],
  );
  $ypos+= 4*13;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point4_label', -font=> $StdWinFont,
    -text=> '4. Point (-X)', -pos=> [$xpos-15,$ypos], #-size=> [55,23],
    -background=> $Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddButton( -name=> 'acc16pcal_Point4_button', -font=> $StdWinFont,
    -text=> 'Accept current readings', -pos=> [$xpos+50,$ypos-3], -width=> 160,
    -onClick => sub{
      Acc16PCalibrationSetPoint4(
        $w_Acc16PCalibration->acc16pcal_ax_av->Text(),
        $w_Acc16PCalibration->acc16pcal_ay_av->Text(),
        $w_Acc16PCalibration->acc16pcal_az_av->Text() );
      Acc16PCalibrationCalc6PointCalibration();
      1;}
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point4_ax_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point4_ay_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 + 60,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point4_az_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 +120,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point4_inRangle', -font=> $StdWinFont,
    -text=> ' -> ', -pos=> [$xpos-40,$ypos], #-size=> [55,23],
    -background=>$AccAcceptPointColors[1], #-foreground=> [255,255,255],
  );
  $ypos+= 4*13;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point5_label', -font=> $StdWinFont,
    -text=> '5. Point (+Y)', -pos=> [$xpos-15,$ypos], #-size=> [55,23],
    -background=> $Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddButton( -name=> 'acc16pcal_Point5_button', -font=> $StdWinFont,
    -text=> 'Accept current readings', -pos=> [$xpos+50,$ypos-3], -width=> 160,
    -onClick => sub{
      Acc16PCalibrationSetPoint5(
        $w_Acc16PCalibration->acc16pcal_ax_av->Text(),
        $w_Acc16PCalibration->acc16pcal_ay_av->Text(),
        $w_Acc16PCalibration->acc16pcal_az_av->Text() );
      Acc16PCalibrationCalc6PointCalibration();
      1;}
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point5_ax_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point5_ay_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 + 60,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point5_az_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 +120,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point5_inRangle', -font=> $StdWinFont,
    -text=> ' -> ', -pos=> [$xpos-40,$ypos], #-size=> [55,23],
    -background=>$AccAcceptPointColors[1], #-foreground=> [255,255,255],
  );
  $ypos+= 4*13;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point6_label', -font=> $StdWinFont,
    -text=> '6. Point (-Y)', -pos=> [$xpos-15,$ypos], #-size=> [55,23],
    -background=> $Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddButton( -name=> 'acc16pcal_Point6_button', -font=> $StdWinFont,
    -text=> 'Accept current readings', -pos=> [$xpos+50,$ypos-3], -width=> 160,
    -onClick => sub{
      Acc16PCalibrationSetPoint6(
        $w_Acc16PCalibration->acc16pcal_ax_av->Text(),
        $w_Acc16PCalibration->acc16pcal_ay_av->Text(),
        $w_Acc16PCalibration->acc16pcal_az_av->Text() );
      Acc16PCalibrationCalc6PointCalibration();
      1;}
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point6_ax_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point6_ay_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 + 60,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point6_az_accepted', -font=> $StdWinFont,
    -text=> '---', -pos=> [$xpos+50 +120,$ypos-3 +26], -width=> 55, #-size=> [55,23],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_Point6_inRangle', -font=> $StdWinFont,
    -text=> ' -> ', -pos=> [$xpos-40,$ypos], #-size=> [55,23],
    -background=>$AccAcceptPointColors[1], #-foreground=> [255,255,255],
  );
  $xpos= 30;
  $ypos= 220;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_1PointHelp', -font=> $StdWinFont,
    -text=> 'Carefully level the imu, with the orientation in which it will be mounted. Keep it at rest,'.
' and watch the acc data. A blue arrow will indicate when they come into range. Wait until the noise'.
' stabilizes at low values, then accept the readings and press OK, or repeat.',
    -pos=> [$xpos,$ypos], -size=> [275,100],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $xpos= 310;
  $ypos= 360;
  $w_Acc16PCalibration->AddLabel( -name=> 'acc16pcal_6PointHelp', -font=> $StdWinFont,
    -text=> 'Carefully position the imu in the six orientations, one by one (the order is irrelevant). Keep it at rest,'.
' and watch the acc data. A blue arrow will indicate when they come into range. Wait until the noise'.
' stabilizes at low values, then accept the readings. When data for all points are recorded press OK, or repeat.',
    -pos=> [$xpos,$ypos], -size=> [270,100],
    -background=>$Acc16PCalBackgroundColor, -foreground=> [255,255,255],
  );
  $w_Acc16PCalibration->AddTimer( 'acc16pcal_Timer', 0 );
  $w_Acc16PCalibration->acc16pcal_Timer->Interval( 10 );
} #end of Acc16PCalInit()

sub acc16pcal_Timer_Timer{ Acc16PCalibrationDoTimer(); 1; }

sub acc16pcal_Window_Terminate{
  Acc16PCalibrationHalt(); $w_Acc16PCalibration->Hide();
  TextOut( "\r\n".'Acc Calibration Tool... ABORTED'."\r\n" );
  0;
}


sub Acc16PCalibrationHandleWhichPointsToShow{
  if( $Acc16PCalibration_Is1Point==1 ){
  $w_Acc16PCalibration->acc16pcal_Point2_label->Hide();
  $w_Acc16PCalibration->acc16pcal_Point2_button->Hide();
  $w_Acc16PCalibration->acc16pcal_Point2_ax_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point2_ay_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point2_az_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point3_label->Hide();
  $w_Acc16PCalibration->acc16pcal_Point3_button->Hide();
  $w_Acc16PCalibration->acc16pcal_Point3_ax_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point3_ay_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point3_az_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point4_label->Hide();
  $w_Acc16PCalibration->acc16pcal_Point4_button->Hide();
  $w_Acc16PCalibration->acc16pcal_Point4_ax_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point4_ay_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point4_az_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point5_label->Hide();
  $w_Acc16PCalibration->acc16pcal_Point5_button->Hide();
  $w_Acc16PCalibration->acc16pcal_Point5_ax_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point5_ay_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point5_az_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point6_label->Hide();
  $w_Acc16PCalibration->acc16pcal_Point6_button->Hide();
  $w_Acc16PCalibration->acc16pcal_Point6_ax_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point6_ay_accepted->Hide();
  $w_Acc16PCalibration->acc16pcal_Point6_az_accepted->Hide();
  $w_Acc16PCalibration->Resize( $Acc16PCalXSize, $Acc16PCalYSize-160 );
  $w_Acc16PCalibration->acc16pcal_Point1_label->Text( '1. Point' );
  $w_Acc16PCalibration->Text( 'o323BGC 1-Point Acc Calibration' );
  $w_Acc16PCalibration->acc16pcal_IntroAAA_label->Text( '1-Point accelerometer calibration for' );
  $w_Acc16PCalibration->acc16pcal_1PointHelp->Show();
  $w_Acc16PCalibration->acc16pcal_6PointHelp->Hide();

  $w_Acc16PCalibration->acc16pcal_Quality_label->Hide();
  $w_Acc16PCalibration->acc16pcal_OK->Move($Acc16PCalibrationOKCancelButtonPosX,$Acc16PCalibrationOKCancelButtonPosY);
  $w_Acc16PCalibration->acc16pcal_Cancel->Move($Acc16PCalibrationOKCancelButtonPosX,$Acc16PCalibrationOKCancelButtonPosY+30);
  $w_Acc16PCalibration->acc16pcal_overwritewarnings->Move($Acc16PCalXSize-19,$Acc16PCalYSize-160 -40);
  }else{
  $w_Acc16PCalibration->acc16pcal_Point2_label->Show();
  $w_Acc16PCalibration->acc16pcal_Point2_button->Show();
  $w_Acc16PCalibration->acc16pcal_Point2_ax_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point2_ay_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point2_az_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point3_label->Show();
  $w_Acc16PCalibration->acc16pcal_Point3_button->Show();
  $w_Acc16PCalibration->acc16pcal_Point3_ax_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point3_ay_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point3_az_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point4_label->Show();
  $w_Acc16PCalibration->acc16pcal_Point4_button->Show();
  $w_Acc16PCalibration->acc16pcal_Point4_ax_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point4_ay_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point4_az_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point5_label->Show();
  $w_Acc16PCalibration->acc16pcal_Point5_button->Show();
  $w_Acc16PCalibration->acc16pcal_Point5_ax_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point5_ay_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point5_az_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point6_label->Show();
  $w_Acc16PCalibration->acc16pcal_Point6_button->Show();
  $w_Acc16PCalibration->acc16pcal_Point6_ax_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point6_ay_accepted->Show();
  $w_Acc16PCalibration->acc16pcal_Point6_az_accepted->Show();
  $w_Acc16PCalibration->Resize( $Acc16PCalXSize, $Acc16PCalYSize );
  $w_Acc16PCalibration->acc16pcal_Point1_label->Text( '1. Point (+Z)' );
  $w_Acc16PCalibration->Text( 'o323BGC 6-Point Acc Calibration' );
  $w_Acc16PCalibration->acc16pcal_IntroAAA_label->Text( '6-Point accelerometer calibration for' );
  $w_Acc16PCalibration->acc16pcal_1PointHelp->Hide();
  $w_Acc16PCalibration->acc16pcal_6PointHelp->Show();

  $w_Acc16PCalibration->acc16pcal_Quality_label->Show();
  $w_Acc16PCalibration->acc16pcal_OK->Move($Acc16PCalibrationOKCancelButtonPosX,$Acc16PCalibrationOKCancelButtonPosY+20);
  $w_Acc16PCalibration->acc16pcal_Cancel->Move($Acc16PCalibrationOKCancelButtonPosX,$Acc16PCalibrationOKCancelButtonPosY+30+20);
  $w_Acc16PCalibration->acc16pcal_SaveToFile->Show();
  $w_Acc16PCalibration->acc16pcal_overwritewarnings->Move($Acc16PCalXSize-19,$Acc16PCalYSize -40);
  }
}

sub Acc16PCalibrationEnableAllAcceptPointButtons{
  $w_Acc16PCalibration->acc16pcal_Point1_button->Enable();
  $w_Acc16PCalibration->acc16pcal_Point2_button->Enable();
  $w_Acc16PCalibration->acc16pcal_Point3_button->Enable();
  $w_Acc16PCalibration->acc16pcal_Point4_button->Enable();
  $w_Acc16PCalibration->acc16pcal_Point5_button->Enable();
  $w_Acc16PCalibration->acc16pcal_Point6_button->Enable();
}

sub Acc16PCalibrationShow{
  $Acc16PCalibration_Is1Point = shift;
  DataDisplayHalt();
  my ($x, $y) = ($w_Main->GetWindowRect())[0..1];
  $w_Acc16PCalibration->Move($x+80,$y+100);
  if( $f_Tab{calibrateacc}->cacc_ImuNumber->GetCurSel()==1 ){ #IMU2 selected
    $Acc16PCalibration_ImuNr= 1;
    $w_Acc16PCalibration->acc16pcal_ImuNr_label->Text( '  Imu2 (2nd IMU)' );
  }else{
    $Acc16PCalibration_ImuNr= 0;
    $w_Acc16PCalibration->acc16pcal_ImuNr_label->Text( ' Imu (camera IMU)' );
  }
  Acc16PCalibrationHalt();
  Acc16PCalibrationCdDataMatrixClear();
  $w_Acc16PCalibration->acc16pcal_OK->Disable();
  Acc16PCalibrationSetCalibration( '', '', '', '', '', '' );
  $w_Acc16PCalibration->acc16pcal_Point1_button->Disable();
  $w_Acc16PCalibration->acc16pcal_Point2_button->Disable();
  $w_Acc16PCalibration->acc16pcal_Point3_button->Disable();
  $w_Acc16PCalibration->acc16pcal_Point4_button->Disable();
  $w_Acc16PCalibration->acc16pcal_Point5_button->Disable();
  $w_Acc16PCalibration->acc16pcal_Point6_button->Disable();
  Acc16PCalibrationSetPoint1( '---', '---', '---' );
  Acc16PCalibrationSetPoint2( '---', '---', '---' );
  Acc16PCalibrationSetPoint3( '---', '---', '---' );
  Acc16PCalibrationSetPoint4( '---', '---', '---' );
  Acc16PCalibrationSetPoint5( '---', '---', '---' );
  Acc16PCalibrationSetPoint6( '---', '---', '---' );
  $w_Acc16PCalibration->acc16pcal_SaveToFile->Disable();
  $w_Acc16PCalibration->acc16pcal_Point1_inRangle->Hide();
  $w_Acc16PCalibration->acc16pcal_Point2_inRangle->Hide();
  $w_Acc16PCalibration->acc16pcal_Point3_inRangle->Hide();
  $w_Acc16PCalibration->acc16pcal_Point4_inRangle->Hide();
  $w_Acc16PCalibration->acc16pcal_Point5_inRangle->Hide();
  $w_Acc16PCalibration->acc16pcal_Point6_inRangle->Hide();
  $w_Acc16PCalibration->acc16pcal_SaveToFile->Hide();
  $w_Acc16PCalibration->acc16pcal_overwritewarnings->Checked(0);
  Acc16PCalibrationHandleWhichPointsToShow();
  $w_Acc16PCalibration->Show();
  TextOut( "\r\n".'Acc Calibration Tool... ' );
#  if( $f_Tab{calibrateacc}->caac_StoreInEEprom->IsEnabled() ){ Acc16PCalibrationRun(); } #let it auto start when the connection was probably confirmed before
  Acc16PCalibrationRun(); #let it auto start
}

sub Acc16PCalibrationStart{
  if( $Acc16PCalibration_IsRunning ){ Acc16PCalibrationHalt(); }else{ Acc16PCalibrationRun(); }
  return 1;
}


sub Acc16PCalibrationRun{
##  if( not OpenPort() ){ ClosePort(); $Acc16PCalibration_IsRunning= 0; return 1; }
##  if( not ConnectionIsValid() ){ ConnectToBoardwoRead(); }
##  if( not ConnectionIsValid() ){ $Acc16PCalibration_IsRunning= 0; return; }
#  SetDoFirstReadOut(0);
#  DisconnectFromBoard(0);
  $ExecuteCmdMutex= 0;
  $Acc16PCalibration_IsRunning= 1;
  if( not ConnectionIsValid() ){
    if( not OpenPort() ){ ClosePort(); $Acc16PCalibration_IsRunning= 0; return; }
    ClosePort(); #close it again
    ConnectToBoardwoRead();
  }
  $w_Acc16PCalibration->acc16pcal_Start->Text( 'Stop' );
  if( not $w_Acc16PCalibration->acc16pcal_overwritewarnings->GetCheck() ){
    $w_Acc16PCalibration->acc16pcal_Point1_button->Disable();
  }
}

sub Acc16PCalibrationHalt{
#  ClosePort();
  $Acc16PCalibration_IsRunning= 0;
  $w_Acc16PCalibration->acc16pcal_Start->Text( 'Start' );
  if( not $w_Acc16PCalibration->acc16pcal_overwritewarnings->GetCheck() ){
    $w_Acc16PCalibration->acc16pcal_Point1_button->Disable();
  }
}

sub Acc16PCalibrationSetPoint1{
  $w_Acc16PCalibration->acc16pcal_Point1_ax_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point1_ay_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point1_az_accepted->Text( shift );
}
sub Acc16PCalibrationSetPoint2{
  $w_Acc16PCalibration->acc16pcal_Point2_ax_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point2_ay_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point2_az_accepted->Text( shift );
}
sub Acc16PCalibrationSetPoint3{
  $w_Acc16PCalibration->acc16pcal_Point3_ax_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point3_ay_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point3_az_accepted->Text( shift );
}
sub Acc16PCalibrationSetPoint4{
  $w_Acc16PCalibration->acc16pcal_Point4_ax_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point4_ay_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point4_az_accepted->Text( shift );
}
sub Acc16PCalibrationSetPoint5{
  $w_Acc16PCalibration->acc16pcal_Point5_ax_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point5_ay_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point5_az_accepted->Text( shift );
}
sub Acc16PCalibrationSetPoint6{
  $w_Acc16PCalibration->acc16pcal_Point6_ax_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point6_ay_accepted->Text( shift );
  $w_Acc16PCalibration->acc16pcal_Point6_az_accepted->Text( shift );
}

sub Acc16PCalibrationSetCalibration{
  $w_Acc16PCalibration->acc16pcal_AccXZero->Text( shift );
  $w_Acc16PCalibration->acc16pcal_AccYZero->Text( shift );
  $w_Acc16PCalibration->acc16pcal_AccZZero->Text( shift );
  $w_Acc16PCalibration->acc16pcal_AccXScale->Text( shift );
  $w_Acc16PCalibration->acc16pcal_AccYScale->Text( shift );
  $w_Acc16PCalibration->acc16pcal_AccZScale->Text( shift );
}

sub Acc16PCalibrationCalc1PointCalibration{
  my $ax_scale = $AccGravityConst;
  my $ay_scale = $AccGravityConst;
  my $az_scale = $AccGravityConst;
  my $ax_zero = $w_Acc16PCalibration->acc16pcal_Point1_ax_accepted->Text();
  my $ay_zero = $w_Acc16PCalibration->acc16pcal_Point1_ay_accepted->Text();
  my $az_zero = $w_Acc16PCalibration->acc16pcal_Point1_az_accepted->Text();
  if( $ax_zero >  0.85*$AccGravityConst ){ $ax_zero -= $AccGravityConst; }
  if( $ax_zero < -0.85*$AccGravityConst ){ $ax_zero += $AccGravityConst; }
  if( $ay_zero >  0.85*$AccGravityConst ){ $ay_zero -= $AccGravityConst; }
  if( $ay_zero < -0.85*$AccGravityConst ){ $ay_zero += $AccGravityConst; }
  if( $az_zero >  0.75*$AccGravityConst ){ $az_zero -= $AccGravityConst; }
  if( $az_zero < -0.75*$AccGravityConst ){ $az_zero += $AccGravityConst; }

  Acc16PCalibrationSetCalibration( $ax_zero, $ay_zero, $az_zero, $ax_scale, $ay_scale, $az_scale );
  $w_Acc16PCalibration->acc16pcal_OK->Enable();
}

sub Acc16PCalibrationCheckIf6PointsOk{
  if( $w_Acc16PCalibration->acc16pcal_Point1_az_accepted->Text() eq '---' ){ return 0; }
  if( $w_Acc16PCalibration->acc16pcal_Point2_az_accepted->Text() eq '---' ){ return 0; }
  if( $w_Acc16PCalibration->acc16pcal_Point3_ax_accepted->Text() eq '---' ){ return 0; }
  if( $w_Acc16PCalibration->acc16pcal_Point4_ax_accepted->Text() eq '---' ){ return 0; }
  if( $w_Acc16PCalibration->acc16pcal_Point5_ay_accepted->Text() eq '---' ){ return 0; }
  if( $w_Acc16PCalibration->acc16pcal_Point6_ay_accepted->Text() eq '---' ){ return 0; }
  return 1;
}

sub Acc16PCalibrationCalc6PointCalibration{  ####CHECK IF ALL POINTS ARE OK!
  if( not Acc16PCalibrationCheckIf6PointsOk() ){ return; }

  my $az_p = $w_Acc16PCalibration->acc16pcal_Point1_az_accepted->Text();
  my $az_m = $w_Acc16PCalibration->acc16pcal_Point2_az_accepted->Text();
  my $ax_p = $w_Acc16PCalibration->acc16pcal_Point3_ax_accepted->Text();
  my $ax_m = $w_Acc16PCalibration->acc16pcal_Point4_ax_accepted->Text();
  my $ay_p = $w_Acc16PCalibration->acc16pcal_Point5_ay_accepted->Text();
  my $ay_m = $w_Acc16PCalibration->acc16pcal_Point6_ay_accepted->Text();

  my $ax_scale = sprintf( "%.0f", ($ax_p - $ax_m)/2.0 );
  my $ay_scale = sprintf( "%.0f", ($ay_p - $ay_m)/2.0 );
  my $az_scale = sprintf( "%.0f", ($az_p - $az_m)/2.0 );
  my $ax_zero  = sprintf( "%.0f", ($ax_p + $ax_m)/2.0 );
  my $ay_zero  = sprintf( "%.0f", ($ay_p + $ay_m)/2.0 );
  my $az_zero  = sprintf( "%.0f", ($az_p + $az_m)/2.0 );

  Acc16PCalibrationSetCalibration( $ax_zero, $ay_zero, $az_zero, $ax_scale, $ay_scale, $az_scale );
  $w_Acc16PCalibration->acc16pcal_OK->Enable();
  $w_Acc16PCalibration->acc16pcal_SaveToFile->Enable();

  my $quality = 0;
  #Z
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point3_az_accepted->Text() - $az_zero );
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point4_az_accepted->Text() - $az_zero );
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point5_az_accepted->Text() - $az_zero );
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point6_az_accepted->Text() - $az_zero );
  #X
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point1_ax_accepted->Text() - $ax_zero );
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point2_ax_accepted->Text() - $ax_zero );
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point5_ax_accepted->Text() - $ax_zero );
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point6_ax_accepted->Text() - $ax_zero );
  #Y
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point1_ay_accepted->Text() - $ay_zero );
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point2_ay_accepted->Text() - $ay_zero );
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point3_ay_accepted->Text() - $ay_zero );
  $quality+= sqr( $w_Acc16PCalibration->acc16pcal_Point4_ay_accepted->Text() - $ay_zero );

  $quality= sqrt( $quality/12 );
  $w_Acc16PCalibration->acc16pcal_Quality_label->Text("quality: ".sprintf("%.0f",$quality)."        ");
}

sub Acc16PCalibrationCdDataMatrixClear{
  for(my $j=0; $j<512; $j++ ){
    for(my $i=0; $i<512; $i++ ){ $CdDataMatrix[$j][$i]= 0; }
  }
}

sub Acc16PCalibrationDoTimer{
##  if( not ConnectionIsValid() ){ Acc16PCalibrationHalt(); return 1; }
  if( not $Acc16PCalibration_IsRunning){ return 1; }
  #read data frame
  my $s= ExecuteCmd( 'Cd', $CMD_Cd_PARAMETER_ZAHL*2 );
  if( substr($s,length($s)-1,1) ne 'o' ){ TextOut( "\r\nSHIT '".substr($s,length($s)-1,1)."'" ); return 1; }
  my @CdData = unpack( "v$CMD_Cd_PARAMETER_ZAHL", $s );
  for(my $n=0;$n<$CMD_Cd_PARAMETER_ZAHL;$n++){
    if( substr($CdDataFormatStr,$n,1) eq 's' ){ if( $CdData[$n]>32768 ){ $CdData[$n]-=65536; }  }
  }

  #Imu1: Gx, Gy, Gz
  $CdDataMatrix[$CdDataGx_i][$CdDataPos]= $CdData[$CdDataGx_p];
  $CdDataMatrix[$CdDataGy_i][$CdDataPos]= $CdData[$CdDataGy_p];
  $CdDataMatrix[$CdDataGz_i][$CdDataPos]= $CdData[$CdDataGz_p];
  #Imu1: Ax, Ay, Az
  $CdDataMatrix[$CdDataAx_i][$CdDataPos]= $CdData[$CdDataAx_p];
  $CdDataMatrix[$CdDataAy_i][$CdDataPos]= $CdData[$CdDataAy_p];
  $CdDataMatrix[$CdDataAz_i][$CdDataPos]= $CdData[$CdDataAz_p];
  #Imu1: Temp
  $CdDataMatrix[$CdDataTemp_i][$CdDataPos]= $CdData[$CdDataTemp_p];
  #Imu2: Gx, Gy, Gz
  $CdDataMatrix[$CdDataGx2_i][$CdDataPos]= $CdData[$CdDataGx2_p];
  $CdDataMatrix[$CdDataGy2_i][$CdDataPos]= $CdData[$CdDataGy2_p];
  $CdDataMatrix[$CdDataGz2_i][$CdDataPos]= $CdData[$CdDataGz2_p];
  #Imu2: Ax, Ay, Az
  $CdDataMatrix[$CdDataAx2_i][$CdDataPos]= $CdData[$CdDataAx2_p];
  $CdDataMatrix[$CdDataAy2_i][$CdDataPos]= $CdData[$CdDataAy2_p];
  $CdDataMatrix[$CdDataAz2_i][$CdDataPos]= $CdData[$CdDataAz2_p];
  #Imu2: Temp
  $CdDataMatrix[$CdDataTemp2_i][$CdDataPos]= $CdData[$CdDataTemp2_p];

  #display
  $CdDataTimeCounter++;
  if( $CdDataTimeCounter>=12 ){ $CdDataTimeCounter= 0; }

  if( $CdDataTimeCounter==0 ){ #slows down update
    if( $Acc16PCalibration_ImuNr!=1 ){ #IMU1
      $w_Acc16PCalibration->acc16pcal_ax->Text( $CdData[$CdDataAx_p] );
      $w_Acc16PCalibration->acc16pcal_ay->Text( $CdData[$CdDataAy_p] );
      $w_Acc16PCalibration->acc16pcal_az->Text( $CdData[$CdDataAz_p] );
      $w_Acc16PCalibration->acc16pcal_temp->Text( sprintf('%.2f°', $CdData[$CdDataTemp_p]/340.0+36.53) );#$CdData[$CdDataTemp_p] );
    }else{ #IMU2
      $w_Acc16PCalibration->acc16pcal_ax->Text( $CdData[$CdDataAx2_p] );
      $w_Acc16PCalibration->acc16pcal_ay->Text( $CdData[$CdDataAy2_p] );
      $w_Acc16PCalibration->acc16pcal_az->Text( $CdData[$CdDataAz2_p] );
      $w_Acc16PCalibration->acc16pcal_temp->Text( sprintf('%.2f°', $CdData[$CdDataTemp2_p]/340.0+36.53) );#$CdData[$CdDataTemp_p] );
    }
  }

  $CdDataPos++;
  if( $CdDataPos>=256 ){ $CdDataPos= 0; }
  
  my $ax_av= 0.0; my $ax_sig= 0.0;
  my $ay_av= 0.0; my $ay_sig= 0.0;
  my $az_av= 0.0; my $az_sig= 0.0;
  my $temp_av= 0.0;
  if( $Acc16PCalibration_ImuNr!=1 ){ #IMU1
    for(my $i=0; $i<256; $i++ ){
      $ax_av += $CdDataMatrix[$CdDataAx_i][$i];
      $ay_av += $CdDataMatrix[$CdDataAy_i][$i];
      $az_av += $CdDataMatrix[$CdDataAz_i][$i];
      $temp_av += $CdDataMatrix[$CdDataTemp_i][$i];
    }
  }else{ #IMU2
    for(my $i=0; $i<256; $i++ ){
      $ax_av += $CdDataMatrix[$CdDataAx2_i][$i];
      $ay_av += $CdDataMatrix[$CdDataAy2_i][$i];
      $az_av += $CdDataMatrix[$CdDataAz2_i][$i];
      $temp_av += $CdDataMatrix[$CdDataTemp2_i][$i];
    }
  }
  $ax_av = $ax_av / 256.0;
  $ay_av = $ay_av / 256.0;
  $az_av = $az_av / 256.0;
  $temp_av = $temp_av / 256.0;
  if( $Acc16PCalibration_ImuNr!=1 ){ #IMU1
    for(my $i=0; $i<256; $i++ ){
      $ax_sig += abs( $CdDataMatrix[$CdDataAx_i][$i]-$ax_av );
      $ay_sig += abs( $CdDataMatrix[$CdDataAy_i][$i]-$ay_av );
      $az_sig += abs( $CdDataMatrix[$CdDataAz_i][$i]-$az_av );
    }
  }else{ #IMU2
    for(my $i=0; $i<256; $i++ ){
      $ax_sig += abs( $CdDataMatrix[$CdDataAx2_i][$i]-$ax_av );
      $ay_sig += abs( $CdDataMatrix[$CdDataAy2_i][$i]-$ay_av );
      $az_sig += abs( $CdDataMatrix[$CdDataAz2_i][$i]-$az_av );
    }
  }

if( $CdDataTimeCounter==0 or $CdDataTimeCounter==4 or $CdDataTimeCounter==8 ){ #slows down update
  $w_Acc16PCalibration->acc16pcal_ax_av->Text( sprintf( "%.0f", $ax_av ) );
  $w_Acc16PCalibration->acc16pcal_ax_sig->Text( sprintf( "%.0f", $ax_sig/256.0) );
  $w_Acc16PCalibration->acc16pcal_ay_av->Text( sprintf( "%.0f", $ay_av ) );
  $w_Acc16PCalibration->acc16pcal_ay_sig->Text( sprintf( "%.0f", $ay_sig/256.0) );
  $w_Acc16PCalibration->acc16pcal_az_av->Text( sprintf( "%.0f", $az_av ) );
  $w_Acc16PCalibration->acc16pcal_az_sig->Text( sprintf( "%.0f", $az_sig/256.0) );
  $w_Acc16PCalibration->acc16pcal_temp_av->Text( sprintf('%.2f°', $temp_av/340.0+36.53) );

  if( $Acc16PCalibration_Is1Point==1 ){
    if(( abs($ax_av) > 0.85*$AccGravityConst )or
       ( abs($ay_av) > 0.85*$AccGravityConst )or
       ( abs($az_av) > 0.75*$AccGravityConst )   ){
      $w_Acc16PCalibration->acc16pcal_Point1_button->Enable();
      $w_Acc16PCalibration->acc16pcal_Point1_inRangle->Show();
    }else{
      if( not $w_Acc16PCalibration->acc16pcal_overwritewarnings->GetCheck() ){
        $w_Acc16PCalibration->acc16pcal_Point1_button->Disable();
      }
      $w_Acc16PCalibration->acc16pcal_Point1_inRangle->Hide();
    }
  }else{
    if( $az_av > 0.75*$AccGravityConst ){
      $w_Acc16PCalibration->acc16pcal_Point1_button->Enable();
      $w_Acc16PCalibration->acc16pcal_Point1_inRangle->Show();
    }else{
      if( not $w_Acc16PCalibration->acc16pcal_overwritewarnings->GetCheck() ){
        $w_Acc16PCalibration->acc16pcal_Point1_button->Disable();
      }
      $w_Acc16PCalibration->acc16pcal_Point1_inRangle->Hide();
    }
    if( $az_av <-0.75*$AccGravityConst ){
      $w_Acc16PCalibration->acc16pcal_Point2_button->Enable();
      $w_Acc16PCalibration->acc16pcal_Point2_inRangle->Show();
    }else{
      if( not $w_Acc16PCalibration->acc16pcal_overwritewarnings->GetCheck() ){
        $w_Acc16PCalibration->acc16pcal_Point2_button->Disable();
      }
      $w_Acc16PCalibration->acc16pcal_Point2_inRangle->Hide();
    }
    if( $ax_av > 0.85*$AccGravityConst ){
      $w_Acc16PCalibration->acc16pcal_Point3_button->Enable();
      $w_Acc16PCalibration->acc16pcal_Point3_inRangle->Show();
    }else{
      if( not $w_Acc16PCalibration->acc16pcal_overwritewarnings->GetCheck() ){
        $w_Acc16PCalibration->acc16pcal_Point3_button->Disable();
      }
      $w_Acc16PCalibration->acc16pcal_Point3_inRangle->Hide();
    }
    if( $ax_av < -0.85*$AccGravityConst ){
      $w_Acc16PCalibration->acc16pcal_Point4_button->Enable();
      $w_Acc16PCalibration->acc16pcal_Point4_inRangle->Show();
    }else{
      if( not $w_Acc16PCalibration->acc16pcal_overwritewarnings->GetCheck() ){
        $w_Acc16PCalibration->acc16pcal_Point4_button->Disable();
      }
      $w_Acc16PCalibration->acc16pcal_Point4_inRangle->Hide();
    }
    if( $ay_av > 0.85*$AccGravityConst ){
      $w_Acc16PCalibration->acc16pcal_Point5_button->Enable();
      $w_Acc16PCalibration->acc16pcal_Point5_inRangle->Show();
    }else{
      if( not $w_Acc16PCalibration->acc16pcal_overwritewarnings->GetCheck() ){
        $w_Acc16PCalibration->acc16pcal_Point5_button->Disable();
      }
      $w_Acc16PCalibration->acc16pcal_Point5_inRangle->Hide();
    }
    if( $ay_av < -0.85*$AccGravityConst ){
      $w_Acc16PCalibration->acc16pcal_Point6_button->Enable();
      $w_Acc16PCalibration->acc16pcal_Point6_inRangle->Show();
    }else{
      if( not $w_Acc16PCalibration->acc16pcal_overwritewarnings->GetCheck() ){
        $w_Acc16PCalibration->acc16pcal_Point6_button->Disable();
      }
      $w_Acc16PCalibration->acc16pcal_Point6_inRangle->Hide();
    }
  }
}
  1;
}

#similar to sub ExecuteSaveCalibrationData()
sub Acc16PCalibrationSave6PointCalibrationData{
  my $file= Win32::GUI::GetSaveFileName( -owner=> $w_Main,
    -title=> 'Save Calibration Data to File',
    -nochangedir=> 1,
    -directory=> $SettingsFile_lastdir, #".\\",
    -defaultextension=> '.cal',
    -filter=> ['*.cal'=>'*.cal','All files' => '*.*'],
    -pathmustexist=> 1,
    -overwriteprompt=> 1,
    -noreadonlyreturn => 1,
    -explorer=>0,
  );
  if( $file ){
    if( !open(F,">$file") ){ $w_Main->MessageBox("Some error occured, sorry",'ERROR'); return; }
    print F 'IMUNAME: '.NameExtStr($file)."\n";
    print F 'IMUTYPE: '.$CalibrationDataRecord{imutype}."\n"; #MPU6050
    print F 'IMUSETTINGS: '.$CalibrationDataRecord{imusettings}."\n"; #get from above
    print F 'RECORD#1'."\n";
    print F 'AXZERO: '.$w_Acc16PCalibration->acc16pcal_AccXZero->Text()."\n";
    print F 'AYZERO: '.$w_Acc16PCalibration->acc16pcal_AccYZero->Text()."\n";
    print F 'AZZERO: '.$w_Acc16PCalibration->acc16pcal_AccZZero->Text()."\n";
    print F 'AXSCALE: '.$w_Acc16PCalibration->acc16pcal_AccXScale->Text()."\n";
    print F 'AYSCALE: '.$w_Acc16PCalibration->acc16pcal_AccYScale->Text()."\n";
    print F 'AZSCALE: '.$w_Acc16PCalibration->acc16pcal_AccZScale->Text()."\n";
    print F 'CALIBRATIONMETHOD: 6 point'."\n";
    print F 'TEMPERATURE: '.$w_Acc16PCalibration->acc16pcal_temp_av->Text()."\n";
    print F 'RAW: '."\n";
    print F '1. (+Z):  ';
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point1_ax_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point1_ay_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point1_az_accepted->Text())."\n";
    print F '2. (-Z):  ';
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point2_ax_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point2_ay_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point2_az_accepted->Text())."\n";
    print F '3. (+X):  ';
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point3_ax_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point3_ay_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point3_az_accepted->Text())."\n";
    print F '4. (-X):  ';
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point4_ax_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point4_ay_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point4_az_accepted->Text())."\n";
    print F '5. (+Y):  ';
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point5_ax_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point5_ay_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point5_az_accepted->Text())."\n";
    print F '6. (-Y):  ';
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point6_ax_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point6_ay_accepted->Text()).", ";
    print F sprintf( "% 6.0f", $w_Acc16PCalibration->acc16pcal_Point6_az_accepted->Text())."\n";
#    print F 'quality:  '.$w_Acc16PCalibration->acc16pcal_Quality_label->Text();
    print F $w_Acc16PCalibration->acc16pcal_Quality_label->Text(); #the 'quality' is already in the Text()
    close(F);
  }elsif( Win32::GUI::CommDlgExtendedError() ){$w_Main->MessageBox("Some error occured, sorry",'ERROR');}
  1;
}
