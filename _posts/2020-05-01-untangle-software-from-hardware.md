---
layout: post
title: Untangle Software From Hardware
tags: [embedded, software development, teamwork]
---

![header image](/public/images/2020/05/01/decouple-header.jpg)

Embedded developers must fight the siren call of hardware. Our whole job is to write code that interacts with the hardware, that talks back and forth and changes the world. But we're seduced by the notion that we can get away with leaking hardware into our design.

Developing software for embedded devices is taught as an exercise in "getting it to work". You're done once your code can talk to the peripheral and it doesn't crash. This works for the classroom. For the professional software engineer it's a dangerous pattern. You're building a hardware dependency into your code. This will increase the cost of everything that you do for the life of the product, and probably have a negative effect on future products as well.

What do we get when we naively build hardware into our embedded code?
1. A waterfall development process: hardware must be ready before software can be developed
1. Reuse for product variations or entirely new products becomes difficult or impossible
1. New code is and untested code is blindly released, or goes through a slug fest of manual testing
1. A collection of bug reports from the field labeled "Can not reproduce"

We can combat this by making a few changes to how we develop software. The fundamental change is changing our development process from experimentation to thinking. This change will address the points raised above by making it easier to develop and maintain the application. As a bonus for the individual developer this also allows offsite development.

We'll cover how to untangle hardware from your code in three different phases of your development process:
1. Design: architect the application to isolate hardware
1. Develop: simulate hardware with mocks
1. Maintain: instrument the application to log data

We'll never be able to decouple 100% of development from the hardware, but we can certainly get most of the way there.

<!--endexcerpt-->

Let's create an example to anchor ourselves. You're developing a smart office building that monitors heating and cooling. This system has a bunch of temperature sensors and HVAC controllers. I'm picking this example because it's an embedded application, but it's also one that most engineers can easily visualize as distinct from the hardware.

In this post I mostly focus on how to mitigate the effects of hardware peripherals, without much focus on the CPU architecture. For example, if your entire application is written in C for running on ARM then you should write your tests to run on the target processor with the target libraries installed. This is a compromise, but worthwhile: the CPU has a huge effect on the application but a relatively small effect on the development process, so we pick our battles and focus on peripherals.

# Design: Hardware Abstraction APIs

![architecture interest image](/public/images/2020/05/01/architecture.jpg)

Hardware independence starts at the architecture stage of our application. In college they teach you to just start talking to the hardware, then build some algorithms into that, and then ship it. Ship it! In the real world that leads to code that is very hard to test and tightly coupled to the hardware.

When we design our application we want to minimize the hardware dependencies. What this means is that we have three levels of hardware abstractions. The lowest level is the actual communication API provided by the operating system. This layer typically deals with specifics like serial communication or writing bytes. The next level is a hardware wrapper that provides higher level, peripheral specific functionality such as setting a value or moving to a position. The third, final, and optional layer is the subsystem abstraction. This is a layer that encapsulates multiple different hardware pieces and multiple different high level actions. For example, it could be a self calibration routine for a camera.

These three layers of hardware abstractions need to be built in and designed from the start. It's very difficult to refactor an application to support these clean layer lines.

The benefits are easier testing of the two categories of code: hardware agnostic and hardware specific. The agnostic code can be easily tested with mocking, discussed below. Counter intuitively, the hardware specific is easier to test as well because the scope is much smaller. Separation into layers means that your hardware code has not seeped into the whole application, and hence you only have to test a small portion of the application with actual hardware.

In our smart office example this means that our control and business logic is distinct from our hardware logic. The hardware wrapper could be something like a temperature sensor API, an occupancy sensor API, and an HVAC control API. The subsystem abstraction could be a representation of an integrated office with options to set building wide temperature across all the rooms.

# Develop: Mocking

![mock interest image](/public/images/2020/05/01/mock.jpg)

For decades, Aerospace and mechanical engineers have been verifying their work with simulations using tools like stress analysis for mechanisms, flow modeling for injection molding, thermal checks for heat transfer, and more. Thousands of simulations, testing anything and everything, checks that the system has the correct behavior. This enables these engineers to design without the hardware, and to test things that would be dangerous or impossible to test in the real world. The end result is that the need for testing with actual hardware happens only rarely, and then only to be the final check.

Somehow the embedded software profession gave built these tools and never learned to adopt them.

Let's look at the simplest form of simulation, mocking. A [mock](https://docs.python.org/3.8/library/unittest.mock.html) is a software component that replaces something else, and allows you to verify that it was called in a desired way. Mocks are powerful because they allow you to test cases that would be very difficult, or even dangerous, to test with real hardware.

Mocking can be at all different levels, whether that's the hardware API level discussed above, or even within that API to mock a very specific hardware interaction.

In our smart office example we could mock the temperature sensor API to create a simulated sensor. This simulated sensor should return values that are normal values, boundary values, and some completely crazy values. This highlights a very important benefit to mocking: we're able to test our software with values that would be difficult or impossible to achieve if we did the same tests with actual hardware.

The prerequisite to mocking is that you must unit test everything. Most engineers working on hardware avoid unit testing because of a perception that it's hard, not worth the time, or just don't know how. The better perspective is that unit testing will help you  understand the hardware and naturally create internal APIs that decouple your stack.

# Maintain: Data Collection

![logging interest image](/public/images/2020/05/01/logging.jpg)

Investigating bug reports is a fact of life for all developers. The first question is "where is this bug coming from?". Can you isolate it to an algorithm problem? What about an exception caused by a peripheral? Maybe it's something stateful. Hardware complicates this because often times a peripheral will have a very rare and unusual failure that you've never seen before, never expected, and can't reproduce.

This is where data and logging comes into it. You should instrument your system so that everything is recorded. Every state change, every warning or failure, and every important piece of data. Most of the time these logs are not used or even looked at, and simply dumped into a data swamp or discarded into `/dev/null`. But that's ok since the computer works for *us*, not the other way around. When a bug report comes in you'll be able to use the data to either solve the problem entirely or reduce your debugging time by isolating the problem to a very specific component.

Data collection is a mitigation technique. It helps you reduce effort after you're done developing. It won't help you much if the foundations of your application are poorly designed, and it won't help you if you don't build the data processing tools that allow you to glean insight.

Our smart office naturally fits into this data collection pattern. Every temperature sensor reading should be recorded, along with commands sent to the HVAC and inputs from the user. With all this it's easy to discover the chain of causality that lead to that really hot office situation (maybe a broken sensor reporting a temperature of -1) or many other issues. It can also let you detect more subtle conditions such as the HVAC unit staying on longer and longer, which might indicate reduced airflow due to a clogged filter.

With data, we can examine systems in the production environment and use that to feed back into our development process, all without ever having to touch and debug hardware. Because hardware always finds a way to mess you up regardless of how much testing you've done.

# Conclusion

Building a hardware product is challenging. It requires the cooperation of diverse engineering disciplines and a strong will to push through roadblocks.

Building software for a hardware product isn't about the hardware. It's about the abilities that software can provide to the hardware. The flexibility to change functionality, the integration with outside services, the cost down that can be done by software defined actions.

Unfortunately, most embedded developers get lost in the hardware. They design with the hardware, they test with the hardware, and they debug with the hardware. This will create a bottleneck since they won't be able to get started until the hardware is ready and sitting on their desk. But I propose that we can do better. As software engineers, we can develop our systems largely independent of the hardware. Let's make the computer work for us, instead of being a slave to the processor.

By following these three techniques we get:
1. A better architecture that is easier to build and test
1. Comprehensive testing, with the ability to easily add tests as corner cases are discovered
1. Faster response times to issues
1. Faster R&D times, since software can be developed before hardware is ready
1. Development that can be done from anywhere, without needing the hardware

Pretty compelling, right? This is how professionals develop embedded software.
