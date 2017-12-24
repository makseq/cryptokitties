#!/usr/bin/env python
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
import time
from multiprocessing import Pool, Process
import argparse
import urllib2

GENS = ['Gen ' + str(i) for i in xrange(0, 5)]
SPEEDS = ['Fast', 'Swift', 'Snappy', 'Brisk', 'Plodding', 'Slow', 'Sluggish', 'Catatonic']
MAX_PRICE = 0.7
MIN_VALUE = 0.0022
CHROME_MODE = 'headless'
BROWSER_WAIT = 7
VALUES = None


def read_value_dex():
    response = urllib2.urlopen('https://cryptokittydex.com/')
    html = response.read()
    html = BeautifulSoup(html, 'lxml')
    attr = html.select('a.badge.badge-pill.badge-cattribute.badge-big.cattribute')

    d = {}
    for a in attr:
        obj = a.text.replace(',', '').split()
        name = obj[0]
        v = float(obj[1])
        value = 1.0 / v
        d.update({name: value})
    return d


def user_print_cat(cat_number):
    global MIN_VALUE, VALUES
    MIN_VALUE = 0
    VALUES = read_value_dex()
    args = 'none', 'none', 'none', 'https://www.cryptokitties.co/kitty/'+str(cat_number), 0
    print_cat(args)


def print_cat(args):
    name, gen, speed, url, price = args
    values = VALUES
    try:
        options = selenium.webdriver.ChromeOptions()
        if CHROME_MODE: options.add_argument(CHROME_MODE)
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        time.sleep(BROWSER_WAIT)
        htmlSource = driver.page_source
        driver.close()

        soup = BeautifulSoup(htmlSource, 'lxml')
        result = soup.select('.ListAttributes-item')
        catributes = [r.string for r in result]

        children = len(soup.select('.KittiesList-item')) - 2

        cat_value = sum([values[v] for v in catributes])
        if cat_value > MIN_VALUE:
            msg = ' ' + name + '\n'
            msg += '\t%6.6s  %7.7s  children %3.3s  value %4.4f  =  %f \n' % (gen, speed, children, cat_value, price)
            msg += '\t' + ' '.join(catributes) + '\n'
            msg += '\t' + url + '\n'
            print msg
        return 0

    except:
        print 'print failed:', url
        return 0


def grab_kittens(url):
    try:
        options = selenium.webdriver.ChromeOptions()
        if CHROME_MODE: options.add_argument(CHROME_MODE)
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        time.sleep(BROWSER_WAIT)
        htmlSource = driver.page_source
        driver.close()

        soup = BeautifulSoup(htmlSource, 'lxml')
        result = soup.select('.KittiesGrid-item')
    except:
        print 'failed:', url
        return []
    return result

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Find optimal kitties.')
    parser.add_argument('-s', type=int, default=0, help='start page')
    parser.add_argument('-N', type=int, default=10, help='number of pages to scan')
    parser.add_argument('--url', default='%i', help='url type [can be "cheap" or custom pattern]')
    parser.add_argument('-v', type=float, default=0.0010, help='min value')
    parser.add_argument('-p', type=float, default=0.7, help='max price in eth')
    parser.add_argument('-g', type=int, default=4, help='max gen')
    parser.add_argument('-b', type=int, default=2, help='breed speed max level')
    parser.add_argument('--browser_wait', type=int, default=7, help='browser wait until page loaded')
    parser.add_argument('--debug', default=False, action='store_true', help='debug flag (show browser window)')
    parser.add_argument('--start_offset', default=False, action='store_true', help='make start offset N on each next scan')
    parser.add_argument('--print_cat', type=int, default=-1, help='print cat value and some info')
    args = parser.parse_args()

    if args.debug:
        CHROME_MODE = ''

    if args.print_cat > 0:
        user_print_cat(args.print_cat)
        exit(-1)

    start, N = args.s, args.N
    args.url = '%i?orderBy=current_price&orderDirection=asc&sorting=cheap' if args.url == 'cheap' else args.url
    MIN_VALUE = args.v
    MAX_PRICE = args.p
    GENS = ['Gen ' + str(i) for i in xrange(0, args.g+1)]
    SPEEDS = SPEEDS[0:args.b]
    BROWSER_WAIT = args.browser_wait
    print 'min value', MIN_VALUE, '| max price', MAX_PRICE, '| max gen', GENS[-1], '| slowest speed', SPEEDS[-1]

    while 1:
        print '---------------------------------------------------------'
        count = 0
        min_p, max_p = None, None
        VALUES = read_value_dex()

        # calc pages to scan
        url = 'https://www.cryptokitties.co/marketplace/sale/' + args.url
        urls = [url % i for i in xrange(start, start + N + 1)]
        print 'URL pattern:', url, '[start', start, 'end %i]' % (start + N)

        pre_results = []
        for result in Pool(N).imap_unordered(grab_kittens, urls):
            if result:
                # print 'Found cats', len(result)
                for cat in result:
                    name = cat.select_one('.KittyCard-subname').string
                    speed = cat.select_one('.KittyCard-coldown').string
                    href = cat.select_one('a')['href']
                    price = cat.select_one('.KittyStatus-note').text
                    price = float(''.join([c for c in price if c in '.0123456789']))

                    catgen = ' '.join(cat.select_one('.KittyCard-subname').string.split()[-2:])
                    gen = [g for g in GENS if catgen == g]
                    gen = gen[0] if gen else ''

                    # stats
                    count += 1
                    if min_p > price or min_p is None: min_p = price
                    if max_p < price or max_p is None: max_p = price

                    # find condition
                    if speed in SPEEDS and gen and price <= MAX_PRICE:
                        pre_results += [[unicode(name), str(catgen), str(speed), str('https://www.cryptokitties.co'+href), float(price)]]

        # print results in multiprocessing
        if pre_results:
            p = Pool(6)
            p.map(print_cat, pre_results)

        # move start to next if need
        start = start + N if args.start_offset else start

        print 'Stats: found', count, 'cats with min price', min_p, 'and max price', max_p
        print '\n\n\n'
        time.sleep(10)

