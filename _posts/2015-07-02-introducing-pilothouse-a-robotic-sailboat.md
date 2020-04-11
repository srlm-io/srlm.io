---
layout: post
title: Introducing Pilothouse - A Robotic Sailboat
tags: [robotics, sailing, edison, linux]
---

Over the past 6 months I've been working on developing an open source robotic sailboat called Pilothouse.

[![](/public/images/2015/7/2/boat_three_quarter_small.jpg)](/public/images/2015/7/2/boat_three_quarter.jpg)

The goal of Pilothouse is to make an open source robotic sailboat that can autonomously navigate and sail itself long distances, and to prove that this can be done using the latest web technology: Node.js.

<!--endexcerpt-->

Pilothouse has a number of awesome features, including:

1. Robotic sailing, with 100% all natural renewable energy.
2. WiFi based monitoring with remote GUI.
3. Full Ubuntu Linux environment onboard.
4. Advanced sensors, including the latest GPS and MEMS.
5. Potential for expansion into a fully autonomous ocean going science vessel.
6. Javascript Node.js based control system.
7. Open source software ([GitHub](https://github.com/srlm-io/pilothouse)).

At this time, this project is just starting to get into autonomous control. Here's the first sail, with autonomous sail control and manual RC rudder.

<iframe width="560" height="315" src="https://www.youtube.com/embed/uy1_pqsoaeA" frameborder="0" allowfullscreen></iframe>

As part of the Pilothouse project the base station displays all relevant boat state information, sent over WiFi.

[![](/public/images/2015/7/2/base_station_with_boat_small.jpg)](/public/images/2015/7/2/base_station_with_boat.jpg)
*The boat transmits the current state over WiFi, which is received by a long range USB WiFi antenna on the laptop. No software besides a web browser is needed.*

This project was inspired by my volunteer work with Diane at [RoboSail](http://www.robosail.org/), an awesome project to teach kids programming through robotic sailboats.

<!--endexcerpt-->

# Mechanical Overview

[![](/public/images/2015/7/2/sailboat_show_all_small.jpg)](/public/images/2015/7/2/sailboat_show_all.jpg)

The boat is a [Ragazza](http://www.proboatmodels.com/Products/Default.aspx?ProdID=PRB07000) sailboat from Pro Boat Models. This is a very nicely designed and built boat with a fiberglass hull, clean rigging, and lots of room inside.

I've modified the inside of the boat a bit for three new features: an improved sheeting system, a water tight hatch, and an internally mounted Pelican case.

Before any of the other modifications, I hacked at the center console to make it shorter. This provided enough room to slip the Pelican case for the electronics into the stern.

[![](/public/images/2015/7/2/console_modification_small.jpg)](/public/images/2015/7/2/console_modification.jpg)
*The center console so that it's not so far towards the stern. The stock console was shortened by cutting out the middle section. To support the winch servo I mounted a piece of Lexan with Sugru.*



## Sheeting System

The sheeting system on the stock boat uses a witch that collects the jib sheet on the top spool, and the main sheet on the bottom spool. While this works ok, it's prone to problems with slack. Based on the [options presented by the AMYA](http://www.theamya.org/hints/sailservo.php), I've implemented a continuous loop sheeting system:

![](/public/images/2015/7/2/sheet_drum.jpg)
*Image courtesy of Hitec RCD*

My implementation essentially follows. Instead of pulleys, which are difficult to find at this small scale, I used steel rings.

The two sheets require approximately 18in of travel from full in to full out. To get that kind of distance I mounted the rings an aluminum U channel, and mounted it so that it passes through the center bulkhead and into the bow of the ship.

[![](/public/images/2015/7/2/in_the_hatch_small.jpg)](/public/images/2015/7/2/in_the_hatch.jpg)
*The sheeting system is visible at the top of the image (lines are green), with the return line going from the O-ring on the left, through a tensioner O ring and to the winch. The tensioner is a piece of elastic, doubled back on itself to get the required length.*

For all lines I've used 65lb test Spectra fishing line. It's strong and doesn't have any stretch.

[![](/public/images/2015/7/2/sheeting_system_a_small.jpg)](/public/images/2015/7/2/sheeting_system_a.jpg)
*The sheeting support bar is on the left, and the sail winch is the black drum on the right. The continuous loop tensioner is the middle.*

[![](/public/images/2015/7/2/sheeting_system_b_small.jpg)](/public/images/2015/7/2/sheeting_system_b.jpg)
*One return pulley (ring) is visible on the left. To tighten the sheets the winch pulls the loop clockwise. The sheets are attached to the knot in the middle of this view, and run to the ring on the left and then out the the respective sail.*


## Watertight Hatch

The stock hatch on the Regazza is just held on with magnets, and is not at all water tight. With all of the very expensive electronics inside I wanted to make sure that as little water got in as possible.

The hatch is a piece of Lexan held to the deck with four stainless steel screws. A tight seal is achieved with two layers of epom rubber weatherseal. One layer is around the hatch opening, and the other is on the Lexan. When the thumbnuts are tightened down the seals squish together nicely.

[![](/public/images/2015/7/2/watertight_hatch_small.jpg)](/public/images/2015/7/2/watertight_hatch.jpg)
*The hatch is held on by four bolts, and a seal is achieved with a ring of epom rubber weatherseal.*

# Electronics

The brains of the system is the [Intel Edison](https://en.wikipedia.org/wiki/Intel_Edison), a dual Atom core processor made for embedded systems. It's running a variant of Ubuntu built for the Edison called [Ubilinux](http://www.emutexlabs.com/ubilinux).

Sparkfun has come up with a really cool ["block" system](https://learn.sparkfun.com/tutorials/general-guide-to-sparkfun-blocks-for-intel-edison) for the Edison. They've designed a number of common periperal blocks that can be stacked much like Arduino shields. For Pilothouse, I've used the following stack:

 - Edison
 - Base Block
 - SD card block
 - I2C block
 - GPIO block
 - PWM block
 - 9DOF block

There are two servos on the boat: a multi-turn winch servo to control sail angle and a rudder servo.

Pilothouse uses a standard LSM9DS0 from ST, mounted on a [Sparkfun block](https://www.sparkfun.com/products/13033). The LSM9DS0 offers a 3 axis accelerometer, a 3 axis gyroscope, and a 3 axis magnetometer all in a single package.

## Wind Sensor

[![](/public/images/2015/7/2/wind_sensor_small.jpg)](/public/images/2015/7/2/wind_sensor.jpg)

The wind sensor uses the [MA3 absolute rotary encoder](http://www.usdigital.com/products/encoders/absolute/rotary/shaft/ma3) from US Digital. This sensor outputs a PWM pulse whose width is proportional to the position of the encoder shaft. The main advantage of this sensor over a potentiometer is the ball bearings, with allow for sensing even the lightest of winds.

The only problem is that the Intel Edison doesn't have a PWM input, and there doesn't seem to be any I2C PWM input chips available. To overcome this I'm using a [Pro Micro Adruino](https://www.sparkfun.com/products/12640) to read the PWM and hang off the I2C bus.

For the wind vane itself I'm using a product from the Western Reserve Model Yacht Club with the addition of a bit more surface area.

## GPS

The GPS is a U-Blox M8 series GPS with a large patch antenna from [CSG Shop](http://www.csgshop.com/product.php?id_product=174). I've been very pleased with the performance of this unit, even in difficult conditions like Boston.


# Base station

The base station is really any WiFi enabled device that has enough range to connect to the boat. Pilothouse sets up a simple web server to provide a GUI to any WiFi client so all that clients have to do is go to the specified URL and they will be provide with the app:

[![](/public/images/2015/7/2/pilothouse_gui.png)](/public/images/2015/7/2/pilothouse_gui.png)
*Early version of the GUI showing live data streamed from the boat to the base station.*

All data is streamed live over WiFi via web sockets. This enables a "fly by wire" control.

# Future

Pilothouse is an ongoing project, and this is just the start. I'll be adding a better GUI with a map and graphs, long term data storage, environmental sensing, and fully autonmous sailing. All code can be found in the [GitHub repository](https://github.com/srlm-io/pilothouse).

[![](/public/images/2015/7/2/sailing_away_small.jpg)](/public/images/2015/7/2/sailing_away.jpg)
