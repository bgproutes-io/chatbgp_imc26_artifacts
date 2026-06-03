import pybgpstream
import datetime
from utils_multiproc import parallel_bgp_collection, parallel_bgp_ribs

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

def get_ribs_multiproc(param_time, collectors_set, filter_aspath=None, max_workers=4):

    # The RIB of all VPs.
    rib = {}

    if len(collectors_set) > 0:
        # Collect RIB from the RIS collectors.        
        time_rib = get_previous_ris_rib_time(param_time)

        updates_list = parallel_bgp_ribs( \
            list(collectors_set), 
            from_time=datetime.datetime.strftime(time_rib-datetime.timedelta(minutes=10), "%m-%d-%Y %H:%M:%S"), \
            until_time=datetime.datetime.strftime(time_rib+datetime.timedelta(minutes=10), "%m-%d-%Y %H:%M:%S"), \
            filter=filter_aspath, \
            max_workers=max_workers
            )

        # Build the RIB
        for elem in updates_list:
            if elem[1] not in rib:
                rib[elem[1]] = {}
            try:
                rib[elem[1]][elem[4]] = list(map(lambda x:int(x), elem[5].split(" ")))
            except ValueError:
                pass

        # Update RIB with the updates between the RIN and the input time.
        updates_list = parallel_bgp_collection( \
            list(collectors_set), \
            from_time=datetime.datetime.strftime(time_rib, "%m-%d-%Y %H:%M:%S"), \
            until_time=param_time, \
            filter=filter_aspath, \
            max_workers=max_workers
            )

        # Update the RIB
        for elem in updates_list:
            # If it is a withdrawal.
            if elem[3] == 'W':
                if elem[1] in rib and elem[4] in rib[elem[1]]:
                    del rib[elem[1]][elem[4]]

            # If it is an announcement.
            elif elem[3] == 'A':
                if elem[1] not in rib:
                    rib[elem[1]] = {}

                try:
                    rib[elem[1]][elem[4]] = list(map(lambda x:int(x), elem[5].split(" ")))
                except ValueError:
                    pass

    return rib


if __name__ == '__main__':
    rib = get_ribs_multiproc("08-01-2024 00:00:20", ['RRC26', 'route-views.peru'])
    for peer_ip in rib:
        print ('{}: {}'.format(peer_ip, len(rib[peer_ip])))