---
layout: post
title: Building Embedded Linux Images for Internal Tools
tags: [linux, deployment, iot, bash, ansible, yocto]
---

![building linux header image](/public/images/2020/04/08/building-linux-header-image.png)

Often when I'm developing software for distributed systems, I run into a situation where I have a small Python script that "just" needs to run on a Linux system. A laptop or RaspberryPi would be fine, but how do you go about setting everything up? You could just flash Raspbian onto an SD card, copy over the application script, and call it a day. But what if you need to make 10 of these? And then, in 3 months, do an update and build 5 more? Is it easy enough to train an intern to reproduce the setup and make more? Beyond a few devices, it makes sense to formalize the process of making the root file system. In this post I'll detail some methods to do that.

<!--endexcerpt-->


# The Goal

Our goal is to figure out a system that will allow us to install Linux on a target system (laptop, RaspberryPi, etc) and then install and configure our target application. This will help us release our embedded software better.

In order of importance, the things we'd like to achieve are:

- A Linux base system with appropriate packages installed and configured
- Reproducible: the build system should be able to make identical (or near enough) machines
- Easy and fast to set up new machines
- Fast to iterate when adding features
- Machines should be able to have unique configurations such as hostname and secrets

The best case is to take a blank disk and convert it into a fully functioning bootable drive with our application loaded and ready to go, all in one command. How difficult this will be to initially develop vs how difficult it is to duplicate will be the essential tradeoff of the methods explored here.

The methods are:

1.  Target manipulation: Manual/shell script
2.  Target manipulation: Ansible
3.  Image building: Archlinux's arch-chroot
4.  Image building: Yocto

One of the major stumbling blocks that I have encountered when learning these tools is that they span a range of disciplines, and none of them are covered in the typical college computer science course. Manual processes are what tutorials show, Ansible comes from web programming, arch-chroot comes from the Arch Linux hacker community, and Yocto comes from the embedded systems community. All of them are viable for building a bootable image, but the cross domain nature of these tools means that comparisons are rarely made.

For this post, we'll consider running the following steps for our hypothetical system:

1. Install dependencies
2. Build compiled applications with native tools
3. Install the application binaries and resources
4. Configure the operating system (start on boot, users, environment, etc.)
5. Add per-machine specific configuration (hostname, secrets, etc.)

Bonus points will be given if the tool supports multiple architectures, in particular x86 and ARM.

There are two major categories of build systems discussed here. The first, which I'll call target manipulation, are systems that work directly on a target machine with a base OS already installed. The second, image building, is systems that build from scratch and produce a .iso that can be installed on a host machine.

Definitions:

* **target machine**: the machine that you'd like your application to run on.
* **build machine**: your development or compiler machine that has the source code.

# Target Manipulation

This technique involves 3 phases:

1. Manually install an OS such as [Ubuntu](https://www.ubuntu.com/) or [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) on the target machine.
2. Manually provide a minimum configuration, enough to bootstrap the next phase.
3. Run some sort of script or instructions that finish configuring the host machine.

Within this category, there are a few tools that you can use. I'll discuss shell scripts and Ansible.

## Create an image with a Shell Script (aka, Manually)

This method is what pretty much every engineer finds themselves at sometime in their career. The script method is simply collecting all the shell commands that are required to configure a system. The good engineers will at least document the process, the better engineers will manu-automate the process by dumping all the commands into a shell script.

In order to get to the point of using a shell script an engineer will first need to install a base operating system. Once that gets booted up they'll need to copy the script onto the target which could be challenging by itself (configuring permissions, etc).

A typical shell script might look something like this:

```bash
opkg update
opkg install sqlite3

# The default bundled busybox tar had some troubles with extracting the 5.1.0 nodejs
opkg install tar

opkg remove --force-removal-of-dependent-packages nodejs
# Build and install the latest version of node
NODE_VERSION=node-v5.1.0
if [ ! -d ${NODE_VERSION} ] ; then
    wget http://nodejs.org/dist/latest-v5.x/${NODE_VERSION}.tar.gz
    tar -zxf ${NODE_VERSION}.tar.gz
fi

cd ${NODE_VERSION}
./configure && make -j 3 && make install
ln -s /usr/local/bin/node /usr/local/bin/nodejs
chmod +x /usr/local/bin/nodejs

cp /home/root/pilothouse/system/hostapd.conf /etc/hostapd/hostapd.conf
cp /home/root/pilothouse/system/udhcpd-for-hostapd.conf /etc/hostapd/udhcpd-for-hostapd.conf

systemctl disable wpa_supplicant.service
systemctl enable hostapd.service
cp /home/root/pilothouse/system/pilothouse.service /lib/systemd/system/
systemctl enable pilothouse.service

mkdir -p /settings
```

This script will install some dependencies, build some others, copy files around, enable services, and create required directories.

Pros:
* Fast to get started.
* Easy for non-specialists to hack.
* Good for short term projects.
* CPU architecture independent.

Cons:
* Need to manually install OS and configure on each unit.
* Hard to reproduce.
* Difficult to make more than a few units.
* Difficult to make idempotent.
* Some configuration might assume an interactive console, and can be really hard to automate.
* Difficult to maintain or upgrade.
* SSH hijinx required to get your files from the build machine to the target machine.


## Create an image with Ansible

[Ansible](https://www.ansible.com/) is a tool from the web development domain for configuring groups of long running systems. It's like shell scripting on steroids. The major benefit is that it offers idempotency: the Ansible configuration will specify the final state of the target system, and Ansible will apply whatever steps are needed to achieve that configuration.

Ansible runs on a host machine, such as your development/build computer, and uses SSH to connect to one or more targets. For each step in the playbook, Ansible will upload a script to the remote host and then execute it. Typically, the script will check the state of the machine and detect if any changes need to be made, and if so, apply those changes.

One nice feature of Ansible is that the script can be divided into smaller files, each with it's own concern. This allows you to make building blocks of your deployment, and gives you flexibility if you're deploying many different kinds of things in many different places.

```yaml
- hosts: localhost
  gather_facts: False
  become: yes
  tasks:
    - name: Create folder on target
      file:
        path: /opt/
        state: directory

    - name: Copy code to target
      copy:
        src: /src
        dest: /opt/

    - name: Update system
      apt:
        upgrade: dist

    - name: Install packages
      apt:
        name: "{{ item }}"
        state: latest
        update_cache: no
      with_items:
        - nodejs
        - npm
        - build-essential

    - name: Install Nodejs packages
      npm:
        name: "{{ item }}"
        state: latest
        global: yes
      with_items:
        - eslint
        - jshint

    - name: Adding existing user "{{ user }}" to groups
      user:
        name: "{{ user }}"
        groups: "{{ item }}"
        append: yes
      with_items:
        - dialout
        - docker

    - name: Increase inotify watches
      lineinfile:
        path: /etc/sysctl.conf
        regexp: '^fs.inotify.max_user_watches='
        line: fs.inotify.max_user_watches=1250000

```

Pros:
* Ensures every unit is in a consistent state.
* Architecture independent.
* Easy to update live systems.
* Easy to get started, and slowly build up a more complex system.

Cons:
* Need to manually install OS and configure on each unit.
* Requires SSH access, which can be difficult for remote systems behind firewalls.
* Systems can drift, since Ansible typically doesn't ensure what's *not* there.
* Updates in the base system can cause Ansible to fail, and you don't have much control over those updates.

# Image Building

We've talked about target manipulation. Target manipulation is good to bootstrap a project, but once you find yourself making the same system over and over again, over the course of months, then it's time to transition to building images.

Image building is fundamentally different: the goal is to use your build machine to make a complete root file system (RFS) that has both the OS and your application files installed. The RFS can then be installed on a USB stick or directly on the target's hard drive.

## arch-chroot

`arch-chroot` is a tool from [Arch Linux](https://www.archlinux.org/) that you can (ab)use for making bootable disks. `chroot` is an OS tool that allows you to create a sort of lightweight virtual environment. Normally it's a handy tool for system recovery, but in this case you can "recover" a system from scratch into your final image.

The basic process is to make your `chroot` and then use the same sort of scripts that you'd have for the "manual" method we looked at above. This would configure the system as if it was the final system. After your root file system is all set, you package it up into a nice disk image.

Overall, I mention this method simply because it's one path that I went down to create bootable images. I wouldn't recommend it, since Arch Linux is notoriously unstable and using `arch-chroot` in this method is definitely irregular.

Pros:
* Geek Status Achieved.
* You can end up with a bootable .iso.

Cons:
* Very unstable, likely to break every few months due to OS updates.
* Difficult to develop cleanly for.
* Lots of almost incomprehensible shell commands needed.

## Yocto

Ah, [Yocto](https://www.yoctoproject.org/). A project where "getting started" means several weeks of bashing your keyboard in frustration. Yocto is a fabulous tool (one of my favorites), but it's not something that you set up in an hour and forget about after that. It's incredibly complicated because, well, you're building Linux from the ground up. And that's literally what it is: the first thing it does is build the toolchain that is required to build the target. Everything is compiled from scratch, which means that the first time you build it can take 10+ hours.

With all the complexity, however, comes an incredible benefit: complete customizeability. You can specify every single detail of the operating system and your application. At the end of the build you end up with an .iso (or .tar.gz or whatever you want) that can be installed on your target operating system.

Yocto is structured as a series of recipes and image metadata files. A recipe typically corresponds to a piece of software. Inside a recipe are specifications for dependencies, what it provides, how to build and install it, and so on. Your image metadata specifies what packages you want and how it should be configured, and Yocto figures out how to assemble everything together into a coherent image.

Here's an (trimmed) example recipe for [gpsd](https://layers.openembedded.org/layerindex/recipe/1120/):

<!-- not technically bash, but Github doesn't seem to actually support bitbake filetypes -->
```bash
LICENSE = "BSD-2-Clause"
LIC_FILES_CHKSUM = "file://COPYING;md5=01764c35ae34d9521944bb6ab312af53"
DEPENDS = "dbus ncurses python3 pps-tools"
PROVIDES = "virtual/gpsd"

SRC_URI = "${SAVANNAH_GNU_MIRROR}/${BPN}/${BP}.tar.gz \
    file://0001-gps_shm_close-Free-privdata.patch \
"
SRC_URI[sha256sum] = "27dd24d45b2ac69baab7933da2bf6ae5fb0be90130f67e753c110a3477155f39"

INITSCRIPT_NAME = "gpsd"
INITSCRIPT_PARAMS = "defaults 35"

do_compile_prepend() {
    export PKG_CONFIG_PATH="${PKG_CONFIG_PATH}"
    export PKG_CONFIG="PKG_CONFIG_SYSROOT_DIR=\"${PKG_CONFIG_SYSROOT_DIR}\" pkg-config"
    export STAGING_PREFIX="${STAGING_DIR_HOST}/${prefix}"
    export LINKFLAGS="${LDFLAGS}"
}

do_install() {
    export PKG_CONFIG_PATH="${PKG_CONFIG_PATH}"
    export PKG_CONFIG="PKG_CONFIG_SYSROOT_DIR=\"${PKG_CONFIG_SYSROOT_DIR}\" pkg-config"
    export STAGING_PREFIX="${STAGING_DIR_HOST}/${prefix}"
    export LINKFLAGS="${LDFLAGS}"

    export DESTDIR="${D}"
    # prefix is used for RPATH and DESTDIR/prefix for instalation
    ${STAGING_BINDIR_NATIVE}/scons prefix=${prefix} python_libdir=${libdir} install ${EXTRA_OESCONS} || \
      bbfatal "scons install execution failed."
}

do_install_append() {
    install -d ${D}/${sysconfdir}/init.d
    install -m 0755 ${S}/packaging/deb/etc_init.d_gpsd ${D}/${sysconfdir}/init.d/gpsd
    install -d ${D}/${sysconfdir}/default
    install -m 0644 ${S}/packaging/deb/etc_default_gpsd ${D}/${sysconfdir}/default/gpsd.default
}

PACKAGES =+ "libgps libgpsd python3-pygps gpsd-udev gpsd-conf gpsd-gpsctl gps-utils"

RDEPENDS_${PN} = "gpsd-gpsctl"
RRECOMMENDS_${PN} = "gpsd-conf gpsd-udev gpsd-machine-conf"

RPROVIDES_${PN} += "${PN}-systemd"
SYSTEMD_SERVICE_${PN} = "${BPN}.socket ${BPN}ctl@.service"
```

Pros:
* Easy to scale to 100s or 1000s of machines.
* Completely reproducible builds.
* Reliable artifacts (.iso, etc).
* Built in open source license support.
* Great excuse for a 64 core 128GB "development" machine.
* Clean and reasonable project organization.

Cons:
* Very difficult to set up.
* Very difficult to maintain.
* Can be very difficult to bump to newer versions.
* Difficult to support a wide range of target hardware.
* Impossible if you don't know Linux

## Honorable Mention: Buildroot

[Buildroot](https://www.buildroot.org/) is an alternative to Yocto, solving the same kind of problems. I don't have any experience with it, so I don't have much more to say, but at some point I'll get around to trying it out.

## Honorable Mention: Docker

[Docker](https://www.docker.com/) can create a root file system, but to run it needs the Docker daemon. This precludes it from being a bootable image, so it's not suitable for installation directly on disk.

Docker is good as a layer on top though. What I've done, and some companies are offering a PaaS solution for, is to create a generic base image that can host Docker containers. This provides easy setup (you have one base image that can be shared across applications) while still maintaining easy application updates.

# Conclusion

We looked a four different ways to make a bootable target machine. Each of the four offers a different trade off between ease of development vs ease of installation, and which you choose will depend on your particular application.

For me, any professional project that I work on I'd prefer to use Yocto. It's a steep learning curve, but in a professional environment it provides the stability and tooling that is required.
