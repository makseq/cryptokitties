Python app for optimal crypto kitties search to buy.
This app is crypto kitties marketplace crawler.
Tested on Ubuntu 16.10 with chromedriver.

# Usage #
```bash
./ck.py -h
usage: ck.py [-h] [-s S] [-N N] [--url URL] [-v V] [-p P] [-g G] [-b B]
             [--browser_wait BROWSER_WAIT] [--debug] [--start_offset]
             [--print_cat PRINT_CAT]

Find optimal kitties.

optional arguments:
  -h, --help            show this help message and exit
  -s S                  start page
  -N N                  number of pages to scan
  --url URL             url type [can be "cheap" or custom pattern]
  -v V                  min value
  -p P                  max price in eth
  -g G                  max gen
  -b B                  breed speed max level
  --browser_wait BROWSER_WAIT
                        browser wait until page loaded
  --debug               debug flag (show browser window)
  --start_offset        make start offset N on each next scan
  --print_cat PRINT_CAT
                        print cat value and some info
```