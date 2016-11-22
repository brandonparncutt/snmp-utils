#!/usr/bin/env python3
#
# snmpd_df.py


import easysnmp
import re
import optparse


storage_table = easysnmp.snmp_walk(['hrStorageDescr', 'hrStorageSize',
                                    'hrStorageUsed',
                                    'hrStorageAllocationUnits'],
                                   hostname='localhost', community='public',
                                   version=2)


disk_index = {item.oid_index: {item.oid: item.value} for item in storage_table}


for item in storage_table:
    oid = item.oid_index
    if oid == item.oid_index:
        disk_index[oid][item.oid] = item.value

mem_match = re.compile('.*[Mm]emory')

badkeys = [key for key in disk_index.keys() if re.match(mem_match,
                                                        disk_index[key]
                                                        ['hrStorageDescr'])]
for key in badkeys:
    disk_index.pop(key)

megabytify = (lambda x: int(x) * int(item[1]
                                     ['hrStorageAllocationUnits']) /
              1024 / 1024)
print('{0:16}{1:>10}{2:>11}{3:>11}{4:>11}'.format('Filesystem', 'Total Size',
                                                  'Used', 'Available',
                                                  'Percent'))

for item in disk_index.items():
    print('{0:15}{1:10d}M{2:10d}M{3:10d}M{4:10d}%'.format(
                    item[1]['hrStorageDescr'],
                    int(megabytify(item[1]['hrStorageSize'])),
                    int(megabytify(item[1]['hrStorageUsed'])),
                    (int(megabytify(item[1]['hrStorageSize'])) -
                     int(megabytify(item[1]['hrStorageUsed']))),
                    round(int(item[1]['hrStorageUsed']) /
                          int(item[1]['hrStorageSize']) * 100)))
