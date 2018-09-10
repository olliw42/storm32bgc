T-STorM32 Group Buy Stuff
===========

This folder contains the files, which were used in the T-STorM32 group buy on rcgroups, initiated by geekness in February 2018. It was comprised of the items

- STorM32 board v3.32m
- NT Imu module v2.11
- NT Motor-Encoder module v2.51e

Corresponding thread at rcgroups: https://www.rcgroups.com/forums/showthread.php?3027947-T-Storm-32-prototype-group-buy

Comments:
* A summary of using these materials for building a T-STorM32 gimbal is found here (thx funth1ngs!): https://www.rcgroups.com/forums/showpost.php?p=40180124&postcount=1033

* Two small issues have been found with the Eagle .brd and BOM files for the NT Motor Encoder module v2.51:
- The BOM lists the TLE5012B E3005 (TLE5012BE3005XUMA1) instead of the recommended TLE5012B E1000 encoder chip.
- The Eagle .brd file shows the values for the parts C12 and R1 in confusing locations.
