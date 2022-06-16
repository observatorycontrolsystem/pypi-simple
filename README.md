# pypi-simple
A hand rolled PEP 503 compatiple PyPi repo

# Why?
I'd like to host Python packages on Github. But Github Packages doesn't support PyPi yet (https://github.com/github/roadmap/issues/94). So by hosting artifacts on Releases and generating the index (by hand for now), we can hack a PyPi repo together.

# Usage
Add YAML docs to `input/` and Github Actions will take care of the rest. Doesn't really matter how you name files or structure them. It'll recursively read all YAMLs in there.
