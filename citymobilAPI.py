import requests
import json

def requestCORDS(latitude, longitude, del_latitude, del_longitude):
    url = 'https://c-api.city-mobil.ru/'
    obj = '{'+ f'"method":"getprice","ver":"4.59.0", "phone_os":"widget","os_version":"web mobile-web","locale":"ru","latitude":{latitude},"longitude":{longitude},"del_latitude":{del_latitude},"del_longitude":{del_longitude},"options":[],"payment_type":["cash"],"tariff_group":[2,4,13,7,5],"source":"O"' + '}'
    x = requests.post(url, obj)
    return sortJsonStr(x.text)






def sortJsonStr(json_str):
    a = json.loads(json_str)
    tariffs = []
    for i in range(len(a['prices'])):
        tariff_type = a['prices'][i]['tariff_info']['name']
        price = a['prices'][i]['price']
        car_models = a['prices'][i]['tariff_info']['car_models']
        space = a['prices'][i]['tariff_info']['car_capacity']
        link = a['prices'][i]['tariff_info']['link']
        tariffs.append({'tariff_type': tariff_type, 'price': price, 'car_models': car_models, 'space': space, 'link': link})
    return tariffs


def findadress(string):
    url = f'https://widget.city-mobil.ru/ws-api/searchaddress?query={string}'
    print(url)
    data = requests.get(url)
    data = json.loads(data.text)

    title = data['data'][0]['title']
    country = data['data'][0]['country']
    region = data['data'][0]['region']
    sub_region = data['data'][0]['sub_locality']
    postal_code = data['data'][0]['postal_code']
    latitude = data['data'][0]['latitude']
    longitude = data['data'][0]['longitude']

    return {'country': country, 'region': region, 'sub_region': sub_region, 'postal_code': postal_code, 'title': title, 'latitude': latitude, 'longitude': longitude}