#!/usr/bin/env python

import re
from datetime import datetime, timedelta
import linecache

#input file
file='/input/log_insight_text.txt'

#output files
out_feat1 = open('/output/hosts.txt','w')    
out_feat2 = open('/output/resources.txt','w')    
out_feat3 = open('/output/hours.txt','w')    
out_feat4 = open('/output/blocked.txt','w')

###########################################

Domain=[];
      
with open(file) as f:
        for l in f:
            #domain
            domain=re.split('[ - [ " ]',l)[0]
            Domain.append(domain)
            

Domain_IP=[]   
Domain_NUM=[]

for d in Domain:
    if d not in Domain_IP:
        Domain_IP.append(d)
        Domain_NUM.append(1)
    else:
        Domain_NUM[Domain_IP.index(d)] +=1
        
             
#################
# FEATURE 1  ####
#################

Zip_Domain=zip(Domain_IP,Domain_NUM)      
Zip_Domain.sort(key=lambda tup: tup[1], reverse=True)

#out_feat1 = open('/Users/uma2103/Insight22/output_test/hosts.txt','w')   
for i in range(3):
    #print Zip_Domain[i]
    print>>out_feat1, Zip_Domain[i]

out_feat1.close()

##################
# FEATURE 2 #####
################

Page=[];
Bandwidth=[];

with open(file) as f:
    for i, l in enumerate(f):
        band=re.split('[ - [ " ]',l)[-1].split('\n')[0]
        if band=='-':
            band=0
        Bandwidth.append(int(band))  

#index of the max. Bandwidth
Bandwidth.index(max(Bandwidth))

#out_feat2 = open('/Users/uma2103/Insight22/output_test/resources.txt','w') 
for i in range(10):
    line_num=Bandwidth.index(max(Bandwidth))
    line = linecache.getline(file, line_num+1) # get line number line_num+1
    page=re.split('[ - [ " ]',line)[8];
    print>>out_feat2, page+', ', max(Bandwidth)
    del Bandwidth[Bandwidth.index(max(Bandwidth))]

out_feat2.close()

##################
# FEATURE 3 #####
###############

Time=[];

with open(file) as f:
        for i, l in enumerate(f):
            time=re.split('[ - [ " ]',l)[4] + ' '+re.split('[ - [ " ]',l)[5].split(']')[0];
            #the followinf will change the format to Python date time format
            Time.append(datetime(int(time[7:11]),7,int(time[0:2]), int(time[12:14]), int(time[15:17]), int(time[18:20]) ))
 


NUM_VISITS=[] # contains number of visits
t=0;
DATE1=Time[0];
END_DATE= Time[-1];
DATE2=DATE1+timedelta(minutes=60)

Which_T=[]

while DATE2<END_DATE:
    NUM_VISITS.append(len([T for T in Time if (T>=DATE1 and T<=DATE2)]))
    Which_T.append(DATE1.strftime('%Y/%m/%d %H:%M:%S'))
    #update date
    DATE1=DATE2
    DATE2= DATE1+timedelta(minutes=60)

    
Zip_NUM_VISIT=zip(Which_T,NUM_VISITS)      
Zip_NUM_VISIT.sort(key=lambda tup: tup[1], reverse=True)

#out_feat3 = open('/Users/uma2103/Insight22/output_test/hours.txt','w')
for i in range(3):
    print Zip_NUM_VISIT[i]
    print>>out_feat3,Zip_NUM_VISIT[i]
    

out_feat3.close()

#################
# FEATURE 4 #####
#################

FAILED_IP=[]
FAILED_TIME=[];
IP_INDEX=[] #index of IP in original file


# identify failed logins and their index
with open(file) as f:
    for i, l in enumerate(f):
        if '"POST' in l and re.split('[ - [ " ]',l)[11]=='401':   # failed login          
            domain =re.split('[ - [ " ]',l)[0]
            time=re.split('[ - [ " ]',l)[4] + ' '+re.split('[ - [ " ]',l)[5].split(']')[0];
            FAILED_IP.append(domain)
            FAILED_TIME.append(datetime(int(time[7:11]),7,int(time[0:2]), int(time[12:14]), int(time[15:17]), int(time[18:20]) ))
            IP_INDEX.append(i) #index of failed IP in original list (log.txt)


Blocked_IND=[] # index of failed IPs in the FAILED_IP (not original)

for i in range(len(FAILED_IP)):
    D1=FAILED_TIME[i]
    D20=D1+timedelta(seconds=20)
    TT= [tt for tt in FAILED_TIME if tt >=D1 and tt<=D20] #
    if len(TT) >=3: # gaurentees three access at least
        ind= FAILED_TIME.index(TT[0]) # index of fist access
        # if fist element (where its failed time>=3) exists three or more times in the array FAILED_IP, keet it index!. 
        if FAILED_IP[ind:ind+len(TT)+1].count(FAILED_IP[ind]) >=3:
            Blocked_IND.append(ind)
 
#out_feat4 = open('/Users/uma2103/Insight22/output_test/blocked.txt','w') 
# Final feature 4!
for blocked_ind in Blocked_IND:
    EVIL_IP=Domain[IP_INDEX[blocked_ind]] #EVIL IP name 
    end_blocked_time= Time[IP_INDEX[blocked_ind]]+timedelta(minutes=5)
    
    TTT= [ttt for ttt in Time if ttt >=Time[IP_INDEX[blocked_ind]] and ttt<=end_blocked_time] #    
    
    ind_end_blocked_time=Time.index(TTT[-1]) # index of 5 mins later.
    with open(file) as f:
        #for l in islice(file,blocked_ind, ind_end_blocked_time):#search between blocked time until 5 mins lter.
        for i, l in enumerate(f):
            if (i>IP_INDEX[blocked_ind] and i<=ind_end_blocked_time):    
                if EVIL_IP in l:
                    print>>out_feat4,l


out_feat4.close()


