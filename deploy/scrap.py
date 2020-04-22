import pandas as pd
import requests as rq
import json

def get_coordinates():
    df = pd.read_csv('district.csv')
    latlon = []
    for key, value in df.iterrows():
        diff = 0.008
        lat = value['Latitude']
        lon = value['Longitude']
        latlon.append([str(round(lat-diff,3))+','+str(round(lon+diff,3)),str(round(lat+diff,3))+','+str(round(lon-diff,3))])    
    df = df.merge(pd.DataFrame(latlon), how='left', left_index=True, right_index=True)
    df.columns = ['District', 'Latitude', 'Longitude', 'Coord_0', 'Coord_1']	
    return df

def conv_bool(feature):
	return 1 if feature==True else 0

def special_feat(feature):
    if feature>4:
        return '[4,%7D'
    else:
        return feature    

def elevator_swpool(elevator, sw_pool):
    if (elevator==1) and (sw_pool==1):
        ele_swim = '(and%20instalacoes:%27Elevador%27instalacoes:%27PISCINA%27)'
    elif (elevator==1) and (sw_pool==0):
        ele_swim = '(and%20instalacoes:%27Elevador%27)'
    elif (elevator==0) and (sw_pool==1):
        ele_swim = '(and%20instalacoes:%27PISCINA%27)'
    else:
        ele_swim = ''
    return ele_swim    
    
def cat_mobilia(feature):
    if feature==1:
        return 'Mobiliado'
    else:
        return 'NaoMobiliado'  

def get_district_coords(district, df):
    return '{}%27,%27{}'.format(df[df['District']==district]['Coord_1'].get_values()[0],
                                df[df['District']==district]['Coord_0'].get_values()[0])        
    
def prepare_data(data, df):
    area = [data[0],data[1]]
    rooms = special_feat(data[2])
    toilets = special_feat(data[3])
    parking = data[5]
    ele_swim = elevator_swpool(conv_bool(data[6]), conv_bool(data[8]))
    furnished = cat_mobilia(data[7])
    coordinates = get_district_coords(data[10], df)
    return [parking, toilets, area, rooms, ele_swim, furnished, coordinates]

def format_query(key):
    rurl = 'https://www.quintoandar.com.br/api/yellow-pages/search?'
    text = 'q=(and%20(and%20(and%20area:{area}(and%20(or%20quartos:%27{rooms}%27)(and%20tipo:%27Apartamento%27(and%20{ele_swim}(and%20for_rent:%27true%27amenidades:%27{furnished}%27)))))))&fq=local:[%27{coordinates}%27]&return=id,local,aluguel,area,quartos,custo,endereco,regiao_nome,vagas&size=1000&q.parser=structured'
    query = text.format(parking=key[0],
                        toilets=key[1],
                        area=key[2],
                        rooms=key[3],
                        ele_swim=key[4],
                        furnished=key[5],
                        coordinates=key[6])
    return rurl+query

def site_search(url):
    response = rq.get(url).json()
    apes = []
    for hit in response["hits"]["hit"]:
        ap_id = hit.get('id')
        rooms = hit.get('fields').get('quartos')
        area = hit.get('fields').get('area')
        rent = hit.get('fields').get('custo')
        park = hit.get('fields').get('vagas')
        local = hit.get('fields').get('local')
        address = hit.get('fields').get('endereco')
        district = hit.get('fields').get('regiao_nome')
        apes.append([ap_id, area, rooms, park, district, address, local, rent])
    apes = pd.DataFrame(apes, columns=['ap_id','area','rooms','park','district','address','local','rent'])
    return apes

def ap_available(data):
    df = get_coordinates()
    url = format_query(prepare_data(data, df))
    apartamentos = site_search(url)
    return apartamentos