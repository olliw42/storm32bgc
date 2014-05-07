STorM32 BGC
===========

<strong>STM32 32-bit microcontroller based 3-axis brushless gimbal controller board</strong>

scheme and design by OlliW<br>
layout by Martinez (v0.17) and OlliW (above v0.17)

current version: v1.3

the STorM32 BGC board is open source hardware, under the terms of the TAPR Open Hardware License as published by the Free Hardware Foundation, see http://www.tapr.org/ohl.html

the firmware is free and the GUI is open source, for the details of the terms of usage/licenses see <a href="http://www.olliw.eu/2013/storm32bgc">here</a>

<strong>further resources:</strong><br>- project web page http://www.olliw.eu/2013/storm32bgc/<br>- thread at rcgroups http://www.rcgroups.com/forums/showthread.php?t=2055844<br>- wiki for the documentation http://www.olliw.eu/storm32bgc-wiki/

<strong>changes in v1.3:</strong><br>- voltage regulator in DPak package<br>- AUX2 instead of 3.3V pin at AUX port<br>- solder jumper to disconnect bluetooth led<br>- values of resistors R12,R13,R22 changed
<br><strong>changes in v1.2:</strong><br>- minor issues of v1.1 corrected<br>- Futaba S-bus support<br>- Spektrum sattelite connector<br>- usb disconnect network modified to suite F4 processors (thanks ala42!)<br>- usb voltage protection diode added (as in v0.17)<br>- further minor changes in scheme and layout
<br><strong>changes in v1.1:</strong><br>- reverse voltage protection added<br>- layout supports TC4452 motor drivers in DFN package for increased power capabilities<br>- high-side pnp open collector output for driving an IR led added<br>- additional connector for I2C#2 port added<br>- larger solder holes and pads for battery power connection<br>- improved pin arrangement for easier use

<strong>pictures of the v1.2 board (with DFN packages) and v1.3 board (with SOIC packages):</strong><br>
<a href="http://www.olliw.eu/uploads/storm32_bgc_v120_board_dfn_mpu-01-wp01.jpg"><img src="http://www.olliw.eu/uploads/storm32_bgc_v120_board_dfn_mpu-01-wp01.jpg" width="300" height="308"/></a> <a href="http://www.olliw.eu/storm32bgc-wiki/images/1/1c/Joepaisley-storm32-bgc-v13-board-wiki.jpg"><img src="http://www.olliw.eu/storm32bgc-wiki/images/1/1c/Joepaisley-storm32-bgc-v13-board-wiki.jpg" width="300"/></a>

