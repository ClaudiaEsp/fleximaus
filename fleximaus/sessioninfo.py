import pandas as pd;
import numpy as np
from matplotlib import style
from scipy import stats
import os
import datetime
import json

## TOD
## MODIFYE CORREC_ORGANIZED WITHOUT CONVOLVED DATA. remove convtrials 

class Infos():
    '''
    It gets gral information of a single training sessions. 
    It reads the csv and the 
    '''
 
    cwd = os.getcwd()
    def __init__(self, path = 'C:\\raw_data\\Behavior\\habituation_complex\\sessions\\', folder = '20210624-162254', n_trials = 26):
        #setting the path and folder name
        self.path = path
        self.folder = folder
        self.n_trials = n_trials # trials to convolve
        os.chdir(os.path.join(self.path,self.folder))
        
        #read a csv file
        self.fname = self.folder + ".csv"
        self.gralinfo = pd.read_csv(self.fname, sep = ';',skiprows = 7, usecols=[4,5], nrows=14, names = ["Msg","Info"]) # Give general information session
        self.mydf = pd.read_csv(self.fname, sep = ';',skiprows = 21, names=["Type", "PC-time", "Bpod-init-time", "Bpod-end-time", "Msg", "Info"]) # give trials info
        # get the information
        self.ttype = self.mydf["Type"].values
        self.ttime = self.mydf['PC-time'].values
        self.msg = self.mydf['Msg'].values
        self.info = self.mydf['Info'].values
        self.idx = self.mydf.index  
        
        #read a json file
        self.jsonname = self.folder +'_settings_obj.json'
        self.fjson = open(self.jsonname,)
        self.datajson = json.load(self.fjson) # returns JSON object as a dictionary
        
        # in this way I discard the last ten trials
        self.idx2 = np.array([c for a,b,c in (zip(self.mydf['Msg'],self.mydf['Info'],self.mydf.index)) if a == 'open_loop' and pd.notnull(b)])
        self.end = self.idx2[-10]
 
 
    def print_gral(self):
        """
        It gives the general data of the subject and session
        the input is pandas data frame from a pybpod session 
        """
        # General session information
        print (self.gralinfo.iloc[4,0], "=", self.gralinfo.iloc[4,1])
        print (self.gralinfo.iloc[1,0], "=", self.gralinfo.iloc[1,1])
        print (self.gralinfo.iloc[6,0], "=", self.gralinfo.iloc[6,1])
        print (self.gralinfo.iloc[9,0], "=", self.gralinfo.iloc[9,1][2:6])
        print (self.gralinfo.iloc[12,0], "=", self.gralinfo.iloc[12,1])
        print ("USER-NAME =", self.gralinfo.iloc[2,1][2:9])
 
 
    def trial_counter(self, msg = None, info = None, idx = None):
        """
        It count the number of corrcet, incorrect, no responded trials and right choices
        Input: 'Msg' and 'Info' dataframe from the csv bypod output file. 
        E.g. msg = mydf['Msg'], info = mydf['Info']
        idx = mydf.index. Correspond to the indexes of a data frame
        Output a dictionary with the keys: corr,incorr,noresp and right
        """
        if msg is None:
            msg = self.msg
            
        if info is None:
            info = self.info
            
        if idx is None:
            idx = self.idx
            
        ## 1. Indexing correct trials (right and left choices) and counting them
        idx_correctright = [c for a,b,c in (zip(msg,info,idx)) if a == 'reward_right' and pd.notnull(b)]
        idx_correctleft = [c for a,b,c in (zip(msg,info,idx)) if a == 'reward_left' and pd.notnull(b)]
        n_corr = len(idx_correctright) + len(idx_correctleft)

        ## 2. Indexing incorrect trial (right and left choices) and counting them
        idx_incorrectright = [c for a,b,c in (zip(msg,info,idx)) if a == 'no_reward_right' and pd.notnull(b)]
        idx_incorrectleft = [c for a,b,c in (zip(msg,info,idx)) if a == 'no_reward_left' and pd.notnull(b)]
        n_incorr = len(idx_incorrectright) + len(idx_incorrectleft)

        ## 3. Indexing non responded trials
        idx_noresp = [c for a,b,c in (zip(msg,info,idx)) if a == 'stop_open_loop_fail' and pd.notnull(b)]
        n_noresp = len(idx_noresp)
    
        ## 4. Right side choices
        n_right = len(idx_correctright) + len(idx_incorrectright)
        return(dict(zip(['corr','incorr','noresp','right'],[n_corr,n_incorr, n_noresp, n_right])))
    
    
    def resp_time(self):
        """
        It calculates the reactions times from stimulus presentation to open  
        """
        # caclculate reaction times       
        i_time = [a for a,b,c in (zip(self.ttime,self.msg.astype(str),self.ttype)) 
                  if b == 'present_stim' and c == 'TRANSITION']
        
        e_time = [a for a,b,c in (zip(self.ttime,self.msg.astype(str),self.ttype)) 
                  if b[:15] == 'stop_open_loop_' and c == 'TRANSITION']
    
        #traform information in data time
        i_dt = np.array([datetime.datetime.strptime(i_time[i], '%Y-%m-%d %H:%M:%S.%f') for i in range(len(i_time))])
        e_dt = np.array([datetime.datetime.strptime(e_time[i], '%Y-%m-%d %H:%M:%S.%f') for i in range(len(e_time))])
    
        if len(i_dt) == len(e_dt):
            diff = e_dt-i_dt
        else:
            diff = e_dt[:]-i_dt[:-1]
    
        diff_sec = np.array([i.total_seconds() for i in diff])
        return(diff_sec)
    
    
    def right(self):
        """
        It gives the right-side choice as 1, and left-side choice as (do not include non-responded trials). 
        Input:'Msg','Info' dataframe from the csv pybpod output file. 
        E.g. msg = mydf['Msg'], info = mydf['Info']
        idx = mydf.index. Correspond to the indexes of a data frame
        Output a dictionary with the keys: corr,incorr,noresp and right (exclude non responded trials)
        """
        right_list = list()
        for a,b in (zip(self.msg,self.info)):
            if a == 'reward_right' and pd.notnull(b) or a == 'no_reward_right' and pd.notnull(b):
                right_list.append(1) # Correct trials
            elif a == 'reward_left' and pd.notnull(b) or a == 'no_reward_left' and pd.notnull(b):
                right_list.append(0) # incorrect trials
        right_array = np.array(right_list , dtype = np.int64 )
        return right_array  
    
    
    def right_organizer(self):
        """
        It include non-responded trials as 0 and also the left desicion.
        It is recommended to mask this values by using the indexes for 0 value from the resp_roganizer()
        Input: 'Msg' and 'Info' dataframe columns (pandas) obtained from the csv bypod output file.
        msg = mydf['Msg'], info = mydf['Info']
        Output: 1 means mouse choose right side, 0 means non-responded or left side. 
        """
        myright= list()
        for a,b in (zip(self.msg,self.info)):
            if a == 'stop_open_loop_fail' and pd.notnull(b):
                myright.append(0) # not responded trials
            elif a == 'reward_left' and pd.notnull(b) or a == 'no_reward_left' and pd.notnull(b):
                myright.append(0) # Correct trials    
            elif a == 'reward_right' and pd.notnull(b) or a == 'no_reward_right' and pd.notnull(b):
                myright.append(1) # Correct trials
    
        myright = np.array(myright,  dtype = np.int64)
        return myright   
    
        
    def corr_organizer(self):
        """
        Input: 'Msg' and 'Info' dataframe columns (pandas) obtained from the csv bypod output file.
        msg = mydf['Msg'], info = mydf['Info']
        ntrials= the number of trial to convolve
        Output responded and non responded: 1 means correc, 0 is incorrec or non-responded
        """ 
        mycorr= list()
        for a,b in (zip(self.msg,self.info)):
            if a == 'stop_open_loop_fail' and pd.notnull(b):
                mycorr.append(0) # not responded trials
            elif a == 'reward_right' and pd.notnull(b) or a == 'reward_left' and pd.notnull(b):
                mycorr.append(1) # Correct trials
            elif a == 'no_reward_right' and pd.notnull(b) or a == 'no_reward_left' and pd.notnull(b):
                mycorr.append(0) # incorrect trials
            
        mycorr = np.array(mycorr)
        #corr_trials = np.convolve(mycorr,np.ones(convtrials,dtype=int),'valid')
        return mycorr
    
    def resp_organizer(self):
        """
        Input: 'Msg' and 'Info' dataframe columns (pandas) obtained from the csv bypod output file.
        msg = mydf['Msg'], info = mydf['Info']
        Output np responded and non-responded trials. 1 means responded trials, 0 is no-responded trials
        """
        myresp= list()
        for a,b in (zip(self.msg,self.info)):
            if a == 'stop_open_loop_fail' and pd.notnull(b):
                myresp.append(0)
            elif a == 'stop_open_loop_reward_right' and pd.notnull(b) or a == 'stop_open_loop_reward_left' and pd.notnull(b):
                myresp.append(1)
        myresp = np.array(myresp)
        return myresp
    
        
    def corr_resp(self):
        """
        It calculate correct and incorrect trials of the only responded trials
        Input: 'Msg' and 'Info' dataframe columns (pandas) obtained from the csv bypod output file.
        msg = mydf['Msg'], info = mydf['Info']
        Output np with 1 means correc, 0 incorrec.
        """ 
        mycorr= list()
        for a,b in (zip(self.msg,self.info)):
            #if a == 'stop_open_loop_fail' and pd.notnull(b):
            #    mycorr.append(0) # not responded trials
            if a == 'reward_right' and pd.notnull(b) or a == 'reward_left' and pd.notnull(b):
                mycorr.append(1) # Correct trials
            elif a == 'no_reward_right' and pd.notnull(b) or a == 'no_reward_left' and pd.notnull(b):
                mycorr.append(0) # incorrect trials
            
        mycorr = np.array(mycorr, dtype = np.int64 )
        return mycorr
   
   
    def right_left(self,data):
        """
        Calculate the ratio left and right
        We use: r-l/r+l
        1 means right bias, -1 means left bias. 0 is not bias.
        Input data is a trial.counter() object
        """
        l = (data['corr'] + data['incorr']) - data['right']
        r = data['right']
        rl_ratio = (r-l)/(r+l)
        return(rl_ratio)      
    
    
    def dic_info(self):
        """
        It retunrs important information from single ssion such as:
        'IDsession': e.g '20210727-145122', string indicates the date and the time of the session
        'ntrial': e.g 139, integer indicating total trial number
        '%resp': e.g 63.5, float number for teh percentage of responded trials. 
        It does not tajke tha last 10 trials in the calculus 
        'sideratio': e.g 0.617, 0 means not bias, 1 rightside bias and -1 left side bias. 
        It stimate the side bias during the task
        'maxcorr': e.g 19, integer for max correct trials in colvoled data using 26 trials
        'meancorr': e.g. 11.23, mean max correc in one session
        'stdcorr': e.g. 3.841, stadart deviation max corre in one session
        'meanrt': e.g. 5.0386, mean response time in asession, 
        from were the stimulus is presented to the reward delivery of extra time out.
        'stdrt': e.g .2.034, standar deviation of response time
        """
        # Get total number of correct responses
        count = self.trial_counter()
        tot_trials = count['corr'] + count['incorr'] + count['noresp']
        
        # Get the counter or the infomration without considering the last n files (end)
        mymsg = self.msg[:self.end] 
        myinfo = self.info[:self.end] 
        myidex = self.idx[:self.end]       
        count2 = self.trial_counter(msg = mymsg, info = myinfo, idx = myidex)    
        # percentage of responded trials (do not consider last 10 trials)
        perc_resp = (count2['corr']+count2['incorr'])*100/(count2['corr']+count2['incorr']+ count2['noresp']) 
        
        # Side ratio
        side_ratio = self.right_left(data = count) 
        
        # give the colvolved correct
        corr = self.corr_organizer() 
        corr_convolved = np.convolve(corr,np.ones(self.n_trials,dtype=int),'valid')
        
        # max correct, or max performance
        max_corrp = (corr_convolved.max())*(100/ self.n_trials)
        mean_corrp = (np.mean(corr_convolved))* (100/self.n_trials)
        ste_corrp = (np.std(corr_convolved)/np.sqrt(np.array(tot_trials)-self.n_trials))* (100/ self.n_trials)
        
        # reaction times
        rtimes = self.resp_time() # reaccion time
        meantime = np.mean(rtimes) # mean reaction time
        stetime = np.std(rtimes)/np.sqrt(np.array(tot_trials)-self.n_trials) # standar deviation time
        
        # create a dictionary with all the data
        session_info = dict(zip(['subject','IDsession','ntrial','%resp','sideratio',
                                 'maxcorr%','meancorr%', 'stecorr%','meanrt', 'stert'],
                        [self.gralinfo.iloc[9,1][2:6],self.folder,tot_trials,perc_resp,
                         side_ratio,max_corrp, mean_corrp,ste_corrp,meantime, stetime]))
        return(session_info)
    
    
    def corr_display(self):
        """
        It reads the information data from json file
        Shows where correct object displayed. 
        1: Object was displayed right, 0: object was diplayed left
        Input: json file output from Pybpod
        """
        right = list()
        for i in range(len(self.datajson['sides_li'])):
            val = int(self.datajson['sides_li'][i]['right'] == True)
            right.append(val)
        
        myright_disp = np.array(right)
        return myright_disp
    
    
    def insist(self):
        """
        It check where the inistive mode is active.
        input json file
        Output with 1 indicating where the instive mode was on and 0 when it was off
        """
        # get only the firts value
        ins = [self.datajson['insist_mode_li'][x][0] for x in range(len(self.datajson['insist_mode_li']))] 
        ins = np.array(ins, dtype = int)
        return ins