---
layout: post
title: Intel Edison Benchmarks
---

I've selected the Intel Edison as the embedded Linux processor of choice for this project. But how does it perform? Let's find out.

![Intel Edison on a Sparkfun Blocks stack. Credit Sparkfun.](/public/images/2015/3/2/sparkfun_edison_stack.jpg)

The nearest competitor to the Edison is the RasberryPi2, which was released on February 2, 2015 at $35. The Intel Edison was released in September 2014, and costs about $85 depending on configuration.

<!--endexcerpt-->

## Feature Comparison

Metric        | RasberryPi 2 | Edison
--------------|--------------|---------
Architecture  | ARM          | Atom (Quark)
Cores         | 4            | 2 (1)
Speed         | 900 MHz      | 500 MHz (100 MHz)
RAM           | 1GB          | 1 GB
USB           | 4 Host       | 1 USB OTG
Display       | HDMI         | No
Ethernet      | Yes          | No
WiFi          | No           | a/b/g/n
Bluetooth     | No           | 4.0
Onboard Flash | None         | 4GB
Size          | 85x56mm      | 45x31mm*
Price         | $35          | $83*

\* using the Sparkfun base block.

The Edison is interesting in that it contains an embedded Intel Quark processor as well as the main Atom processor.

# Commands Used

To measure power consumption and performance I ran sysbench and wget. I ran these in a multi-pane tmux session so that I can test multiple aspects in parallel:

```bash
# Download Speed
wget --output-document=/dev/null http://speedtest.wdc01.softlayer.com/downloads/test500.zip

# Upload Speed (by sending characters to the connected terminal)
ls -lR /

# CPU
sysbench --num-threads=1 --test=cpu run
```


# CPU Performance

```bash
sudo apt-get install sysbench
sysbench --test=cpu run
sysbench --test=cpu --num-threads=2 run

git clone https://github.com/dai-shi/benchmark-octane.git
cd benchmark-octane
node run.js
```

Raspberry pi times taken from [Adafruit](https://learn.adafruit.com/introducing-the-raspberry-pi-2-model-b/performance-improvements) and [Mikronauts](http://www.mikronauts.com/raspberry-pi/raspberry-pi-2-model-b-review/6/). Desktop times taken on my Core i7-2600k Sandybridge (January 2011).

System   | Cores | Time (s)
---------|-------|----------
Edison   | 1     | 118 
Edison   | 2     | 60
PiB+     | 1     | 507
Pi2      | 1     | 295
Pi2      | 2     | 149
Pi2      | 4     | 74
i7       | 1     | 7.5
i7       | 2     | 3.7

I also ran [JS Octane](https://github.com/dai-shi/benchmark-octane) tests:

System   | Score | Time (s)
---------|-------|-----------
EdisonJS | 949   | 331
Desktop  | 17363 | 40

# Power Consumption

I tested this with a stack of Edison blocks:

 - Edison
 - Base Block
 - SD card block (no SD)
 - I2C block
 - GPIO block
 - PWM block
 - 9DOF block

The stack was powered from USB through the "console" input. Except for the base block, nothing was connected to the stack, including no SD card. For measuring power consumption I'm using a USB inline power meter.

Power (mW) | Current (@5v) | CPU    | WiFI
-----------|---------------|--------|-----------
0.22       | 44            | idle   | connected, idle
0.38       | 76            | 1 CPU  | connected, idle
0.45       | 90            | 2 CPU  | connected, idle
0.75       | 150           | 2 CPU  | Rx/Tx

Note that running just the Rx/Tx tests resulted in near 100% CPU consumption, so I wasn't able to accurately measure WiFi power without the CPU cost as well.

For comparison, this Mikronauts test [measured](http://www.mikronauts.com/raspberry-pi/raspberry-pi-2-model-b-review/7/) the power consumption of a RasberryPi 2 at 310mA average and 450mA maximum (at 5v).

# Conclusion

The Intel Edison is a faster and more power efficient processor that the RasberryPi 2, and the higher price point is entirely justified for a the improved specifications.
