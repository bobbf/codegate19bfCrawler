import sys
import json
import urllib.request
from datetime import datetime
import datetime as DT
import socket
import wave
import pyaudio
import key

def play_error_voice():
    chunk = 1024
    #음성파일 변경
    error_voice = wave.open("error_voice.wav","rb")
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(error_voice.getsampwidth()),
            channels = error_voice.getnchannels(),
            rate = error_voice.getframerate(),
            output = True)
    data = error_voice.readframes(chunk)

    while data:
        stream.write(data)
        data = error_voice.readframes(chunk)

    stream.stop_stream()
    stream.close()
    p.terminate()


def getJsonFromUrl(urlString):
    #print(urlString)

    start_time = datetime.now(DT.timezone.utc)
    response = urllib.request.urlopen(urlString).read().decode('utf-8')
    responseJson = json.loads(response)
    while True:
        end_time = datetime.now(DT.timezone.utc)
        if( end_time-start_time > DT.timedelta(seconds=1)):
            break
    return responseJson
'''test
url = "https://graph.facebook.com/v3.2/me?fields=posts&"+tokenParam
url = "https://graph.facebook.com/v3.2/me?"+tokenParam
testJson = getJsonFromUrl(url)
print(testJson)
'''
try:
    access_token= key.token
    client_id= 345750606037202
    client_secret = key.client_secret
    shortLiveToken = access_token
    getLongLiveTokenUrl = "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id="+str(client_id)+"&client_secret="+client_secret+"&fb_exchange_token="+access_token
    #print(getLongLiveTokenUrl)
    longLiveToken = getJsonFromUrl(getLongLiveTokenUrl)["access_token"]
    #print(longLiveToken)
    access_token = longLiveToken
    tokenParam = "access_token="+access_token
except:
    print("**********\nwrong usage : python3 crawl.py"); 
    sys.exit()

def get_posts():
    url = "https://graph.facebook.com/v3.2/me?fields=posts&"+tokenParam
    postsJson = getJsonFromUrl(url)
    for post in postsJson["posts"]["data"]:
        print("---------------------------post")
        print("id :" + post["id"])
        if "message" in post:
            print("message : " + post["message"])
        print("---------------------------")

def get_like_count(e):
    return e["like_count"]

def get_comments(post_id):

    url = "https://graph.facebook.com/v3.2/"+post_id+"/comments?limit=10000000&"+tokenParam
    commentJson = getJsonFromUrl(url)
    result = []
    for comment in commentJson["data"]:
        #print(comment)
        #print("--------------------------comment")
        #print("created_time: "+comment["created_time"])
        #print("message: " +comment["message"])
        '''get Likes
        '''
        likeUrl="https://graph.facebook.com/v3.2/"+comment["id"]+"/reactions?limit=500&"+tokenParam
        #likeJson = getJsonFromUrl(likeUrl)
        #print(likeJson["data"])
        #print("like count :",len(likeJson["data"]))
        #print("--------------------------")        
        resultComment = comment
        #resultComment["writer"] = comment["from"]["name"]
        #resultComment["like_count"] = len(likeJson["data"])
        resultComment["like_count"]=0
        #print(get_comments(comment["id"]))
        #result += get_comments(comment["id"])
        if "from" in resultComment:
            resultComment["writer"] = comment["from"]["name"]
            del resultComment["from"]
        del resultComment["id"]
        result.append(resultComment)
    #print(commentJson["paging"])

    return sorted(result, key=lambda k : k["created_time"], reverse=False)


#get_posts()
post_num = "264581367591821_264581670925124"
#post_num = "264581367591821_264973414219283"
#post_num = "264581367591821_264973414219283"
while True:
    start_time = datetime.now(DT.timezone.utc)
    try:
        all_comments = get_comments(post_num)
        filtered_comments=[]
        this_time = datetime.now(DT.timezone.utc)
        for comment in all_comments:
            that_time = datetime.strptime(comment["created_time"], "%Y-%m-%dT%H:%M:%S%z")
            #print("--------------------")
            #print("this time : ", this_time)
            #print("that time : ", that_time)
            #print("time delta : ", this_time-that_time)
            #print("--------------------")
            #print("message : ", comment["message"], "// like :", comment["like_count"])
            if(len(comment["message"]) > 20):
                #print("Fail - long commnet")
                continue
            if(this_time-that_time <  DT.timedelta(seconds=60*30) ):
            #if(True):
                #print("add :",comment)
                filtered_comments.append(comment)
            #else:
               # print("Fail - old comment")

        filtered_comments = sorted(filtered_comments, key=lambda k : k["created_time"], reverse=False)
        #print("================================================")
        #print(json.dumps(filtered_comments,indent=2, sort_keys=True))
        #print("-----------------------------------------------")
        #print(json.dumps(all_comments,indent=2, sort_keys=True))
        #print("===============================================")
        filteredJson={}
        filteredJson["data"] = filtered_comments
        print(filteredJson)
        sendData= json.dumps(filteredJson)
        #print(sendData)
        byteData = sendData.encode()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(byteData,("127.0.0.1",1234))
    except Exception as e:
        print("**************************program error************************")
        print(e)
        # wave 로 알림
        play_error_voice()
    while True:
        end_time = datetime.now(DT.timezone.utc)
        if( end_time-start_time > DT.timedelta(seconds=5)):
            break
