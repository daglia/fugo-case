from dotenv import load_dotenv
import os
import validators
import requests
from functools import reduce
from services.log import log

load_dotenv()

api_url = os.getenv("API_URL")
api_key = os.getenv("API_KEY")

def get(url, params=None):
    if not validators.url(url):
        print("Not a valid URL.")
        return
    
    log(f"GET: {url} Params: {params}")
    
    params = {'api_key': api_key} if params == None else params | {'api_key': api_key}

    res = requests.get(url=url, params=params)
    data = res.json()
    
    return data

def get_series_data():
    # Turkey
    # Amazon Prime
    # >=750 viewers rated
    # >= 8.3 avg. rate
    # the oldest 3 series

    url = f"{api_url}/watch/providers/tv"
    providers_res = get(url, {'watch_region': 'TR'})

    if not 'results' in providers_res:
        log("Could not get providers data")
        return

    filtered_providers_data = [x for x in providers_res['results'] if 'Amazon' in x['provider_name']] 
    provider_id_list = list(map((lambda x: x['provider_id']), filtered_providers_data))

    if provider_id_list.count == 0:
        return

    params = {
        'watch_region': 'TR',
        'with_watch_providers': '|'.join(str(v) for v in provider_id_list),
        'vote_count.gte': 750,
        'vote_average.gte': 8.3,
        'sort_by': 'first_air_date.asc'
    }

    url = f"{api_url}/discover/tv"
    series_res = get(url, params)

    if not 'results' in series_res:
        log("Could not get series data")
        return

    filtered_series_data = series_res['results'][:3]
    series_id_list = list(map((lambda x: x['id']), filtered_series_data))
    
    series_data = []

    for id in series_id_list:
        url = f"{api_url}/tv/{id}"
        serie_detail = get(url)
        series_data.append(serie_detail)

    return series_data

def get_credits_data(series_id_list):
    credits_data = []

    for id in series_id_list:
        url = f"{api_url}/tv/{id}/aggregate_credits"
        credits_res = get(url)
        
        cast_data = list(map((lambda x: {
            'person_id': x['id'], 
            'serie_id': id,
            'name': x['name'], 
            'gender': x['gender'], 
            'known_for_department': x.get('known_for_department'), 
            'popularity': x['popularity'], 
            'role': 'Cast',
            'character': ', '.join(list(map((lambda y: y['character']), x['roles']))),
            'episode_count': reduce((lambda a, b: a + b), list(map((lambda y: y['episode_count']), x['roles'])))
            }), credits_res['cast']))
            
        crew_data = list(map((lambda x: {
            'person_id': x['id'], 
            'serie_id': id,
            'name': x['name'], 
            'gender': x['gender'], 
            'known_for_department': x['known_for_department'], 
            'popularity': x['popularity'], 
            'role': 'Crew',
            'job': ', '.join(list(map((lambda y: y['job']), x['jobs']))),
            'episode_count': reduce((lambda a, b: a + b), list(map((lambda y: y['episode_count']), x['jobs'])))
            }), credits_res['crew']))
        
        credits_data += cast_data + crew_data

    return credits_data