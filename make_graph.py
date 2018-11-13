from collections import Counter
from dateutil import parser
import pandas as pd
import networkx as nx
import numpy as np
import json


def timedelta_compare(delta, threshold):
    return delta.total_seconds() <= threshold


def group_by_time(times, interval=(60 * 10)):
    groups = [False]
    groups.extend([timedelta_compare(times[i] - times[i+1], interval) for i in range(len(times)-1)])
    groups.append(False) # get last idx as a group too
    return groups


def assign_groups(break_points):
    grps = {}
    old_bp = 0
    for g, bp in enumerate(break_points):
        grps.update({i: g for i in range(break_points[g-1], bp)})
        old_bp = bp
    return grps


def minmax_scale(col):
    def _scale(x, cmin, cmax):
        return (x-cmax + cmin)/(cmax-cmin)
    cmin, cmax = col.min(), col.max()
    return (col-cmin)/(cmax-cmin)


def make_graph(df, counts):
    incl_songs = set(list(df.name_from) + list(df.name_to))
    counts = {k:v for k, v in song_counts.items() if k in incl_songs}
    G = nx.MultiGraph()

    for song, count in counts.items():
        G.add_node(song, count=count)

    for song_pair in df[['name_to', 'name_from', 'group', 'scaled_delta_s']].to_dict(orient='index').values():
        G.add_edge(song_pair['name_to'], song_pair['name_from'], group=str(song_pair['group']), dist=str(song_pair['scaled_delta_s']))
    return G


if __name__=="__main__":
    song_hist_path = 'song_hist/song_history.csv'
    graph_save_path = 'graph_viz/graph.json'

    graph_cnt_threshold = 1 
    song_grp_threshold = 60 * 10 
    song_distance_threshold = 6

    songs = pd.read_csv(song_hist_path)

    # parse date played at from str
    songs['played_at'] = songs['played_at'].apply(parser.parse)
    break_points = [i for i,x in enumerate(group_by_time(songs.played_at, interval=song_grp_threshold)) if x==False]

    song_groups = {idx: i for i, idx in enumerate(break_points)}
    assigned_groups = assign_groups(break_points)

    songs['group'] = -1
    for idx, grp in assigned_groups.items():
        songs.at[idx, 'group']=grp
    songs = songs.sort_values(by=['group', 'played_at'])
    songs['grp_idx'] = songs.groupby('group').cumcount()+1

    song_counts = dict(Counter(songs.name))
    songs_cartesian = pd.merge(songs, songs, on=['group'], how='outer', suffixes=['_to', '_from'])
    songs_cartesian = songs_cartesian[songs_cartesian.played_at_from != songs_cartesian.played_at_to]
    songs_cartesian = songs_cartesian[songs_cartesian.apply(lambda r: np.abs(r['grp_idx_to'] - r['grp_idx_from']) < song_distance_threshold,axis=1)]
    songs_cartesian['delta_s'] = songs_cartesian.apply(lambda r: (np.abs(r['played_at_to'] - r['played_at_from']).total_seconds()), axis=1)
    songs_cartesian = songs_cartesian.sort_values(['name_to', 'name_from']).drop_duplicates(subset=['group', 'delta_s'])
    songs_cartesian['scaled_delta_s'] = minmax_scale(songs_cartesian.delta_s)
    songs_ct_filt = songs_cartesian[(songs_cartesian.name_from.apply(lambda x:
        song_counts[x]>graph_cnt_threshold)) & \
				    (songs_cartesian.name_to.apply(lambda x:
                                        song_counts[x]>graph_cnt_threshold))]

    G = make_graph(songs_ct_filt, counts=song_counts)
    links = nx.node_link_data(G)['links']
    nodes = {x['id']: x for x in nx.node_link_data(G)['nodes']}
    print(f"Made graph with {len(nodes)} nodes and {len(links)} edges")
    json.dump({'nodes': nodes, 'links': links}, open(graph_save_path, 'w'))
    print(f"Saved graph to {graph_save_path}")
