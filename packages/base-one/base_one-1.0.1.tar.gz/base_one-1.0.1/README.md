# base1 (python implementation)

This is a python implementation of Base1 encoding, as detailed in https://github.com/qntm/base1. It follows that API. I implemented this largely on 2025-12-29, for fun.

Fun fact: this project has to be called "base-one" on pypi because "base1" is considered too similar to an existing project, "basel". https://stackoverflow.com/a/71490005

It is a python library, but you can also use it as a simple command-line utility as a bonus. Given a string input, the first argument to the command, it gives you the base1n of that data. (Internally, the program takes whatever python gives it as the string that "is" argv[1] and then calls .encode() directly on that to get a `bytes`. If you're having problems with complicated utf-8/other-encoding characters, that might be the culprit.)

Qntm's base1 works with javascript concepts, which have analogues in python. So, we use `bytes` instead of UInt8Array or whatever, and `int` instead of BigInt. The names of functions uses snakecase instead of camelcase.

The algorithm to encode and decode base1, especially in closed form, is not entirely trivial if you just read qntm's readme. You can derive, with some analytical work. It's all there, but you have to think about it a little. (What does it mean, mathematically to, eg, "sort all possible buffers by length and then lexicographically"? that seems like it would take a lot of time for the CPU to execute). I purposefully did not read any of his code, so that I could use my own license instead of his. This software is public domain btw. Also, my test examples are just from his readme, which I'm treating as a standard (and also those cases as non-copyrightable due to the concept-expression merger for math (don't worry about that)).

I lost interest in this project after completing it but before testing it very well. I mean, I guess I do test it pretty well, because those test cases are how I figured out what the heck I was doing, but I don't know about code coverage, test framework, CI, etc etc.

Since the important part of Base1 encoding is the length of the base1 string, various (but not all) parts of this program refer to that concept as a "base1n" (it's just an int holding the value of the length instead of the string that is that long). That's... you know, kind of the joke of this whole project, when you get right down to it.
