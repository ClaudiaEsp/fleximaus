import pandas as pd;
import numpy as np
import matplotlib.pyplot as plt
import time
import os
import msvcrt
""""
This Script plot behavioral information from the csv file output from PyBpod for the flexibility project. 
To run the script set (e.g.):
- path = 'C:\\_work_cespinoza\\Analyses\\Behavior\\TestPyBpod\\training_simple\\'
- folder = '20210702-144506'
The output:
Correspond to four plots: right-side choices, maximum correct achieved, correct responses and
responded trials. By default it uses data from the last 10 trials. This can be modified in "n_trials"

Important: after using the script the path in the python kernel is changed. 
Restart python to run again this script
To finish running the script, press "Esc" in the console (or python kernel)
"""""

## 1. Importing information

plt.ion() # plt in interactive mode
cwd = os.getcwd()
#path = 'C:\\maxland\\maxland_TRAINING01\\experiments\\confidentiality_task\\setups\\confidentiality_task_training_simple\\sessions\\'
path = 'C:\\maxland\\experiments\\confidentiality_task\\setups\\habituation_complex\\sessions'
folder = '20210721-112902'
fname = folder + ".csv"
os.chdir(os.path.join(path,folder))

n_trials = 15 # number of trials to convolve the data
reward = 0.01 # time open the valve. It was calculated to get 1 ml in 100 correct trials.

### 2. Defining functions for organizing data ###
def dic_counter(msg):
    """
    It counts General info trials: n trials, n correct, n incorrect, n not responded, n wheel not stopping
    Input: msg = mydf['Msg']
    It retunr a dictionary with the message output of each trial
    """
    unique, counts = np.unique(mydf['Msg'], return_counts=True)
    DictCounter = dict(zip(unique, counts))
    return (DictCounter)


def gral_counter(msg,info):
    """
    It count the number of corrcet, incorrect, no responded trials and right choices
    Input: 'Msg' and 'Info' dataframe from the csv bypod output file. E.g. msg = mydf['Msg'], info = mydf['Info']
    Output a dictionary with the keys: corr,incorr,noresp and right
    """
    ## 1. Indexing correct trials (right and left choices) and counting them
    idx_correctright = [c for a,b,c in (zip(mydf['Msg'],mydf['Info'],mydf.index)) if a == 'reward_right' and pd.notnull(b)]
    idx_correctleft = [c for a,b,c in (zip(mydf['Msg'],mydf['Info'],mydf.index)) if a == 'reward_left' and pd.notnull(b)]
    n_corr = len(idx_correctright) + len(idx_correctleft)

    ## 2. Indexing incorrect trial (right and left choices) and counting them
    idx_incorrectright = [c for a,b,c in (zip(mydf['Msg'],mydf['Info'],mydf.index)) if a == 'no_reward_right' and pd.notnull(b)]
    idx_incorrectleft = [c for a,b,c in (zip(mydf['Msg'],mydf['Info'],mydf.index)) if a == 'no_reward_left' and pd.notnull(b)]
    n_incorr = len(idx_incorrectright) + len(idx_incorrectleft)

    ## 3. Indexing non responded trials
    idx_noresp = [c for a,b,c in (zip(mydf['Msg'],mydf['Info'],mydf.index)) if a == 'stop_open_loop_fail' and pd.notnull(b)]
    n_noresp = len(idx_noresp)
    
    ## 4. Right side choices
    n_right = len(idx_correctright) + len(idx_incorrectright)
    
    return(dict(zip(['corr','incorr','noresp','right'],[n_corr,n_incorr, n_noresp, n_right])))
    
    
def corr_organizer(msg,info):
    """
    Input: 'Msg' and 'Info' dataframe columns (pandas) obtained from the csv bypod output file.
    msg = mydf['Msg'], info = mydf['Info']
    Output np with convolved data for correct responded trials. 1 means correc, 0 is incorrec or non-responded
    """ 
    mycorr= list()
    for a,b in (zip(msg,info)):
        if a == 'stop_open_loop_fail' and pd.notnull(b):
            mycorr.append(0) # not responded trials
        elif a == 'reward_right' and pd.notnull(b) or a == 'reward_left' and pd.notnull(b):
            mycorr.append(1) # Correct trials
        elif a == 'no_reward_right' and pd.notnull(b) or a == 'no_reward_left' and pd.notnull(b):
            mycorr.append(0) # incorrect trials
            
    mycorr = np.array(mycorr)
    corr_trials = np.convolve(mycorr,np.ones(n_trials,dtype=int),'valid')
    return (corr_trials)


def resp_organizer(msg,info):
    """
    Input: 'Msg' and 'Info' dataframe columns (pandas) obtained from the csv bypod output file.
    msg = mydf['Msg'], info = mydf['Info']
    Output np with convolved data for responded trials. 1 means responded trials, 0 is no-responded trials
    """
    myresp= list()
    for a,b in (zip(msg,info)):
        if a == 'stop_open_loop_fail' and pd.notnull(b):
            myresp.append(0)
        elif a == 'stop_open_loop_reward_right' and pd.notnull(b) or a == 'stop_open_loop_reward_left' and pd.notnull(b):
            myresp.append(1)
    myresp = np.array(myresp)
    resp_trials = np.convolve(myresp,np.ones(n_trials,dtype=int),'valid')
    return (resp_trials)


def right_organizer(msg,info):
    """
    Input: 'Msg' and 'Info' dataframe columns (pandas) obtained from the csv bypod output file.
    msg = mydf['Msg'], info = mydf['Info']
    Output np with convolved data for Right choices. 1 means mouse choose right side, 0 means non-responded or left side
    """
    myright= list()
    for a,b in (zip(msg,info)):
        if a == 'stop_open_loop_fail' and pd.notnull(b):
            myright.append(0) # not responded trials
        elif a == 'reward_left' and pd.notnull(b) or a == 'no_reward_left' and pd.notnull(b):
            myright.append(0) # Correct trials    
        elif a == 'reward_right' and pd.notnull(b) or a == 'no_reward_right' and pd.notnull(b):
            myright.append(1) # Correct trials
    
    myright = np.array(myright)
    right_choice = np.convolve(myright,np.ones(n_trials,dtype=int),'valid')
    return (right_choice)


def maxcorr_organizer(corr_update):
    """
    Calculate the max corrected from covolved data
    input = corr_update. It is a numpy array
    """
    maxcorr_list = list()
    x = corr_update[0]
    for a,b in enumerate(corr_update): 
        if x > corr_update[a]:
            maxcorr_list.append(x)
        elif x <= corr_update[a]:
            x = corr_update[a]
            maxcorr_list.append(x)

    maxcorr_array = np.array(maxcorr_list)
    return(maxcorr_array)


def plotstyle(x):
    """
    Set the values of the axes of a plot object
    """
    ax[0,0].text(max(x)*0.45, 1.1, 'Response', color ="red", fontsize =14);
    ax[0,0].set_ylabel('Proportion', fontsize =14);
    ax[0,0].axhline(y=0.85, xmin=0, xmax=len(x), color ='r', ls = '-.', lw = 0.4);
    
    ax[0,1].text(max(x)*0.45, 1.1, 'Right side', color ="#e97854",fontsize =14);
    ax[0,1].plot(x, right_update/n_trials, color = "purple", alpha = 0.2);
    
    ax[1,0].set_ylabel('Proportion', fontsize =14);
    ax[1,0].axhline(y=0.85, xmin=0, xmax=len(x), color ='r', ls = '-.', lw = 0.4);
    ax[1,0].text(max(x)*0.45, 1.1, 'Correct', color ="blue", fontsize =14);  
    ax[1,0].set_xlabel('Trials', fontsize =14);
    
    ax[1,1].set_xlabel('Trials', fontsize =14);
    ax[1,1].text(max(x)*0.45, 1.1, 'Maximum Correct', color ="purple", fontsize =14);
    ax[1,1].axhline(y=0.85, xmin=0, xmax=len(x), color ='r', ls = '-.', lw = 0.4);
    
    for myax in ax.flatten():
        myax.set(ylim = (0,1.0))
        myax.set_yticks([0.00,0.25,0.50,0.75,1.00])        
       
    return(ax)
    
## 3. ploting fig ##
fig,ax = plt.subplots(2, 2, figsize = (9,4), sharey = True)
fig.set_tight_layout(False)
fig.subplots_adjust(hspace=0.6)

#mycolor = 0
while True:
    if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode(): # Esc key cancel the plot
        print('Plot cancelled!')
        os.chdir(cwd)
        break
    else:
        time.sleep(2)
        mydf = pd.read_csv(fname, sep = ';',skiprows = 21, usecols=[4,5], names=["Msg", "Info"])
        msg_update = mydf['Msg'].values
        info_update = mydf['Info'].values
        trial_counter = dic_counter(msg_update)
        itrials = trial_counter['New trial'] # it gives the n of initialized trials     
        
        if itrials > n_trials:
            corr_update = corr_organizer(msg = msg_update, info = info_update)
            resp_update = resp_organizer(msg = msg_update, info = info_update)
            right_update = right_organizer(msg = msg_update, info = info_update)
            maxcorr_update = maxcorr_organizer(corr_update = corr_update)
            new_trial_info = gral_counter(msg_update,info_update)
            
            x = range((n_trials-1),len(resp_update)+(n_trials-1)) # x axis trials, start cunting 10 (n trials)

            for myax in ax.flatten():
                myax.clear()
            
        #mycolor +=1      
            ax[1,0].fill_between(x, corr_update/n_trials, color = 'blue', alpha = 0.3); # plot correct response 'f'C{mycolor}'
            ax[0,0].fill_between(x, resp_update/n_trials, color = "red", alpha = 0.3); # plot responded trials 
            ax[0,1].fill_between(x, right_update/n_trials, color =  "#e97854", alpha = 0.3); # plot right choices (correct/incorrect)
            ax[1,1].fill_between(x, maxcorr_update/n_trials, color ="purple", alpha = 0.3);# plot maximum correct responses.   
            plotstyle(x = x);
        
            print('Number of trials:', (n_trials+len(x)), 'water consumption (ml):', new_trial_info["corr"]*reward) # forn trials also itrials
            print ('Total Correct trials:', new_trial_info["corr"], '\n')
            fig.canvas.draw()
            fig.canvas.flush_events()
            
        else:
            new_trial_info = gral_counter(msg_update,info_update)           
            print('not enought trials to plot,', 'trials:', (itrials), "<", "trials to convolve:", n_trials)
            print ('Correct trials:', new_trial_info["corr"])
            print ('Incorrect trials:', new_trial_info["incorr"])
            print ('No responded trials:', new_trial_info["noresp"])
            print ('Right choices:', new_trial_info["right"], '\n')
            fig.canvas.draw()
            fig.canvas.flush_events()