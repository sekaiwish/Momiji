import urllib
import requests
import os

def downloadTxt(location, channelName):
    file = open(location, "r")
    lines = file.readlines()
    strippedLines = []
    for line in lines:
        strippedLines.append(line.strip('\n'))
    i = 0
    for line in strippedLines:
        print(i)
        try:
            fileDir = os.path.dirname(os.path.realpath('__file__'))
            realPath = os.path.join(fileDir, channelName)
            if not os.path.exists(realPath):
                os.makedirs(realPath)
            stuff = line.split('/')
            realPath2 = os.path.join(realPath, str(stuff[-1]))
            with open(realPath2, 'wb') as handle:
                response = requests.get(line, stream=True)
                if not response.ok:
                    print
                    response
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
                i += 1
        except:
            i += 1
            print("error pass...")
            pass
    print("done")
