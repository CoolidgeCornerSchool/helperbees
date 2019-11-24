---
title: CONTRIBUTING
layout: default
---

# Contributing Guide

Helper Bees is entirely a volunteer effort. Thanks for your interest in contributing!

## Admins

If you are interested in being a Helper Bees admin, please email [ccs.helperbees@gmail.com](mailto:ccs.helperbees@gmail.com)

Admin responsibilities include:

- Monitoring the [ccs.helperbees@gmail.com](mailto:ccs.helperbees@gmail.com) account.
- Answering questions from parents.
- Helping students with their accounts.

## Ideas

The best way to contribute ideas is to email [ccs.helperbees@gmail.com](mailto:ccs.helperbees@gmail.com) or create an issue in our [issue tracker][]. If you know any of the [contributors][], you are also welcome to buy them a beverage while you chat with them about your idea. :smile:

## Front end development

The following technologies are used on the front end:

- Jekyll
- Bootstrap
- jQuery

Hacking on the front end requires Jekyll to be installed. "Get up and running in seconds" from <https://jekyllrb.com> is a bit optimistic unless you are already a developer. Casual and non-developers should look at <https://jekyllrb.com/docs/installation/>

On Mac, we've seen decent success with installing Homebrew from <https://brew.sh> followed by the command below (then make sure `jekyll` is in your `$PATH`):

    gem install --user-install bundler jekyll

Once you have Jekyll installed you can run the following command...

    jekyll serve

... and then see the Helper Bees website at <http://localhost:4000>

To get a better understanding of available APIs, see <https://www.helperbees.org/api>

You can find "to do" items on our [project board][]. If you find something small to work on, please go ahead and make a pull request! You can also create an issue to explain any new feature or bug fix you'd like to implement.

## Back end development

The following technologies are used on the back end:

- Python
- AWS DynamoDB
- AWS Lambda

Please see the [back end documentation](docs/back_end.md) for additional details.

[issue tracker]: https://github.com/CoolidgeCornerSchool/issues
[contributors]: https://github.com/CoolidgeCornerSchool/helperbees/graphs/contributors
[project board]: https://github.com/CoolidgeCornerSchool/helperbees/projects/1
