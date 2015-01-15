Inverter Monitor
=================
An MK2/USB monitor for the Victron Multiplus.

The Multiplus interface is based on the Lua web interface by fab13n (https://github.com/fab13n/elorn_energy).

Multiplus
=========
The idea is to have the mk2 daemon running on a machine that can produce JSON stats.

LCD Display
==========
An Arduino Leonardo with a 12864wz graphics display is used to display the statistics of the Multiplus. U8glibi(http://code.google.com/p/u8glib/) is used as the graphics library for the arduino.

TODO
====

* Improve mk2Daemon multithreading
* Setup Daemon Logging to print to syslog
* Create Munin plugin for Multiplus via deamon
