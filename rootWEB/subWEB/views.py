from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from haversine import haversine
import pandas as pd

center = pd.read_csv('C:/Users/esthe/0.project/dsaster_alert/code/rootWEB/subWEB/templates/csv/center.csv')
data =   pd.read_csv('C:/Users/esthe/0.project/dsaster_alert/code/rootWEB/subWEB/templates/csv/data.csv')
len_center = len(center)

# Create your views here.

def main(request):
    print('client request url : http://127.0.0.1:8000/subWEB/main , main() call')
    return render(request, 'subWEB/index.html')

def res(request):
    alert_text = request.GET['alert']
    point_lat = request.GET['here_lat']
    point_lng = request.GET['here_lng']

    disaster = discrimination_text(alert_text)
    shelter_idx = find_shelter( (float(point_lat),float(point_lng)), disaster)
    # print("shelter " , shelter_idx , ">>", data.loc[shelter_idx])
    print("shelter ", shelter_idx)


    info_data = {
        'alert_text': alert_text,
        'disaster' : disaster,
        'point_lat': point_lat,
        'point_lng': point_lng,
        'shelter_lat' : data.loc[shelter_idx, 'lat'],
        'shelter_lng' : data.loc[shelter_idx, 'lng'],
        'shelter_name' : data.loc[shelter_idx, '대피소명'],
        'shelter_addr' : data.loc[shelter_idx, '도로명주소'],
    }

    return render(request, 'subWEB/index.html',info_data)



# 재난 문자 판별 알고리즘
def discrimination_text(alert_t):

    from ckonlpy.tag import Postprocessor

    twitter = Twitter()
    twitter.add_dictionary(['화학사고', '유해화학', '풍수해', '낙하물', '높음'], 'Noun')

    passwords = {'화학 사고', '지진 해일', '해일', '강풍', '호우', '유해 화학', '지진', '낙하물', '민방공', '여진', '태풍', '풍수해', '침수', '접근자제', '산불',
                 '미사일', '화재', '월파', '낙석', '주의', '유의', '대피', '높음'}
    stopwords = {'코로나', '거리두기', '훈련', '실종', '찾습니다', '소음', '오발송', '파업'}
    postprocessor = Postprocessor(twitter, passwords=passwords, stopwords=stopwords)
    result = postprocessor.pos(alert_t)

    re = []
    l_re = len(re)
    for idx in range(l_re):
        re.append(result[idx][0])

    earth = ('지진 해일', '지진', '여진 ', '낙하물',)
    continent = '지진'
    earth_dic = dict.fromkeys(earth, continent)

    chemi = ('유해화학', '화학사고')
    continent = '화학사고'
    chemi_dic = dict.fromkeys(chemi, continent)

    rain = ('태풍', '풍수해', '침수', '월파', '낙석')
    continent = '풍수해'
    rain_dic = dict.fromkeys(rain, continent)

    civil = ("민방공", '민방위')
    continent = '민방위'
    civil_dic = dict.fromkeys(civil, continent)

    alret = ('주의', '유의', '대피', '높음')
    continent = '알림'
    alret_dic = dict.fromkeys(alret, continent)

    dic_type =  [earth_dic,chemi_dic,rain_dic,civil_dic,alret_dic]






    type = alert_t
    return type


def find_cluster(point):

    res_clus = 0
    res_dis = 999999

    for idx in range(len_center):
        des_lat = center.loc[idx, 'lat']
        des_lng = center.loc[idx, 'lng']
        des = (des_lat, des_lng)

        cal = haversine(point, des, unit='m')

        if cal < res_dis:
            res_dis = cal
            res_clus = idx
    return res_clus


def find_shelter(point, di_type):

    point_cluster = find_cluster(point)
    sub_df = data[data['180k_cluster'] == point_cluster]
    sub_df = sub_df[sub_df['type'] == di_type]
    idx_li = sub_df.index

    len_li = len(idx_li)

    if len_li == 0 :
        return -1

    res_shelter = idx_li[0]
    res_dis = 999999

    for idx in range(len_li):
        idx = idx_li[idx]
        des_lat = data.loc[idx, 'lat']
        des_lng = data.loc[idx, 'lng']
        des = (des_lat, des_lng)

        cal = haversine(point, des, unit='km')

        if cal < res_dis:
            res_dis = cal
            res_shelter = idx

    return res_shelter


def find_info(point, di_type):
    idx = find_shelter(point, di_type)
    info_dic = {
        '대피소명': data.loc[idx, '대피소명'],
        '도로명주소': data.loc[idx, '도로명주소'],
        '위도': data.loc[idx, 'lat'],
        '경도': data.loc[idx, 'lng'],
        '재난유형': data.loc[idx, 'type']
    }

    return info_dic