#!/usr/bin/env python

from __future__ import print_function, absolute_import

import os
import re
import socket
import sys

from collections import OrderedDict

def hostnameId():
    """ Return the identification part of our hostname. 

    Returns
    -------
      hostid : str
         For example, with hostname == 'bee-r3.pfs', returns 'r3'
             or 'moxa-sm1.pfs' returns 'sm1'
    """

    fullHostname = socket.gethostname()
    hostname = os.path.splitext(fullHostname)[0]

    try:
        _, hostid = hostname.split('-')
    except ValueError:
        raise ValueError("hostname (%s) is not for a PFS spectrograph host" % (fullHostname))

    return hostid

class SpectroIds(object):
    validSites = {'S','J','L','X'}

    def __init__(self, unitName=None, site=None):
        """ Parse our name into component parts.

        By default, uses our hostname and the site.pfs dns value.

        Args
        ----
        unitName : string
           If set, something like 'sm2' or 'r1'
        site : %s
           One of the valid PFS sites

        Internally, we track:
          - the spectrograh module (1-4)
          - the arm (b,r,n,None)
          - the site
        and construct other names from those.

        """ % (SpectroIds.validSites)

        if unitName is None:
            unitName = hostnameId()

        m = re.search('^sm([0-4])$', unitName)
        if m is not None:
            self.sm = int(m.group(1))
            self.arm = None
        else:
            m = re.search('^([brn])([0-4])$', unitName)
            if m is not None:
                self.sm = int(m.group(2))
                self.arm = m.group(1)
            else:
                raise NameError('name (%s) is neither a module nor a camera name' % (unitName))

        if site is None:
            import os
            site = os.environ.get('PFS_SITE')

        if site not in self.validSites:
            raise RuntimeError('site (%s) must one of: %s' % (site, self.validSites))
        self.site = site

    @property
    def cam(self):
        if self.arm is None:
            return None
        return "%s%d" % (self.arm, self.sm)

    @property
    def specNum(self):
        return self.sm

    @property
    def specModule(self):
        return 'sm%d' % (self.sm)

    @property
    def idDict(self):
        """ Return all our parts in a dictionary/namespace. """

        _idDict = OrderedDict(site=self.site,
                              cam=self.cam,
                              arm=self.arm,
                              specNum=self.specNum,
                              specName=self.specModule)
        return _idDict

    ids = idDict

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if isinstance(argv, str):
        import shlex
        argv = shlex.split(argv)

    import argparse

    sites = SpectroIds.validSites

    parser = argparse.ArgumentParser()
    parser.add_argument('--site', default=None, choices=sites,
                        help='pass in site name')

    ourName = parser.add_mutually_exclusive_group()
    ourName.add_argument('--cam', dest='unitName', default=None,
                         help='pass in camera name (e.g. "b2")')
    ourName.add_argument('--module', dest='unitName', default=None,
                         help='pass in module name (e.g. "sm3")')

    parser.add_argument('--key', default=None,
                        help='instead of all part names and values, print just this value.')
    args = parser.parse_args(argv)

    try:
        ids = SpectroIds(unitName=args.unitName, site=args.site)
    except:
        parser.print_help()
        raise

    idDict = ids.idDict

    if args.key is None:
        print(' '.join(["%s=%s" % (k,idDict[k]) for k in idDict]))
    else:
        try:
            print(idDict[args.key])
        except KeyError:
            print("unknown id key: %s" % (args.key))
            sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
