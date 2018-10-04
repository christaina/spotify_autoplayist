import spotipy
import spotipy.util as util
import pandas as pd
import os
from dateutil.parser import parse

def get_song_data(song_info):
    """Parse song data from api response
    
    Parameters
    ----------
    song_info: dict

    Returns
    -------
    dict
    """
    track = (song_info['track'])
    data = {
            'played_at': song_info['played_at'],
            'id': track['id'],
            'name': track['name'],
            'explicit': track['explicit'],
            'artists': ', '.join([artist['name'] for artist in
                track['artists']]),
            }
    return data

def load_last_indexed(last_indexed_path):
    """Load last indexed date from path and convert to datetime
    
    Parameters
    ----------
    last_indexed_path : str
        Path to file containing last indexed date str

    Returns
    -------
    datetime.datetime
    """
    # if there was no last indexed....return my birthday!
    if not os.path.exists(last_indexed_path):
        return parse("1993-11-26T13:00:00Z")
    # else open file, read, and parse into datetime
    last_idxed = open(last_indexed_path).read().strip()
    return parse(last_idxed)

def find_last_indexed(song_df, last_index_path):
    # sort by parsed date
    sorted_song_times = sorted(song_df.played_at, key=lambda x: parse(x))
    # get latest date
    new_last_idxed = sorted_song_times[-1] 
    return new_last_idxed

def save_last_indexed(path, last_indexed):
    """Write str of last indexed date to file"""
    open(path, 'w').write(last_indexed)


def filt_by_last_idxed(song_df, last_indexed):
    """Filter song df to only incl songs after the last indexed data
    
    Parameters
    ----------
    song_df: pd.DataFrame
    last_indexed: datetime.datetime
    """
    return song_df[song_df.played_at.apply(parse) > last_indexed]


if __name__=='__main__':
    scope = 'user-read-recently-played'
    username='121027976'
    last_idx_path='data/last_indexed.txt'
    song_history_path = 'data/song_history.csv'

    # setup
    token = util.prompt_for_user_token(username, scope)
    sp = spotipy.client.Spotify(auth=token)

    # get recently played tracks (max 50 can be returned from api)
    recently_played = sp._get('me/player/recently-played', limit=50)['items']
    recent_songs = [get_song_data(song) for song in recently_played]

    # create df out of song info
    recent_songs_df = pd.DataFrame(recent_songs)

    # check last time songs were indexed + only append new songs
    old_last_indexed = (load_last_indexed(last_idx_path))
    print(f"Previously indexed at {old_last_indexed}")
    filt_song_history = filt_by_last_idxed(recent_songs_df, old_last_indexed)
    print(f"Found {len(filt_song_history)} new songs in your history!")
    filt_song_history.to_csv(song_history_path, index=False, mode='a')

    # save the new index date (latest played_at timestamp)
    new_last_indexed = (find_last_indexed(recent_songs_df, last_idx_path))
    save_last_indexed(last_idx_path, new_last_indexed)
