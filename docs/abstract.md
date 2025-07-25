# Abstract {#S-abstract}

This document is a set of guidelines for using C++ well.
The aim of this document is to help people to use modern C++ effectively.
By "modern C++" we mean effective use of the ISO C++ standard (currently C++20, but almost all of our recommendations also apply to C++17, C++14 and C++11).
In other words, what would you like your code to look like in 5 years' time, given that you can start now? In 10 years' time?

The guidelines are focused on relatively high-level issues, such as interfaces, resource management, memory management, and concurrency.
Such rules affect application architecture and library design.
Following the rules will lead to code that is statically type safe, has no resource leaks, and catches many more programming logic errors than is common in code today.
And it will run fast -- you can afford to do things right.

We are less concerned with low-level issues, such as naming conventions and indentation style.
However, no topic that can help a programmer is out of bounds.

Our initial set of rules emphasizes safety (of various forms) and simplicity.
They might very well be too strict.
We expect to have to introduce more exceptions to better accommodate real-world needs.
We also need more rules.

You will find some of the rules contrary to your expectations or even contrary to your experience.
If we haven't suggested you change your coding style in any way, we have failed!
Please try to verify or disprove rules!
In particular, we'd really like to have some of our rules backed up with measurements or better examples.

You will find some of the rules obvious or even trivial.
Please remember that one purpose of a guideline is to help someone who is less experienced or coming from a different background or language to get up to speed.

Many of the rules are designed to be supported by an analysis tool.
Violations of rules will be flagged with references (or links) to the relevant rule.
We do not expect you to memorize all the rules before trying to write code.
One way of thinking about these guidelines is as a specification for tools that happens to be readable by humans.

The rules are meant for gradual introduction into a code base.
We plan to build tools for that and hope others will too.

Comments and suggestions for improvements are most welcome.
We plan to modify and extend this document as our understanding improves and the language and the set of available libraries improve.
