#!/usr/bin/env python3
#
# Brandon Parncutt
# brandon.parncutt@gmail.com
#
# snmpwalk.py


import optparse
import easysnmp
from threading import Thread
from queue import Queue


class SnmpSession(object):
    """Sets up a basic SNMP session"""

    def __init__(self, oid, version=2, hostname="localhost",
                 community="wookie"):
        self.oid = oid.split()
        self.version = version
        self.hostname = hostname
        self.community = community

    def walk(self):
        dictresult = {}
        try:
            result = easysnmp.snmp_walk(self.oid, hostname=self.hostname,
                                        community=self.community,
                                        version=self.version)
            dictresult = {item.oid_index: {item.oid: (item.value,
                                                      item.snmp_type)}
                          for item in result}
            for item in result:
                oid = item.oid_index
                if oid == item.oid_index:
                    dictresult[oid][item.oid] = (item.value, item.snmp_type)

        except:
            import sys
            print(sys.exc_info())
            result = None
        return dictresult


class SnmpController(object):
    """
    Controls the behavior and format of the output of the SnmpSession().
    """

    def config(self):
        results = {}
        ips = []
        p = optparse.OptionParser(description='A tool to query SNMP',
                                  prog='snmpwalk', version='snmpwalk 0.1a',
                                  usage='%prog [Options] [IP/Mask]')
        p.add_option('-c', '--community', help='Community String',
                     default='wookie')
        p.add_option('-o', '--oid', help='Object Identifier',
                     default='sysDescr', action='store')
        p.add_option('-H', '--hostname', help='Hostname or IP',
                     default='localhost', dest='host')
        p.add_option('-V', '--Version', help='SNMP version', default='2')
        p.add_option('-f', '--file', help='Read IPs or hostnames from a file',
                     dest='hosts_file', action="store", type="string")
        p.add_option('-r', '--range', help='specify or list IPs',
                     dest='range', action='store_true', default=False)

        options, arguments = p.parse_args()

        import sys
        if len(sys.argv) <= 1:
            p.print_help()
            sys.exit(1)

        if options.range:
            for arg in arguments:
                print(arg)
                try:
                    ips = IPy.IP(arg, ipversion=4)
                except:
                    print('Ignoring %s...not a valid IP' % arg)
                    continue
        if options.hosts_file:
            with open(options.hosts_file, 'r') as ipaddr:
                ips = [ip.rstrip() for ip in ipaddr]
        if ips:
            queue = Queue()
            if len(ips) < 25:
                num_threads = len(ips)
            else:
                num_threads = 25
            for i in range(num_threads):
                worker = Thread(target=self.queue_launcher,
                                args=(queue, options.oid, options.community))
                worker.setDaemon(True)
                worker.start()
            for ip in ips:
                queue.put(ip)
            queue.join()

        if options.host:
            self.run(options.oid, options.host, options.community)

    def queue_launcher(self, q, oid, community):
        while True:
            ip = q.get()
            print('Getting SNMP info for host:  %s' % ip)
            self.run(oid, ip, community)
            q.task_done()

    def run(self, oid, host, community):
        session = SnmpSession(oid, hostname=host,
                              community=community)
        results = session.walk()
        for item in results.values():
            print([(k, v) for k, v in item.items()])


if __name__ == '__main__':
    try:
        import easysnmp
    except ImportError as importerr:
        print(importerr, '\nPlease install the module "easysnmp".')
        sys.exit(1)
    try:
        import IPy
    except ImportError as importerr:
        print(importerr, '\nPlease install the module "IPy".')

    start = SnmpController()
    start.config()
