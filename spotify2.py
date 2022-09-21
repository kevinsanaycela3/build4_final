import base64
import requests
import pandas as pd
import os 

######################################################################
############# PART ONE: Retrieving Access Token ######################
######################################################################

#Reading in user input for the URL in question

url = input("Please enter the URL to your playlist: ")

#Keys needed 
client_id = 'ece2a663c1f4442cb384fe5b29218825'
client_secret = '80e47af01e274cb6aa37f670f7b42d7f'

token_url = 'https://accounts.spotify.com/api/token'
method = 'POST'

#Converting to base64 according to the Spotify documentation 
client_creds = f"{client_id}:{client_secret}"
client_creds_base64 = base64.b64encode(client_creds.encode()) #encoding into a byte first 

#Headers needed for getting token
token_data = {
    "grant_type":"client_credentials"
}
token_header = {
    "Authorization": f"Basic {client_creds_base64.decode()}",
    "Content-Type":"application/x-www-form-urlencoded"
}


#Making API request for the access token
r = requests.post(url=token_url, data=token_data, headers=token_header)
access_token = r.json()["access_token"]


######################################################################
############# PART TWO: Accessing Playlist Data Using Token ##########
######################################################################

#Reading in the url of the playlist user is interested in, retrieving URI

playlist_id = url.split("/")[-1].split("?")[0]

request_header = {
    "Authorization":f"Bearer {access_token}"
}
r2 = requests.get(url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=request_header)

#Making arrays for columns we will be storing in the .csv file 
song_names = []
popularity = []
duration = []
explicit = []
album_name = []
artist_name = []

#Looping through all of the songs in the playlist
number_of_songs = len(r2.json()["items"])
for i in range(0, number_of_songs):

    #Get a list of the names of songs in the playlist 
    song_names.append(r2.json()["items"][i]["track"]["name"])

    #Get a list of the popularity across the playlist 
    popularity.append(r2.json()["items"][i]["track"]["popularity"])

    #Duration of song in minutes
    duration.append(int(r2.json()["items"][i]["track"]["duration_ms"])/60000)

    #Explicit song?
    explicit.append(r2.json()["items"][i]["track"]["explicit"])

    #Album Name
    album_name.append(r2.json()["items"][i]["track"]["album"]["name"])

    #Artist(s) name
    number_of_artists = len(r2.json()["items"][i]["track"]["artists"])
    artist_list = []
    for k in range(0,number_of_artists):
        artist_list.append(r2.json()["items"][i]["track"]["artists"][k]["name"])
        k = k + 1
    artist_name.append(artist_list)
    

#PRINTING FINAL DATAFRAME    
final_dataframe = pd.DataFrame({
    "Song Name":song_names,
    "Album Name":album_name,
    "Artist(s)":artist_name,
    "Duration (min)":duration,
    "Explicit?":explicit,
    "Popularity":popularity
})
print(final_dataframe)

######################################################################
############# PART THREE: Storing Playlist Data for User #############
######################################################################




#Get playlist name, make a folder in user's current location with the playlist info
r3 = requests.get(url=f"https://api.spotify.com/v1/playlists/{playlist_id}", headers=request_header)
playlist_name = r3.json()["name"]
playlist_name_ascii = playlist_name.encode("ascii", "ignore").decode()


currentwd = os.getcwd()
os.makedirs(f'{currentwd}/playlist_data', exist_ok=True) 
final_dataframe.to_csv(f'{currentwd}/playlist_data/{playlist_name_ascii}.csv') 


