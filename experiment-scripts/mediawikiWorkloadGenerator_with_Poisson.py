# Example 1: asynchronous requests with larger thread pool
import asyncio
import concurrent.futures
import requests
import random
import time
import sys
import datetime
from numpy import random

counter = 0
generatedRequests = []

random.seed(0)

maxWorkers = int(sys.argv[1])
lambdaValue = int(sys.argv[2])
runningDuration = float(sys.argv[3])
fileName = str(sys.argv[4])

#numberOfRequests = int(sys.argv[1])
#runningDuration = float(sys.argv[2])
#fileName = str(sys.argv[3])

out = open(fileName, "a")
Links = open("/workspace/mediawiki-experiment/links.out", 'r')

links = Links.readlines()
links = [l.strip() for l in links]

host = 'http://192.168.245.53:8082'
#LINK = 'gw/index.php/Porsche_935'

print('Experiment is launching ...')
print('Experiment start time:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file=out)

async def main(numberOfRequest):
    global counter

    with concurrent.futures.ThreadPoolExecutor(max_workers=maxWorkers) as executor:
    #with concurrent.futures.ProcessPoolExecutor(max_workers=maxWorkers) as executor:

        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor, 
                requests.get, 
                str(host + random.choice(links))               
            )
            
            for i in range(numberOfRequest)
        ]

        for response in await asyncio.gather(*futures):
            print(response.status_code, response.elapsed.total_seconds(), file=out)
        
        counter = counter + 1
 
experiment_start_time = time.time()

totalRequest = 0

while (time.time() - experiment_start_time) < runningDuration:
    numberOfRequest = random.poisson(lam=lambdaValue, size=1)[0] 
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(numberOfRequest))
    print('Current iteration number', counter)
    print('Number of request', numberOfRequest)
    generatedRequests.append(numberOfRequest)
    totalRequest += numberOfRequest

print('Total number of request:', totalRequest)

print('Experiment finish time:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file=out)
print ('Total number of iteration:', counter, file=out)
print('Total number of request:', totalRequest, file=out)
print('List of generated request numbers:', generatedRequests, file=out)
