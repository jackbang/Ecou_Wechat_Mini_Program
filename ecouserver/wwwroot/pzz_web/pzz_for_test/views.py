import time
from pzz_web import settings
from datetime import date, datetime, timedelta
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import filters
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from pzz_for_test.models import TestStoreInfo, TestPlayInfo, TestQueueInfo, TestLabelInfo, TestPlayerInfo, TestStorePlayRepoInfo, TestUserInfo, TestAdminInfo, TestAdminStoreInfo
from pzz_for_test.serializers import StoreSerializer, PlaySerializer, QueueSerializer, LabelSerializer, PlayerSerializer, TestStorePlayRepoSerializer
from . import sendSMS
from .const import const
from .utils import WXBizDataCrypt, decrypt
import requests
import json
import random
import secrets
import hashlib
import os
from PIL import Image, ImageDraw
import numpy as np

def index(request):
    return render(request, 'index.html', {"temp_para": "test_ok!"})

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super().__init__(content, **kwargs)

@csrf_exempt
def test_store_list(request):
    if request.method == 'GET':
        test_store_info = TestStoreInfo.objects.all()
        serializer = StoreSerializer(test_store_info, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = StoreSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def test_play_list(request):
    if request.method == 'GET':
        test_store_info = TestPlayInfo.objects.all()
        serializer = PlaySerializer(test_store_info, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = PlaySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def test_queue_list(request):
    if request.method == 'GET':
        test_store_info = TestQueueInfo.objects.all()
        serializer = QueueSerializer(test_store_info, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = QueueSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def test_store_play_repo(request):
    if request.method == 'GET':
        test_store_play_repo_info = TestStorePlayRepoInfo.objects.all()
        serializer = TestStorePlayRepoSerializer(test_store_play_repo_info, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = TestStorePlayRepoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)

#def test_store_index(request, pk):
#    try:
#        test_store_index = StoreSerializer.objects.get(pk=pk)
#    except StoreSerializer.DoesNotExist:
#        return Response(status=status.HTTP_404_NOT_FOUND)
#
#    if request.method == 'GET':
#        serializer = StoreSerializer(test_store_index)
#        return JSONResponse(serializer.data)

#    elif request.method == 'PUT':
#        #TODO
#        return Response(status=status.HTTP_204_NO_CONTENT)
#    elif request.method == 'DELETE':
#        serializer = StoreSerializer(test_store_index)
#        serializer.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)

def test_store_api(request, store_index):
    try:
        test_store_index = TestStoreInfo.objects.get(store_id=store_index)
    except TestStoreInfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StoreSerializer(test_store_index)
        return JSONResponse(serializer.data)

def test_store_queue_api(request, store_index):
    try:
        test_queues_info = TestStoreInfo.objects.get(store_id=store_index).all_queues.all()
    except TestStoreInfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = QueueSerializer(test_queues_info, many=True)
        return JSONResponse(serializer.data)

def test_queue_play_api(request, store_index, queue_index):
    try:
        test_play_info = TestStoreInfo.objects.get(store_id=store_index).all_queues.get(queue_id = queue_index).play_id
    except TestStoreInfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PlaySerializer(test_play_info)
        return JSONResponse(serializer.data)

class label_list(APIView):
    def get(self, request, format=None):
        label_info = TestLabelInfo.objects.all()
        serializer = LabelSerializer(label_info, many=True)
        return JSONResponse(serializer.data)

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        serializer = LabelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)

class player_list(APIView):
    def get(self, request, format=None):
        player_info = TestPlayerInfo.objects.all()
        serializer = PlayerSerializer(player_info, many=True)
        return JSONResponse(serializer.data)

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        serializer = PlayerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)

##Test APIs
class TestStoreInfoAPI(APIView):
    def get_object(self, ModelName, pk):
        try:
            return ModelName.objects.get(pk=pk)
        except ModelName.DoesNotExist:
            self.code=0
            self.data={}
            self.output = {"code":self.code, "data":self.data}
            return JSONResponse(self.output)

    def get(self, request, pk, format=None):
        '''
        self.store_name  store_name
        self.store_address  store_address
        self.store_info  store_info
        self.store_status  store_status
        self.store_tel  store_tel
        self.store_logo  store_pic
        '''
        store_info = self.get_object(TestStoreInfo, pk)
        try:
            test = store_info.store_id
        except:
            return store_info
        self.store_name = store_info.store_name
        self.store_address = store_info.store_address
        self.store_info = store_info.store_info
        self.store_status = store_info.store_status
        self.store_tel = store_info.store_tel
        self.store_logo = store_info.store_pic
        self.store_deposit = store_info.store_deposit

        self.data={
            "store_name": self.store_name,
            "store_address": self.store_address,
            "store_info": self.store_info,
            "store_status": self.store_status,
            "store_deposit": self.store_deposit,
            "store_tel": self.store_tel,
            "store_logo": self.store_logo,
            "store_latitude": store_info.store_latitude,
            "store_longitude": store_info.store_longitude
        }
        self.code = 1
        self.output = {"code":self.code, "data":self.data}
        return JSONResponse(self.output)

class TestQueuesInStoreAPI(APIView):
    def get_object(self, ModelName, pk):
        try:
            return ModelName.objects.get(pk=pk)
        except ModelName.DoesNotExist:
            self.code=0
            self.data={}
            self.output = {"code":self.code, 
                "queue_num": [],
                "queue_date":[],
                "queue_data":[]
                }
            return JSONResponse(self.output)

    def get(self, request, pk, format=None):
        '''
        "queue_num" = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        "queue_date":["今天04-03","周二04-04","周三04-05",
            "周四04-06","周五04-07","周六04-08",
            "周日04-09","周一04-10","周二04-11",
            "周三04-12","周四04-13","周五04-14",
            "周六04-15","周日04-16"],
        "queue_data":[
            {
            "queue_id": 1,
            "queue_status": 0,
            "queue_end_time": "2021-04-09T23:59:59",
            "queue_current_num": 6,
            "queue_current_male_num": 4,
            "queue_current_female_num": 2,
            "play_name": "剧本名字1",
            "play_pic": "/media/test_logo.png",
            "play_antigender": 0,
            "play_labels": ["欢乐", "现代"]
            }
        ]
        '''
        store_info = self.get_object(TestStoreInfo, pk)
        try:
            test = store_info.store_id
        except:
            return store_info
        todayDate = date.today()
        queues_info = store_info.all_queues.all().filter(queue_end_time__gt=todayDate).order_by('queue_end_time')
        queues_length = len(queues_info)
        '''
        下面一部分完成日期的format
        '''
        today_weekday = date.today().weekday()
        tomorrow_weekday = today_weekday+1
        if (today_weekday == 7):
            tomorrow_weekday = 1
        today_date = date.today()
        #temp_date = today_date + timedelta(days=1)
        today_data_str = today_date.strftime('%m-%d')
        weekday_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.queue_date = ["今天 "+today_data_str]
        for day_index in range(1,14):
            temp_date = today_date + timedelta(days=day_index)
            self.queue_date.append(weekday_name[temp_date.weekday()] + " " +temp_date.strftime('%m-%d'))
        '''
        下面一部分 完成每日局数统计
        '''
        self.queue_num = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for queue_index in range(0, queues_length):
            queue_time = queues_info[queue_index].queue_end_time.strftime('%m-%d')
            for ind in range(0,14):
                if (queue_time == self.queue_date[ind][3:8]):
                    self.queue_num[ind] += 1

        '''
        完成 每日队列queue data填充
        '''
        self.queue_data = []
        self.play_data = []
        for queue_index in range(0, queues_length):
            play_info = queues_info[queue_index].play_id
            labels_info = queues_info[queue_index].play_id.all_labels.all()
            play_labels = []
            for label_index in range(0, len(labels_info)):
                play_labels.append(labels_info[label_index].label_content)
            self.queue_content ={
                "queue_id": queues_info[queue_index].queue_id,
                "queue_status": queues_info[queue_index].queue_status,
                "queue_end_time": queues_info[queue_index].queue_end_time.strftime('%m月%d日  %H:%M'),
                "queue_current_num": queues_info[queue_index].queue_current_num,
                "queue_current_male_num": queues_info[queue_index].queue_current_male_num,
                "queue_current_female_num": queues_info[queue_index].queue_current_female_num,
                "queue_antigender": queues_info[queue_index].queue_allow_antigender,
                "play_id": play_info.play_id,
            }
            self.queue_data.append(self.queue_content)
            self.play_content ={
                "play_id": play_info.play_id,
                "play_name": play_info.play_name,
                "play_headcount": play_info.play_headcount,
                "play_male_num": play_info.play_male_num,
                "play_female_num": play_info.play_female_num,
                "play_score": play_info.play_score,
                "play_intro": play_info.play_intro,
                "play_duration": play_info.play_duration,
                "play_pic": play_info.play_img,
                "play_labels": play_labels
            }
            self.play_data.append(self.play_content)
        '''
        从label中取数据
        '''

        self.code = 1
        return JSONResponse({"code":self.code, "data": {"queue_num":self.queue_num, "queue_date":self.queue_date, "queue_data":self.queue_data, "play_data":self.play_data}})

class TestQueueInfoInStoreAPI(APIView):
    def get_object(self, ModelName, pk):
        try:
            return ModelName.objects.get(pk=pk)
        except ModelName.DoesNotExist:
            self.code=0
            self.data={}
            self.output = {"code":self.code, "data":self.data}
            return JSONResponse(self.output)
        
    def get(self, request, pk, format=None):
        queue_info = self.get_object(TestQueueInfo, pk)
        try:
            play_info = queue_info.play_id
        except:
            return queue_info
        play_male_num = play_info.play_male_num
        play_female_num = play_info.play_female_num
        self.queue_current_num = queue_info.queue_current_num
        self.queue_q_male_num = play_male_num - queue_info.queue_current_male_num
        self.queue_q_female_num = play_female_num - queue_info.queue_current_female_num
        weekday_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.queue_end_time = queue_info.queue_end_time.strftime('%m月%d日 ') + weekday_name[queue_info.queue_end_time.weekday()] + queue_info.queue_end_time.strftime(' %H:%M')
        self.queue_antigender = queue_info.queue_allow_antigender

        self.play_name = play_info.play_name
        self.play_score = play_info.play_score
        self.play_headcount = play_info.play_headcount
        self.play_male_num = play_male_num
        self.play_female_num = play_female_num
        self.play_intro = play_info.play_intro
        self.play_pic = play_info.play_img
        self.play_duration = play_info.play_duration
        self.play_labels = []
        labels_info = queue_info.play_id.all_labels.all()
        for label_index in range(0, len(labels_info)):
            self.play_labels.append(labels_info[label_index].label_content)

        self.player_list = []

        player_info = queue_info.all_players.all()
        for player_index in range(0, len(player_info)):
            player_name = player_info[player_index].player_name
            player_gender = player_info[player_index].player_gender
            player_pic = player_info[player_index].player_pic
            player_data = {
                "player_name": player_name,
                "player_gender": player_gender,
                "player_pic": player_pic
            }
            self.player_list.append(player_data)
        self.data = {
            "queue_end_time": self.queue_end_time,
            "queue_current_num": self.queue_current_num,
            "queue_q_male_num": self.queue_q_male_num,
            "queue_q_female_num": self.queue_q_female_num,
            "queue_antigender": self.queue_antigender,
            "play_name": self.play_name,
            "play_score": self.play_score,
            "play_headcount": self.play_headcount,
            "play_male_num": self.play_male_num,
            "play_female_num": self.play_female_num,
            "play_intro": self.play_intro,
            "play_pic": self.play_pic,
            "play_duration": self.play_duration,
            "play_labels": self.play_labels,
            "player_list": self.player_list
        }
        self.code = 1
        return JSONResponse({"code": self.code, "data": self.data})

class TestSearchPlaytoJoinAPI(APIView):
    def get_object(self, ModelName, pk):
        try:
            return ModelName.objects.get(pk=pk)
        except ModelName.DoesNotExist:
            self.code=0
            self.data={}
            self.output = {"code":self.code, "data":self.data}
            return JSONResponse(self.output)

    def get(self, request, store_id, format=None):
        try:
            search_content = request.GET['title']
        except:
            search_content=''
        store_info = self.get_object(TestStoreInfo, store_id)
        items_info = store_info.all_plays.all().filter(play_id__play_name__icontains=search_content)
        self.play_nums = len(items_info)
        self.plays_list = []
        for item in items_info:
            play_labels = []
            labels_info = item.play_id.all_labels.all()
            for label in labels_info:
                play_labels.append(label.label_content)
            self.plays_list.append({
                'play_id': item.play_id.play_id,
                'play_name':item.play_id.play_name,
                'play_headcount':item.play_id.play_headcount,
                'play_male_num':item.play_id.play_male_num,
                'play_female_num':item.play_id.play_female_num,
                'play_score':item.play_id.play_score,
                'play_intro':item.play_id.play_intro,
                'play_pic':item.play_id.play_img,
                'play_duration':item.play_id.play_duration,
                'play_labels':play_labels
            })
        self.data = {
            'total_play_num':self.play_nums,
            'plays_list':self.plays_list
        }
        self.code = 1
        return JSONResponse({"code":self.code, "data":self.data})
        
class TestQueuesPersonInfoAPI(APIView):
    def get_object(self,ModelName,pk):
        try:
            return ModelName.objects.get(pk=pk)
        except ModelName.DoesNotExist:
            self.code = 0
            self.data = {}
            self.output = {"code":self.code, "data":self.data}
            return JSONResponse(self.output)
    
    def get(self, request, queue_id, format=None):
        self.code = 0
        queue_info = self.get_object(TestQueueInfo, queue_id)
        try:
            self.queue_id = queue_info.queue_id
        except:
            return queue_info
        self.queue_status = queue_info.queue_status
        self.queue_end_time = queue_info.queue_end_time
        self.queue_current_num = queue_info.queue_current_num
        self.queue_current_male_num = queue_info.queue_current_male_num
        self.queue_current_female_num = queue_info.queue_current_female_num
        self.queue_allow_antigender = queue_info.queue_allow_antigender
        self.code = 1
        self.output = {
            "code":self.code,
            "data":{
                "queue_id": self.queue_id,
                "queue_status": self.queue_status,
                "queue_end_time": self.queue_end_time,
                "queue_current_num": self.queue_current_num,
                "queue_male_num": self.queue_current_male_num,
                "queue_female_num": self.queue_current_female_num,
                "queue_allow_antigender": self.queue_allow_antigender,
            }
        }
        return JSONResponse(self.output)


class TestQueuesPlayDetailInfoAPI(APIView):
    def get_object(self,ModelName,pk):
        try:
            return ModelName.objects.get(pk=pk)
        except ModelName.DoesNotExist:
            self.code = 0
            self.data = {}
            self.output = {"code":self.code, "data":self.data}
            return JSONResponse(self.output)        

    def get(self, request, queue_id, format=None):
        self.code = 0
        queue_info = self.get_object(TestQueueInfo, queue_id)
        try:
            play_id_fk = queue_info.play_id
        except:
            return play_info
        self.play_id = play_id_fk.play_id
        self.play_name = play_id_fk.play_name
        self.play_headcount = play_id_fk.play_headcount
        self.play_male_num = play_id_fk.play_male_num
        self.play_female_num = play_id_fk.play_female_num
        self.play_score = play_id_fk.play_score
        self.play_intro = play_id_fk.play_intro
        self.play_pic = play_id_fk.play_img #!!!!!! pic 和 img是故意这么写的
        self.play_duration = play_id_fk.play_duration
        self.labels_info = play_id_fk.all_labels.all()
        self.play_labels = []
        for i in range(len(self.labels_info)):
            self.play_labels.append(self.labels_info[i].label_content)
        self.code = 1
        self.output = {
            "code":self.code,
            "data":{
                "play_id" : self.play_id,
                "play_name" : self.play_name,
                "play_headcount" : self.play_headcount,
                "play_male_num" : self.play_male_num,
                "play_female_num" : self.play_female_num,
                "play_score" : self.play_score,
                "play_intro" : self.play_intro,
                "play_pic" : self.play_pic, #!!!!!! pic 和 img是故意这么写的
                "play_duration" : self.play_duration,
                "play_labels" : self.play_labels,
            }
        }
        return JSONResponse(self.output)

class TestQueuesPersonDetailInfoAPI(APIView):
    def get_object(self,ModelName,pk):
        try:
            return ModelName.objects.get(pk=pk)
        except ModelName.DoesNotExist:
            self.code = 0
            self.data = {}
            self.output = {"code":self.code, "data":self.data}
            return JSONResponse(self.output)
    
    def get(self, request, queue_id, format=None):
        queue_info = self.get_object(TestQueueInfo,queue_id)
        self.player_info_list = queue_info.all_players.all()
        self.player_info = []
        for i in range(len(self.player_info_list)):
            player_id = self.player_info_list[i].player_id
            player_name = self.player_info_list[i].player_name
            player_gender = self.player_info_list[i].player_gender
            player_pic = self.player_info_list[i].player_pic
            self.player_info.append(
                {
                    "player_id": player_id,
                    "player_name": player_name,
                    "player_gender": player_gender,
                    "player_pic" : player_pic,
                }
            )
        self.code = 1
        self.output = {
            "code" : self.code,
            "data" : {
                "player_info" : self.player_info
            }
        }
        return JSONResponse(self.output)

class TestQueueSearchAPI(APIView):
    def get(self, request):
        data_json = request.GET
        user_id = data_json["adminId"]
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()

        ServerSession = ''

        if (appId == const.ownerapp_appid):
            # admin Version
            try:
                user = TestAdminInfo.objects.select_related().get(admin_id=user_id)
            except:
                return JSONResponse({"code":0, "data":"adminId is wrong"})
            ServerSession = user.admin_last3rdSession
        elif (appId == const.weapp_appid):
            # user Version
            try:
                user = TestUserInfo.objects.select_related().get(user_id=user_id)
            except:
                return JSONResponse({"code":0, "data":"userId is wrong"})
            ServerSession = user.user_last3rdSession

        if ((ServerSession == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            store_id = data_json["store_id"]
            title = data_json["title"]

            todayDate = date.today()

            queues = TestQueueInfo.objects.select_related().filter(store_id__store_id__exact=store_id, play_id__play_name__icontains=title, queue_end_time__gte=todayDate, queue_status__exact=0)

            try:
                playsResponse = queues.values(
                                    'play_id__play_id', 
                                    'play_id__play_name', 
                                    'play_id__play_headcount', 
                                    'play_id__play_male_num', 
                                    'play_id__play_female_num',
                                    'play_id__play_score', 
                                    'play_id__play_intro', 
                                    'play_id__play_img',
                                    'play_id__play_antigender',
                                    'play_id__play_duration'
                                )
            except:
                playsResponse = []

            try:
                queuesResponse = queues.values(
                    'queue_id',
                    'queue_status',
                    'queue_end_time',
                    'queue_current_num',
                    'queue_current_male_num',
                    'queue_current_female_num',
                    'queue_allow_antigender',
                    'play_id__play_id'
                )
            except:
                queuesResponse = []

            for i in range(0, len(playsResponse)):
                temp = queues[i].play_id.all_labels.values_list('label_content', flat=True)[:4]
                playsResponse[i]['play_labels'] = temp
                playsResponse[i]['play_id'] = playsResponse[i].pop('play_id__play_id')
                playsResponse[i]['play_name'] = playsResponse[i].pop('play_id__play_name')
                playsResponse[i]['play_headcount'] = playsResponse[i].pop('play_id__play_headcount')
                playsResponse[i]['play_male_num'] = playsResponse[i].pop('play_id__play_male_num')
                playsResponse[i]['play_female_num'] = playsResponse[i].pop('play_id__play_female_num')
                playsResponse[i]['play_score'] = playsResponse[i].pop('play_id__play_score')
                playsResponse[i]['play_intro'] = playsResponse[i].pop('play_id__play_intro')
                playsResponse[i]['play_img'] = playsResponse[i].pop('play_id__play_img')
                playsResponse[i]['play_antigender'] = playsResponse[i].pop('play_id__play_antigender')
                playsResponse[i]['play_duration'] = playsResponse[i].pop('play_id__play_duration')
            
            for i in range(0, len(queuesResponse)):
                queuesResponse[i]['play_id'] = queuesResponse[i].pop('play_id__play_id')
                
            #playsResponse['play_labels'] = labelList
            return JSONResponse({"code":0, "data":{"plays": playsResponse, "queues": queuesResponse}})
            

        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestQueueGetAPI(APIView):
    def get(self, request):
        data_json = request.GET
        queue_id = data_json["queueId"]
        
        try:
            theQueue = TestQueueInfo.objects.get(queue_id = queue_id)
        except: 
             return JSONResponse({"code":0, "data":"queueId error"})
        
        thePlay = theQueue.play_id

        theLabels = thePlay.all_labels.values_list('label_content', flat=True)[:4]

        data = {
            'queue': {
                'queue_id': theQueue.queue_id,
                'queue_status': theQueue.queue_status,
                'queue_end_time': theQueue.queue_end_time,
                'queue_current_num': theQueue.queue_current_num,
                'queue_current_male_num': theQueue.queue_current_male_num,
                'queue_current_female_num': theQueue.queue_current_female_num,
                'queue_allow_antigender': theQueue.queue_allow_antigender,
                'play_id' : thePlay.play_id
            },
            'play': {
                'play_id': thePlay.play_id, 
                'play_name': thePlay.play_name, 
                'play_headcount': thePlay.play_headcount, 
                'play_male_num': thePlay.play_male_num, 
                'play_female_num': thePlay.play_female_num,
                'play_score': thePlay.play_score, 
                'play_intro': thePlay.play_intro, 
                'play_img': thePlay.play_img,
                'play_antigender': thePlay.play_antigender,
                'play_labels': theLabels,
                'play_duration': thePlay.play_duration
            }
        }

        return JSONResponse({"code":1, "data":data})

        







class TestWechatLoginAPI(APIView):
    #def get(self, request, format=None):
        #code_data = request.GET['code']
        #payload ={
        #    'appid': const.weapp_appid,
        #    'secret': const.weapp_secret,
        #    'js_code': code_data,
        #    'grant_type': 'authorization_code'
        #}
        #res = requests.get('https://api.weixin.qq.com/sns/jscode2session', params=payload)
        #res_json = json.load(type(res.text))
        #session_key = res.json().session_key
        #openid = res.json().openid
        #errcode = res.json().errcode
        #res_json = res.json()
        #errcode = res_json.get("errcode")
        #if (errcode):
        #    return JSONResponse({'errcode': errcode})
        #else:
        #    #request.session[res_json.session_key]
        #    return JSONResponse(res_json.get('session_key'))
    def get(self, request, format=None):
        return JSONResponse("")
    def post(self, request, format=None):
        user_data = json.loads(request.body)
        code = user_data["code"]
        watermark = user_data["watermark"]
        appId = watermark["appId"]
        timestamp = (watermark["token"] >> 1) - 1000
        serverTimeStamp = time.time()
        
        if ((code != "") & (appId == const.weapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            payload ={
            'appid': const.weapp_appid,
            'secret': const.weapp_secret,
            'js_code': code,
            'grant_type': 'authorization_code'
            }
            weappLoginRes = requests.get('https://api.weixin.qq.com/sns/jscode2session', params=payload)
            weappLoginResJson = weappLoginRes.json()
            openid = weappLoginResJson["openid"]
            session_key = weappLoginResJson["session_key"]
            userInfo = user_data["userInfo"]
            
            #3rd session key
            newSession = secrets.token_urlsafe(16)

            try:
                oldUser = TestUserInfo.objects.get(user_openid=openid)
                oldUser.user_gender = userInfo["gender"]
                oldUser.user_nickName = userInfo["nickName"]
                oldUser.user_avatarUrl = userInfo["avatarUrl"]
                oldUser.user_province = userInfo["province"]
                oldUser.user_city = userInfo["city"]
                oldUser.user_lastLoginTime = datetime.now()
                systemInfo = user_data["systemInfo"]
                oldUser.user_lastLoginSysInfo = str(systemInfo)
                
                if request.META.get('HTTP_X_FORWARDED_FOR'):
                    ip = request.META.get("HTTP_X_FORWARDED_FOR")
                else:
                    ip = request.META.get("REMOTE_ADDR")
                oldUser.user_lastLoginIp = ip

                oldUser.user_lastSessionKey = session_key
                oldUser.user_last3rdSession = newSession
                oldUser.save()
            except:
                user = TestUserInfo()
                user.user_openid = openid
                user.user_gender = userInfo["gender"]
                user.user_nickName = userInfo["nickName"]
                user.user_avatarUrl = userInfo["avatarUrl"]
                user.user_province = userInfo["province"]
                user.user_city = userInfo["city"]
                user.user_lastLoginTime = datetime.now()
                systemInfo = user_data["systemInfo"]
                user.user_lastLoginSysInfo = systemInfo
                
                if request.META.get('HTTP_X_FORWARDED_FOR'):
                    ip = request.META.get("HTTP_X_FORWARDED_FOR")
                else:
                    ip = request.META.get("REMOTE_ADDR")
                user.user_lastLoginIp = ip

                user.user_lastSessionKey = session_key
                user.user_last3rdSession = newSession
                user.save()
            theUser = TestUserInfo.objects.get(user_openid=openid)
            return JSONResponse({"code":1, "data":{"sessionId": newSession, "userId": theUser.user_id}})
        else :
            return JSONResponse({"code":0, "data":{}})#"timeDif": serverTimeStamp - timestamp, "idSame": appId == const.weapp_appid }})

class TestGetPhoneNumberAPI(APIView):
    def post(self, request, format=None):
        data_json = json.loads(request.body)
        encryptedData = data_json['encryptedData']
        iv = data_json['iv']
        sessionId = data_json['sessionId']
        user_id = data_json['user_id']
        appId = data_json['watermark']['appId']
        timestamp = (data_json['watermark']['token'] >> 1) - 1000
        serverTimeStamp = time.time()

        userOrAdmin = 0 #1 is user 2 is admin

        if (appId == const.weapp_appid):
            # userInfo
            try:
                user = TestUserInfo.objects.get(user_id=user_id)
                userOrAdmin = 1
                serverSessionId = user.user_last3rdSession
            except:
                return JSONResponse({"code":0, "data":"user id error"})
        elif (appId == const.ownerapp_appid):
            # adminInfo
            try:
                user = TestAdminInfo.objects.get(admin_id=user_id)
                userOrAdmin = 2
                serverSessionId = user.admin_last3rdSession
            except:
                return JSONResponse({"code":0, "data":"user id error"})
        else:
            return JSONResponse({"code":0, "data":"appId error"})

        if ((serverSessionId == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            if (userOrAdmin == 1):
                sessionKey = user.user_lastSessionKey
                pc = WXBizDataCrypt(appId, sessionKey)
                phoneNum = pc.decrypt(encryptedData, iv)
                user.user_phoneNum = phoneNum['phoneNumber']
                user.user_purePhoneNum = phoneNum['purePhoneNumber']
                user.user_countryCode = phoneNum['countryCode']
                user.save()
            elif (userOrAdmin == 2):
                sessionKey = user.admin_lastSessionKey
                pc = WXBizDataCrypt(appId, sessionKey)
                phoneNum = pc.decrypt(encryptedData, iv)
                user.admin_phoneNum = phoneNum['phoneNumber']
                user.admin_purePhoneNum = phoneNum['purePhoneNumber']
                user.admin_countryCode = phoneNum['countryCode']
                user.save()
            return JSONResponse({"code":1, "data":phoneNum})
        else:
            return JSONResponse({"code":0, "data":'certification failed'})

class TestJoinQueueAPI(APIView):
    def post(self, request, format=None):
        data_json = json.loads(request.body)
        playerList = data_json["player_info"]
        player_tel = data_json["player_tel"]
        player_comment = data_json["player_comment"]
        queue_id = data_json["queue_id"]
        user_id = data_json["user_id"]
        sessionId = data_json['sessionId']
        appId = data_json["watermark"]["appId"]
        timestamp = (data_json['watermark']['token'] >> 1) - 1000
        serverTimeStamp = time.time()
        if(len(TestPlayerInfo.objects.filter(user_id__user_id__exact=user_id, queue_id__queue_id__exact=queue_id))>0):
            return JSONResponse({"code":0, "data":{"errcode":1}})
        try:
            user = TestUserInfo.objects.get(user_id=user_id)
        except:
            return JSONResponse({"code":0, "data":{}})
        if ((user.user_last3rdSession == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5) & (appId == const.weapp_appid)):
            for index in range(0, len(playerList)):
                player = TestPlayerInfo()
                player.player_name = playerList[index]['player_name']
                player.player_gender = playerList[index]['player_gender']
                player.player_pic = playerList[index]['player_pic']
                player.player_tel = player_tel
                player.user_id = user
                player.player_comment = player_comment
                
                try:
                    queue = TestQueueInfo.objects.get(queue_id=queue_id)
                except:
                    return JSONResponse({"code":0, "data":{}})
                player.queue_id = queue
                queue.queue_current_num = queue.queue_current_num + 1
                if (playerList[index]['player_gender'] == 1):
                    queue.queue_current_male_num = queue.queue_current_male_num + 1
                elif (playerList[index]['player_gender'] == 0):
                    queue.queue_current_female_num = queue.queue_current_female_num + 1
                player.save()
                queue.save()
            return JSONResponse({"code":1,"data":{"errcode":0}})
        else:
            return JSONResponse({"code":0, "data":{}})

class TestQueueHistoryAPI(APIView):
    def post(self, request, format=None):
        data_json = json.loads(request.body)
        store_id = data_json['store_id']
        user_id = data_json['user_id']
        sessionId = data_json['sessionId']
        appId = data_json["watermark"]["appId"]
        timestamp = (data_json['watermark']['token'] >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            user = TestUserInfo.objects.get(user_id=user_id)
        except:
            return JSONResponse({"code":0, "data":"userId error"})
        if ((user.user_last3rdSession == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5) & (appId == const.weapp_appid)):
            todayDate = date.today()
            playerQuerySet = user.all_players.all().filter(queue_id__queue_end_time__gt=todayDate, queue_id__store_id__exact=store_id).order_by('queue_id').values('queue_id_id').distinct()#.distinct('queue_id_id')
            queueList = [];
            for queueIdx in range(0,len(playerQuerySet)):
                queueInfo = TestQueueInfo.objects.get(queue_id = playerQuerySet[queueIdx]['queue_id_id'])
                queueData = {
                    "queue_id":queueInfo.queue_id,
                    "queue_status":queueInfo.queue_status,
                    "queue_end_time":queueInfo.queue_end_time,
                    "queue_current_num":queueInfo.queue_current_num,
                    "queue_current_male_num":queueInfo.queue_current_male_num,
                    "queue_current_female_num":queueInfo.queue_current_female_num,
                    "queue_antigender":queueInfo.queue_allow_antigender,
                    "play_id":queueInfo.play_id.play_id
                }
                queueList.append(queueData)
            return JSONResponse({"code":1,"data":{"queueList":queueList}})
        else:
            return JSONResponse({"code":0,"data":"certification failed"})

class TestMineQueueHistoryAPI(APIView):
    def post(self, request, format=None):
        data_json = json.loads(request.body)
        user_id = data_json['user_id']
        sessionId = data_json['sessionId']
        appId = data_json["watermark"]["appId"]
        timestamp = (data_json['watermark']['token'] >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            user = TestUserInfo.objects.get(user_id=user_id)
        except:
            return JSONResponse({"code":0, "data":{}})
        if ((user.user_last3rdSession == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5) & (appId == const.weapp_appid)):
            todayDate = date.today()
            playerQuerySet = user.all_players.all().order_by('queue_id').values('queue_id_id').distinct()#.distinct('queue_id_id')
            queueList = [];
            storeList = [];
            playList = [];
            for queueIdx in range(0,len(playerQuerySet)):
                queueInfo = TestQueueInfo.objects.get(queue_id = playerQuerySet[queueIdx]['queue_id_id'])
                queueData = {
                    "queue_id":queueInfo.queue_id,
                    "queue_status":queueInfo.queue_status,
                    "queue_end_time":queueInfo.queue_end_time,
                    "queue_current_num":queueInfo.queue_current_num,
                    "queue_current_male_num":queueInfo.queue_current_male_num,
                    "queue_current_female_num":queueInfo.queue_current_female_num,
                    "queue_antigender":queueInfo.queue_allow_antigender,
                    "play_id":queueInfo.play_id.play_id,
                    "store_id":queueInfo.store_id.store_id
                }
                storeInfo = queueInfo.store_id
                storeData = {
                    "store_id": storeInfo.store_id,
                    "store_name": storeInfo.store_name,
                    "store_address": storeInfo.store_address,
                    "store_latitude": storeInfo.store_latitude,
                    "store_longitude": storeInfo.store_longitude,
                    "store_tel": storeInfo.store_tel
                }
                playInfo = queueInfo.play_id
                labelsInfo = playInfo.all_labels.all()
                playLabels = []
                for i in range(len(labelsInfo)):
                    playLabels.append(labelsInfo[i].label_content)
                playData = {
                    "play_id" : playInfo.play_id,
                    "play_name" : playInfo.play_name,
                    "play_headcount" : playInfo.play_headcount,
                    "play_male_num" : playInfo.play_male_num,
                    "play_female_num" : playInfo.play_female_num,
                    "play_score" : playInfo.play_score,
                    "play_intro" : playInfo.play_intro,
                    "play_pic" : playInfo.play_img, #!!!!!! pic 和 img是故意这么写的
                    "play_duration" : playInfo.play_duration,
                    "play_antigender": playInfo.play_antigender,
                    "play_labels" : playLabels
                }
                storeList.append(storeData)
                queueList.append(queueData)
                playList.append(playData)
        return JSONResponse({"code":1,"data":{"queueList":queueList, "storeList":storeList, "playList":playList}})

class TestCreateQueueAPI(APIView):
    def post(self, request, format=None):
        data_json = json.loads(request.body)
        playerList = data_json["player_info"]
        player_tel = data_json["player_tel"]
        player_comment = data_json["player_comment"]
        queue_data = data_json["queue_info"]
        user_id = data_json["user_id"]
        sessionId = data_json['sessionId']
        appId = data_json["watermark"]["appId"]
        timestamp = (data_json['watermark']['token'] >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            user = TestUserInfo.objects.get(user_id=user_id)
        except:
            return JSONResponse({"code":0, "data":{}})
        if ((user.user_last3rdSession == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5) & (appId == const.weapp_appid)):
            queue = TestQueueInfo()
            queue.queue_status = 0
            queue.queue_end_time = queue_data['queue_end_time']
            queue.queue_current_num = queue_data['queue_current_num']
            queue.queue_current_male_num = queue_data['queue_current_male_num']
            queue.queue_current_female_num = queue_data['queue_current_female_num']
            queue.queue_allow_antigender = queue_data['queue_antigender']
            queue.play_id_id = queue_data['play_id']
            queue.store_id_id = queue_data['store_id']
            queue.save()
            for index in range(0, len(playerList)):
                player = TestPlayerInfo()
                player.player_name = playerList[index]['player_name']
                player.player_gender = playerList[index]['player_gender']
                player.player_pic = playerList[index]['player_pic']
                player.player_tel = player_tel
                player.user_id = user
                player.player_comment = player_comment
                player.queue_id = queue
                player.save()

            
            return JSONResponse({"code":1,"data":{"errcode":0, "queue_id": queue.queue_id}})
        else:
            return JSONResponse({"code":0, "data":{}})

class TestCheckQueueAPI(APIView):
    def post(self, request, format=None):
        data_json = json.loads(request.body)
        queue_data = data_json["queue_info"]
        user_id = data_json["user_id"]
        sessionId = data_json['sessionId']
        appId = data_json["watermark"]["appId"]
        timestamp = (data_json['watermark']['token'] >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            user = TestUserInfo.objects.get(user_id=user_id)
        except:
            return JSONResponse({"code":0, "data":{}})
        if ((user.user_last3rdSession == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5) & (appId == const.weapp_appid)):

            thePlay = TestPlayInfo.objects.select_related().filter(play_id__exact=queue_data['play_id'])
            if (len(thePlay) == 0):
                return JSONResponse({"code":0, "data":"playId error"})
            format1 = '%Y-%m-%dT%H:%M:%S'
            repeatQueues = TestQueueInfo.objects.select_related().filter(\
                store_id__store_id__exact=queue_data['store_id'], \
                play_id__play_id__exact=queue_data['play_id'], \
                queue_end_time__gt=datetime.strptime(queue_data['queue_end_time'], format1)-timedelta(hours=thePlay[0].play_duration), \
                queue_end_time__lt=datetime.strptime(queue_data['queue_end_time'], format1)+timedelta(hours=thePlay[0].play_duration),\
                )

            if (len(repeatQueues) == 0):
                return JSONResponse({"code":1, "data":"no repeat"})
            else :
                return JSONResponse({"code":2, "data":"repeated"})
        else :
            return JSONResponse({"code":0, "data":"certification failed"})


class TestAdminLoginAPI(APIView):
    def post(self, request, format=None):
        

        admin_data = json.loads(request.body)
        code = admin_data["code"]
        watermark = admin_data["watermark"]
        appId = watermark["appId"]
        timestamp = (watermark["token"] >> 1) - 1000
        serverTimeStamp = time.time()
        
        if ((code != "") & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            payload ={
            'appid': const.ownerapp_appid,
            'secret': const.ownerapp_secret,
            'js_code': code,
            'grant_type': 'authorization_code'
            }
            weappLoginRes = requests.get('https://api.weixin.qq.com/sns/jscode2session', params=payload)
            weappLoginResJson = weappLoginRes.json()
            openid = weappLoginResJson["openid"]
            session_key = weappLoginResJson["session_key"]
            adminInfo = admin_data["adminInfo"]
            
            #3rd session key
            newSession = secrets.token_urlsafe(16)

            

            if (len(TestAdminInfo.objects.filter(admin_openid__exact=openid))):
                ###这里有这个人的资料，re login的时候更新last信息
                admin = TestAdminInfo.objects.get(admin_openid=openid)
                
            else:
                ###这里没有这个人的信息，建立一个新的索引
                admin = TestAdminInfo()
                admin.admin_openid = openid

            admin.admin_gender = adminInfo["gender"]
            admin.admin_nickName = adminInfo["nickName"]
            admin.admin_avatarUrl = adminInfo["avatarUrl"]
            admin.admin_province = adminInfo["province"]
            admin.admin_city = adminInfo["city"]
            admin.admin_lastLoginTime = datetime.now()
            systemInfo = admin_data["systemInfo"]
            admin.admin_lastLoginSysInfo = str(systemInfo)
            if request.META.get('HTTP_X_FORWARDED_FOR'):
                ip = request.META.get("HTTP_X_FORWARDED_FOR")
            else:
                ip = request.META.get("REMOTE_ADDR")
            admin.admin_lastLoginIp = ip
            admin.admin_lastSessionKey = session_key
            admin.admin_last3rdSession = newSession
            admin.save()

            adminStores = TestAdminStoreInfo.objects.filter(admin_id__admin_id__exact=admin.admin_id)

            storeList = []


            if (len(adminStores) == 0):
                newAdmin = 1
            else:
                newAdmin = 0
                for i in range(0, len(adminStores)):
                    storeInfo = adminStores[i].store_id
                    permission = adminStores[i].adminStore_permission
                    storeList.append({
                        "storeInfo": {
                            "store_id": storeInfo.store_id,
                            "store_name": storeInfo.store_name,
                            "store_address": storeInfo.store_address,
                            "store_info": storeInfo.store_info,
                            "store_status": storeInfo.store_status,
                            "store_deposit": storeInfo.store_deposit,
                            "store_tel": storeInfo.store_tel,
                            "store_logo": storeInfo.store_pic,
                            "store_latitude": storeInfo.store_latitude,
                            "store_longitude": storeInfo.store_longitude
                        },
                        "permission": permission
                    })
            
            return JSONResponse({"code":1, "data":{"sessionId": newSession, "adminId": admin.admin_id, "newAdmin": newAdmin, "storeList": storeList}})
        else :
            return JSONResponse({"code":0, "data":{}})#"timeDif": serverTimeStamp - timestamp, "idSame": appId == const.weapp_appid }})
            '''
            try:
                oldUser = TestUserInfo.objects.get(user_openid=openid)
                oldUser.user_gender = userInfo["gender"]
                oldUser.user_nickName = userInfo["nickName"]
                oldUser.user_avatarUrl = userInfo["avatarUrl"]
                oldUser.user_province = userInfo["province"]
                oldUser.user_city = userInfo["city"]
                oldUser.user_lastLoginTime = datetime.now()
                systemInfo = user_data["systemInfo"]
                oldUser.user_lastLoginSysInfo = str(systemInfo)
                
                if request.META.get('HTTP_X_FORWARDED_FOR'):
                    ip = request.META.get("HTTP_X_FORWARDED_FOR")
                else:
                    ip = request.META.get("REMOTE_ADDR")
                oldUser.user_lastLoginIp = ip

                oldUser.user_lastSessionKey = session_key
                oldUser.user_last3rdSession = newSession
                oldUser.save()
            except:
                user = TestUserInfo()
                user.user_openid = openid
                user.user_gender = userInfo["gender"]
                user.user_nickName = userInfo["nickName"]
                user.user_avatarUrl = userInfo["avatarUrl"]
                user.user_province = userInfo["province"]
                user.user_city = userInfo["city"]
                user.user_lastLoginTime = datetime.now()
                systemInfo = user_data["systemInfo"]
                user.user_lastLoginSysInfo = systemInfo
                
                if request.META.get('HTTP_X_FORWARDED_FOR'):
                    ip = request.META.get("HTTP_X_FORWARDED_FOR")
                else:
                    ip = request.META.get("REMOTE_ADDR")
                user.user_lastLoginIp = ip

                user.user_lastSessionKey = session_key
                user.user_last3rdSession = newSession
                user.save()
            theUser = TestUserInfo.objects.get(user_openid=openid)
            return JSONResponse({"code":1, "data":{"sessionId": newSession, "userId": theUser.user_id}})
        else :
            return JSONResponse({"code":0, "data":{}})#"timeDif": serverTimeStamp - timestamp, "idSame": appId == const.weapp_appid }})
        '''

class TestSendSMSAPI(APIView):
    def post(self, request, format=None):
    
        data_json = json.loads(request.body)
        admin_id = data_json["adminId"]
        sessionId = data_json['sessionId']
        phone = data_json['phone']
        appId = data_json["watermark"]["appId"]
        timestamp = (data_json['watermark']['token'] >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":{}})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            admin.admin_last3rdSession = secrets.token_urlsafe(16)
            admin.save()
            randomInt = random.randint(1,9)*100000+ \
                        random.randint(0,9)*10000+ \
                        random.randint(0,9)*1000+ \
                        random.randint(0,9)*100+ \
                        random.randint(0,9)*10+ \
                        random.randint(0,9)*1
            sendRandomInt = randomInt *2 + 1000

            errcode = sendSMS.sendSMS('+86'+phone, randomInt)

            return JSONResponse({"code":1, "data":{"sessionId": admin.admin_last3rdSession, "token": sendRandomInt, 'errcode': errcode}})
        else:
            return JSONResponse({"code":0, "data":{}})

class TestUploadFileAPI(APIView):
    def post(self, request):
        IMG_ROOT = settings.MEDIA_ROOT
        body = request.POST
        
        name = body['name']
        idCard = body['idCard']
        phone = body['phone']

        store_name = body['store_name']
        store_position = body['store_position']
        store_address = body['store_address']
        store_latitude = body['store_latitude']
        store_longitude = body['store_longitude']
        store_tel = body['store_tel']
        store_tel2 = body['store_tel2']

        admin_id = int(body["adminId"])
        sessionId = body['sessionId']
        appId = body["appId"]
        timestamp = (int(body['token']) >> 1) - 1000
        serverTimeStamp = time.time()
        
        key = str(float(store_latitude)+float(store_longitude))+str(timestamp)
        
        name = decrypt(name, key)
        idCard = decrypt(idCard, key)
        
        try:
            admin = TestAdminInfo.objects.get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"user id error"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            admin.admin_last3rdSession = secrets.token_urlsafe(16)
            admin.admin_phoneNum = phone
            admin.save()
            img = request.FILES['file'].read()
            img_md5 = hashlib.md5(img).hexdigest()
            img_original_md5 = body["imgMD5"]
            if (img_md5 == img_original_md5) :
                path = os.path.join(IMG_ROOT, 'storePic',request.FILES['file'].name)
                with open(path, "wb") as f:
                    f.write(img)
                
                storeInfo = TestStoreInfo()
                storeInfo.store_name = store_name
                storeInfo.store_position = store_position
                storeInfo.store_address = store_address
                storeInfo.store_latitude = store_latitude
                storeInfo.store_longitude = store_longitude
                storeInfo.store_tel = store_tel
                storeInfo.store_tel2 = store_tel2
                storeInfo.store_pic = os.path.join('/media', 'storePic',request.FILES['file'].name)
                storeInfo.save()

                adminStoreInfo = TestAdminStoreInfo()
                adminStoreInfo.adminStore_name = name
                adminStoreInfo.adminStore_idCard = idCard
                adminStoreInfo.adminStore_phone = phone
                adminStoreInfo.admin_id = admin
                adminStoreInfo.store_id = storeInfo
                adminStoreInfo.adminStore_permission = 1
                adminStoreInfo.adminStore_verify = 1
                adminStoreInfo.save()
                
                out_data = {
                    "store_id": storeInfo.store_id,
                    "store_name": storeInfo.store_name,
                    "store_address": storeInfo.store_address,
                    "store_info": storeInfo.store_info,
                    "store_status": storeInfo.store_status,
                    "store_deposit": storeInfo.store_deposit,
                    "store_tel": storeInfo.store_tel,
                    "store_logo": storeInfo.store_pic,
                    "store_latitude": storeInfo.store_latitude,
                    "store_longitude": storeInfo.store_longitude
                }
                
                
                return JSONResponse({"code":1, "data":{"sessionId": admin.admin_last3rdSession, "storeInfo": out_data}})
            else:
                return JSONResponse({"code":0, "data":"File MD5 checks error", "md51": img_original_md5, "md52": img_md5})
        else:
            return JSONResponse({"code":0, "data":"Login out"})

class TestTotalSearchAPI(APIView):
    def get(self, request):
        data_json = request.GET
        admin_id = data_json["adminId"]
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            title = data_json["title"]
            hd = int(data_json["hd"])
            playTheme = data_json["type1"]
            playType = data_json["type2"]
            playBg = data_json["type3"]
            page = data_json["page"]
            playResults = TestPlayInfo.objects.select_related().filter(play_is_original__exact=1)


            if (hd != 0):
                playResults = playResults.filter(play_headcount__exact=hd)

            if (len(title) != 0):
                playResults = playResults.filter(play_name__icontains=title)

            if (len(playTheme) != 0):
                playResults = playResults.filter(all_labels__label_type__exact=1 ,all_labels__label_content__icontains=playTheme)

            if (len(playType) != 0):
                playResults = playResults.filter(all_labels__label_type__exact=2 ,all_labels__label_content__icontains=playType)

            if (len(playBg) != 0):
                playResults = playResults.filter(all_labels__label_type__exact=3 ,all_labels__label_content__icontains=playBg)
            
            playResultsPage = Paginator(playResults, 20)

            try:
                playsResponse = playResultsPage.page(page).object_list.values(
                                    'play_id', 
                                    'play_name', 
                                    'play_headcount', 
                                    'play_male_num', 
                                    'play_female_num',
                                    'play_score', 
                                    'play_intro', 
                                    'play_img',
                                    'play_antigender',
                                    'play_duration'
                                )
            except:
                playsResponse = []
            
            for i in range(0, len(playsResponse)):
                temp = playResultsPage.page(page).object_list[i].all_labels.values_list('label_content', flat=True)[:4]
                playsResponse[i]['play_labels'] = temp
            #playsResponse['play_labels'] = labelList
            return JSONResponse(playsResponse)
            

        else:
            return JSONResponse({"code":0, "data":"certification failed"})
            

class TestStoreSearchAPI(APIView):
    def get(self, request):
        data_json = request.GET
        user_id = data_json["adminId"]
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()

        ServerSession = ''

        if (appId == const.ownerapp_appid):
            # admin Version
            try:
                user = TestAdminInfo.objects.select_related().get(admin_id=user_id)
            except:
                return JSONResponse({"code":0, "data":"adminId is wrong"})
            ServerSession = user.admin_last3rdSession
        elif (appId == const.weapp_appid):
            # user Version
            try:
                user = TestUserInfo.objects.select_related().get(user_id=user_id)
            except:
                return JSONResponse({"code":0, "data":"userId is wrong"})
            ServerSession = user.user_last3rdSession

        if ((ServerSession == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            store_id = data_json["store_id"]
            title = data_json["title"]
            hd = int(data_json["hd"])
            playTheme = data_json["type1"]
            playType = data_json["type2"]
            playBg = data_json["type3"]
            page = data_json["page"]

            storePlays = TestStorePlayRepoInfo.objects.select_related().filter(store_id__store_id__exact=store_id)

            if (hd != 0):
                storePlays = storePlays.filter(play_id__play_headcount__exact=hd)

            if (len(title) != 0):
                storePlays = storePlays.filter(play_id__play_name__icontains=title)

            if (len(playTheme) != 0):
                storePlays = storePlays.filter(play_id__all_labels__label_type__exact=1 ,play_id__all_labels__label_content__icontains=playTheme)

            if (len(playType) != 0):
                storePlays = storePlays.filter(play_id__all_labels__label_type__exact=2 ,play_id__all_labels__label_content__icontains=playType)

            if (len(playBg) != 0):
                storePlays = storePlays.filter(play_id__all_labels__label_type__exact=3 ,play_id__all_labels__label_content__icontains=playBg)
            
            playResultsPage = Paginator(storePlays, 20)

            try:
                playsResponse = playResultsPage.page(page).object_list.values(
                                    'play_id__play_id', 
                                    'play_id__play_name', 
                                    'play_id__play_headcount', 
                                    'play_id__play_male_num', 
                                    'play_id__play_female_num',
                                    'play_id__play_score', 
                                    'play_id__play_intro', 
                                    'play_id__play_img',
                                    'play_id__play_antigender',
                                    'play_id__play_duration'
                                )
            except:
                playsResponse = []

            for i in range(0, len(playsResponse)):
                temp = playResultsPage.page(page).object_list[i].play_id.all_labels.values_list('label_content', flat=True)[:4]
                playsResponse[i]['play_labels'] = temp
                playsResponse[i]['play_id'] = playsResponse[i].pop('play_id__play_id')
                playsResponse[i]['play_name'] = playsResponse[i].pop('play_id__play_name')
                playsResponse[i]['play_headcount'] = playsResponse[i].pop('play_id__play_headcount')
                playsResponse[i]['play_male_num'] = playsResponse[i].pop('play_id__play_male_num')
                playsResponse[i]['play_female_num'] = playsResponse[i].pop('play_id__play_female_num')
                playsResponse[i]['play_score'] = playsResponse[i].pop('play_id__play_score')
                playsResponse[i]['play_intro'] = playsResponse[i].pop('play_id__play_intro')
                playsResponse[i]['play_img'] = playsResponse[i].pop('play_id__play_img')
                playsResponse[i]['play_antigender'] = playsResponse[i].pop('play_id__play_antigender')
                playsResponse[i]['play_duration'] = playsResponse[i].pop('play_id__play_duration')
            #playsResponse['play_labels'] = labelList
            return JSONResponse(playsResponse)
            

        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestStoreDeleteAPI(APIView):
    def get(self, request):
        data_json = request.GET
        user_id = data_json["adminId"]
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        play_id = data_json["play_id"]
        store_id = data_json["store_id"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            user = TestAdminInfo.objects.select_related().get(admin_id=user_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((appId == const.ownerapp_appid) & (user.admin_last3rdSession == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            deletePlay = TestStorePlayRepoInfo.objects.select_related().filter(store_id__store_id__exact=store_id, play_id__play_id=play_id)
            if (deletePlay[0].play_id.play_is_original == 0):
                result = deletePlay[0].play_id.delete()
            else:
                result = deletePlay.delete()
            return JSONResponse({"code":1, "data":result})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestStoreAddAPI(APIView):
    def get(self, request):
        data_json = request.GET
        user_id = data_json["adminId"]
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        play_id = data_json["play_id"]
        store_id = data_json["store_id"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            user = TestAdminInfo.objects.select_related().get(admin_id=user_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        
        if ((appId == const.ownerapp_appid) & (user.admin_last3rdSession == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            checkRepeat = TestStorePlayRepoInfo.objects.select_related().filter(play_id__play_id__exact=play_id, store_id__store_id__exact=store_id)
            if (len(checkRepeat) == 0):
                newItem = TestStorePlayRepoInfo()
                newItem.store_id = TestStoreInfo.objects.get(store_id = store_id)
                newItem.play_id = TestPlayInfo.objects.get(play_id = play_id)
                newItem.save()
                newSessionId = secrets.token_urlsafe(16)
                user.admin_last3rdSession = newSessionId
                user.save()
                return JSONResponse({"code":1, "data":{"sessionId": newSessionId}})
            else:
                return JSONResponse({"code":2, "data":"play has been at store repo"})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestStoreAdminInfoAPI(APIView):
    def get(self, request):
        data_json = request.GET
        user_id = data_json["adminId"]
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        store_id = data_json["store_id"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            user = TestAdminInfo.objects.select_related().get(admin_id=user_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        
        if ((appId == const.ownerapp_appid) & (user.admin_last3rdSession == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            adminSet = TestAdminStoreInfo.objects.select_related().filter(store_id__store_id__exact = store_id)
            adminSet = adminSet.values(
                'adminStore_id',
                'adminStore_phone',
                'admin_id__admin_nickName',
                'adminStore_verify',
                'adminStore_permission'
            )

            storeInfo = TestStoreInfo.objects.get(store_id = store_id)

            storeInfo = {
                "store_id": storeInfo.store_id,
                "store_name": storeInfo.store_name,
                "store_logo": storeInfo.store_pic,
                "store_status": storeInfo.store_status,
                "store_info": storeInfo.store_info,
                "store_deposit": storeInfo.store_deposit,
                "store_position": storeInfo.store_position,
                "store_address": storeInfo.store_address,
                "store_latitude": storeInfo.store_latitude,
                "store_longitude": storeInfo.store_longitude,
                "store_tel1": storeInfo.store_tel,
                "store_tel2": storeInfo.store_tel2
            }

            for i in range(0, len(adminSet)):
                adminSet[i]['admin_nickName'] = adminSet[i].pop('admin_id__admin_nickName')

            return JSONResponse({"code":1, "data": {"adminList": adminSet, "storeInfo": storeInfo}})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestUploadPlayAPI(APIView):
    def post(self, request):
        data_json = json.loads(request.body)
        admin_id = data_json["adminId"]
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (data_json['token'] >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            user = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((appId == const.ownerapp_appid) & (user.admin_last3rdSession == sessionId) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            playInfo = data_json["play_info"]
            store_id = data_json["store_id"]
            playPrice = data_json["price"]
            serverPlay = TestPlayInfo.objects.select_related().get(play_id = playInfo['play_id'])
            if (serverPlay.play_is_original == 1):
                # 修改原创剧本，则新建一个剧本, 别忘了最后处理labels
                newPlay = TestPlayInfo()
                newPlay.play_name = playInfo['play_name']
                newPlay.play_headcount = playInfo['play_headcount']
                newPlay.play_male_num = playInfo['play_male_num']
                newPlay.play_female_num = playInfo['play_female_num']
                newPlay.play_score = playInfo['play_score']
                newPlay.play_intro = playInfo['play_intro']
                newPlay.play_img = playInfo['play_img']
                newPlay.play_is_original = 0
                newPlay.play_duration = playInfo['play_duration']
                newPlay.play_antigender = playInfo['play_antigender']
                newPlay.save()

                playItem = TestStorePlayRepoInfo.objects.select_related().filter(store_id__store_id__exact=store_id, play_id__play_id__exact=playInfo['play_id'])
                playItem[0].item_id = playItem[0].item_id
                playItem = TestStorePlayRepoInfo.objects.get(item_id = playItem[0].item_id)
                playItem.play_id = newPlay
                #playItem[0].store_id = playItem[0].store_id
                playItem.item_price = playPrice
                playItem.save()

                playLabels = TestLabelInfo.objects.select_related().filter(play_id__play_id__exact=playInfo['play_id'])
                for idx in range(0, len(playLabels)):
                    newLabel = TestLabelInfo()
                    newLabel.label_type = playLabels[idx].label_type
                    newLabel.label_content = playLabels[idx].label_content
                    newLabel.play_id = newPlay
                    newLabel.save()

                playResponse = {}

                playResponse['play_id'] = newPlay.play_id
                playResponse['play_name'] = newPlay.play_name
                playResponse['play_headcount'] = newPlay.play_headcount
                playResponse['play_male_num'] = newPlay.play_male_num
                playResponse['play_female_num'] = newPlay.play_female_num
                playResponse['play_score'] = newPlay.play_score
                playResponse['play_intro'] = newPlay.play_intro
                playResponse['play_img'] = newPlay.play_img
                playResponse['play_antigender'] = newPlay.play_antigender
                playResponse['play_duration'] = newPlay.play_duration
                playResponse['play_labels'] = playInfo['play_labels']

                return JSONResponse({"code":1, "data": playResponse})
            else:
                serverPlay.play_name = playInfo['play_name']
                serverPlay.play_headcount = playInfo['play_headcount']
                serverPlay.play_male_num = playInfo['play_male_num']
                serverPlay.play_female_num = playInfo['play_female_num']
                serverPlay.play_score = playInfo['play_score']
                serverPlay.play_intro = playInfo['play_intro']
                serverPlay.play_img = playInfo['play_img']
                serverPlay.play_is_original = 0
                serverPlay.play_duration = playInfo['play_duration']
                serverPlay.play_antigender = playInfo['play_antigender']
                serverPlay.save()

                playItem = TestStorePlayRepoInfo.objects.select_related().filter(store_id__store_id__exact=store_id, play_id__play_id__exact=playInfo['play_id'])
                playItem[0].play_id = serverPlay
                playItem[0].item_price = playPrice
                playItem[0].save()

                playResponse = {}

                playResponse['play_id'] = serverPlay.play_id
                playResponse['play_name'] = serverPlay.play_name
                playResponse['play_headcount'] = serverPlay.play_headcount
                playResponse['play_male_num'] = serverPlay.play_male_num
                playResponse['play_female_num'] = serverPlay.play_female_num
                playResponse['play_score'] = serverPlay.play_score
                playResponse['play_intro'] = serverPlay.play_intro
                playResponse['play_img'] = serverPlay.play_img
                playResponse['play_antigender'] = serverPlay.play_antigender
                playResponse['play_duration'] = serverPlay.play_duration
                playResponse['play_labels'] = playInfo['play_labels']

                return JSONResponse({"code":1, "data": playResponse})
        else :
            return JSONResponse({"code":0, "data":"certification failed"})

class TestUploadPlayWithImgAPI(APIView):
    def post(self, request):
        IMG_ROOT = settings.MEDIA_ROOT
        body = request.POST

        play_id = int(body['play_id'])
        play_name = body['play_name']
        play_headcount = body['play_headcount']
        play_male_num = body['play_male_num']
        play_female_num = body['play_female_num']
        play_score = body['play_score']
        play_intro = body['play_intro']
        play_duration = body['play_duration']
        play_antigender = body['play_antigender']
        play_labels = body['play_labels']

        store_id = body["store_id"]
        playPrice = body["price"]

        admin_id = int(body["adminId"])
        sessionId = body['sessionId']
        appId = body["appId"]
        timestamp = (int(body['token']) >> 1) - 1000
        serverTimeStamp = time.time()
        
        try:
            admin = TestAdminInfo.objects.get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"user id error"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            admin.admin_last3rdSession = secrets.token_urlsafe(16)
            admin.save()
            img = request.FILES['file'].read()
            img_md5 = hashlib.md5(img).hexdigest()
            img_original_md5 = body["imgMD5"]
            if (img_md5 == img_original_md5) :
                path = os.path.join(IMG_ROOT, 'customPlayPic',request.FILES['file'].name)
                with open(path, "wb") as f:
                    f.write(img)
                try:
                    serverPlay = TestPlayInfo.objects.select_related().get(play_id = play_id)
                except:
                    newPlay = TestPlayInfo()
                    newPlay.play_name = play_name
                    newPlay.play_headcount = play_headcount
                    newPlay.play_male_num = play_male_num
                    newPlay.play_female_num = play_female_num
                    newPlay.play_score = play_score
                    newPlay.play_intro = play_intro
                    newPlay.play_img = os.path.join('/media', 'customPlayPic',request.FILES['file'].name)
                    newPlay.play_is_original = 0
                    newPlay.play_duration = play_duration
                    newPlay.play_antigender = play_antigender
                    newPlay.save()

                    playItem = TestStorePlayRepoInfo()
                    playItem.play_id = newPlay
                    playItem.item_price = playPrice
                    playItem.store_id_id = store_id
                    playItem.save()

                    newLabel = TestLabelInfo()
                    newLabel.label_type = 1
                    newLabel.label_content = '其他'
                    newLabel.play_id = newPlay
                    newLabel.save()

                    playResponse = {}

                    playResponse['play_id'] = newPlay.play_id
                    playResponse['play_name'] = newPlay.play_name
                    playResponse['play_headcount'] = newPlay.play_headcount
                    playResponse['play_male_num'] = newPlay.play_male_num
                    playResponse['play_female_num'] = newPlay.play_female_num
                    playResponse['play_score'] = newPlay.play_score
                    playResponse['play_intro'] = newPlay.play_intro
                    playResponse['play_img'] = newPlay.play_img
                    playResponse['play_antigender'] = newPlay.play_antigender
                    playResponse['play_duration'] = newPlay.play_duration
                    playResponse['play_labels'] = ['其他']

                    return JSONResponse({"code":1, "data": {"sessionId": admin.admin_last3rdSession, "playInfo": playResponse}})

                if (serverPlay.play_is_original == 1) :
                    newPlay = TestPlayInfo()
                    newPlay.play_name = play_name
                    newPlay.play_headcount = play_headcount
                    newPlay.play_male_num = play_male_num
                    newPlay.play_female_num = play_female_num
                    newPlay.play_score = play_score
                    newPlay.play_intro = play_intro
                    newPlay.play_img = os.path.join('/media', 'customPlayPic',request.FILES['file'].name)
                    newPlay.play_is_original = 0
                    newPlay.play_duration = play_duration
                    newPlay.play_antigender = play_antigender
                    newPlay.save()

                    playItem = TestStorePlayRepoInfo.objects.select_related().filter(store_id__store_id__exact=store_id, play_id__play_id__exact=play_id)
                    playItem[0].item_id = playItem[0].item_id
                    playItem = TestStorePlayRepoInfo.objects.get(item_id = playItem[0].item_id)
                    playItem.play_id = newPlay
                    #playItem[0].store_id = playItem[0].store_id
                    playItem.item_price = playPrice
                    playItem.save()

                    playLabels = TestLabelInfo.objects.select_related().filter(play_id__play_id__exact=play_id)
                    for idx in range(0, len(playLabels)):
                        newLabel = TestLabelInfo()
                        newLabel.label_type = playLabels[idx].label_type
                        newLabel.label_content = playLabels[idx].label_content
                        newLabel.play_id = newPlay
                        newLabel.save()

                    playResponse = {}

                    playResponse['play_id'] = newPlay.play_id
                    playResponse['play_name'] = newPlay.play_name
                    playResponse['play_headcount'] = newPlay.play_headcount
                    playResponse['play_male_num'] = newPlay.play_male_num
                    playResponse['play_female_num'] = newPlay.play_female_num
                    playResponse['play_score'] = newPlay.play_score
                    playResponse['play_intro'] = newPlay.play_intro
                    playResponse['play_img'] = newPlay.play_img
                    playResponse['play_antigender'] = newPlay.play_antigender
                    playResponse['play_duration'] = newPlay.play_duration
                    playResponse['play_labels'] = playLabels.values_list('label_content', flat=True)

                    return JSONResponse({"code":1, "data": {"sessionId": admin.admin_last3rdSession, "playInfo": playResponse}})

                else :
                    serverPlay.play_name = play_name
                    serverPlay.play_headcount = play_headcount
                    serverPlay.play_male_num = play_male_num
                    serverPlay.play_female_num = play_female_num
                    serverPlay.play_score = play_score
                    serverPlay.play_intro = play_intro
                    serverPlay.play_img = os.path.join('/media', 'customPlayPic',request.FILES['file'].name)
                    serverPlay.play_is_original = 0
                    serverPlay.play_duration = play_duration
                    serverPlay.play_antigender = play_antigender
                    serverPlay.save()

                    playItem = TestStorePlayRepoInfo.objects.select_related().filter(store_id__store_id__exact=store_id, play_id__play_id__exact=play_id)
                    playItem[0].play_id = serverPlay
                    playItem[0].item_price = playPrice
                    playItem[0].save()

                    playResponse = {}

                    playResponse['play_id'] = serverPlay.play_id
                    playResponse['play_name'] = serverPlay.play_name
                    playResponse['play_headcount'] = serverPlay.play_headcount
                    playResponse['play_male_num'] = serverPlay.play_male_num
                    playResponse['play_female_num'] = serverPlay.play_female_num
                    playResponse['play_score'] = serverPlay.play_score
                    playResponse['play_intro'] = serverPlay.play_intro
                    playResponse['play_img'] = serverPlay.play_img
                    playResponse['play_antigender'] = serverPlay.play_antigender
                    playResponse['play_duration'] = serverPlay.play_duration
                    playResponse['play_labels'] = play_labels

                    return JSONResponse({"code":1, "data": {"sessionId": admin.admin_last3rdSession, "playInfo": playResponse}})
                
                
            else:
                return JSONResponse({"code":0, "data":"File MD5 checks error", "md51": img_original_md5, "md52": img_md5})
        else:
            return JSONResponse({"code":0, "data":"Login out"})

class TestSaveStoreWithImgAPI(APIView):
    def post(self, request):
        IMG_ROOT = settings.MEDIA_ROOT
        body = request.POST

        store_id = body['store_id']
        store_name = body['store_name']
        store_position = body['store_position']
        store_address = body['store_address']
        store_latitude = body['store_latitude']
        store_longitude = body['store_longitude']
        store_tel = body['store_tel']
        store_tel2 = body['store_tel2']

        admin_id = int(body["adminId"])
        sessionId = body['sessionId']
        appId = body["appId"]
        timestamp = (int(body['token']) >> 1) - 1000
        serverTimeStamp = time.time()
        
        try:
            admin = TestAdminInfo.objects.get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"user id error"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            admin.admin_last3rdSession = secrets.token_urlsafe(16)
            admin.save()
            img = request.FILES['file'].read()
            img_md5 = hashlib.md5(img).hexdigest()
            img_original_md5 = body["imgMD5"]
            if (img_md5 == img_original_md5) :
                path = os.path.join(IMG_ROOT, 'storePic',request.FILES['file'].name)
                with open(path, "wb") as f:
                    f.write(img)
                
                storeInfo = TestStoreInfo.objects.get(store_id = store_id)
                storeInfo.store_name = store_name
                storeInfo.store_position = store_position
                storeInfo.store_address = store_address
                storeInfo.store_latitude = store_latitude
                storeInfo.store_longitude = store_longitude
                storeInfo.store_tel = store_tel
                storeInfo.store_tel2 = store_tel2
                storeInfo.store_pic = os.path.join('/media', 'storePic',request.FILES['file'].name)
                storeInfo.save()
                
                out_data = {
                    "store_id": storeInfo.store_id,
                    "store_name": storeInfo.store_name,
                    "store_logo": storeInfo.store_pic,
                    "store_status": storeInfo.store_status,
                    "store_info": storeInfo.store_info,
                    "store_deposit": storeInfo.store_deposit,
                    "store_position": storeInfo.store_position,
                    "store_address": storeInfo.store_address,
                    "store_latitude": storeInfo.store_latitude,
                    "store_longitude": storeInfo.store_longitude,
                    "store_tel1": storeInfo.store_tel,
                    "store_tel2": storeInfo.store_tel2
                }
                
                
                return JSONResponse({"code":1, "data":{"sessionId": admin.admin_last3rdSession, "storeInfo": out_data}})
            else:
                return JSONResponse({"code":0, "data":"File MD5 checks error", "md51": img_original_md5, "md52": img_md5})
        else:
            return JSONResponse({"code":0, "data":"Login out"})

class TestSaveStoreWithoutImgAPI(APIView):
    def post(self, request):
        data_json = json.loads(request.body)

        store_id = data_json['store_id']
        store_name = data_json['store_name']
        store_position = data_json['store_position']
        store_address = data_json['store_address']
        store_latitude = data_json['store_latitude']
        store_longitude = data_json['store_longitude']
        store_tel = data_json['store_tel']
        store_tel2 = data_json['store_tel2']

        admin_id = int(data_json["adminId"])
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json['token']) >> 1) - 1000
        serverTimeStamp = time.time()
        
        try:
            admin = TestAdminInfo.objects.get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"user id error"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            admin.admin_last3rdSession = secrets.token_urlsafe(16)
            admin.save()
            storeInfo = TestStoreInfo.objects.get(store_id = store_id)
            storeInfo.store_name = store_name
            storeInfo.store_position = store_position
            storeInfo.store_address = store_address
            storeInfo.store_latitude = store_latitude
            storeInfo.store_longitude = store_longitude
            storeInfo.store_tel = store_tel
            storeInfo.store_tel2 = store_tel2
            storeInfo.save()
            
            out_data = {
                "store_id": storeInfo.store_id,
                "store_name": storeInfo.store_name,
                "store_logo": storeInfo.store_pic,
                "store_status": storeInfo.store_status,
                "store_info": storeInfo.store_info,
                "store_deposit": storeInfo.store_deposit,
                "store_position": storeInfo.store_position,
                "store_address": storeInfo.store_address,
                "store_latitude": storeInfo.store_latitude,
                "store_longitude": storeInfo.store_longitude,
                "store_tel1": storeInfo.store_tel,
                "store_tel2": storeInfo.store_tel2
            }

            return JSONResponse({"code":1, "data":{"sessionId": admin.admin_last3rdSession, "storeInfo": out_data}})
        else:
            return JSONResponse({"code":0, "data":"Login out"})

class TestGetStoreListAPI(APIView):
    def get(self, request):
        data_json = request.GET
        admin_id = data_json["adminId"]
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        phone = data_json["phone"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            storeList = TestAdminStoreInfo.objects.select_related().filter(adminStore_phone__exact = phone).values(
                'adminStore_id', 
                'adminStore_verify',
                'adminStore_permission', 
                'store_id__store_id',
                'store_id__store_name',
                'store_id__store_pic',
                'store_id__store_status',
                'store_id__store_info',
                'store_id__store_deposit',
                'store_id__store_position',
                'store_id__store_address',
                'store_id__store_latitude',
                'store_id__store_longitude',
                'store_id__store_tel',
                'store_id__store_tel2',
                'admin_id__admin_id'
            )

            storeSet = [];

            for i in range(0, len(storeList)):
                storeList[i]['admin_id'] = storeList[i].pop('admin_id__admin_id')
                if ( (storeList[i]['admin_id'] == int(admin_id)) or (storeList[i]['admin_id'] == 1)):
                    storeList[i]['store_id'] = storeList[i].pop('store_id__store_id')
                    storeList[i]['store_name'] = storeList[i].pop('store_id__store_name')
                    storeList[i]['store_logo'] = storeList[i].pop('store_id__store_pic')
                    storeList[i]['store_status'] = storeList[i].pop('store_id__store_status')
                    storeList[i]['store_info'] = storeList[i].pop('store_id__store_info')
                    storeList[i]['store_deposit'] = storeList[i].pop('store_id__store_deposit')
                    storeList[i]['store_position'] = storeList[i].pop('store_id__store_position')
                    storeList[i]['store_address'] = storeList[i].pop('store_id__store_address')
                    storeList[i]['store_latitude'] = storeList[i].pop('store_id__store_latitude')
                    storeList[i]['store_longitude'] = storeList[i].pop('store_id__store_longitude')
                    storeList[i]['store_tel1'] = storeList[i].pop('store_id__store_tel')
                    storeList[i]['store_tel2'] = storeList[i].pop('store_id__store_tel2')
                    storeSet.append(storeList[i])

            return JSONResponse({"code":0, "data":storeSet})
        else: 
            return JSONResponse({"code":0, "data":"certification failed"})

class TestVerifyStoreAPI(APIView):
    def get(self, request):
        data_json = request.GET
        admin_id = data_json["adminId"]
        sessionId = data_json['sessionId']
        adminStore_id = data_json['adminStore_id']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            adminStoreInfo = TestAdminStoreInfo.objects.get(adminStore_id=adminStore_id)
            adminStoreInfo.admin_id = admin
            adminStoreInfo.adminStore_verify = 1
            adminStoreInfo.save()
            return JSONResponse({"code":1, "data":"verified"})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestShareStoreAPI(APIView):
    def get(self, request):
        data_json = request.GET
        admin_id = data_json["adminId"]
        sessionId = data_json['sessionId']
        store_id = data_json['store_id']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            payload ={
            'grant_type': 'client_credential',
            'appid': const.weapp_appid,
            'secret': const.weapp_secret
            }
            getAccessToken = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=payload)
            access_token = getAccessToken.json()['access_token']

            data = {"path":"pages/StoreInfo/StoreInfo?storeId="+store_id}
            data = json.dumps(data)
            bufferData = requests.post('https://api.weixin.qq.com/wxa/getwxacode?access_token='+access_token, data)
            img = bufferData.content

            #PIL 图像处理

            theStore = TestStoreInfo.objects.select_related().get(store_id=int(store_id))

            store_img = Image.open('/home/pzz_data/wwwroot/pzz_web'+theStore.store_pic)
            store_img = store_img.resize((200, 200),Image.ANTIALIAS)
            store_img = store_img.convert('RGBA')

            IMG_ROOT = settings.MEDIA_ROOT
            temp_path = os.path.join(IMG_ROOT, 'storeQRcode', 'temp_store_id_'+store_id+'.png')
            path = os.path.join(IMG_ROOT, 'storeQRcode', 'store_id_'+store_id+'.png')
            with open(path, "wb") as f:
                f.write(img)
            
            img = Image.open(path)
            draw = ImageDraw.Draw(img)
            draw.ellipse((115, 115, 315, 315), fill=(255,255,255,255))
            img = img.convert("RGBA")
            
            alpha_layer = Image.new('L', (200, 200), 0)
            draw = ImageDraw.Draw(alpha_layer)
            draw.ellipse((0, 0, 200, 200), fill=255)

            #img = np.array(img)
            #img[115:315, 115:315] = npImage

            #Image.fromarray(img).save(path)

            img.paste(store_img, (115,115), alpha_layer)
            img.save(path)

            return JSONResponse({"code":1, "data":'/media/storeQRcode/store_id_'+store_id+'.png'})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestAddAdminAPI(APIView):
    def get(self, request):
        data_json = request.GET
        admin_id = data_json["adminId"]
        store_id = data_json['store_id']
        phone = data_json['phone']
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            ownerAdminStoreInfo = TestAdminStoreInfo.objects.filter(admin_id__admin_id__exact=admin_id, store_id__store_id__exact=store_id, adminStore_permission__exact=1)
            if (len(ownerAdminStoreInfo) == 0):
                return JSONResponse({"code":0, "data":"admin does not have the permission"})
            else:
                newAdmin = TestAdminStoreInfo()
                newAdmin.store_id_id = store_id
                newAdmin.admin_id_id = 1
                newAdmin.adminStore_phone = phone
                newAdmin.adminStore_permission = 0
                newAdmin.save()
                return JSONResponse({"code":1, "data":"admin has been added"})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestDeleteAdminAPI(APIView):
    def get(self, request):
        data_json = request.GET
        admin_id = data_json["adminId"]
        store_id = data_json['store_id']
        adminStore_id = data_json['adminStore_id']
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            ownerAdminStoreInfo = TestAdminStoreInfo.objects.filter(admin_id__admin_id__exact=admin_id, store_id__store_id__exact=store_id, adminStore_permission__exact=1)
            if (len(ownerAdminStoreInfo) == 0):
                return JSONResponse({"code":0, "data":"admin does not have the permission"})
            else:
                adminStore = TestAdminStoreInfo.objects.select_related().get(adminStore_id=adminStore_id)
                if (adminStore.store_id.store_id == int(store_id)):
                    adminStore.delete()
                    return JSONResponse({"code":1, "data":"admin has been deleted"})
                else:
                    return JSONResponse({"code":0, "data":"storeId error"})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestStoreQueueListAPI(APIView):
    def get_object(self, ModelName, pk):
        try:
            return ModelName.objects.get(pk=pk)
        except ModelName.DoesNotExist:
            self.code=0
            self.data={}
            self.output = {"code":self.code, 
                "queue_num": [],
                "queue_date":[],
                "queue_data":[]
                }
            return JSONResponse(self.output)

    def get(self, request, store_id, format=None):
        store_info = self.get_object(TestStoreInfo, store_id)
        try:
            test = store_info.store_id
        except:
            return store_info
        todayDate = date.today()
        queues_info = store_info.all_queues.select_related().filter(queue_end_time__gte=todayDate, queue_status__exact=0).order_by('queue_end_time')
        queues_length = len(queues_info)
        '''
        New 每日局数统计
        '''
        self.queue_num = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for i in range(1,15):
            today_queues = queues_info.filter(queue_end_time__gte=todayDate+timedelta(days=i-1), queue_end_time__lt=todayDate+timedelta(days=i))
            self.queue_num[i-1] = len(today_queues)

        '''
        New 队列剧本信息输出
        '''
        self.queue_data = []
        self.play_data = []
        queuePlayInfo = queues_info.values(
            'queue_id',
            'queue_status',
            'queue_end_time',
            'queue_current_num',
            'queue_current_male_num',
            'queue_current_female_num',
            'queue_allow_antigender',
            'play_id__play_id',
            'play_id__play_name',
            'play_id__play_headcount',
            'play_id__play_male_num',
            'play_id__play_female_num',
            'play_id__play_score',
            'play_id__play_intro',
            'play_id__play_duration',
            'play_id__play_img',
            'play_id__play_antigender'
        )

        for i in range(0, len(queues_info)):
            playLabelList = queues_info[i].play_id.all_labels.values_list('label_content', flat=True)[:4]
            queue_data = {}
            queue_data['queue_id'] = queuePlayInfo[i]['queue_id']
            queue_data['queue_status'] = queuePlayInfo[i]['queue_status']
            queue_data['queue_end_time'] = queuePlayInfo[i]['queue_end_time']
            queue_data['queue_current_num'] = queuePlayInfo[i]['queue_current_num']
            queue_data['queue_current_male_num'] = queuePlayInfo[i]['queue_current_male_num']
            queue_data['queue_current_female_num'] = queuePlayInfo[i]['queue_current_female_num']
            queue_data['queue_allow_antigender'] = queuePlayInfo[i]['queue_allow_antigender']
            queue_data['play_id'] = queuePlayInfo[i]['play_id__play_id']
            play_data = {}
            play_data['play_id'] = queuePlayInfo[i]['play_id__play_id']
            play_data['play_name'] = queuePlayInfo[i]['play_id__play_name']
            play_data['play_headcount'] = queuePlayInfo[i]['play_id__play_headcount']
            play_data['play_male_num'] = queuePlayInfo[i]['play_id__play_male_num']
            play_data['play_female_num'] = queuePlayInfo[i]['play_id__play_female_num']
            play_data['play_score'] = queuePlayInfo[i]['play_id__play_score']
            play_data['play_intro'] = queuePlayInfo[i]['play_id__play_intro']
            play_data['play_duration'] = queuePlayInfo[i]['play_id__play_duration']
            play_data['play_img'] = queuePlayInfo[i]['play_id__play_img']
            play_data['play_antigender'] = queuePlayInfo[i]['play_id__play_antigender']
            play_data['play_labels'] = playLabelList
            self.queue_data.append(queue_data)
            self.play_data.append(play_data)

        self.code = 1
        return JSONResponse({"code":self.code, "data": {"queue_num":self.queue_num, "queue_data":self.queue_data, "play_data":self.play_data}})

class TestStoreLockedQueueListAPI(APIView):
    def get_object(self, ModelName, pk):
        try:
            return ModelName.objects.get(pk=pk)
        except ModelName.DoesNotExist:
            self.code=0
            self.data={}
            self.output = {"code":self.code, 
                "queue_num": [],
                "queue_date":[],
                "queue_data":[]
                }
            return JSONResponse(self.output)

    def get(self, request, store_id, format=None):
        store_info = self.get_object(TestStoreInfo, store_id)
        try:
            test = store_info.store_id
        except:
            return store_info
        data_json = request.GET
        showDays = int(data_json["showDays"])
        todayDate = date.today()

        if (showDays == 0):
            
            queues_info = store_info.all_queues.select_related().filter(queue_status__exact=1).order_by('-queue_end_time')
        else:

            queues_info = store_info.all_queues.select_related().filter(queue_end_time__gte=todayDate, queue_end_time__lt=todayDate+timedelta(days=showDays),queue_status__exact=1).order_by('-queue_end_time')

        '''
        New 队列剧本信息输出
        '''
        self.queue_data = []
        self.play_data = []
        queuePlayInfo = queues_info.values(
            'queue_id',
            'queue_status',
            'queue_end_time',
            'queue_current_num',
            'queue_current_male_num',
            'queue_current_female_num',
            'queue_allow_antigender',
            'play_id__play_id',
            'play_id__play_name',
            'play_id__play_headcount',
            'play_id__play_male_num',
            'play_id__play_female_num',
            'play_id__play_score',
            'play_id__play_intro',
            'play_id__play_duration',
            'play_id__play_img',
            'play_id__play_antigender'
        )

        for i in range(0, len(queues_info)):
            playLabelList = queues_info[i].play_id.all_labels.values_list('label_content', flat=True)[:4]
            queue_data = {}
            queue_data['queue_id'] = queuePlayInfo[i]['queue_id']
            queue_data['queue_status'] = queuePlayInfo[i]['queue_status']
            queue_data['queue_end_time'] = queuePlayInfo[i]['queue_end_time']
            queue_data['queue_current_num'] = queuePlayInfo[i]['queue_current_num']
            queue_data['queue_current_male_num'] = queuePlayInfo[i]['queue_current_male_num']
            queue_data['queue_current_female_num'] = queuePlayInfo[i]['queue_current_female_num']
            queue_data['queue_allow_antigender'] = queuePlayInfo[i]['queue_allow_antigender']
            queue_data['play_id'] = queuePlayInfo[i]['play_id__play_id']
            play_data = {}
            play_data['play_id'] = queuePlayInfo[i]['play_id__play_id']
            play_data['play_name'] = queuePlayInfo[i]['play_id__play_name']
            play_data['play_headcount'] = queuePlayInfo[i]['play_id__play_headcount']
            play_data['play_male_num'] = queuePlayInfo[i]['play_id__play_male_num']
            play_data['play_female_num'] = queuePlayInfo[i]['play_id__play_female_num']
            play_data['play_score'] = queuePlayInfo[i]['play_id__play_score']
            play_data['play_intro'] = queuePlayInfo[i]['play_id__play_intro']
            play_data['play_duration'] = queuePlayInfo[i]['play_id__play_duration']
            play_data['play_img'] = queuePlayInfo[i]['play_id__play_img']
            play_data['play_antigender'] = queuePlayInfo[i]['play_id__play_antigender']
            play_data['play_labels'] = playLabelList
            self.queue_data.append(queue_data)
            self.play_data.append(play_data)

        self.code = 1
        return JSONResponse({"code":self.code, "data": {"queue_data":self.queue_data, "play_data":self.play_data}})

class TestLockQueueAPI(APIView):
    def get(self, request):
        data_json = request.GET
        admin_id = data_json["adminId"]
        store_id = data_json['store_id']
        queue_id = data_json['queue_id']
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            queueInfo = TestQueueInfo.objects.select_related().filter(queue_id__exact=queue_id)
            adminStore = TestAdminStoreInfo.objects.select_related().filter(admin_id__admin_id__exact=admin_id, store_id__store_id__exact=store_id)
            if (len(queueInfo)==1):
                if (len(adminStore) != 0):
                    queueInfo = queueInfo[0]
                    if(queueInfo.store_id_id == int(store_id)):
                        queueInfo.queue_status = 1
                        queueInfo.save()
                        return JSONResponse({"code":1, "data":"lock the queue"})
                    else:
                        return JSONResponse({"code":0, "data":"storeId error"})
                else:
                    return JSONResponse({"code":0, "data":"storeId adminId matching error"})
            else:
                return JSONResponse({"code":0, "data":"queueId error"})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestDelockQueueAPI(APIView):
    def get(self, request):
        data_json = request.GET
        admin_id = data_json["adminId"]
        store_id = data_json['store_id']
        queue_id = data_json['queue_id']
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            queueInfo = TestQueueInfo.objects.select_related().filter(queue_id__exact=queue_id)
            adminStore = TestAdminStoreInfo.objects.select_related().filter(admin_id__admin_id__exact=admin_id, store_id__store_id__exact=store_id)
            if (len(queueInfo)==1):
                if (len(adminStore) != 0):
                    queueInfo = queueInfo[0]
                    if(queueInfo.store_id_id == int(store_id)):
                        queueInfo.queue_status = 0
                        queueInfo.save()
                        return JSONResponse({"code":1, "data":"lock the queue"})
                    else:
                        return JSONResponse({"code":0, "data":"storeId error"})
                else:
                    return JSONResponse({"code":0, "data":"storeId adminId matching error"})
            else:
                return JSONResponse({"code":0, "data":"queueId error"})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestDeleteQueueAPI(APIView):
    def get(self, request):
        data_json = request.GET
        admin_id = data_json["adminId"]
        store_id = data_json['store_id']
        queue_id = data_json['queue_id']
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            queueInfo = TestQueueInfo.objects.select_related().filter(queue_id__exact=queue_id)
            adminStore = TestAdminStoreInfo.objects.select_related().filter(admin_id__admin_id__exact=admin_id, store_id__store_id__exact=store_id)
            if (len(queueInfo)==1):
                if (len(adminStore) != 0):
                    queueInfo = queueInfo[0]
                    if(queueInfo.store_id_id == int(store_id)):
                        queueInfo.delete()
                        return JSONResponse({"code":1, "data":"lock the queue"})
                    else:
                        return JSONResponse({"code":0, "data":"storeId error"})
                else:
                    return JSONResponse({"code":0, "data":"storeId adminId matching error"})
            else:
                return JSONResponse({"code":0, "data":"queueId error"})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestAdminQueuePlayerListAPI(APIView):
    def get(self, request):
        data_json = request.GET
        admin_id = data_json["adminId"]
        queue_id = data_json['queue_id']
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            playerList = TestPlayerInfo.objects.select_related().filter(queue_id__queue_id__exact=queue_id).values(
                'player_id',
                'player_pic',
                'player_name',
                'player_gender', 
                'player_tel'
            )
            return JSONResponse({"code":1, "data":playerList})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestAdminQueueAddPlayerAPI(APIView):
    def get(self, request):
        data_json = request.GET
        totalNum = int(data_json['totalNum'])
        maleNum = int(data_json['maleNum'])
        femaleNum = int(data_json['femaleNum'])
        admin_id = data_json['adminId']
        queue_id = data_json['queue_id']
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            theQueue = TestQueueInfo.objects.select_related().filter(queue_id__exact=queue_id)
            if (len(theQueue) == 0):
                return JSONResponse({"code":0, "data":"queueId is wrong"})
            else:
                theQueue = theQueue[0]
                if (theQueue.play_id.play_male_num == 999 or theQueue.play_id.play_female_num == 999):
                    theQueue.queue_current_num = theQueue.queue_current_num + totalNum
                    theQueue.save()

                    for i in range(0, totalNum):
                        newPlayer = TestPlayerInfo()
                        newPlayer.player_name = '到店玩家'
                        newPlayer.player_gender = 3
                        newPlayer.player_pic = 'https://api.ecou.com.cn/media/member.png'
                        newPlayer.player_tel = '到店玩家'
                        newPlayer.queue_id = theQueue
                        newPlayer.user_id_id = 1
                        newPlayer.save()
                else:
                    theQueue.queue_current_num = theQueue.queue_current_num + maleNum + femaleNum
                    theQueue.queue_current_male_num = theQueue.queue_current_male_num + maleNum
                    theQueue.queue_current_female_num = theQueue.queue_current_female_num + femaleNum
                    theQueue.save()

                    for i in range(0, maleNum):
                        newPlayer = TestPlayerInfo()
                        newPlayer.player_name = '到店玩家'
                        newPlayer.player_gender = 1
                        newPlayer.player_pic = 'https://api.ecou.com.cn/media/member.png'
                        newPlayer.player_tel = '到店玩家'
                        newPlayer.queue_id = theQueue
                        newPlayer.user_id_id = 1
                        newPlayer.save()

                    for i in range(0, femaleNum):
                        newPlayer = TestPlayerInfo()
                        newPlayer.player_name = '到店玩家'
                        newPlayer.player_gender = 0
                        newPlayer.player_pic = 'https://api.ecou.com.cn/media/member.png'
                        newPlayer.player_tel = '到店玩家'
                        newPlayer.queue_id = theQueue
                        newPlayer.user_id_id = 1
                        newPlayer.save()

                playerList = TestPlayerInfo.objects.select_related().filter(queue_id__queue_id__exact=queue_id).values(
                    'player_id',
                    'player_pic',
                    'player_name',
                    'player_gender', 
                    'player_tel'
                )
                return JSONResponse({"code":1, "data":playerList})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

class TestAdminQueuePopPlayerAPI(APIView):
    def get(self, request):
        data_json = request.GET
        player_id = int(data_json['player_id'])
        admin_id = data_json['adminId']
        queue_id = int(data_json['queue_id'])
        sessionId = data_json['sessionId']
        appId = data_json["appId"]
        timestamp = (int(data_json["token"]) >> 1) - 1000
        serverTimeStamp = time.time()
        try:
            admin = TestAdminInfo.objects.select_related().get(admin_id=admin_id)
        except:
            return JSONResponse({"code":0, "data":"adminId is wrong"})
        if ((admin.admin_last3rdSession == sessionId) & (appId == const.ownerapp_appid) & (serverTimeStamp - timestamp < 60) & (serverTimeStamp - timestamp > -5)):
            theQueue = TestQueueInfo.objects.select_related().filter(queue_id__exact=queue_id)
            if (len(theQueue) == 0):
                return JSONResponse({"code":0, "data":"queueId is wrong"})
            else:
                theQueue = theQueue[0]
                try:
                    thePlayer = TestPlayerInfo.objects.select_related().get(player_id=player_id)
                except:
                    return JSONResponse({"code":0, "data":"playerId is wrong"})
                if (thePlayer.queue_id_id == queue_id):
                    if (thePlayer.player_gender == 3):
                        theQueue.queue_current_num = theQueue.queue_current_num -1
                    elif (thePlayer.player_gender == 1):
                        theQueue.queue_current_num = theQueue.queue_current_num -1
                        theQueue.queue_current_male_num = theQueue.queue_current_male_num - 1
                    elif (thePlayer.player_gender == 0):
                        theQueue.queue_current_num = theQueue.queue_current_num -1
                        theQueue.queue_current_female_num = theQueue.queue_current_female_num - 1
                    thePlayer.delete()
                    theQueue.save()
                    playerList = TestPlayerInfo.objects.select_related().filter(queue_id__queue_id__exact=queue_id).values(
                        'player_id',
                        'player_pic',
                        'player_name',
                        'player_gender', 
                        'player_tel'
                    )
                    return JSONResponse({"code":1, "data":playerList})
                else:
                    return JSONResponse({"code":0, "data":"queueId matching error"})
        else:
            return JSONResponse({"code":0, "data":"certification failed"})

                        