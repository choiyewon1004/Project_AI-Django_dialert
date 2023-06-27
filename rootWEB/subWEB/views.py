from django.shortcuts import render

# [포항시] 오늘 포항시 남부 지역에 천둥,번개를 동반한 국지성 호우가 예보되어 있으니 야외활동을 자제하여 주시고 시설물 관리에 각별히 유의하여 주시기 바랍니다.
# [행정안전부] 오늘 20시20분 경북(고령) 호우주의보 발효. 대중교통을 이용하시고 빗길 안전에 주의하시기 바랍니다.
# [서울특별시청]화재발생. 근처에 계신 등산객들은 대피하시고 다른 등산객들도 화재 지역으로 접근하지 마시기 바랍니다.

# 127.0.0.1:8000/subWEB/test/


# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from haversine import haversine
import pandas as pd
from ckonlpy.tag import Postprocessor
from ckonlpy.tag import Twitter


center = pd.read_csv('C:/Users/esthe/0.project/dsaster_alert/code/rootWEB/subWEB/static/csv/center.csv')
data = pd.read_csv('C:/Users/esthe/0.project/dsaster_alert/code/rootWEB/subWEB/static/csv/data.csv')
len_center = len(center)
global flag,point_lat,point_lng
flag= -1
point_lat = 37.49316124
point_lng = 127.0326027

# Create your views here.

def main(request):
    global flag

    print('client request url : http://127.0.0.1:8000/subWEB/main , main() call')
    flag = -1

    info_data = {
        'flag' : flag,
        'shelter_lat':37.49316124 ,
        'shelter_lng': 127.0326027
    }

    return render(request, 'subWEB/index.html', info_data)

def test(request):
    global flag

    print('client request url : http://127.0.0.1:8000/subWEB/test , test() call')
    flag = -1

    info_data = {
        'flag' : flag,
        'shelter_lat':37.49316124 ,
        'shelter_lng': 127.0326027
    }

    return render(request, 'subWEB/index2.html', info_data)

def res(request):
    global flag,point_lat,point_lng

    if flag == -1:
        alert_text = request.GET['alert']
        point_lat = request.GET['here_lat']
        point_lng = request.GET['here_lng']
    else:
        alert_text = request.GET['alert']


    res_dic = analyze_text(alert_text)
    print(">>", res_dic)

    disaster = res_dic['재해']
    stage = res_dic['bell_co']

    shelter_idx = find_shelter( (float(point_lat),float(point_lng)), disaster)

    print("shelter ", shelter_idx)

    if shelter_idx == -1:
        flag = 0
        info_data = {
            'alert_text': alert_text,
            'disaster': disaster,
            'point_lat': point_lat,
            'point_lng': point_lng,
            'flag': flag
        }
    else:
        flag = 2
        info_data = {
            'alert_text': alert_text,
            'disaster' : disaster,
            'point_lat': point_lat,
            'point_lng': point_lng,
            'shelter_lat' : data.loc[shelter_idx, 'lat'],
            'shelter_lng' : data.loc[shelter_idx, 'lng'],
            'shelter_name' : data.loc[shelter_idx, '대피소명'],
            'shelter_addr' : data.loc[shelter_idx, '도로명주소'],
            'stage' : stage,
            'flag' : flag
        }

    return render(request, 'subWEB/index2.html',info_data)



# 재난 문자 판별 알고리즘
def find_bell_color(re_text):

    if re_text == '대피':
        re_c = '#FA5858'
    elif re_text == '주의':
        re_c = '#FE9A2E'
    elif re_text == '유의':
        re_c = '#5882FA'
    elif re_text == '높음':
        re_c = '#5882FA'
    else :
        re_c ='#dfdfdf'

    return re_c


def find_di(tt):

    if tt in ['지진 해일', '지진', '여진 ', '낙하물']:
        re_di = '지진'
    elif tt in ['유해 화학', '화학사고']:
        re_di = '화학사고'
    elif tt in ['태풍', '풍수해', '침수', '월파', '낙석', '호우', '해일', '산불', '화재', '강수량']:
        re_di = '수해'
    elif tt in ["민방공", '민방위', '미사일']:
        re_di = '민방위'

    return re_di

def find_stage(tt):
    bell_c = '#dfdfdf'
    if tt in ['주의', '유의', '대피', '높음']:
        re_al = tt
        bell_c = find_bell_color(re_al)
    return bell_c

def analyze_text(alert_t):
    hang =[]
    twitter = Twitter()
    twitter.add_dictionary(['화학사고', '유해화학', '풍수해', '낙하물', '높음'], 'Noun')

    passwords = {'화학 사고', '지진 해일', '해일', '강풍', '호우', '유해 화학', '지진',
                 '낙하물', '민방공', '여진', '태풍', '풍수해', '침수', '접근자제', '산불',
                 '미사일', '화재', '월파', '낙석', '주의', '유의', '대피', '높음', '강수량',
                 '침수', '태풍', '호우','낙뢰','강풍','풍랑','대설','한파','폭염','황사',
                 '지진','해일','지진해일','화산폭발','가뭄','홍수','산사태','조류대발생','녹조',
                 '화재','산불','화학물질사고' }

    stopwords = {'코로나', '거리두기', '훈련', '실종', '찾습니다', '소음', '오발송', '파업'}
    postprocessor = Postprocessor(twitter, passwords=passwords, stopwords=stopwords)
    result = postprocessor.pos(alert_t)

    print(">>>>>>>>>>>>>>>>>>>>>> ", result)
    re_di = "재난"

    l_re = len(result)

    for idx in range(l_re):
        tt = result[idx][0]
        if tt in ['화학 사고', '지진 해일', '해일', '강풍', '호우', '유해 화학', '지진', '낙하물', '민방공', '여진', '태풍', '풍수해', '침수', '접근자제', '산불',
                 '미사일', '화재', '월파', '낙석', '강수량'] :
            re_di = find_di(tt)
        if tt in ['주의', '유의', '대피', '높음']:
            bell_col = find_stage(tt)

        if tt in ['지진','해일','지진해일','화산폭발','가뭄','홍수','산사태','조류대발생','녹조','화재','산불','화학물질사고' ]:
            hang.append(tt)
        print(">>>>>>>>>> ",tt , re_di )



    res_dic = {'재해': re_di,  'bell_co': bell_col , '행동' : hang}

    return res_dic


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
    print(di_type)

    point_cluster = find_cluster(point)
    sub_df = data[data['180k_cluster'] == point_cluster]

    # if di_type =='지진':
    #     sub_df = sub_df[sub_df['type'] == '지진' or sub_df['type'] == '지진옥외']
    # else :
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