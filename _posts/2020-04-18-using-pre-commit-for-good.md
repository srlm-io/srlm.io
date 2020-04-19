---
layout: post
title: Using pre-commit for good
tags: [git, software development]
---

![header image](/public/images/2020/04/18/pre-commit-header-image.jpg)

Git has the ability to add hooks to common actions like committing. This allows you to run custom checks and stop the commit if something looks bad. I customize the pre-commit hook based on the particular project, but at a minimum I like to always have a staged file check and link check as baseline sanity checks.

I added the features discussed in the post to the [pre-commit hook](https://github.com/srlm-io/srlm-io.github.io/blob/master/.githooks/pre-commit) for this site.

<!--endexcerpt-->

# Make sure all your changes are staged

Often in the heat of the moment I forget to `git add -u :/` (add all tracked files to staging), and end up not committing everything that I wanted. I've found that in nearly all cases I want to commit all changes to every file that's being tracked by git. To do that, I have this little bash check:

```bash
if ! git diff --exit-code 1>/dev/null 2>&1; then
    echo "Please add unstaged changes"
    exit 1
fi
```

In the rare case where I don't want to commit a changed file I `git stash` the changes to get them out of the workspace.

# Make sure all your links are golden

Link rot is real. Also, I tend to forget to add the target of local links, or I don't format the link right, or all sorts of things. So I wrote a small [Python script](https://github.com/srlm-io/srlm-io.github.io/blob/master/scripts/link-checker.py) to scan and check all the links in the repository. The output is something like this:

```bash
$ python3 scripts/link-checker.py
_posts/2020-04-31-file.md: Web link invalid [http://fake.abc/]
_posts/2020-04-31-file.md: Invalid mailto link [mailto:bad]
_posts/2020-04-31-file.md: Unknown link [other/not-a-link]
_posts/2020-04-31-file.md: Not a file [/public/other/missing]
_posts/2020-04-31-file.md: File not tracked in git [/public/untracked]
Broken links found
```

# Skipping the pre-commit hook

Sometimes you want to skip the hook. Maybe you know it's going to fail but want to commit anyways, or maybe you're only making a small change that you know won't fail. You can skip it with the `--no-verify` flag to `git commit`.
