---
layout: post
title: Make a Robust Codebase
tags: [software development, teamwork, docker]
---

![robust code base header image](/public/images/2020/03/23/robust-code-base-header-image.jpg)

Maintaining and managing a project that spans dozens of contributors and years of usage isn't simple. However, there are a few tips that can help make it easier. In this post, I examine my top four tips to make it easier to work with big projects. By following these tips, you'll have a codebase that is more robust to external shocks, easier to change, and just more fun to work with.

<!--endexcerpt-->

# Add Automated Quality Checks

Automated tooling will help catch the dumb errors that are really hard to catch in code review. I like to have this hooked up to the git [pre-commit hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks), so that it's run on every commit. Obviously this can be bypassed by developers, but in that case they'll need to have a good reason.

The first thing to do is to make sure that unit tests run on every commit. This ensures that your code at least resembles some sort of functionality, can compile, etc.

Secondly, I like to run code style checks. For Python, this is Flake8. It ensures that everyone is writing code that at least looks similar.

For Python, I also run it through Mypy type checking. There's been many times where Mypy has caught issues with what variable is passed where, and the use of `# type: ignore` is an automatic red flag during code review ("Why are we ignoring that call?").

You probably have configuration or settings files somewhere. These files are typically considered "lower cost" to change, which can lead to faster release cycles. Great! But it's also really easy to forget a comma in a JSON, or get the wrong indentation in a YAML file. Here's where it's good to add a format check on these files to make sure that they don't have any syntax errors.

Finally, adding documentation checks to the pre-commit hook is extremely helpful. You can have it run the auto-doc generation program to make sure that works. You can also write a script to scan through your documentation, find links, and verify that the links have not gone stale.

As a bonus, these automated checks can be added to your Continuous Integration server. This will help prevent bad pull requests from being merged.

# Use Setup Scripts

A reproducible build is absolutely critical to a successful software project. When debugging, you need to understand which software packages are installed and how they're configured. A simple option is to put this into some documentation somewhere, but that is not sufficient. Documentation has to be read and gets out of date. Much better is to put setup into a script.

A setup script simply lists the steps needed to take a blank machine into one ready to run the application. This can include installing packages (`apt` and `pip`, for example). It can also include configuring the setup by tweaking settings files or other parameters. Finally, the setup script should install the application appropriately along with any scripts needed to start it (`init.d` or the like).

Writing a setup script is not easy. Many tasks, like "edit a file" can become extended exercises in `grep` and `sed`, or require investigation in alternative methods of configuration. The payoff is worth it though. First, new contributors can get up and running with a single script instead of hours of rooting around their computer. Second, deployed services can be recreated with little to no pain.

# Run In Docker or Virtual Machine

I don't know anybody who has a development machine where they know exactly what went into setting it up. On my machine I've tried to [document everything](https://github.com/srlm-io/provision-workstation) that I've changed, but in reality it's pretty much impossible to be able to recreate your development machine exactly.

When working with a shared code base this is even more of an issue. In the previous section we learned about using setup scripts to automate and make consistent our project's setup. But what happens when that setup script fails due to a conflict with your host machine? A common issue is that your host machine has version X of a packaged, but the project requires version Y. Or what happens when you have two projects, each requiring a different version?

Using a virtualized environment is perfect for solving the problem of project execution:
* You can have different environments for different projects
* The host operating system can follow the developer preference, while the project operating system can follow the project needs. Windows? Mac? Linux? Doesn't matter. Choose what works.
* You know and control exactly what goes into the environment. No need to guess or be surprised.

# Code Review Everything

Every submission to the repository should be code reviewed, and extensively so. Things that I look for:

* A submission should not have extra changes in it (like an unrelated bug fix or accidental submodule bump).
* Variable names make sense.
* The architecture of the solution makes sense.
* The changes are documented appropriately.
* The submitted solution is complete, and not lacking.

I tend to give quite a few comments on pull requests, especially for new hires or interns. Usually in their 1:1 meeting, before their first submission, I'll let them know to expect a bunch of comments, and that it is feedback on their code, not their ability. My goal with pull request feedback is to start a discussion, not to issue an edict.

Overall, I think extensive PR review helps make the code base healthier over the long run. It also ensures that it feels like one consistent artifact rather than a collection from many authors.

I also like to use the code review to slow things down a bit. I find that when I'm writing a new feature, I'll often be able to complete it in one go. However, if I come back a week later I'll discover a number of bugs or unintended side effects or just missing pieces. Slowing down the code submission process, and taking my time, results in higher quality code with fewer follow-on fix PRs. Obviously this principle can conflict with the needs of the business to get things done quick, but I've found that in most cases the end result is better and ultimately results in moving faster.
