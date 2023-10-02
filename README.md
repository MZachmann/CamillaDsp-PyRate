# CamillaDsp-PyRate
A short python application to direct CamillaDsp to handle changing capture rates.

This tiny python app is designed to work with CamillaDsp. This is used in the case of a Wiim Mini Pro with bitperfect SPDIF/optical output and a Hifime UR23 SPDIF->USB converter. The UR23 converter works just fine but has no indication of the data rate.

Instead, this application calls (via websocket) into CamillaDsp and asks it for the current capture rate. If the rate has changed to one of the predefined settings then a command is sent to CamillaDsp to change the configuration file to the correct one for that data rate.

In the source code find 'targets' and 'filenames'.

targets - a list of target capture rates
filenames - the name of .yml configuration files to switch to for the matched capture rate

Issues
-----

1. There is no easy way to get the data size since each capture rate supports a single data format.
2. It is important to make the default configuration file (loaded at startup) the highest capture rate. When CamillaDsp is set for too low a capture rate it overflows, stops, and restarts with the default file. Making this default file 96Khz capture rate (or 192 or ...) means that it will not overflow and RateAdjuster thus can deal with the new rate.


