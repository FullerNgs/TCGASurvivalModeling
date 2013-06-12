${toc}


#Overview

The goal of the TCGA Pancancer Survival Prediction Challenge is to asses the predictive value of different molecular phenotypes and computational models in predicting overall survival in four cancers part of the The Cancer Genome Atlas (TCGA).  The TCGA has collected data on copy number variation, gene expression, micro RNA expression, protein expression, methylation and clinical covariates.  Even though this data is available for almost all 24 cancers being studied by the TCGA only four cancers - Glioblastoma (GBM), Ovarian serous cystadenocarcinoma (OV), Kidney renal clear cell carcinoma (KIRC) and Lung squamous cell carcinoma(LUSC) - have had enough follow-up time to make the survival data usefull for modeling.   This challenge will not only  leverage your machine learning and statistical skills but also your ability to transfer knowledge from other datasets (both within TCGA and outside).


#How to participate

Anyone is welcome and highly encouraged to submit models to be included in this project.  By submitting models using the formats described below they will be automatically added to the leaderboard.  A submission consists, predictions of relative survival times for 100 subsamples of the data but for maximum utility submitting the model, parameters used and selected features is preferable.  For convenience we have created a set of training testing datasets and some example code for submitting models.


##Data

All input data is available in the Input parameters directory (syn1714078) divided by cancer type.  For each cancertype there are:

* A training set, which is a tab delimited file with 100 columns each column containing different subsamplings of the patient id's to be used for training the model
* A testing set, built like the training set, with the 100 corresponding testing patient id's left-out of the training sets
* A core set of tab delimited files for each platform (CNV, RPPA, mRNA, methylation and miRNA) of measurements.
* A file with survival data including two columns with time and 1/0 for weather an event has occured.
* Clinical covariates

Specifically these data are stored in:
     
Data Type  | GBM        | KIRC       | LUSC       |  OV       
test       |syn1714083  | syn1714090 | syn1714096 | syn1714102 
train      |syn1714087 	| syn1714093 | syn1714099 | syn1714105 
CNV        |syn1710366 	| syn1710287 | syn1710378 | syn1710316 
RPPA       |            | syn1710306 | syn1710386 | syn1710314 
mRNA       |syn1710372 	| syn1710293 | syn1710382 | syn1710361 
methylation|syn1710374 	| syn1710289 |            | syn1710320
miRNA      |syn1710368 	| syn1710291 | syn1710380 | syn1710359
Survival   |syn1710370 	| syn1710303 | syn1710384 | syn1710363 
clinical   |syn1715822 	| syn1715824 | syn1715826 | syn1715828 

##Participation by example (using Python)
The following code is also available as a code object in Synapse (syn1876293)

####Setup environment, login, and some helper functions
```
import synapseclient
import os
syn = synapseclient.Synapse()
syn.login()

ACRONYM = 'GBM'
trainLabelsId = "syn1714087"   # Training bootstraps for GBM
testLabelsId = "syn1714083"    # Testing boostraps for GBM
dataId = "syn1710368"          # for miRNA GBM data
survivalDataId = 'syn1710370'


def readFile(entity, strip=None):
    with open(os.path.join(entity['cacheDir'], entity['files'][0])) as f:
        data = np.asarray([l.strip(strip).split('\t') for l in f])
    return data

def match(seq1, seq2):
    """Finds the index locations of seq1 in seq2"""
    return [ np.nonzero(seq2==x)[0][0] for x in seq1  if x in seq2 ]
```

####Downloand and extract the data from Synapse
```
#Download bootstrap labels
testLabels = readFile(syn.get(testLabelsId))
trainLabels = readFile(syn.get(trainLabelsId))

#Download specific data
data = readFile(syn.get(dataId))
features=data[0,1:]
samples=data[1:,0]
data=data[1:,1:].astype(np.float).T

#Download and extract the survival data
survival=readFile(syn.get(survivalDataId), '\n')
survTime = survival[1:,1].astype(np.int)
survStatus = survival[1:,2].astype(np.int)
```

####Train 100 models and predict survival time for each test sample (uses Rpy to run R random survival forest)
```
%load_ext rmagic
%R require(survival); require(randomSurvivalForest); require(survcomp)
predictions=[]
for bootstrapIdx in range(trainLabels.shape[1]):
    #Determine Extract the training and testing sets of one bootstrap
    trainIdx = match(trainLabels[:,bootstrapIdx], samples)
    testIdx = match(testLabels[:,bootstrapIdx], samples)

    #Verify that the labels are the same
    assert (np.all(trainLabels[:,bootstrapIdx]==samples[trainIdx]) and 
            np.all(testLabels[:,bootstrapIdx]==samples[testIdx]))

    #Exctract traing and testing set
    trainData = data[:, trainIdx].T
    trainSurvStatus = survStatus[trainIdx]
    trainSurvTime = survTime[trainIdx]
    testData = data[:, testIdx].T
    testSurvStatus = survStatus[testIdx]
    testSurvTime = survTime[testIdx]

    #Push to R, model and predict
    %Rpush trainData trainSurvStatus trainSurvTime testData testSurvStatus testSurvTime
    %R rsf.model.fit <- rsf(Surv(time,status) ~ ., data=data.frame(time=trainSurvTime,status=trainSurvStatus, trainData), ntree=1000, na.action="na.impute", splitrule="logrank", nsplit=1, importance="randomsplit", seed=-1)
    %R -o predictedResponse predictedResponse <- predict(rsf.model.fit, data.frame(testData), na.action="na.impute")$mortality
    #TODO replace this with creating the matrix of results
    %R -o concordance concordance <- concordance.index(predictedResponse, testSurvTime, testSurvStatus)$c.index
    print concordance
    predictions.append(predictedResponse)
```

####Save predictions to file and push results to Synapse

```
#Save predictions to file
predictions = np.asarray(predictions).T
np.savetxt('predictions.csv', predictions, fmt='%.4g', delimiter='\t')


#Save this code object into Synapse
codeEntity = synapseclient.File('Analyze.ipy', parentId='syn1720423')
codeEntity = syn.store(codeEntity)

#Set annotations and store predictions to Synapse
results = synapseclient.File('predictions.csv', name='Toy random forest model', parentId='syn1720419')
results.cancer = ACRONYM
results.dataType = 'miRNA'
results.method = 'Random Forest'
results.normalization = 'None'
results.featureSelection='None'
results.clinicalUsed = 'No'

results = syn.store(results,  used=[trainLabelsId, testLabelsId, dataId, survivalDataId], executed=[codeEntity])
```

#Submit the Results to Leaderboard
submission=syn.submit(1876290, results)
