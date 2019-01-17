from getpass import getpass
import sys

from splunklib.results import results
from splunklib.client import client


"""
Typical splunk query - ref http://dev.splunk.com/view/python-sdk/SP-CAAAEE5
"""

def return_stats(job):
    stats = {"isDone": job["isDone"],
             "doneProgress": float(job["doneProgress"])*100,
              "scanCount": int(job["scanCount"]),
              "eventCount": int(job["eventCount"]),
              "resultCount": int(job["resultCount"])}
    return stats

passwd = getpass('enter mpenning Splunk password: ')

# Connect to Splunk Enterprise, assume splunk server is at localhost:8089
service = client.connect(username='mpenning', password=passwd,
    port=8089, host='localhost')

# Get the collection of search jobs
jobs = service.jobs

# Create a search job
job = jobs.create()

# Run a blocking search--search everything
query = "search index=* sourcetype=* foo bar me"
print "Waiting for the search to finish..."

# A blocking search returns the job's SID when the search is done
job = jobs.create(searchquery_blocking, **{"exec_mode": "blocking"})

while True:
    while not job.is_ready():
        pass

    stats = return_stats(job)
    status = ("\r%(doneProgress)03.1f%%   %(scanCount)d scanned   "
              "%(eventCount)d matched   %(resultCount)d results") % stats

    sys.stdout.write(status)
    sys.stdout.flush()

    # Break out of the while loop, if done...
    if stats["isDone"] == "1":
        sys.stdout.write("\n\nDone!\n\n")
        break

    sleep(0.25)

# Get the results and display them
for result in results.ResultsReader(job.results()):
    print result

job.cancel()   
sys.stdout.write('\n')

# Get properties of the job
print "Search job properties"
print "Search job ID:        ", job["sid"]
print "The number of events: ", job["eventCount"]
print "The number of results:", job["resultCount"]
print "Search duration:      ", job["runDuration"], "seconds"
print "This job expires in:  ", job["ttl"], "seconds"
