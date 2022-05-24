"""
reader.pyt
Claudia Espinoza, claudia.espinoza@meduniwien.ac.at
Created: 10:00 AM 11/03/2022
Last modifcation: 23/05/2022

1. Contains a class to load binary files recorded with INTAN together with Pybpod information

Example:
>>> import reader 
>>> mypath = "C:\\raw_data\\Analysis\\maousename\\folder intan date\\Data\\"
>>> myfile = "name folder Pybpod"
>>> data = reader.Trials_info(path = mypath, pybpodfile = myfile) --> Object to load experimental information
>>> myexp = data.ttl_organizer() --> print a general TTL INTAN and PYBPOD info
>>> myname = myfile + ".pkl"
>>> myexp.to_pickle(myname)  # where to save it, usually as a .pkl # to save the file

>>> data.print_gral() --> print a general TTL INTAN and PYBPOD info

Extra info:
To run json file, I hadd to install in the environment: conda install prompt_toolkit=2.0.10
to read it again
>>> df = pd.read_pickle(myname)
"""

import os
import pandas as pd
import numpy as np
import json
import glob
from pathlib import Path


class Trials_info():
    '''
    It loads binary files recorded with INTAN together with Pybpod information (labels).
    It contains:
    It is important to introduce the path, This can be done manually, better to use the following logic:
    C:\\raw_data\\Analysis\\subject_name\\experiment_date\\Data\\foldername_intan
    How to run it: In the reader file, include the name of the file and or the path, or doing it in 
    e.g. import reader
    mypath = 'C:\\raw_data\\Analysis\\mouse_animal\\fileintan_name\Data\\pybpodfile_name
    exp = reader.Trials_info(path = mypath, pybpodfile = myfile)
    myfile = exp.ttl_organizer()
    ''' 
    cwd = os.getcwd()
    
    def __init__(self, path = 'C:\\raw_data\\Analysis\\Test\\20211126_A\\Data\\', pybpodfile = '211126_150834' ):
        #setting the path and folder name
        self.path = path
        self.pybpodfile = pybpodfile  
        os.chdir(self.path)
        #os.chdir(os.path.join(self.path,self.pybpodfile))
        
        #read json and csv file
        csvname = glob.glob(path +"/*.csv")[0]
        self.csvname = csvname
        jsonname = glob.glob(path + "/*_settings_obj.json")[0]
        self.jsonname = jsonname
        
        # General information session from csv
        self.gralinfo = pd.read_csv(self.csvname, sep = ';',skiprows = 7, usecols=[4,5], nrows=14, names = ["Msg","Info"]) 
        # trials info
        self.mydf = pd.read_csv(self.csvname, sep = ';',skiprows = 21, usecols=[0,1,4], names=["Type", "PC-time", "Msg"]) 
        
        # Opening JSON file
        self.loadjson = open(self.jsonname,)
        self.jsondata = json.load(self.loadjson) # returns JSON object as a dictionary
        
        # Opening a intan file with ttl signals (digitalin.dat)
        
        with open('digitalin.dat', 'rb') as fp:
            self.rec_ch = np.fromfile(fp, np.dtype('uint16')) # will transform to 16-bit integers 
        
        # Chanels to read from digitial intan. Check speifications function binreader
        self.BNC1 = 1
        self.BNC2 = 0
    
    
    def binreader(self, data, ch):
        """
        It reads the TTL signal from PyBpod to INTAN file to obtain 
        Rotary encoder: intan channels (ch) 0,1 and BNC1 and BNC2: positions 4,5.
        For more explanation check notion page: Lab\seccion Analysis and Methods\Organization analyzes Behavior\
        (reading binary data by using 2**0, 2**1, 2**2, 2**3, etc)
        Input: file as np.dtype('uint16') with the information from e.g.: 'digitalin.dat'
        output
        """
        digital_channel = list(map( lambda x: int((x & (2** ch)) > 0 ), data)) # int allows logical comparison with 0 (1-0 instead true and false)
        return(np.array(digital_channel))
     
        
    def print_gral(self):
        """
        It print general infomration of the subject and session, summary trials
        """
         ## 1. Counting all the messages output
        unique, counts = np.unique(self.mydf['Msg'].astype(str), return_counts=True)
        DictCounter = dict(zip(unique, counts))

        ## 2. Indexing correct trials (right and left choices)
        idx_correctright = [c for a,b,c in (zip(self.mydf['Msg'],self.mydf['Type'],self.mydf.index)) 
                            if a == 'reward_right' and b == "TRANSITION" ]
        idx_correctleft = [c for a,b,c in (zip(self.mydf['Msg'],self.mydf['Type'],self.mydf.index)) 
                           if a == 'reward_left' and b == "TRANSITION"]

        ## 3. Indexing incorrect trial (right and left choices)
        idx_incorrectright = [c for a,b,c in (zip(self.mydf['Msg'],self.mydf['Type'],self.mydf.index)) 
                              if a == 'no_reward_right' and b == "TRANSITION"]
        idx_incorrectleft = [c for a,b,c in (zip(self.mydf['Msg'],self.mydf['Type'],self.mydf.index)) 
                             if a == 'no_reward_left' and b == "TRANSITION"]

        ## 4. Indexing non responded trials
        idx_noresp = [c for a,b,c in (zip(self.mydf['Msg'],self.mydf['Type'],self.mydf.index)) 
                      if a == 'stop_open_loop_fail' and b == "TRANSITION"]
        
        ## 5. Number of rule present in the session
        unique2 = np.unique(self.jsondata['rule_switch_li'])
        
        # General session information   
        print (self.gralinfo.iloc[4,0], "=", self.gralinfo.iloc[4,1])
        print (self.gralinfo.iloc[1,0], "=", self.gralinfo.iloc[1,1])
        print (self.gralinfo.iloc[6,0], "=", self.gralinfo.iloc[6,1])
        print (self.gralinfo.iloc[9,0], "=", self.gralinfo.iloc[9,1][2:6])
        print (self.gralinfo.iloc[12,0], "=", self.gralinfo.iloc[12,1])
        print ("USER-NAME =", self.gralinfo.iloc[2,1][2:9])
        
        print ('Total initialized trials:', DictCounter['New trial'])
        print ('Total finalized trials:', DictCounter["The trial ended"])
        print ('N Correct trials:', len(idx_correctright) + len(idx_correctleft))
        print ('N Incorrect trials:', len(idx_incorrectright) + len(idx_incorrectleft))
        print ('N No responded trials:', len(idx_noresp))
        print ('N Right choices:', len(idx_correctright) + len(idx_incorrectright))
        print ('Responded trials:', len(idx_correctright) + len(idx_correctleft) + len(idx_incorrectright) + len(idx_incorrectleft ))
        print ('Rules present in the task:', unique2)

    
    def ttl_organizer(self):
        """
        It creates a new data frame with the TTL signals included
        How to use it:
        >>> data = reader.Trials_info(path = mypath, pybpodfile = myfile)
        >>> myexp = data.ttl_organizer();
        save the information later manually
        >>> myexp.to_pickle(mynamepkl)
        Read after as
        >>> mydf = pd.read_pickle(mypathpkl)
        """
        # 1. Creates a data frame only with the information need it
        nmydf = self.mydf.copy()
        myidx = np.where((nmydf['Type'] == "SOFTCODE") | (nmydf['Type'] == "EVENT") | 
                         (nmydf['Type'] == "INFO") | (nmydf['Type'] == "STATE") | (nmydf['Type'] == "END-TRIAL"))[0]
        nmydf.drop(myidx, axis =0, inplace=True) # drop specific rows
        nmydf = nmydf.reset_index(drop=True) # reset the indexes
        
        # eliminate rows that are need it
        myidx2 = np.where((nmydf['Msg'] == "sync_state_1") | (nmydf['Msg'] == "sync_state_2") | 
                  (nmydf['Msg'] == "sync_state_3") | (nmydf['Msg'] == "wheel_stopping_check") |
                  (nmydf['Msg'] == "open_loop") |  (nmydf['Msg'] == "inter_trial")|
                  (nmydf['Msg'] == "check_reward_left") | (nmydf['Msg'] == "check_reward_right")|
                  (nmydf['Msg'] == "end_state") | (nmydf['Msg'] == "end_state"))[0]
        nmydf.drop(myidx2, axis =0, inplace=True)
        nmydf = nmydf.reset_index(drop=True) 
        fsize = len(nmydf["Msg"]) # size of the file
        
        # 2. RENAMING: change labels of the Msg!!!!!
        myidx3 = np.where(nmydf['Msg'] == "reset_rotary_encoder_open_loop")[0]
        for idx in myidx3:
            nmydf['Msg'][idx] = "closed_loop"
        
        # 3. Indexing correct and incorrect trials to create an array with the information 
        ## 3.1. Indexing correct trials (right and left choices)
        idx_correct =  np.where((nmydf['Msg'] == 'reward_right') | (nmydf['Msg'] == 'reward_left'))[0]
        whole_cor = [vals for idx in idx_correct for vals in list(range(idx-3,idx+3))] # correct trials have 6 indexes from stim presentation to end
       
        ## 3.2. Indexing incorrect trial (right and left choices)
        idx_incorrect = np.where((nmydf['Msg'] == 'no_reward_right') | (nmydf['Msg'] == 'no_reward_left'))[0]
        whole_incor = [vals for idx in idx_incorrect for vals in list(range(idx-3,idx+3))]

        ## 3.3. Indexing non responded trials
        idx_noresp = np.where(nmydf['Msg'] == 'stop_open_loop_fail')[0]
        whole_noresp = [vals for idx in idx_noresp for vals in list(range(idx-2,idx+3))] # whole trial has 5 index from stim presentation

        ## 3.4. Indexing wheel-not stopping (CHECK!!)
        idx_wns = np.where(nmydf['Msg'] == 'wheel_stopping_check_failed_punish')[0]
        
        ## 3.5. Indexing the begginning and end of each trial
        idx_init = np.where(nmydf['Msg'] == 'New trial')[0] #used for the json file and intan
        idx_end = np.where(nmydf['Msg'] == 'end_state_signal')[0] # used for jason file and intan
       
        ## 4. Creating a comlumn for summary data frame with corrcet and incorrect trials
        ## Important states New trial and reset_rotary_encoder... are NaN values (affected by wheel not stopping)      
        response = np.full(fsize, np.nan)
        for c in whole_cor:
            try:
                response[c] = 1
            except IndexError:
                pass
            continue

        for i in whole_incor:
            try:
                response[i] = 0
            except IndexError:
                pass
            continue
            
        ## 4.2 adding the column to the data frame
        nmydf["Response"] = response
        
        # 5. INSISTIVE MODE ON. None = isit off, right, on the right side, left in the left side
        # 5.1 tranform to right =  1, left = -1, no active = 0. Then to get when the mode is active use unsigned values
        insist = [self.jsondata['insist_mode_li'][x][1] for x in range(len(self.jsondata['insist_mode_li']))] 
        insist = np.array(insist)
        insist = np.where(insist == 'right',1, insist)
        insist = np.where(insist == 'left',-1, insist) 
        insist = np.where((insist != 1) & (insist != -1), 0, insist)
        
        # 5.2 insiston = np.full(len(nmydf["Msg"]), np.nan)
        ins_mode = list(range(fsize))
        ins_trials = ins_mode
        for i in range(len(idx_end)):
            ins_trials = np.where((ins_mode >= idx_init[i]) & (ins_mode <= idx_end[i]), insist[i], ins_trials)

        ins_trials = np.where((ins_trials != 1) & (ins_trials != -1)  & (ins_trials != 0), np.nan, ins_trials)
        
        ## 5.3 Adding the column to the data frame
        nmydf["Insistive_mode"] = ins_trials
 
        # 6. SIDE OBJECT PRESENTATION: Object presented in the right side. 1 is right, 0 is left
        # In the Msg left or right indicates mouse choice. When mouse choice (Msg, keft or right) and side_stimulus
        # are the same the response is correct (1)
        right_json = np.array([int(self.jsondata['sides_li'][r]['right']) for r in range(len(self.jsondata['sides_li']))], dtype = int)
        
        right_idx = list(range(fsize))
        right_trials = right_idx
        for i in range(len(idx_end)):
            right_trials = np.where((right_idx >= idx_init[i]) & (right_idx <= idx_end[i]), right_json[i], right_trials)

        right_trials = np.where((right_trials != 1) & (right_trials != 0), np.nan, right_trials)
        ## 6.2 adding the column to the data frame
        nmydf["Side_stimulus"] = right_trials
        
        # Rules
        # 7. Rule 0 or 1 (rule first or second) CHECK!!!!! WITH DATA WITH TWO RULES
        rule_json = [int(self.jsondata['rule_switch_li'][i][-1]) for i in range(len(self.jsondata['rule_switch_li']))]
        rule_json = np.array(rule_json)

        rule_idx = list(range(fsize))
        rule_trials = rule_idx
        for i in range(len(idx_end)):
            rule_trials = np.where((rule_idx >= idx_init[i]) & (rule_idx <= idx_end[i]), rule_json[i], rule_trials)

        rule_trials = np.where((rule_trials != 1) & (rule_trials != 0), np.nan, rule_trials)
        ## 7.2 adding the column to the data frame
        nmydf["Rule"] = rule_trials
        
        
        ## 8. INTAN FILE
        # 8.1 Trasform the binary data from intan 
        dg0 = self.binreader(data = self.rec_ch, ch = self.BNC2) # BNC 2
        dg1 = self.binreader(data = self.rec_ch, ch = self.BNC1) # BNC 1
        
        # 8.2 Tranform previous values in ttl signals 0, on and -1 when the ttl is on and 1 when it is off.
        ttl0 = np.diff(dg0) # BNC 2
        ttl1 = np.diff(dg1) # BNC 1
        
        # 8.3 Getting speific times from INTAN
        # Getting reward periods from INTAN file
        rw_time = np.where((ttl1 == 1) & (ttl0 == 0)) #responded trials. It signals reward check time
        
        # beginning and end of each trial
        ttrials = np.where((ttl1 == 1) & (ttl0 == 1)) #all iitialized trials
        start_trials = ttrials[0][0::2] #beggining of the trials
        end_trials = ttrials[0][1::2] # end of the trials
        
        # Intermediate transitions states
        trans_time = np.where((ttl1 == 0) & (ttl0 == 1))
        
        # reward waiting 
        rwwaiting = np.where((ttl1 == -1) & (ttl0 == 1))
        
        # 8.4 In the PYBPOD file the beginning and the end of a signal
        pybpodIE = np.where((nmydf["Msg"] == "New trial") | (nmydf["Msg"] == "end_state_signal"))
        # Signaling reward
        pybpodrward = np.where((nmydf["Msg"] == "reward_left") | (nmydf["Msg"] == "reward_right") | 
                       (nmydf["Msg"] == "no_reward_left") | (nmydf["Msg"] == "no_reward_right"))
        # intermidiate transitions states pybpod BNC1, BNC2 == 0 1
        pybpodtrans = np.where((nmydf["Msg"] == "reset_rotary_encoder_wheel_stopping_check") | (nmydf["Msg"] == "wheel_stopping_check_failed_punish") | 
                        (nmydf["Msg"] == "present_stim") | (nmydf["Msg"] == "closed_loop") | 
                        (nmydf["Msg"] == "stop_open_loop_fail") | (nmydf["Msg"] == "open_loop_fail_punish") |
                        (nmydf["Msg"] == "stop_open_loop_reward_left") | (nmydf["Msg"] == "stop_open_loop_reward_right") )
        pybpodwaiting  = np.where((nmydf["Msg"] == "reward_left_waiting") | (nmydf["Msg"] == "reward_right_waiting"))
        
        # Creating an array and including ttl signals position from the intan file
        ttlintan = np.zeros(len(nmydf["Msg"]))
        for a,b in zip(pybpodIE[0], ttrials[0]):
            ttlintan[a] = b    
        for a,b in zip(pybpodrward[0], rw_time[0]):
            ttlintan[a] = b  
        for a,b in zip(pybpodtrans[0], trans_time[0]):
            ttlintan[a] = b 
        for a,b in zip(pybpodwaiting[0], rwwaiting[0]):
            ttlintan[a] = b 
        
        nmydf['Ttl_Intan'] = ttlintan 
        return(nmydf)
    
    
    def stm(self):
        """
        stm: Spike time matrix. It creates and store a matrix containing columns with
        the cluster of good units and the rows are all the spike times of a session. Only use after clusterind data
        Input: It reads the output from phy: spike_times.py, spike_cluster.py and cluster_info
        to read the file use the following path C:\raw_data\Analysis\"mouse"\"session_intan"\Data\sorting
        Output: a matrix saved as Data frame. To read it, use pickle 
        the file is stored in C:\raw_data\Analysis\"mouse"\"session_inta"\Data
        To read and posterior work on the file, use the following
        To use it:
        >>> mystm = data.stm()
        It save the information inmediately
        >>> mystm = pd.read_pickle("STM")
        """
        # 1. Info for loading the file containing the infomration
        pathinfo_clust = self.path +'\\sorting\cluster_info.tsv' # file containing general info session
        pathspike_times = self.path +'\\sorting\spike_times.npy' # file containig the spike times
        pathspike_cluster = self.path +'\\sorting\spike_clusters.npy' # file containing the clusters 
    
        # 2. Importing the general information from "cluster_info.tsv" To select GOOD UNITS
        myclust = pd.read_csv(pathinfo_clust, sep = '\t')# red the summary information of the clusters
        mygood = myclust[myclust.group == 'good'] # select the information only from the good cluster
    
        # 3. Data containing the spike information: firSt the times, the the clusters (UNITS)
        spk_time = np.load(pathspike_times).flatten() # read the spike times files as numpy array
        spk_clust = np.load(pathspike_cluster) # read the spikes cluster as numpy array
    
        # 4. Selecting the id of the cluster per spikes of the good cluster
        id_good = mygood.cluster_id # Getting the indexes of the good clusters
        goodClust = dict()
        for cl in id_good:
            goodClust[cl] = np.where(spk_clust == cl)[0]
        
        # 5. It creates a dictionary with all the clusters containing the spike times
        gClust_times = dict()
        for key,value in goodClust.items():
            gClust_times[key] = spk_time[value]
    
        # 6. Create a data frame from a dictironary. Column are the cluster(units) and rows, spike times
        df_Clustimes = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in gClust_times.items()])) # its contains Nans
    
        # 7. save data
        mypathpkl_times = Path(self.path, "STM") # give the path to the file
        df_Clustimes.to_pickle(mypathpkl_times)
        
        return df_Clustimes
    
    
    
