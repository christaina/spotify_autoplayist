#!/bin/bash

export SPOTIPY_CLIENT_ID=698a641faba74984a6f124bfea6b60b9
export SPOTIPY_CLIENT_SECRET=0c085e7956794548a664228f0dba3f21
export SPOTIPY_REDIRECT_URI=http://localhost:8888/callback

cd /root/spotify_autoplayist/
/root/miniconda3/envs/spot/bin/python index_songs.py
/root/miniconda3/envs/spot/bin/python make_graph.py
git add graph_viz/graph.json && git commit -m 'update graph' && git push
