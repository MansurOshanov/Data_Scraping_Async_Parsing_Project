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

def helper_function_example():
    return 'Hello, I am a supposed to be a helper function'

def get_movies_by_actor_url(actor_page_url, num_of_movies_limit = None):
    while True:
        response = requests.get(actor_page_url, headers = headers)
        if response.status_code == 503:
            print("Error in request: 503. Trying again in 60 sec")
            time.sleep(60)
            continue
        break
    soup = BeautifulSoup(response.text)
    return get_movies_by_actor_soup(soup, num_of_movies_limit)

def get_actors_by_movie_url(movie_page_url, num_of_actors_limit = None):
    cast_page_url = movie_page_url + 'fullcredits'
    response = requests.get(url = cast_page_url, headers = headers)
    soup = BeautifulSoup(response.text)
    return get_actors_by_movie_soup(soup, num_of_actors_limit)

async def get_movie_distances_for_top_actors():
    movie_distances = dict()
    top_paid_actors_list = list(top_paid_actors.items())
    for i in range(0, len(top_paid_actors_list)):
        for j in range(i+1, len(top_paid_actors_list)):
            print(top_paid_actors_list[i][0], top_paid_actors_list[j][0])
            distance = await get_movie_distance(top_paid_actors_list[i][1], top_paid_actors_list[j][1],5,5)
            movie_distances[(top_paid_actors_list[i][0], top_paid_actors_list[j][0])] = distance
    return movie_distances

def plot_network(movie_distances, shown_distances = None):
    G = nx.Graph()
    
    if shown_distances:
        for k,v in movie_distances.items():
            node1 = k[0]
            node2 = k[1]
            weight = v
            if weight != shown_distances:
                continue
            G.add_edge(node1, node2, weight=weight)
    else:
        for k,v in movie_distances.items():
            node1 = k[0]
            node2 = k[1]
            weight = v
            if weight > 3:
                continue
            G.add_edge(node1, node2, weight=weight)

    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] == 3]
    emedium = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] == 2]
    esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] == 1]

    pos = nx.spring_layout(G, seed=7)  # positions for all nodes - seed for reproducibility

    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=100)

    # edges
    nx.draw_networkx_edges(G, pos, edgelist=elarge, width=1, edge_color = 'b')
    nx.draw_networkx_edges(G, pos, edgelist=emedium, width=1, edge_color = 'y')
    nx.draw_networkx_edges(
        G, pos, edgelist=esmall, width=1, alpha=0.5, edge_color="g", style="dashed"
    )

    # labels
    labels = nx.get_edge_attributes(G,'weight')
    nx.draw_networkx_edge_labels(G,pos,edge_labels=labels, font_size=8)
    nx.draw_networkx_labels(G, pos, font_size=8, font_family="sans-serif")


    ax = plt.gca()
    ax.margins(0.08)
    #plt.axis("off")
    plt.tight_layout()
    plt.show()
    
def save_movie_descriptions_to_file():
    for actor_name, actor_url in top_paid_actors.items():
        print(f"Actor name: {actor_name}")
        actor_page_soup = BeautifulSoup(requests.get(url=actor_url, headers=headers).text)
        movie_descriptions = get_movie_descriptions_by_actor_soup(actor_page_soup)
        text = " ".join(movie_descriptions)
        #print(text)
        with open(actor_name+'.txt', 'w', encoding='utf-8') as f:
            f.write(text)
            
def read_movie_distances(filename):
    new_dict = dict()
    with open(filename, "r", newline="") as f:
        while True:
            line = f.readline()
            if line == '':
                break
            row = line.split(',')
            new_dict[(row[0], row[1])] = float(row[2])
    return new_dict
            
    

def draw_workcloud(movie_description_file):
    with open(movie_description_file, 'r', encoding='utf-8') as f:
        text = f.read()
        word_tokens = text.split()
        filtered_text = [w for w in word_tokens if not w.lower() in stop_words]
        # Start with one review:
        full_filtered_text = " ".join(filtered_text)
        # Create and generate a word cloud image:
        wordcloud = WordCloud().generate(full_filtered_text)

        # Display the generated image:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()