---
layout: post
title: Pilothouse Project Setup, Edison
---

In this post I have some comments on installing Ubilinux on an Intel Edison. Mostly it's a scratch pad for me to record the configuration of the processor.


# Installing Ubilinux

I tried the tutorial [here](https://learn.sparkfun.com/tutorials/loading-debian-ubilinux-on-the-edison). My host machine is running on Ubuntu 14.04, 64 bit version.

Of course, `dfu-util` isn't installed be default in Ubuntu.

```bash
sudo apt-get install dfu-util
```

After running the single command, I got this error output

```bash
user@desktop:~/Downloads/edison/toFlash$ sudo ./flashall.sh 
Using U-Boot target: edison-blank
Now waiting for dfu device 8087:0a99
Flashing IFWI
##################################################] finished!
##################################################] finished!
Flashing U-Boot
##################################################] finished!
Flashing U-Boot Environment
##################################################] finished!
Flashing U-Boot Environment Backup and rebooting to apply partiton changes
##################################################] finished!
Now waiting for dfu device 8087:0a99
Timed out while waiting for dfu device 8087:0a99
DEBUG: lsusb
Bus 002 Device 006: ID 0cf3:3005 Atheros Communications, Inc. AR3011 Bluetooth
Bus 002 Device 004: ID 0556:0001 Asahi Kasei Microsystems Co., Ltd AK5370 I/F A/D Converter
Bus 002 Device 012: ID 046d:c06b Logitech, Inc. G700 Wireless Gaming Mouse
Bus 002 Device 010: ID 03f0:2514 Hewlett-Packard 
Bus 002 Device 022: ID 8087:0a99 Intel Corp. 
Bus 002 Device 003: ID 0bda:0119 Realtek Semiconductor Corp. Storage Device (SD card reader)
Bus 002 Device 002: ID 8087:0024 Intel Corp. Integrated Rate Matching Hub
Bus 002 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 006 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 005 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 003 Device 026: ID 0488:0280 Cirque Corp. 
Bus 003 Device 025: ID 05f3:0007 PI Engineering, Inc. Kinesis Advantage PRO MPC/USB Keyboard
Bus 003 Device 003: ID 05f3:0081 PI Engineering, Inc. Kinesis Integrated Hub
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 003: ID 11b0:6178 ATECH FLASH TECHNOLOGY 
Bus 001 Device 002: ID 8087:0024 Intel Corp. Integrated Rate Matching Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
DEBUG: dfu-util -l
dfu-util 0.5

(C) 2005-2008 by Weston Schmidt, Harald Welte and OpenMoko Inc.
(C) 2010-2011 Tormod Volden (DfuSe support)
This program is Free Software and has ABSOLUTELY NO WARRANTY

dfu-util does currently only support DFU version 1.0

Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=0, name="ifwi00"
Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=1, name="ifwib00"
Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=2, name="u-boot0"
Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=3, name="u-boot-env0"
Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=4, name="u-boot1"
Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=5, name="u-boot-env1"
Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=6, name="boot"
Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=7, name="rootfs"
Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=8, name="update"
Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=9, name="home"
Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=10, name="vmlinuz"
Found DFU: [8087:0a99] devnum=0, cfg=1, intf=0, alt=11, name="initrd"
Did you plug and reboot your board?
If yes, please try a recovery by calling this script with the --recovery option
```


And when I tried to run with the --recovery option, it complained

```bash
user@desktop:~/Downloads/edison/toFlash$ sudo ./flashall.sh --recovery
Starting Recovery mode
Please plug and reboot the board
Flashing IFWI
!!! You should install xfstk tools, please visit http://xfstk.sourceforge.net/
```

Installing the xfstk tools took up 500MB on my machine, but after following their instructions (including a `make install`) I was able to run the recovery

```
user@desktop:~/Downloads/edison/toFlash$ sudo ./flashall.sh --recovery
Starting Recovery mode
Please plug and reboot the board
Flashing IFWI

XFSTK Downloader Solo 0.0.0 
Copyright (c) 2015 Intel Corporation
Build date and time: Mar  1 2015 12:39:24

Intel SoC Device Detection Failed: Attempt #0
Intel SoC Device Detection Failed: Attempt #1
Intel SoC Device Detection Failed: Attempt #2
Intel SoC Device Detection Failed: Attempt #3
Intel SoC Device Detection Failed: Attempt #4
Intel SoC Device Detection Failed: Attempt #5
Intel SoC Device Detection Failed: Attempt #6
Intel SoC Device Detection Failed: Attempt #7
.Intel SoC Device Detection Found
Parsing Commandline.... 
Registering Status Callback.... 
.Initiating Download Process.... 
.....................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................XFSTK-STATUS--Reconnecting to device - Attempt #1
................................................................................................................................Recovery Success...
You can now try a regular flash
```

And, magically, running `sudo ./flashall.sh` now works. Notice the `sudo`? I don't know if that was the difference or not.

# Installing Packages

After following the Sparkfun instructions to setup WiFi and change users, I installed some useful packages. These instructions are taken from [Sparkfun](https://learn.sparkfun.com/tutorials/installing-libmraa-on-ubilinux-for-edison) and personal scripts.

For Node.js support we don't need to build MRAA ourselves: it's in npm.

```bash
sudo apt-get update
sudo apt-get upgrade
sudo npm install -g grunt-cli nodemon bower
sudo apt-get install iotop git htop tmux sysstat

# Recover every last bit of space
sudo apt-get autoremove --purge
```

# Connecting over WiFi

We can find out the IP address with the following command (the first three numbers must match your network)

```bash
sudo nmap -sP 192.168.1.0/24
```

And it will give us something like this

```bash
Starting Nmap 6.40 ( http://nmap.org ) at 2015-03-01 15:30 EST
...
Nmap scan report for ubilinux (192.168.1.133)
Host is up (0.49s latency).
MAC Address: FC:C2:DE:3F:CE:37 (Unknown)
...
Nmap done: 256 IP addresses (7 hosts up) scanned in 5.84 seconds
```

But, as it turns out, ubilinux will broadcast it's name so we can more easily ssh in.

```bash
ssh root@ubilinux
```

# Getting mraa working

I couldn't get the npm version working. It wouldn't compile. So, here's the process for building mraa from scratch. Resources
 - [Sparkfun tutorial](https://learn.sparkfun.com/tutorials/installing-libmraa-on-ubilinux-for-edison)
 - [SWIG Build instructions](http://www.swig.org/Doc3.0/Preface.html)
 - [Nodejs Debian Backport](https://github.com/joyent/node/wiki/backports.debian.org)


The problem is that nodejs-dev isn't available for the standard ubilinux distribution.

```
# Add debian backport as an option
echo "deb http://http.debian.net/debian wheezy-backports main" | sudo tee /etc/apt/sources.list.d/backports.list

# Update nodejs to use the latest version
sudo apt-get remove nodejs
sudo rm -rf /usr/lib/node_modules
sudo apt-get -t wheezy-backports install nodejs-legacy nodejs-dev


# But it doesn't include NPM, so we need that too.
sudo apt-get install curl
curl -L --insecure https://www.npmjs.org/install.sh | sudo bash

# And get some useful packages
sudo npm install -g bower grunt-cli nodemon

# Prepare dependencies for the main build
sudo apt-get install libpcre3-dev cmake python-dev

# Build SWIG
wget http://prdownloads.sourceforge.net/swig/swig-3.0.5.tar.gz
tar -zxvf swig-3.0.5.tar.gz
cd swig-3.0.5
./configure
make
sudo make install
cd ~

# Build mraa
git clone https://github.com/intel-iot-devkit/mraa.git
mkdir mraa/build && cd $_
cmake ..
make
sudo make install
cd ~



# Build from npm

sudo ln -s /home/pilothouse/.node-gyp/0.10.36/src/ /usr/include/node

# Build Node.js (about an hour)
git clone https://github.com/joyent/node.git
cd node
git checkout v0.10.36
./configure && make -j 3 && sudo make install




```

# Add SSH keys
```
cat ~/.ssh/id_rsa.pub | ssh core@ubilinux2 'touch ~/.ssh/authorized_keys'
cat ~/.ssh/id_rsa.pub | ssh core@ubilinux2 'cat - >> ~/.ssh/authorized_keys'
```



# Can't access sudo

First off, install it:
```
# apt-get install sudo
# adduser core sudo
```


If you cut power to the Edison without doing a proper shutdown, you may get an error that says sudoers is read only. The solution is taken from [here](https://communities.intel.com/thread/58152):

```bash
umount /dev/mmcblk0p8
e2fsck /dev/mmcblk0p8
reboot
```

