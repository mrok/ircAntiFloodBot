import os
import time
import json
from util import hook

def readConfig():
    ### Read config json and parse it

    confJson = None
    with open(os.getcwd() + '/antiFloodBotConfig.json', 'r') as confFile:
        confJson = confFile.read()

    return json.loads(confJson)

inputs =  {} #store time (unixtimestamp in sec) of every entry sent by user in map where key is user nickname
kicked = []  #store nicknames of kicked users
conf = readConfig()

timeIntervalScope = conf['timeIntervalScope'] # interval when entries are collected [sec]
entryThreshold = conf['entryThreshold'] #how many entries are allowed in timeIntervalScope
logFile = conf['logFile']

@hook.event('PRIVMSG')
def antiFlood(inp, nick=None, msg=None, conn=None, chan=None):

    if (nick not in inputs):
        inputs[nick] = []

    currentTime = time.time()
    timeThreshold = currentTime - timeIntervalScope
    inputs[nick].append(currentTime)

    inputs[nick] = filter(lambda x: x > timeThreshold, inputs[nick]) #filter out every entry older than 8 sec (threshold)

    if len(inputs[nick]) >= entryThreshold: #if user has good day, kick one
        explanationMessage = conf['kickMessage']
        file = open(logFile, 'a')
        file.write('Trying to kick %s on channel %s \n' % (nick, chan))
        if nick in kicked:
            explanationMessage =  conf['banMessage']
            out = "MODE %s +b %s" % (chan, nick)
            conn.send(out)
            file.write('%s is kicked with ban \n' % (nick))
        out = "KICK %s %s : %s" % (chan, nick, explanationMessage)

        conn.send(out)
        kicked.append(nick)
        file.close()


#todo
#if the same user joins again within 24 hour and keeps spamming temp ban in XX time.
#step 3) if the same user joins after the removal of the ban and spams, permanent ban.


@hook.event("NICK")
def onnick(param, conn=None, raw=None):
    file = open(logFile, 'a')
    file.write(json.dumps(param))
    file.close()


@hook.event("004")
def onConnect(param, conn=None, raw=None):
    conn.send("Antiflod bot is ready")