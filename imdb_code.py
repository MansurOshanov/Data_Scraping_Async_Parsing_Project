# define helper functions if needed
# and put them in `imdb_helper_functions` module.
# you can import them and use here like that:

import requests
import urllib
from bs4 import BeautifulSoup
import time
import re
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import re
import asyncio
import aiohttp
import os
import time
from aiohttp import ClientSession
import nest_asyncio
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
nest_asyncio.apply()
headers = {'Accept-Language': 'en',
          'X-FORWARDED-FOR': '2.21.184.0'}
from .imdb_helper_functions import *
import re

def get_actors_by_movie_soup(cast_page_soup, num_of_actors_limit = None):
    url = 'https://www.imdb.com/'

    rows = cast_page_soup.find_all('tr', attrs = {'class': ['odd','even']})
    actors = []
    for row in rows:
        actor_name = row.find_all('a')[1].getText().strip()
        actor_page = urllib.parse.urljoin(url, row.find_all('a')[1]['href'])
        actors.append((actor_name, actor_page))
    
    if num_of_actors_limit is None:
        return actors
    else:
        return actors[0:num_of_actors_limit]


def get_movies_by_actor_soup(actor_page_soup, num_of_movies_limit = None):
    url = 'https://www.imdb.com/'
    
    films = actor_page_soup.find_all('div', attrs={'class': ['filmo-row odd', 'filmo-row even'], 'id': re.compile(r'actor|actress')})
    films_list = []
    for film in films:
        if not film.getText().find(")") != -1:
            movie_name = film.find('a').getText()
            movie_page = urllib.parse.urljoin(url, film.find('a')['href'])
            films_list.append((movie_name, movie_page))
            
    if num_of_movies_limit is None:
        return films_list
    else:
        return films_list[0:num_of_movies_limit]


async def get_movie_distance(actor_start_url, actor_end_url, num_of_actors_limit=None, num_of_movies_limit=None):
    start = time.time()
    print(f'actor_url: {actor_start_url}')
    movies = get_movies_by_actor_url(actor_start_url,5)
    depth = 1
    checked_movies = set()
    checked_actors = set()

    while True:
        if depth > 3:
            print("No Success")
            return float('inf')
        print(f"Current Depth:{depth}")
        new_movies = []
        movies_url = [pair[1] for pair in movies]

        async def get_movie_response(movie_url, session):
            while True:
                response = await session.request(method='GET', url=movie_url+'fullcredits', headers = headers)
                if response.status == 503:
                    print("Error 503, trying again after timeout")
                    await asyncio.sleep(60)
                    continue
                break
            #print(f"Response status ({movie_url}): {response.status}")
            response_text = await response.text()
            return response_text

        async def collect_movies(movie_url, session):
            """Wrapper for running program in an asynchronous manner"""
            try:
                response_text = await get_movie_response(movie_url, session)
                return response_text
            except Exception as err:
                print(f"Exception occured: {err}")
                pass

        async with ClientSession() as session:
            movie_response_texts = await asyncio.gather(*[collect_movies(movie_url, session) for movie_url in movies_url])



        for m, (movie_name, movie_url) in enumerate(movies):
            print(f"\t Movie:{movie_name}")

            movie_soup = BeautifulSoup(movie_response_texts[m])
            actors_list = get_actors_by_movie_soup(movie_soup, num_of_actors_limit)
            actors_url = [pair[1] for pair in actors_list]

            async def get_actor_response(actor_url, session):
                while True:
                    response = await session.request(method='GET', url=actor_url, headers = headers)
                    if response.status == 503:
                        print("Error 503, trying again after timeout")
                        await asyncio.sleep(60)
                        continue
                    break
                #print(f"Response status ({actor_url}): {response.status}")
                response_text = await response.text()
                return response_text

            async def collect_actors(actor_url, session):
                """Wrapper for running program in an asynchronous manner"""
                try:
                    response_text = await get_actor_response(actor_url, session)
                    return response_text
                except Exception as err:
                    print(f"Exception occured: {err}")
                    pass

            async with ClientSession() as session:
                actors_response_texts = await asyncio.gather(*[collect_actors(actor_url, session) for actor_url in actors_url])



            for a, (actor_name, actor_url) in enumerate(actors_list):
                print(f"\t\t Actor:{actor_name}")
                if actor_url.strip("/") == actor_end_url.strip("/"):
                    print("Distance Found!")
                    print(f"Elapsed Time:{time.time()-start}")
                    return depth
                elif actor_url not in checked_actors:
                    actor_soup = BeautifulSoup(actors_response_texts[a])
                    new_movies += get_movies_by_actor_soup(actor_soup, num_of_actors_limit)
                    checked_actors.add(actor_url)
            checked_movies.add(movie_url)
        
        
        new_movies_set = set()
        for (movie_name, movie_url) in new_movies:
            new_movies_set.add((movie_name, movie_url))
        
        movies = new_movies_set - checked_movies
        depth += 1


def get_movie_descriptions_by_actor_soup(actor_page_soup):
    movies = get_movies_by_actor_soup(actor_page_soup)
    movie_descriptions = []
    for movie in movies:
        print(f"\t Movie name: {movie[0]}")
        try:
            response = requests.get(url=movie[1], headers = headers)
            soup = BeautifulSoup(response.text)
            movie_description = soup.find('div', attrs={'class': 'ipc-html-content ipc-html-content--base'}).find('div').text
            movie_descriptions.append(movie_description)
        except:
            print("Cannot parse this movie")
    return movie_descriptions
