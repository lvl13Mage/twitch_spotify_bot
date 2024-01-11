import json
from typing import List, Dict, Union

class JsonSongRequestStorageHandler:
    def __init__(self, filename: str):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self) -> List[Dict[str, Union[str, int]]]:
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)

    def add_entry(self, id: int, spotifyid: str, artist: str, songname: str, username: str):
        self.data.append({
            "id": id,
            "spotifyid": spotifyid,
            "artist": artist,
            "songname": songname,
            "username": username
        })
        self.save_data()

    def fetch_by_spotifyid(self, spotifyid: str) -> List[Dict[str, Union[str, int]]]:
        return [entry for entry in self.data if entry['spotifyid'] == spotifyid]

    def fetch_by_username(self, username: str) -> List[Dict[str, Union[str, int]]]:
        return [entry for entry in self.data if entry['username'] == username]
    
    # fetch by spotifyID from top of list but only return first entry
    def fetch_by_spotifyid_top(self, spotifyid: str) -> List[Dict[str, Union[str, int]]]:
        return [entry for entry in self.data if entry['spotifyid'] == spotifyid][0]

    def pop_until_song(self, spotifyid: str):
        for i, entry in enumerate(self.data):
            if entry['spotifyid'] == spotifyid:
                self.data = self.data[i:]
                self.save_data()
                break