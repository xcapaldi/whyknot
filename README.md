[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

 _________
< whyknot >
 ---------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

# whyknot
Very simple program which allows you to draw knots and extract knot parameters.

This package is really a wrapper over the pyknotid package which is capable of
identifying the important parameters of knots. That package lacks an easy interface with
which to describe knots arising in physical experiments so this hopes to remedy that. In
addition, this makes it easy to save the resulting data to csv or txt for later
analysis.

## Contributor guidelines

Try to follow PEP8 guidelines as much as possible (except that black line length
defaults are used; 88 chars). I also require the following to merge changes:

* Run pipreqs to generate an updated requirements.txt
* Run black to autoformat your code following PEP8 convention.

Otherwise just try to comment your work clearly.

## TODO

* Fix bridge switching algorithm
* Implement 3d plot display
* Migrate whole system to object oriented interface
