#!/usr/bin/env python3

import urllib.request, urllib.parse, os.path

APIKEY = open(os.path.expanduser('~/.ddns-api-key')).read().strip()

def call(cmd, **args):
  '''Call a DreamHost API method'''
  args['key'] = APIKEY
  args['cmd'] = cmd
  result = [l.decode('ascii').strip() for l in
      urllib.request.urlopen('https://api.dreamhost.com/?' +
        urllib.parse.urlencode(args)).readlines()]
  return result[0], result[1:]

def replace_record(name, ip):
  '''Replace DH DNS records'''
  # find existing records
  status, response = call('dns-list_records')
  if status == 'success':
    for account_id, zone, record, type, value, comment, editable in (r.split('\t') for r in response[1:]):
      # and remove them
      if record == name and editable == '1':
        call('dns-remove_record', record=name, type=type, value=value)
  else:
    return False
  # add the new record
  status, response = call('dns-add_record', record=name, type='A', value=ip, comment='DDNS')
  return status == 'success'

print('Content-type: text/plain')
print('')


fs = dict(urllib.parse.parse_qsl(os.environ['QUERY_STRING']))
if 'hostname' in fs and 'myip' in fs:
  if fs['hostname'] != os.environ['REMOTE_USER']:
    print('nohost') # not a valid hostname / username combo
  else:
    myip = fs['myip']
    if replace_record(fs['hostname'], myip):
      print('good ' + myip) # worked according to plan
    else:
      print('nochg ' + myip) # didn't work out
else:
  print('error')
