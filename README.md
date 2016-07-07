======================================
ZenPacks.community.DurationThreshold
======================================


Description
===========

This ZenPack adds a new Duration Threshold type for determining when to trigger an event. 
The threshold count average value for datapoints in the time interval.

Requirements & Dependencies
===========================

    * Zenoss Versions Supported: > 4.0
    * External Dependencies: 
    * ZenPack Dependencies:
    * Installation Notes: zenhub and zopectl restart after installing this ZenPack.
    * Configuration: 

Installation
============
Normal Installation (packaged egg)
----------------------------------
Copy the downloaded .egg to your Zenoss server and run the following commands as the zenoss
user::

   zenpack --install <package.egg>
   zenhub restart
   zopectl restart

Developer Installation (link mode)
----------------------------------
If you wish to further develop and possibly contribute back to this 
ZenPack you should clone the git repository, then install the ZenPack in
developer mode::

   zenpack --link --install <package>
   zenhub restart
   zopectl restart

Configuration
=============

Tested with Zenoss 4.2.5 

Screenshots
===========
|DurationThresholdEdit|
|DurationThresholdEvent|
