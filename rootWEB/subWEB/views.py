from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from haversine import haversine
import pandas as pd

center = pd.read_csv('C:/Users/esthe/0.project/dsaster_alert/code/rootWEB/subWEB/templates/csv/center.csv')
data =   pd.read_csv('C:/Users/esthe/0.project/dsaster_alert/code/rootWEB/subWEB/templates/csv/data.csv')
len_center = len(center)

flag =0

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
    print("shelter " , shelter_idx , ">>", data.loc[shelter_idx])
    flag =1

    info_data = {
        'alert_text': alert_text,
        'disaster' : disaster,
        'point_lat': point_lat,
        'point_lng': point_lng,
        'shelter_lat' : data.loc[shelter_idx, 'lat'],
        'shelter_lng' : data.loc[shelter_idx, 'lng'],
        'shelter_name' : data.loc[shelter_idx, '대피소명'],
        'shelter_addr' : data.loc[shelter_idx, '도로명주소'],
        'flag' : flag
    }

    return render(request, 'subWEB/index.html',info_data)



# 재난 문자 판별 알고리즘
def discrimination_text(alert_t):
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

    res_shelter = idx_li[0]
    len_li = len(idx_li)
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