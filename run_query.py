from getpass import getpass
from time import sleep
import sys

import splunklib.results as results
import splunklib.client as client

"""
Typical splunk query - ref http://dev.splunk.com/view/python-sdk/SP-CAAAEE5
"""

def return_stats(job):
    """Collect various stats into a dictionary"""
    stats = {"isDone": job["isDone"],
             "doneProgress": float(job["doneProgress"])*100,
              "scanCount": int(job["scanCount"]),
              "eventCount": int(job["eventCount"]),
              "resultCount": int(job["resultCount"])}
    return stats

passwd = getpass('enter Splunk password: ')

# Connect to Splunk Enterprise, assume splunk server is at localhost:8089
service = client.connect(username='mpenning', password=passwd,
    port=8089, host='localhost')

# Get the collection of search jobs
jobs = service.jobs

# Run a blocking search--search everything
print "Waiting for the search to finish..."

###
### Create a blocking search which returns the job's SID when the search is done
###
query = "search index=* sourcetype=* foo bar me earliest=-1d@d"
job = jobs.create(query, **{"exec_mode": "blocking"})

###
### Wait for search results to come back... poll until done
### 
while not job.is_done():

    stats = return_stats(job)
    status = ("\r%(doneProgress)03.1f%%   %(scanCount)d scanned   "
              "%(eventCount)d matched   %(resultCount)d results") % stats

    sys.stdout.write(status)
    sys.stdout.flush()

    sleep(0.25)

###
### Get the results and print each result dictionary
### 
offset = 0
count = 500
block_results = job.results(**{"count": count, "offset": offset})
while offset < return_stats(job)['resultCount']:

    for result in results.ResultsReader(block_results):
        print result

    offset += count
    block_offset = job.results(**{"count": count, "offset": offset})

job.cancel()   
sys.stdout.write('\n')

# Get properties of the job
print "Search job properties"
print "Search job ID:        ", job["sid"]
print "The number of events: ", job["eventCount"]
print "The number of results:", job["resultCount"]
print "Search duration:      ", job["runDuration"], "seconds"
print "This job expires in:  ", job["ttl"], "seconds"
