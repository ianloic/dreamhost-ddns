#!/usr/bin/env python

import urllib
import cgi
import sys
import os.path

APIKEY = open(os.path.expanduser('~/.ddns-api-key')).read().strip()

def call(cmd, **args):
  '''Call a DreamHost API method. Turn each named python argument into named REST argument.'''
  args['key'] = APIKEY
  args['cmd'] = cmd
  result = [l.strip() for l in 
            urllib.urlopen('https://api.dreamhost.com/?' +
                           urllib.urlencode(args)).readlines()]
  return result[0], result[1:]

def replace_record(hostname, ip):
  '''Replace DH DNS records'''
  # find existing records
  status, response = call('dns-list_records')
  if status == 'success':
    for account_id, zone, record, type, value, comment, editable in (r.split('\t') for r in response[1:]):
      # and remove them
      if record == hostname and editable == '1':
        call('dns-remove_record', record=hostname, type=type, value=value)
  else:
    return False
  # add the new record
  status, response = call('dns-add_record', record=hostname, type='A', value=ip, comment='DDNS')
  return status == 'success'

print 'Content-type: text/plain'
print ''

try:
  hostname = os.environ['REMOTE_USER']
except KeyError:
  print("REMOTE_USER not provided. .htaccess may not be set properly.")
  exit(0)
  
try:
  myip = os.environ['REMOTE_ADDR']
except KeyError:
  print("REMOTE_ADDR not provided. Are you running in a web sever?")
  exit(0)

if replace_record(hostname, myip):
  print 'good: {} set to {}'.format(hostname,myip)
else:
  print 'nochg ' + myip # didn't work out
