---
layout: post
title: My Programming Statistics
tags: [software development, personal, git]
---

![header image](/public/images/2020/03/30/programming-statistics-header-image.png)

I've been contracting for most of the last year. As part of this, I've been keeping careful record of my hours and how much code I write. I thought it would be interesting to dig deep through the data and answer an age old question: how fast am I?

<!--endexcerpt-->

# Method

All of my contracting has been targeted towards submitting code. There has been work on specifications, calls, reviews, and so on, but the end goal is all about the code. Therefore, all my hours eventually end up in the code base via pull requests.

I wrote a script to automate calculating the statistics for me. The heart of the script is two git commands. First, we get the commit hash for each of my pull requests:

```bash
git log --grep="Merge pull request #[0-9]* from AUTHOR" --oneline --pretty="%H,%cd,%ct" --since="DATE"
```

Then, for each hash, we get the statistics:

```bash
git diff --find-copies --find-renames --shortstat HASH^ HASH
```

I cleaned up the data a bit by removing bulk changes such as deleting entire directories, formatting large chunks of code, and so on. This removed 10s of thousands of changes from the final result.

After that, I summed up the statistics for each file to get some total numbers that I can compare to my total hours.

# Results

So, the interesting stuff. All of these are averages across the entire contracting period:

* 7.9 hours per pull request
* 2.1 files changed per hour
* 20 lines additions per hour
* 12 lines deletions per hour

One interesting conclusion is that it takes about a full work day for a pull request. I've submited many small, easily mergeable PRs, but there are also a few very large new features that I've worked on that have had quite a bit of time devoted to them, both in and out of the IDE. I suspect that's what's driving up the hours per pull request.

The other numbers refer to how fast I write code. These additions and deletions seems sort of slow. I'm supposed to be a professional software engineer, right? I think the numbers are low because I'm working with an existing code base and I try to be very careful with any changes I make, which tends to result in very few follow-up changes being required. That, plus the fact that this includes some pretty extensive R&D makes these results something I'm pretty comfortable with.
