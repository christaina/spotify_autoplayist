# Spotify Autoplayist

A project to store my song history and eventually do data viz + automatic playlist generation!!

# Visualization

View graph visualization [here](https://christaina.github.io/spotify_autoplayist/graph_viz/). Writeup [here](https://github.com/christaina/spotify_autoplayist/blob/master/writeup/viz_outline.md).

# Environment

Create the conda environment I used for this project with 

```
conda env create -f environment.yml
```

# Running it yourself

To run `index_songs.py` yourself, you will need to set your `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, and `SPOTIPY_REDIRECT_URI` environment variables. 
You'll also need to change `username` in the script to be your spotify username (for now...)
