#!/usr/bin/env python
# coding: utf-8

# # This should become model.py and be imported
# It will contain all the function necessary for the server to function

# ## Init
# This code will run will the module is imported. It will train the model. Since the code is imported by the server, this code will run on server init. This means it will always run when the server restarts, and the model will be perpetually retrained.

# In[1]:


import parselmouth
import os
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, brier_score_loss


# ### Helper function(s)

# In[2]:


def makeCSV(keyfile, outputLocation):
    os.makedirs(outputLocation, exist_ok=True);
    
    snd = parselmouth.Sound(keyfile)

    intensity = snd.to_intensity()
    pitch = snd.to_pitch()

    intensityxs = intensity.xs()
    pitchxs = pitch.xs()

    intensityindex = 0;
    pitchindex = 0;

    pitch_values = pitch.selected_array['frequency'];
    intensity_values = intensity.values[0]

    result = "";

    while (pitchindex < len(pitchxs) and intensityindex < len(intensityxs)):
        if(intensityindex >= len(intensityxs) or pitchxs[pitchindex] < intensityxs[intensityindex]):
            result += str(pitchxs[pitchindex]) + ", " +str(pitch_values[pitchindex])+', '+str(intensity_values[intensityindex])+'\n';
            pitchindex += 1;
        elif(pitchindex >= len(pitchxs) or pitchxs[pitchindex] > intensityxs[intensityindex]):
            result += str(intensityxs[intensityindex]) + ", " +str(pitch_values[pitchindex])+', '+str(intensity_values[intensityindex])+'\n';
            intensityindex += 1;
        elif(pitchxs[pitchindex] == intensityxs[intensityindex]):
            result += str(intensityxs[intensityindex]) + ", " +str(pitch_values[pitchindex])+', '+str(intensity_values[intensityindex])+'\n';
            intensityindex += 1;
            pitchindex += 1;
    
    #Create output of basic evaluation
    filename = outputLocation+'/'+os.path.basename(keyfile) + ".csv";
    file = open(filename, 'w');
    file.write(result);
    file.close();
    
    return filename;


# In[3]:


def data_process(csvfile, num=10):
    
    pitch=[]
    volume=[]    
    plot=open(csvfile)
    for row in plot:
        arr=row.split(',')
        if float(arr[1])!=0:
            pitch.append( float(arr[1]) ) 
            volume.append( float(arr[2][0:17]) )
        
    num_lines_v=len(volume)  
    size_v=int(num_lines_v/num)
    num_lines_p=len(pitch) 
    size_p=int(num_lines_p/num)

    sum2=0
    pitch1=[]
    volume1=[]
    a=0
    b=size_v
    
    for j in range(num-1):
        for i in range(a,b): 
           sum2+= volume[i]
        data2=sum2/size_v
        volume1.append(data2)
        a=b
        b=b+size_v
        sum2=0

    for i in range(a,len(volume)):
        sum2+= volume[i]
    s=len(volume)-a
    data2=sum2/s
    volume1.append(data2)
    
    sum1=0
    a=0
    b=size_p
    for j in range(num-1):
        for i in range(a,b): 
           sum1+= pitch[i]
        data1=sum1/size_p
        pitch1.append(data1)
        a=b
        b=b+size_p
        sum1=0
    
    for i in range(a,len(pitch)):
        sum1+=float(pitch[i])
    s=len(pitch)-a
    data1=sum1/s
    pitch1.append(data1)
    
    return (volume1,pitch1);


# In[4]:


def calculateBaselineValues(baselineFile):
    snd = parselmouth.Sound(baselineFile);
    pitch_values = list(filter(lambda a: a != 0, snd.to_pitch().selected_array['frequency']))
    baselineValues = (snd.get_intensity(),sum(pitch_values)/len(pitch_values));
    return baselineValues;


# In[5]:


def calculateFeatureVector(file,baseline):
    intensity,pitch = data_process(file,25)
    intensity = list(map(lambda x: x-baseline[0], intensity))
    pitch = list(map(lambda x: x-baseline[1], pitch))
    return intensity+pitch+[1]


# In[6]:


def calculateFeatureVectorCmp1(file,baseline):
    snd = parselmouth.Sound(file);
            
    pitch_values = list(filter(lambda a: a != 0, snd.to_pitch().selected_array['frequency']))
    minpitch = min(pitch_values);
    minpitch -= baseline[1];
    
    maxintensity = max(snd.to_intensity().values[0])
    maxintensity -= baseline[0]
    
    intensity,pitch = data_process(file+'.csv',24)
    intensity = list(map(lambda x: x-baseline[0], intensity))
    pitch = list(map(lambda x: x-baseline[1], pitch))
    
    #print(intensity,maxintensity,pitch,minpitch,[1])
    
    return intensity+[maxintensity]+pitch+[minpitch]+[1]


# In[7]:


def calculateVariety(wavefilename):
    snd = parselmouth.Sound(wavefilename)
    total_change = 0;
    speaking_duration = snd.duration;
    
    pitch = snd.to_pitch()    
    pitch_values = pitch.selected_array['frequency'];
    pitchxs = pitch.xs()

    for i in range(len(pitch_values)-1):
        if(pitch_values[i] == 0):
            total_change += abs(pitch_values[i+1] - pitch_values[i]);
        else:
            speaking_duration -= snd.time_step;
    pitchChange = total_change/speaking_duration
    
    total_change = 0;
    
    intensity = snd.to_intensity()
    intensity_values = intensity.values[0]
    intensityxs = intensity.xs()
    
    for i in range(len(intensity_values)-1):
        total_change += abs(intensity_values[i+1] - intensity_values[i]);
    intensityChange = total_change/speaking_duration
    
    return (intensityChange, pitchChange)


# In[8]:


# calculateVariety('Record_0002.wav')


# ### Actual code

# #### This section preprocesses
# It determines all the baseline values and creates the csv files.

# In[9]:


trainingFilePath = '/home/ubuntu/flaskapp/view/trainningAudio/'
baselineDictionary = {}

with os.scandir(trainingFilePath) as basedirectory:
    for subdirectory in basedirectory:
        if subdirectory.is_dir():
########### At this point, we're looking at all of the folders of training data
            print(subdirectory.name)
            with os.scandir(trainingFilePath+subdirectory.name) as it2:
                baselineValues = (0,0) #intensity,pitch
                for wavfile in it2:
################### At this point, we're looking at every file in the current training data folder
                    if wavfile.is_file() and wavfile.name.endswith('.wav') and not 'polite' in wavfile.name:
####################### This is the baseline file, in most (hopefully all) cases
                        if(not (baselineValues == (0,0))):
                            print("Welp, somehow we found two baseline files; please check this directory",subdirectory.name);
                        else:
                            baselineValues = calculateBaselineValues(trainingFilePath+subdirectory.name+'/'+wavfile.name)
                            baselineDictionary[subdirectory.name] = baselineValues;
                            print (baselineValues)
                    elif wavfile.is_file() and wavfile.name.endswith('.wav'):
                        makeCSV(trainingFilePath+subdirectory.name+'/'+wavfile.name,trainingFilePath+subdirectory.name)
                if(baselineValues == (0,0)):
                    print("Welp, somehow we didn't find a baseline file; please check this directory",subdirectory.name);


# #### This section trains the model
# We start by getting the features from the dataset and putting them into our arrays

# In[10]:


X = [];
y = [];

with os.scandir(trainingFilePath) as basedirectory:
    for subdirectory in basedirectory:
        if subdirectory.is_dir():
########### At this point, we're looking at all of the folders of training data
            print(subdirectory.name)
            with os.scandir(trainingFilePath+subdirectory.name) as it2:
                impoliteFileCount = 0; politeFileCount = 0;
                for file in it2:
################### At this point, we're looking at every file in the current training data folder
                    if file.is_file() and file.name.endswith('.wav') and 'polite' in file.name:
                        #print("\t- "+file.name)
                        try:
                            #X.append(calculateFeatureVector(trainingFilePath+subdirectory.name+'/'+file.name, baselineDictionary[subdirectory.name]))
                            X.append(calculateFeatureVectorCmp1(trainingFilePath+subdirectory.name+'/'+file.name, baselineDictionary[subdirectory.name]))
                            if 'impolite' in file.name:
                                y.append(0)
                                impoliteFileCount += 1;
                            else:
                                y.append(1)
                                politeFileCount += 1;
                        except ZeroDivisionError:
                            print("Welp, we got a division by zero error", file.name)
                if(impoliteFileCount != 8 or politeFileCount != 8) :
                    print("Welp, there doesn't seem to be the right number of files here (or they're misnamed or something)",subdirectory.name)
                    
print(len(X[1]))


# Next we actually set up the model and run the training functions.
# 
# Based primarily on: https://towardsdatascience.com/building-a-logistic-regression-in-python-301d27367c24
# 
# **X and y were defined above to hold the features and the expected results, respectively.**
# Note that the model requires a 2D array as input, where each row corresponds to a single object, and in that row is the list of features. The model outputs a list of values and each one corresponds to a row of the input. This is the same format the expected output should be in for training the model.

# In[11]:


#model = LogisticRegression(solver='lbfgs',max_iter=10000)
model = LogisticRegression(solver='liblinear',max_iter=100)
model.fit(X, y)


# The following section is just for evaluationg the model; it doesn't need to be run on import, but it's nice for me to have here to test the accuracy.

# In[12]:


# if __name__ == "__main__":
#     predicted_classes = model.predict(X)
#     accuracy = accuracy_score(y,predicted_classes)
#     print("Accuracy:\t",accuracy)
    
#     predicted_classes = model.predict_proba(X)[:,1]
#     loss = log_loss(y, predicted_classes)
#     print("Log loss:\t",loss)
    
#     loss = brier_score_loss(y, predicted_classes)
#     print("Brier loss:\t",loss)

#parameters = model.coef_


# ## Function to call by server
# This is the function for the server to call. It takes two file paths and returns a tuple containing the location of a csv and the politeness score.

# In[13]:


def evaluate(basefile, keyfile):
    csv = makeCSV(keyfile,'/home/ubuntu/flaskapp/static/RealResult')
    
    #calculateFeatureVector(csv,calculateBaselineValues(basefile))
    #print(calculateBaselineValues(basefile))
    score = model.predict_proba([calculateFeatureVector(csv,calculateBaselineValues(basefile))])
    
    mono, tony = calculateVariety(keyfile);
    
    return (csv, min(score[0][1]+.25,.95), mono,tony);



