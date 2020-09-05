'''
Created on Jan 3, 2020

@author: ahmeda
'''
import math
import random
from time import sleep

import datetime
import sys
import random             
import multiprocessing as mp
import time,requests,math,traceback,glob,os
import numpy as np
from __main__ import traceback

fn = str(sys.argv[3]) #'/workspace/keras-experiment/KerasImageNetTest.out'
my_file = open(fn, "a")

print("Keras experiment is launching...")
print('Experiment start time:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file=my_file) 
random.seed(0)
def nextTime(rateParameter):
     return -math.log(1.0 - random.random()) / rateParameter
 
TimeOfReq=[]
for i in range(5,161,5):
    for j in range(10):
              summer=0
              for k in range(1,i):
                      const=nextTime(i)
                      TimeOfReq+=[const]
                      summer+=const
              if summer<1:
                TimeOfReq[-1]=1-summer+TimeOfReq[-1]

HOST = "http://obelix53:8084/predict"
images=[]
os.chdir("/workspace/mediawiki-keras-sysbench-experiments/experiment-scripts/testSet/")
for file in glob.glob("*.jpg"):
    images+= [open(file, "rb").read()]
print(len(images))
os.chdir("/workspace/mediawiki-keras-sysbench-experiments/")

lambdaValue = int(sys.argv[1])
TIME_OF_RUNNING = int(sys.argv[2])

CONSTANT_WORKLOAD=[]

total_number_of_request = 0

for i in range(TIME_OF_RUNNING):
    generated_poisson_value = np.random.poisson(lam=lambdaValue, size=1)[0]
    print("Generated Poisson value:", generated_poisson_value)
    CONSTANT_WORKLOAD.append(generated_poisson_value)
    total_number_of_request += generated_poisson_value
#CONSTANT_WORKLOAD=[generated_poisson_value]*TIME_OF_RUNNING

print("Total number of requests", total_number_of_request)

DROP_REQUESTS_AFTER=30
SLEEP=1

RAMP=[500.0]*10
RAMP+=[600.0]*10
RAMP+=[700.0]*10
RAMP+=[800.0]*10
RAMP+=[900.0]*10
RAMP+=[1000.0]*10

NUMBER_OF_REQUESTS=CONSTANT_WORKLOAD
print("Array length", len(NUMBER_OF_REQUESTS))
host=HOST
payload={"image":random.choice(images)}
r = requests.post(host,files=payload).json()
if r["success"]:
    for (i, result) in enumerate(r["predictions"]):
        print("{}. {}: {:.4f}".format(i + 1, result["label"],
            result["probability"]))
else:
    print("Request failed")
    
#fn = str(sys.argv[3]) #'/workspace/keras-experiment/KerasImageNetTest.out'

def worker(j,q):
    '''stupidly simulates long running process'''
#     for weights in ['uniform', 'distance']:
    t1=time.time()
    payload={"image":random.choice(images)}
    #print LINK
    
    r = requests.post(HOST,files=payload,timeout=300).json()
    t2=time.time()
    
    RT=t2-t1
    out= str(RT)
#    out=r," ", t1, t2, " ", RT
    q.put(out)
#     print "out", out
    return out
 
def listener(q):
    '''listens for messages on the q, writes to file. '''
 
    f = open(fn, 'w') 
    while 1:
        m = q.get()
#
       # print("m", m)
        if m == 'kill':
#            f.write('killed')
            break
        f.write(str(m) + '\n')
    f.flush()
    f.close()

def main():
    #must use Manager queue here, or will not work
    manager = mp.Manager()
    q = manager.Queue()    
    pool = mp.Pool(150)
 
    #put listener to work first
    watcher = pool.apply_async(listener, (q,))
 
     
    jobs = []
    #fire off workers
    for i in NUMBER_OF_REQUESTS:
        time.sleep(SLEEP)
        for j in range(1,int(i+1)):
            job = pool.apply_async(worker, (i,q))
            jobs.append(job)
        
 
    # collect results from the workers through the pool result queue
    for job in jobs: 
        try:
            job.get()
#        print xxx
        except :
          print("There was an error")
          print(traceback.print_exc())
          continue
  
    #now we are done, kill the listener
    q.put('kill')
    pool.close()
 
if __name__ == "__main__":
    #print('Experiment is launching ...')
    main()
    print('Total number of request', file=my_file)
    print('Generated request numbers:', CONSTANT_WORKLOAD, file=my_file)
    print('Experiment end time:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file=my_file)
