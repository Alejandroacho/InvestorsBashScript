# Investor bill and verification bash script made in python

#### Requirements

You can install the bash requirementes running:

`pip3 install -r requirements.txt`

You must move to the simple script folder:

`cd Simple_script`

Then you will be able to run the bash like:

`python3 script.py --all=True`

There are many flags that you can look for running:

`python3 script.py -h`

You can run the tests running:

`pytest`

#### Assumptions

* Yearly subscription will not be payed if some year before was invested €50k or more.
* Percentage of the days in a year must be considered as first of January corresponds to100%.
* When you rests 1% to fees percentage the final percentage is the fee minus 1. Ex: 14% -> 13%.
