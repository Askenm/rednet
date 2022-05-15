import pandas as pd
import networkx as nx
from urllib.parse import urlparse


def extract_url_host(url):
    suffix = ['www.','mobile.','.com','.org','.au','.uk','.co']
    parsed = urlparse(url)[1]
    for sx in suffix:
        parsed = parsed.replace(sx,'')
    parsed = parsed.replace('en.m.','en.')
    return parsed


def assign_host_ids(data):
    url_id_map = {'cleaned_url':[],'host_id':[]}
    for ix,url in enumerate(data.cleaned_url.value_counts().keys()):
        url_id_map['cleaned_url'].append(url)
        url_id_map['host_id'].append(ix)

    url_id_frame = pd.DataFrame.from_dict(url_id_map)
    data = pd.merge(data,url_id_frame,left_on='cleaned_url',right_on = 'cleaned_url')
    return data

def add_subreddit_ids(data):
    unk_sr = data.subreddit.unique().tolist()
    max_host_id = data.host_id.max()+1

    sr_id_map = {'subreddit':[],'subreddit_id':[]}

    for ix,sr in enumerate(unk_sr):
        sr_id = ix+max_host_id
        sr_id_map['subreddit'].append(sr)
        sr_id_map['subreddit_id'].append(sr_id)

    sr_id_frame = pd.DataFrame.from_dict(sr_id_map)
    data = pd.merge(data,sr_id_frame,left_on='subreddit',right_on = 'subreddit')
    
    return data

def clean_data(data):
    data = data.loc[data.title!='title']
    data['cleaned_url'] = data['url'].apply(lambda x: extract_url_host(x))
    data = data.loc[(~data.cleaned_url.isin(['i.redd.it','reddit','v.redd.it']))&
                           (~data.cleaned_url.str.contains('img'))&
                          (~data.cleaned_url.str.contains('youtu'))]
    
    data = assign_host_ids(data)
    
    data = add_subreddit_ids(data)
    
    return data




def generate_node_attributes(data,G):
    subreddits = data['subreddit'].unique().tolist()
    names = {}
    types = {}
    for sr in subreddits:
        cur = data.loc[data['subreddit']==sr]
        cur_id = cur['subreddit_id'].values.tolist()[0]
        names[cur_id] = sr
        types[cur_id] = 'SUBREDDIT'
        
    hosts = data['cleaned_url'].unique().tolist()
    for host in hosts:
        cur = data.loc[data['cleaned_url']==host]
        cur_id = cur['host_id'].values.tolist()[0]
        names[cur_id] = host
        types[cur_id] = 'WEBPAGE'
        
        
    nx.set_node_attributes(G,names,'node_name')
    nx.set_node_attributes(G,types,'node_type')
    
    return G
    
    
def create_reddit_bp_G(data):
    edges = [(row['host_id'],row['subreddit_id']) for k,row in data.iterrows()]
    rednet = nx.Graph()
    rednet.add_edges_from(edges)
    
    rednet = generate_node_attributes(data,rednet)
    
    print(nx.info(rednet))
    
    return rednet



if __name__ =='__main__':
    data = clean_data(data)
    rednet = create_reddit_bp_G(data)