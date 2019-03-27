import requests
import json
import pandas as pd
import numpy as np
from pprint import pprint as pp
from config import config

# Request info
TOKEN = config["TOKEN"]
baseURL = "https://api.groupme.com/v3"
auth = "?token="+TOKEN
endPoint = "/groups/47836505/messages"


# Determine whether to hit API for new data
pullNewData = False
if pullNewData:
    allMessages = []
    messages = json.loads(requests.get(
        baseURL+endPoint+auth).text)["response"]["messages"]
    ID = messages[-1]["id"]

    # Deal with paging
    moreMessages = True
    while moreMessages:
        try:
            messages = json.loads(requests.get(
                baseURL+endPoint+auth+"&before_id="+ID).text)["response"]["messages"]
            allMessages += messages
            print(len(allMessages))
            ID = messages[-1]["id"]
        except:
            moreMessages = False

    # Save data
    messages = pd.DataFrame(allMessages)
    messages.to_csv("messages.csv")


def getLikes(messages):
    """Get a users likes from their messages

    Returns:
        int -- [number of likes]
    """
    s = 0
    for i in messages["favorited_by"]:
        s += len(set(i))
    return s


# Get
def createStats(messages):
    """
    Get stats from user groupby obj
    """
    numMessages = []
    numLikes = []
    messages = messages.groupby("name")
    for name, group in messages:
        numMessages.append((name, len(group)))
        numLikes.append((name, getLikes(group)))
    numMessages.sort(key=lambda x: x[1], reverse=True)
    numLikes.sort(key=lambda x: x[1], reverse=True)
    return numMessages, numLikes


# Read data from CSV
messages = pd.read_csv("messages.csv")
mesDic = messages.to_dict('records')
# Get Stats
numMessages, numLikes = createStats(messages)


mesDic.sort(key=lambda x: len(x["favorited_by"]), reverse=True)
print("MOST LIKED MESSAGES")
print("")
pp(mesDic[:5])
print("")

topLikes = numLikes[:10]
print("Top Users by Like Count")
pp(topLikes)
print("")

topMessages = numMessages[:10]
print("Top Users by Message #")
print("")
pp(topMessages)
