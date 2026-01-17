# L* Algorithm Implementation

Pure Python implementation of Angluin's L* for learning regular languages from a black-box teacher.

## Features
- Starts with minimal E = {""}
- Automatic growth of S (prefixes) and E (suffixes)
- Full loop: closure → consistency → hypothesis → equivalence
- Visualizes learned DFA with Graphviz (tables + diagrams)

## Languages Learned
- Even number of 1s (2 states)
- Ends with "00" (3 states)
- No three consecutive 1s (4 states)
- No four consecutive 1s (5 states)
- Even 1s AND 0s mod 3=0 AND no three consecutive 1s (~19 states)

## How to Use
Change only the `Teacher` class for new languages.