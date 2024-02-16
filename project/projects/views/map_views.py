from django.shortcuts import render, redirect
from math import radians, sin, cos, sqrt, atan2
import geopandas as gpd
from shapely.geometry import Point, shape
import json
import requests
import csv
from ..models import Location, Bookmark
from ..forms import BookmarkForm
from django.contrib.auth.decorators import login_required

# 각좌표간의 거리 반경 계산기 함수 (하버사인 공식)
# def calculate_distance(lat1, lon1, lat2, lon2):
#     # 하버사인 공식을 사용하여 두 좌표 사이의 거리를 계산하는 함수
#     R = 6371  # 지구의 반지름 (킬로미터 단위)

#     dlat = radians(lat2 - lat1)
#     dlon = radians(lon2 - lon1)

#     a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))

#     distance = R * c * 1000
#     return distance # 거리를 미터 단위로 변환

# 각좌표간의 거리 반경 계산기 함수 (직선 거리 공식)
def calculate_distance(lat1, lon1, lat2, lon2):
    # 두 지점 간의 직선 거리를 계산하는 함수
    # 두 지점 간의 x, y 좌표 차이를 사용하여 계산
    dx = lon2 - lon1
    dy = lat2 - lat1
    distance = sqrt(dx**2 + dy**2) * 111000  # 경도와 위도의 차이를 고려하여 거리를 계산 (단위: 미터)
    return distance

# CSV을 읽어오고, 입력한 좌표의 반경 내에 있는 좌표만 전달하는 함수
def read_csv(file_path, reference_lat, reference_lon, radius):
    coordinates = []
    with open(file_path, 'r', encoding='cp949') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header if exists
        for row in reader:
            district = row[0]  # Assuming the first column is district name
            latitude = float(row[1])  # Assuming the second column is latitude
            longitude = float(row[2])  # Assuming the third column is longitude

            # 참조 지점에서의 거리 계산
            distance = calculate_distance(reference_lat, reference_lon, latitude, longitude)

            # 거리가 지정된 반경 내에 있는지 확인
            if distance <= radius:
                coordinates.append({'district': district, 'latitude': latitude, 'longitude': longitude})
    return coordinates

# 좌표값 구분 후에 해당 좌표를 딕셔너리로 저장하는 함수
def mark_district_coordinates(api_key, coordinates):
    markers = []
    for coordinate in coordinates:
        district = coordinate['district']
        latitude = coordinate['latitude']
        longitude = coordinate['longitude']
        
        # Call Kakao Maps API to get more information if needed
        # Example: https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={longitude}&y={latitude}
        marker = {
            'title': district,
            'latlng': {'lat': latitude, 'lng': longitude},
        }
        markers.append(marker)
    return markers

# 가장 가까운 지역구를 찾아주는 함수
def distance_gu(reference_lat, reference_lng):
    # 좌표값
    latitude = reference_lat
    longitude = reference_lng

    # GeoJSON 파일에서 지역구 경계 읽기 (파일 경로는 실제 경로로 변경 필요)
    geojson_file_path = 'hangjeongdong_서울특별시.geojson'
    gdf = gpd.read_file(geojson_file_path)

    # 좌표를 Shapely Point로 변환
    point = Point(longitude, latitude)

    # 지역구 경계 중 가장 가까운 것 찾기
    min_distance = float('inf')
    nearest_district = None

    for index, row in gdf.iterrows():
        district_shape = shape(row['geometry'])
        distance = point.distance(district_shape)
        
        if distance < min_distance:
            min_distance = distance
            nearest_district = row['sggnm']

    return nearest_district

# 여러 계산을 진행 후에 페이지를 만드는 함수
def map_detail(request):
    search_keyword = request.GET.get('search_keyword', '')
    reference_lng = addr_lng(search_keyword)
    reference_lat = addr_lat(search_keyword)
    gu_name = distance_gu(reference_lat, reference_lng)

    location_instance = Location.objects.get(name=gu_name)
    crime_danger = location_instance.crime_danger

    # 거리 단위를 가져오기
    distance_unit = request.GET.get('distance', '')
    # 거리 단위에 따라 radius 값 설정 (기본값은 500m)
    radius = int(distance_unit) if distance_unit.isdigit() else 500
    
    csv_file_path = '서울시 통합 좌표.csv'
    api_key = '5b2f66c85f3743a2bc9b7c204f357893'

    search_time = request.GET.get('search_time')
    # 시간대에 따른 점수 계산
    if search_time == 'morning':
        score = 0.3
        count = location_instance.morning_count
    elif search_time == 'afternoon':
        score = 0.25
        count = location_instance.afternoon_count
    elif search_time == 'evening':
        score = 0.2
        count = location_instance.evening_count
    elif search_time == 'night':
        score = 0.1
        count = location_instance.night_count
    elif search_time == 'dawn':
        score = 0.3
        count = location_instance.dawn_count
    else:
        score = 0.3
        count = location_instance.morning_count
        
    filtered_coordinates = read_csv(csv_file_path, reference_lng, reference_lat, radius)
    markers = mark_district_coordinates(api_key, filtered_coordinates)

    context = {'markers': markers, 'x' : reference_lng, 'y' : reference_lat, 'search_keyword': search_keyword, 'score': score,
               'search_time': search_time, 'gu_name':gu_name, 'crime_danger':crime_danger, 'count':count, 'radius':radius}
    return render(request, 'projects/map_detail.html', context)

# Y 좌표 할당해주는 함수
def addr_lat(addr):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query={address}'.format(address=addr)
    headers = {"Authorization": "KakaoAK " + "943e784f9ac8621fd887cd598cea9f18"}
    result = json.loads(str(requests.get(url, headers=headers).text))
    match_first = result['documents'][0]
    return float(match_first['y'])

# X 좌표 할당해주는 함수
def addr_lng(addr):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query={address}'.format(address=addr)
    headers = {"Authorization": "KakaoAK " + "943e784f9ac8621fd887cd598cea9f18"}
    result = json.loads(str(requests.get(url, headers=headers).text))
    match_first = result['documents'][0]
    return float(match_first['x'])

# 기본 지도 페이지
def map(request):
    return render(request, 'projects/map.html')