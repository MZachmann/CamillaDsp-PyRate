# CamillaDsp-PyRate
A short python application to direct CamillaDsp to handle changing capture rates.

This tiny python app is designed to work with CamillaDsp. This is used in the case of a Wiim Mini Pro with bitperfect SPDIF/optical output and a Hifime UR23 SPDIF->USB converter. The UR23 converter works just fine but has no indication of the data rate.

Instead, this application calls (via websocket) into CamillaDsp and asks it for the current capture rate. If the rate has changed to one of the predefined settings then a command is sent to CamillaDsp to change the configuration file to the correct one for that data rate.

In the source code find 'targets' and 'filenames'.

targets - a list of target capture rates
filenames - the name of .yml configuration files to switch to for the matched capture rate

## Issues

1. There is no easy way to get the data size since each capture rate supports a single data format.
2. It is important to make the default configuration file (loaded at startup) the highest capture rate. When CamillaDsp is set for too low a capture rate it overflows, stops, and restarts with the default file. Making this default file 96Khz capture rate (or 192 or ...) means that it will not overflow and RateAdjuster thus can deal with the new rate.

## Latest Changes (Feb 2024)

This upgrades to V2 of CamillaDsp.
The CamillaDsp websocket syntax has changed so this will not work with V1.

The rate-change now changes the config rather than the config file, which automatically updates without a reset (yay). ALso, it *only* changes the device settings on rate change. When you define an automatic yml file
in CamillaDsp this new logic will leave all the filters and other stuff set to those settings and only change the device settings. So, you don't have to mirror filters and pipeline to all the ymls.

While CamillaDsp reports sample rate religiously at 44.1 and 48 it doesn't at 96 so this adds
some new logic that resets to 96K (my highest rate) if nothing else makes sense. 
Once set to 96 things work well again at lower rates so it's a good patch.
