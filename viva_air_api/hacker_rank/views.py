from django.shortcuts import render
from django.http import HttpResponse
import urllib.request
import json
import time
from django.core import serializers
from datetime import datetime
from django.utils import timezone
from . import models

def isPostTableEmpty():
    posts = models.Post.objects.all()
    if(posts): 
        return False
    else: 
        return True
    
def savePostsInDB(postId, details):
    post = models.Post(postId=postId, details=details)
    post.save()
    return post

def getLatestPostsFromHackernewsAPI():
    response = urllib.request.urlopen('https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty')
    res_body = response.read()
    postsToJson = json.loads(res_body.decode("utf-8"))
    return postsToJson

def getLatestPostsFromDB():
    posts = models.Post.objects.all()
    return posts

def getPostDetail(postId):
    response = urllib.request.urlopen(f'https://hacker-news.firebaseio.com/v0/item/{postId}.json?print=pretty')
    res_body = response.read()
    postToJson = json.loads(res_body.decode("utf-8"))
    return postToJson

def shouldUpdateDBFromHackernewsAPI():
    lastPost = models.Post.objects.last()
    timedelta = datetime.now(timezone.utc) - lastPost.created_at
    timeDeltaInSeconds = timedelta.days * 24 * 3600 + timedelta.seconds
    if timeDeltaInSeconds > 10:
        return True
    else:
        return False

def deleteAllRegisterFromDB():
    result = models.Post.objects.all().delete()
    return result

def index(request):
    i = request.GET['i']
    n = request.GET['n']
    print('i', i)
    print('n', n)
    startTime = time.localtime()
    startTimeToStr = time.strftime("%m/%d/%Y, %H:%M:%S", startTime)

    postsData = []
    if isPostTableEmpty():
        postsData = getLatestPostsFromHackernewsAPI()
        for post in postsData:
            detail = getPostDetail(post)
            savePostsInDB(post, detail)
    else: 
        if(shouldUpdateDBFromHackernewsAPI()):
            print('Deleting all registers')
            deleteAllRegisterFromDB()
            postsData = getLatestPostsFromHackernewsAPI()
            for post in postsData:
                detail = getPostDetail(post)
                savePostsInDB(post, detail)
        else:
            postsData = getLatestPostsFromDB()

    endTime = time.localtime()
    endTimeToStr = time.strftime("%m/%d/%Y, %H:%M:%S", endTime)
    print(startTimeToStr)
    print(endTimeToStr)

    if i and n:
        i = int(i)
        n = int(n)
        postsData = postsData[i:i+n]

    serialized_obj = serializers.serialize('json', postsData)
    return HttpResponse(serialized_obj)
