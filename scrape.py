import requests
import argparse
import json
import pandas as pd
from pprint import pprint as pp
from config import config


def pullData():
    """
    Pull Data from GroupMe API
    """
    # Request info
    TOKEN = config["TOKEN"]
    GROUP_ID = config["GROUP_ID"]
    baseURL = "https://api.groupme.com/v3"
    auth = "?token="+TOKEN
    endPoint = "/groups/"+GROUP_ID+"/messages"
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
    """
    Get a users likes from their messages
    """
    s = 0
    for i in messages["favorited_by"]:
        s += len(set(i))
    return s


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


def processMessageDF(messages):
    """
    Process messages dataframe
    """

    mesDic = messages.to_dict('records')
    mesDic = [{"likes": int((len(x["favorited_by"]) / 12)), "text": x["text"],
               "attachments": x["attachments"], "name": x["name"]} for x in mesDic]
    mesDic.sort(key=lambda x: x["likes"], reverse=True)
    return mesDic


def displayStats(pullNewData=False):
    if pullNewData:
        pullData()

    # Read data from CSV
    messages = pd.read_csv("messages.csv")

    # Get Stats
    mesDic = processMessageDF(messages)
    numMessages, numLikes = createStats(messages)

    print("MOST LIKED MESSAGES")
    pp(mesDic[: 5])
    print("")

    topLikes = numLikes[: 10]
    print("Top Users by Like Count")
    pp(topLikes)
    print("")

    topMessages = numMessages[: 10]
    print("Top Users by Message #")
    pp(topMessages)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pullData')
    args = parser.parse_args()
    if args.pullData == "True":
        pullNewData = True
    else:
        pullNewData = False

    displayStats(pullNewData)
