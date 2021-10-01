# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 19:07:29 2021

@author: phc722
@author: akwrl
@author: 
"""

import xml.etree.ElementTree as ET
import requests
import re
import time 
import numpy as np
import threading as TH
import json
from flask import Flask, request as flask_req

app = Flask(__name__)

servicekey = "FiTKahy9SE4+5R5jgInCMRYC0ERbDNBIiWWCxIcsGlJV6UuXbFbVwCFzcusVJT856FWLCRKxvCJkrTy+LoF6jA=="

# 정류소고유번호를 입력받아 경유하는 노선목록을 조회한다.
api_url_1 = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid"
params_get = {"serviceKey":servicekey, "arsId":"06175"}

#승차벨 리스트
bus_reserved_list = []

# 여기에 승차벨 버스 정보 보내는 기능 추가하기
@app.route('/busdata/parking')
def parking_data():     #P1, P2 데이터 보내기
    #flask_req.get_data()
    print(bus_goatdochak_list)
    return json.dumps(bus_goatdochak_list)

# 승차벨 받아오기
@app.route('/busdata/call', methods=["GET"])
def buscall():
    global bus_reserved_list
    busid = flask_req.args.get('rtNm')
    print(busid)
    if (busid == None):
        return "NOQUERY"   # 쿼리문 없음
    print(f"list:: {list(map(lambda x:x[0], bus_goatdochak_list))}")
    if (busid in list(map(lambda x:x[0], bus_goatdochak_list))) and (busid not in bus_reserved_list):
        bus_reserved_list.append(busid)
        return "SUCCEED"    # 성공
    else:
        return "FAIL"   # 이미 승차벨에 존재하거나, 곧 도착하는 버스가 아닌 경우.

def deviceRun(): # api를 받아서 [노선명, 남은 시간, 노선 별 해당 버스 순서] 순서로 저장
    global api_url_1, params_get
    bus_list = [] 

    r = requests.get(api_url_1, params = params_get)
    if (r.status_code == 200): #정상적으로 응답했으면
        #print(r.text)
    
        root = ET.fromstring(r.text)
        body = root.find("msgBody")
        itemlists = body.findall("itemList")
        
        for i in itemlists:
            number = i.findtext("rtNm")
            state = i.findtext("arrmsg1")
            first = i.findtext("traTime1")
            second = i.findtext("traTime2")
            print("%s번 버스 1순위:%s (%s), 2순위:%s" % (number, first, state, second))
            # 2순위 버스도 추가하기
            time_bus = re.findall("\d+", state) # 숫자 모두 찾아 리스트로 저장
            if state == '곧 도착' or len(time_bus) >= 2: # 곧 도착 (시간 정보 x)
                sec = int(first)
            else: # 운행종료/ 출발대기/ 그 외...
                sec = 9999
            bus = [number, sec] #0 없앰
            bus_list.append(bus)
    else:
        print("인터넷 오류.")
    return bus_list

UPDATE_TERM = 10 # 새로고침 간격
DWELL_TIME = 30 # 버스 정차 시간
GOATDOCHAK_TIME = 180 # 곧 도착으로 전환되는 남은 시간
flag = 0
bus_goatdochak_list = []
a = []

#main
if __name__ == '__main__':
    app1 = TH.Thread(target=app.run, daemon=True)
    app1.start()
    print("----------start----------")

    while True:
        time.sleep(8)
        print("-------- call list ---------: "+str(bus_reserved_list))
        flag = 0
        # UPDATE_TERM 간격마다 아래 문장 실행
        bus_list = deviceRun()
        #P1Lcd.clear()
        #P2Lcd.clear()
        #print(bus_list)
        bus_list.sort(key= lambda x:x[1])
        
        prv_sec = -1
        empty_erea = -1
        for bus in bus_list:
            if bus[1] < GOATDOCHAK_TIME:
                if prv_sec == -1:
                    empty_erea = -1
                elif bus[1] - prv_sec <DWELL_TIME:
                    empty_erea *= -1
                else:
                    empty_erea = -1
                if  empty_erea == -1:
                    bus_goatdochak_list.append([bus[0], "P1"])
                    print(bus_goatdochak_list)
                    # print(bus[0])
                else:
                    bus_goatdochak_list.append([bus[0], "P2"])
                    if "P2" == bus[0]:
                        
                        print(bus[0])
                    else:
                        
                        print("None")


                prv_sec = bus[1]

                bus_count = 0
                for bus_goatdochak in bus_goatdochak_list:
                    if bus[0] == bus_goatdochak[0]:
                        # 곧도착에 두개 이상 있어야 하나 지우게
                        bus_count += 1
                    if bus_count >= 2:
                        bus_goatdochak_list.pop()
                        bus_count -= 1
                    
            else:
                for bus_goatdochak in bus_goatdochak_list:
                    if bus[0] == bus_goatdochak[0]:
                        bus_goatdochak_list.remove(bus_goatdochak) 
                if len(bus_goatdochak_list) ==0:
                    
                    print("None")
                else:
        
                    print(bus_goatdochak_list[0][0])
                                            
        print(bus_goatdochak_list)
        if len(bus_goatdochak_list) >=2:
            if "P2" == bus_goatdochak_list[1][1]:
                print(bus_goatdochak_list[1][1])
            

        
        #print(bus_goatdochak_list[0][0])
        #rint(bus_goatdochak_list[0][1]) 
        #print(bus_goatdochak_list[1][0])
        x = len(bus_goatdochak_list)
        print(x) 
        #print(bus_goatdochak_list[1][1])
        test_list = np.array(bus_goatdochak_list)
        value = 'P2'
        print(np.where(test_list == value))
