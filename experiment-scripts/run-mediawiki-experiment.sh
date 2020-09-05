#!/bin/bash

#echo Experiment start time : $(date) >> $4

python3 mediawikiWorkloadGenerator_with_Poisson.py $1 $2 $3 $4

#echo Experiment finish time : $(date) >> $4
