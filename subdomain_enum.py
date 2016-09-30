#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys
import argparse
import socket
import requests
import signal
from ping import *

# Initialize the global variable
def init_enumeration():
	global online_subdmn
	online_subdmn = []


# CTRL+C Handler
def signal_handler(signal, frame):
	print "Subdomains founds : ",online_subdmn

	# Save subdomain's list
	with open('subdomain.lst','w+') as f:
		f.write("\n".join(online_subdmn))
	print "Exported in subdomain.lst"

	# Exit the soft
	exit(0)

	
# Scan a subdomain to determine if it's online
def scan_subdomain(dest_addr, timeout = 1, count = 1, psize = 64):
    mrtt = None
    artt = None
    lost = 0
    plist = []
    dest_addr = dest_addr.replace('https://','').replace('http://','')

    for i in xrange(count):
        try:
            delay = do_one(dest_addr, timeout, psize)
        except socket.gaierror, e:
            # Do not show failed host
            break

        if delay != None:
            delay = delay * 1000
            plist.append(delay)

    # Find lost package percent
    percent_lost = 100 - (len(plist) * 100 / count)

    # Find max and avg round trip time
    if plist:
        mrtt = max(plist)
        artt = sum(plist) / len(plist)


	if( percent_lost  == 0 ):
		print "\033[92mUP - \033[0m" + dest_addr
		return True
	else:
		# Do not show failed host
		return False


# Generate a list of potential subdomain
def brute_with_file(domain):
	print "[+] Brute subdomain from names.txt ..."
	# This interruption will manage CTRL+C in different states
	signal.signal(signal.SIGINT, signal_handler)

	with open('names.txt','r') as dict_file:
		dict_file = dict_file.readlines()
		
		# Determine online subdomain
		for index,subdmn in enumerate(dict_file):
			if scan_subdomain("http://"+subdmn.strip()+"."+domain):
				online_subdmn.append("http://"+subdmn.strip()+"."+domain)

	

# Extract subdomain from google results
def crawl_google_for_subdomain(domain):
	print "[+] Crawl from Google..."
	global online_subdmn
	for i in range(0,10):
		google_source = requests.get('https://www.google.fr/search?&q=site:*.'+domain+"&start="+str(i*10)).text
		websites = tuple(re.finditer(r'<cite>([^\'" <>]+)<\/cite>', google_source))

		for website in websites:
			print i, websites
			clean_url = '/'.join(website.group(1).split('/',3)[:-1])
			
			if(not "http" in clean_url):
				clean_url = "http://" + clean_url

			if(not clean_url in online_subdmn and not "www" in clean_url):
				online_subdmn.append(clean_url)

	# Sort the result
	online_subdmn = sorted(online_subdmn)
	for subdmn in online_subdmn:
		print "\033[92mFound - \033[0m" + subdmn