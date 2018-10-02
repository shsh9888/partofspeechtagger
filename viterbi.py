import random, math
import numpy as np
from  collections import Counter
sentences =[]
sentencewisetags=[]
train_sentences =[]
train_sentencewisetags =[]
test_sentences = []
test_sentencewisetags =[]

## Following are use
uniqueTagList = []
tagCount = {}
tagVsTagCount={} #count of tag coming after another tag

wordVsTagCount ={}
uniqueWordList=[]

wordCount ={}

def updateWordCount(word):
    if word in wordCount:
        wordCount[word] += 1
    else:
        wordCount[word] = 1

def updateWordList(word):
    if word not in uniqueWordList:
        uniqueWordList.append(word)

def updateTagList(tag):
    if tag not in uniqueTagList:
        uniqueTagList.append(tag)


def incrementTagCount(tag):
    if tag in tagCount:
        tagCount[tag] += 1
    else:
        tagCount[tag] = 1


def getMostCommonTag(word):
    if word in wordVsTagCount:
        tagDict = wordVsTagCount[word]
        finalTag = ""
        maxVal =0
        for key, value in tagDict.items():
            if value > maxVal:
                finalTag =key
                maxVal =value
        return finalTag
    else:
        return "na"

def populateTagVsTagCount(previousTag,givenTag):
    key = previousTag + "|" + givenTag
    if key in tagVsTagCount:
        tagVsTagCount[key] += 1
    else:
        tagVsTagCount[key] =1


def getTagVsTagCount(previousTag, givenTag):
    key = previousTag + "|" + givenTag
    if key in tagVsTagCount:
        return tagVsTagCount[key]
    else:
       # print(givenTag ," and given previous ", previousTag, " not found")
        return 0

def populateWordVsTagCount(word,tag):
    if word in wordVsTagCount:
        if tag in wordVsTagCount[word]:
            wordVsTagCount[word][tag] += 1
        else:
            wordVsTagCount[word][tag] = 1
    else:
        wordVsTagCount[word] = {tag :1}


def getWordVsTagCount(word,tag):
    if word in wordVsTagCount:
        if tag in wordVsTagCount[word]:
            return wordVsTagCount[word][tag]
    return 0


with open("berp-POS-training.txt", "r+") as f:
    lines = f.readlines()
    tempWordList, tempTagList = [], []
    for line in lines:
        if line.strip() == "":
            sentences.append(tempWordList)
            sentencewisetags.append(tempTagList)
            tempWordList, tempTagList = [],[]
        else:
            props =line.split('\t')
            word,tag =props[1].strip(),props[2].strip()
            tempTagList.append(tag)
            tempWordList.append(word)

##adding the last one
sentences.append(tempWordList)
sentencewisetags.append(tempTagList)
print(len(sentences))

sentenceLen = len(sentences)
train_sentences = sentences[:]
train_sentencewisetags = sentencewisetags[:]
test_sentences =[]
test_sentencewisetags = []

with open("assgn2-test-set.txt", "r+") as f:
    lines = f.readlines()
    tempTestWordList= []
    for line in lines:
        if line.strip() == "":
            test_sentences.append(tempTestWordList)
            tempTestWordList = []
        else:
            props =line.split('\t')
            word=props[1].strip()
            tempTestWordList.append(word)
#adding the last one
test_sentences.append(tempTestWordList)
"""
#Training with splitting 80/20
sentenceLen = len(sentences)
train_index = math.ceil(0.80  * sentenceLen)
train_sentences = sentences[:train_index]
train_sentencewisetags = sentencewisetags[:train_index]
test_sentences =sentences[train_index:]
test_sentencewisetags = sentencewisetags[train_index:]
"""


"""
#Training with splitting 80/20 randomnly
train_sentences =[]
train_sentencewisetags = []
test_sentences =[]
test_sentencewisetags = []
## formulating the trainset and test now | random 80/20
##train set
randomIndices =  random.sample(range(sentenceLen),math.ceil(0.80  * sentenceLen))
for index in randomIndices:
    train_sentences.append(sentences[index])
    train_sentencewisetags.append(sentencewisetags[index])

#test set
for index in range(sentenceLen):
    if index in randomIndices: continue
    test_sentences.append(sentences[index])
    test_sentencewisetags.append(sentencewisetags[index])
"""

for index in range(len(train_sentences)):
    for word in train_sentences[index]:
        updateWordCount(word)

unkList = []
for key, value in wordCount.items():
    if value <= 10:
        unkList.append(key)

## Creating the coutns for the train set
for index in range(len(train_sentences)):
    previousTag = "<s>"
    incrementTagCount(previousTag)
    updateTagList(previousTag)
    for word, tag in zip(train_sentences[index], train_sentencewisetags[index]):
        populateTagVsTagCount(previousTag,tag)
        incrementTagCount(tag)
        updateTagList(tag)
        previousTag =tag
        if word in unkList:
            populateWordVsTagCount("<unk>",tag)
            updateWordList("<unk>")
        else:
            populateWordVsTagCount(word,tag)
            updateWordList(word)



"""
#BASELINE IMPLEMENTATION
totalCount =0
rightAnswer = 0
for index in range(len(test_sentences)):
    for word,tag in zip(test_sentences[index], test_sentencewisetags[index]):
        totalCount += 1
        predictedTag = getMostCommonTag(word)
        if predictedTag == tag:
            rightAnswer += 1

print("Base Line Accuracy:", rightAnswer/totalCount)
"""
## For the tag vs tag matrix
tagVsTagRowList = uniqueTagList
tagVsTagColumnList = uniqueTagList[1:]
tagVsTagRows = len(tagVsTagRowList)
tagVsTagColumns = len(tagVsTagColumnList)


##For the wordvstag matrix
tagVsWordRowList = uniqueTagList[1:]
tagVsWordColumnList = uniqueWordList
tagVsWordRows = len(tagVsWordRowList)
tagVsWordColumns = len(tagVsWordColumnList)



#print("total tags :", tagVsTagRowList)

tagVsTagMatrix = np.zeros(shape=(tagVsTagRows,tagVsTagColumns))
tagVsWordMatrix = np.zeros(shape=(tagVsWordRows, tagVsWordColumns))
#print("unique words", len(uniqueWordList))

def computeTagVsTagMatrixProbability(previousTag, currentTag, totalTags,smoothingFactr):
    return ((getTagVsTagCount(previousTag,currentTag)+smoothingFactr)/(tagCount[previousTag] + totalTags))

def computeTagVsWordMatrixProbability(tag, word, totalTags,smoothingFactr):
    return ((getWordVsTagCount(word,tag)+smoothingFactr)/(tagCount[tag] + totalTags))

## calculating the probablity for tag vs tag matrix
for (i,j), x in np.ndenumerate(tagVsTagMatrix):
    tagVsTagMatrix[i,j] = computeTagVsTagMatrixProbability(tagVsTagRowList[i],tagVsTagColumnList[j], len(tagVsTagColumnList), 1)

## calculating the probablity for word vs
for (i,j), x in np.ndenumerate(tagVsWordMatrix):
    tagVsWordMatrix[i,j] = computeTagVsWordMatrixProbability(tagVsWordRowList[i],tagVsWordColumnList[j], len(uniqueWordList), 1)



def Viterbi(numberOfViterbiRows, numberOfViterbiColumns, viterbiMatrix, backTrackMatrix,wordList):
    ##Filling the first column
    for row in range(numberOfViterbiRows):
        viterbiMatrix[row,0] = tagVsTagMatrix[0,row] * tagVsWordMatrix[row,uniqueWordList.index(wordList[0])]
        backTrackMatrix[row,0]=0

    ##Fill all the rows and columns of the viterbi matrix
    for column in range(1,numberOfViterbiColumns):
        for row in range(numberOfViterbiRows):
            maxProb =0
            fromWhere =-1
            for prevRow in range(numberOfViterbiRows):
                current =(viterbiMatrix[prevRow,column-1] * tagVsTagMatrix[prevRow+1,row] * tagVsWordMatrix[row, uniqueWordList.index(wordList[column])])
                if current > maxProb:
                    maxProb = current
                    fromWhere = prevRow
            viterbiMatrix[row,column] = maxProb
            backTrackMatrix[row,column] = int(fromWhere)

    ## Find out the max probability in the final column
    finalrow = 0
    finalColumn = numberOfViterbiColumns-1
    maxProb =0
    for row in range(numberOfViterbiRows):
        if viterbiMatrix[row,finalColumn] > maxProb:
            maxProb = viterbiMatrix[row,finalColumn]
            finalrow = row
    # Max prob is at finalrow and finalcolumn, backtrack using these indices, use backtrack matrix
    tagIndex = []
    while finalColumn >=0:
        tagIndex.append(finalrow)
        finalrow = backTrackMatrix[finalrow,finalColumn]
        finalColumn =  finalColumn -1
    tagIndex.reverse()
    return tagIndex


###Implementing Viterbi
viterbiRowList = uniqueTagList[1:]
numberOfViterbiRows = len(viterbiRowList)
numberOfViterbiColumns =0

"""
## test with baseline counting
totalCount =0
rightAnswer = 0
inlist =0
outlist =0
for index,sentence in enumerate(test_sentences):
    true_tags = test_sentencewisetags[index]
    viterbiColumnList=sentence[:]
    inlist +=1
    print(inlist)
    for i,word in enumerate(sentence):
        if word not in uniqueWordList:
            viterbiColumnList[i] = "<unk>"

    numberOfViterbiColumns =len(viterbiColumnList)
    #matices
    viterbiMatrix = np.zeros(shape=(numberOfViterbiRows,numberOfViterbiColumns))
    backTrackMatrix = np.zeros(shape=(numberOfViterbiRows,numberOfViterbiColumns), dtype=int)

    tagIndices =Viterbi(numberOfViterbiRows,numberOfViterbiColumns,viterbiMatrix,backTrackMatrix, viterbiColumnList)
    # print("right :", true_tags)
    # print("predicted :", viterbiRowList[tagInd.] )
    for i,tag in enumerate(tagIndices):
        totalCount += 1
        if viterbiRowList[tag] == true_tags[i]:
            rightAnswer += 1


print("Accuracy:",rightAnswer/totalCount)
"""
inlist =0
final_output_tagList = []
print(len(test_sentences))
for index,sentence in enumerate(test_sentences):
    viterbiColumnList=sentence[:]
    inlist +=1
    print(inlist)
    for i,word in enumerate(sentence):
        if word not in uniqueWordList:
            viterbiColumnList[i] = "<unk>"

    numberOfViterbiColumns =len(viterbiColumnList)
    #matices
    viterbiMatrix = np.zeros(shape=(numberOfViterbiRows,numberOfViterbiColumns))
    backTrackMatrix = np.zeros(shape=(numberOfViterbiRows,numberOfViterbiColumns), dtype=int)

    tagIndices =Viterbi(numberOfViterbiRows,numberOfViterbiColumns,viterbiMatrix,backTrackMatrix, viterbiColumnList)
    # print("right :", true_tags)
    # print("predicted :", viterbiRowList[tagInd.] )
    for tag in tagIndices:
        final_output_tagList.append(viterbiRowList[tag])


##Writing into the file
tagIndex =0
with open("shetty-shravan-assgn2-test-output.txt", "w+") as f:
    for sentence in test_sentences:
        i = 1
        for word in sentence:
            f.write(str(i) + "\t" + word + "\t" + final_output_tagList[tagIndex] + "\n")
            i =i+1
            tagIndex = tagIndex +1
        f.write("\n")
    f.close()

print("Done, Please check the output here : shetty-shravan-assgn2-test-output.txt")