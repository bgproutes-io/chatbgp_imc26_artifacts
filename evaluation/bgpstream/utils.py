import os
import re
import time
import urllib.request
from datetime import datetime

def get_routeviews_peers():
    # Update the route views peers file if current one is older than 24 hours.
    if not os.path.isfile('route-views.txt') or time.time() - os.path.getmtime('route-views.txt') > 60*60*24:
        print ('Update Route-Views peers file.')
        url = 'http://www.routeviews.org/peers/peering-status.html'

        with open('route-views.txt', 'w') as fd:
            fd.write(urllib.request.urlopen(url).read().decode())

    peer_list = []
    with open('route-views.txt', 'r') as fd:
        for line in fd.readlines():
            if 'routeviews.org' in line:
                line = ' '.join(line.split())
                meta = line.split('|')[0]
                metatab = meta.split(' ')

                collector = metatab[0].replace('.routeviews.org', '')
                asn = int(metatab[1])
                peer_addr = metatab[2]
                nb_pref = int(metatab[3])

                peer_list.append((collector, peer_addr, asn, nb_pref))

    return peer_list

def get_ris_peers():
    # Update the route views peers file if current one is older than 24 hours.
    if not os.path.isfile('ris.txt') or time.time() - os.path.getmtime('ris.txt') > 60*60*24:
        print ('Update RIS peers file.')
        url = 'http://www.ris.ripe.net/peerlist/all.shtml'

        with open('ris.txt', 'w') as fd:
            fd.write(urllib.request.urlopen(url).read().decode())

    peer_list = []
    cur_collector = None

    cur_line = 0

    with open('ris.txt', 'r') as fd:
        for line in fd.readlines():
            line = line.strip()

            if '<h2> RRC' in line:
                cur_collector = line.split(' -- ')[0].replace('<h2>', '').strip()

            # Get the AS number.
            if cur_line == 0 and line.startswith('<td> <a href="https://stat.ripe.net/'):
                linetab = line.split('<td>')
                asn = int(linetab[1].split('>')[1].replace('</a', '').replace('AS', ''))
                cur_line += 1

            elif cur_line == 1: 
                linetab = line.split('<td>')
                name = linetab[1].replace('</td>', '').strip()
                cur_line += 1
            
            elif cur_line == 2:
                linetab = line.split('<td>')
                peerip = linetab[1].replace('</td>', '').strip()
                cur_line += 1

            elif cur_line == 3:
                linetab = line.split('<td>')
                nb_pref_ipv4 = int(linetab[1].replace('</td>', '').strip())
                cur_line += 1

            elif cur_line == 4:
                linetab = line.split('<td>')
                nb_pref_ipv6 = int(linetab[1].replace('</td>', '').strip())
                cur_line = 0

                peer_list.append((cur_collector, peerip, asn, nb_pref_ipv4+nb_pref_ipv6))

    return peer_list    

def get_vps_info():
    peers_list_rv = get_routeviews_peers()
    peers_list_ris = get_ris_peers()

    dic_peer = {} # ASN -> vps.
    for collector, peerip, asn, nb_pref in peers_list_rv+peers_list_ris:
        if asn not in dic_peer:
            dic_peer[asn] = set()
        dic_peer[asn].add((collector, asn, peerip))

    return dic_peer

def get_collector_from_ip(ip_protocol=None, vantage_points=None):
    collector_set = set()
    asn_set = set()

    dic_peer = get_vps_info()
    for asn in dic_peer:
        for collector, asn, peerip in dic_peer[asn]:
            if ip_protocol is None or ':' in peerip and 'ipv6' in ip_protocol:
                if vantage_points is None or peerip in vantage_points:
                    collector_set.add(collector)
                    asn_set.add(asn)
            elif ip_protocol is None or ':' not in peerip and 'ipv4' in ip_protocol:
                if vantage_points is None or peerip in vantage_points:
                    collector_set.add(collector)
                    asn_set.add(asn)

    return collector_set, asn_set

def get_asn_from_ip(ip_protocol=None, vantage_points=None):
    asn_set = set()

    dic_peer = get_vps_info()
    for asn in dic_peer:
        for collector, asn, peerip in dic_peer[asn]:
            if ip_protocol is None or ':' in peerip and 'ipv6' in ip_protocol:
                if peerip in vantage_points:
                    collector_set.add(collector)
            elif ip_protocol is None or ':' not in peerip and 'ipv4' in ip_protocol:
                if peerip in vantage_points:
                    collector_set.add(collector)
    return collector_set

def fill_ases():
    asset = set()
    with open('20240701.as-rel.txt', 'r') as fd:
        for line in fd.readlines():
            if line.startswith('#'):
                continue 

            linetab = line.rstrip('\n').split('|')
            as1 = int(linetab[0])
            as2 = int(linetab[1])
            asset.add(as1)
            asset.add(as2)

    with open('ases.txt', 'w') as fd:
        for asn in asset:
            fd.write(str(asn)+'\n')

def fill_comm():
    commset = set()
    with open('tmp.txt', 'r') as fd:
        for line in fd.readlines():
            if line.startswith('#'):
                continue
            linetab = line.rstrip('\n').split('|')
            commstr = linetab[11]
            commlist = commstr.split(' ')
            for c in commlist:
                commset.add(c)
    
    with open('comm.txt', 'w') as fd:
        for c in commset:
            fd.write(str(c)+'\n')

def fill_prefixes():
    prefset = set()
    with open('tmp.txt', 'r') as fd:
        for line in fd.readlines():
            if line.startswith('#'):
                continue
            linetab = line.rstrip('\n').split('|')
            prefset.add(linetab[5])
            
    with open('prefixes.txt', 'w') as fd:
        for p in prefset:
            fd.write(str(p)+'\n')


if __name__ == "__main__":
    # print (get_vps_info())
    # fill_prefixes()
    print (get_routeviews_peers())