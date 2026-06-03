import pybgpstream
import datetime

# Function to get the last RIS RIB.
def get_previous_ris_rib_time(time):
    # Determine the closest preceding RIB time (midnight, 8 AM, 4 PM)
    dt = datetime.datetime.strptime(time, "%m-%d-%Y %H:%M:%S")
    rib_times = [
        dt.replace(hour=0, minute=0, second=0, microsecond=0),
        dt.replace(hour=8, minute=0, second=0, microsecond=0),
        dt.replace(hour=16, minute=0, second=0, microsecond=0)
    ]
    previous_rib_time = max([rib_time for rib_time in rib_times if rib_time <= dt])
    return previous_rib_time

# Function to get the last routeviews RIB.
def get_previous_routeviews_rib_time(time):
    # Determine the closest preceding RIB time (midnight, 8 AM, 4 PM)
    dt = datetime.datetime.strptime(time, "%m-%d-%Y %H:%M:%S")
    rib_times = [
        dt.replace(hour=0, minute=0, second=0, microsecond=0),
        dt.replace(hour=3, minute=0, second=0, microsecond=0),
        dt.replace(hour=6, minute=0, second=0, microsecond=0),
        dt.replace(hour=9, minute=0, second=0, microsecond=0),
        dt.replace(hour=12, minute=0, second=0, microsecond=0),
        dt.replace(hour=15, minute=0, second=0, microsecond=0),
        dt.replace(hour=18, minute=0, second=0, microsecond=0),
        dt.replace(hour=21, minute=0, second=0, microsecond=0)
    ]
    previous_rib_time = max([rib_time for rib_time in rib_times if rib_time <= dt])
    return previous_rib_time

def get_ribs(param_time, collectors_set, filter_aspath=None):

    # The RIB of all VPs.
    rib = {}

    ####################################
    ############ RIPE RIS ##############
    ####################################

    # Get the RIS collectors.
    ris_collectors = set()
    for c in collectors_set:
        if 'RRC' in c:
            ris_collectors.add(c)
    # print (ris_collectors)

    if len(ris_collectors) > 0:
        # Collect RIB from the RIS collectors.
        time_rib = get_previous_ris_rib_time(param_time)
        stream = pybgpstream.BGPStream(
            from_time=datetime.datetime.strftime(time_rib-datetime.timedelta(minutes=10), "%m-%d-%Y %H:%M:%S"), \
            until_time=datetime.datetime.strftime(time_rib+datetime.timedelta(minutes=10), "%m-%d-%Y %H:%M:%S"), \
            collectors=list(ris_collectors),
            record_type="ribs",
            filter=filter_aspath
        )
        stream.set_data_interface_option("broker", "cache-dir", "/root/chatbgp/bgpstream/cache")

        # Build the RIB
        for rec in stream.records():
            for elem in rec:
                if elem.peer_address not in rib:
                    rib[elem.peer_address] = {}
                try:
                    rib[elem.peer_address][elem.fields['prefix']] = list(map(lambda x:int(x), elem.fields['as-path'].split(" ")))
                except ValueError:
                    pass

        # Update RIB with the updates between the RIN and the input time.
        stream = pybgpstream.BGPStream(
            from_time=datetime.datetime.strftime(time_rib, "%m-%d-%Y %H:%M:%S"), \
            until_time=param_time, \
            collectors=list(ris_collectors),
            record_type="updates",
            filter=filter_aspath
        )
        stream.set_data_interface_option("broker", "cache-dir", "/root/chatbgp/bgpstream/cache")

        # Update the RIB
        for rec in stream.records():
            for elem in rec:
                # If it is a withdrawal.
                if elem.type == 'W':
                    if elem.peer_address in rib and elem.fields['prefix'] in rib[elem.peer_address]:
                        del rib[elem.peer_address][elem.fields['prefix']]

                # If it is an announcement.
                elif elem.type == 'A':
                    if elem.peer_address not in rib:
                        rib[elem.peer_address] = {}

                    try:
                        rib[elem.peer_address][elem.fields['prefix']] = list(map(lambda x:int(x), elem.fields['as-path'].split(" ")))
                    except ValueError:
                        pass

    ####################################
    ########### Routeviews #############
    ####################################

    # Get the route-views collectors.
    rv_collectors = set()
    for c in collectors_set:
        if 'route-views' in c:
            rv_collectors.add(c)
    # print (rv_collectors)

    if len(rv_collectors) > 0:

        # Collect RIB from the RIS collectors.
        time_rib = get_previous_routeviews_rib_time(param_time)
        stream = pybgpstream.BGPStream(
            from_time=datetime.datetime.strftime(time_rib-datetime.timedelta(minutes=10), "%m-%d-%Y %H:%M:%S"), \
            until_time=datetime.datetime.strftime(time_rib+datetime.timedelta(minutes=10), "%m-%d-%Y %H:%M:%S"), \
            collectors=list(rv_collectors),
            record_type="ribs",
            filter=filter_aspath
        )
        stream.set_data_interface_option("broker", "cache-dir", "/root/chatbgp/bgpstream/cache")

        # Build the RIB
        for rec in stream.records():
            for elem in rec:
                if elem.peer_address not in rib:
                    rib[elem.peer_address] = {}

                try:
                    rib[elem.peer_address][elem.fields['prefix']] = list(map(lambda x:int(x), elem.fields['as-path'].split(" ")))
                except ValueError:
                    pass

        # Update RIB with the updates between the Routeviews peers and the input time.
        stream = pybgpstream.BGPStream(
            from_time=datetime.datetime.strftime(time_rib, "%m-%d-%Y %H:%M:%S"), \
            until_time=param_time, \
            collectors=list(rv_collectors),
            record_type="updates",
            filter=filter_aspath
        )
        stream.set_data_interface_option("broker", "cache-dir", "/root/chatbgp/bgpstream/cache")

        # Update the RIB
        for rec in stream.records():
            for elem in rec:
                # If it is a withdrawal.
                if elem.type == 'W':
                    if elem.peer_address in rib and elem.fields['prefix'] in rib[elem.peer_address]:
                        del rib[elem.peer_address][elem.fields['prefix']]

                # If it is an announcement.
                elif elem.type == 'A':
                    if elem.peer_address not in rib:
                        rib[elem.peer_address] = {}

                    try:
                        rib[elem.peer_address][elem.fields['prefix']] = list(map(lambda x:int(x), elem.fields['as-path'].split(" ")))
                    except ValueError:
                        pass

    return rib