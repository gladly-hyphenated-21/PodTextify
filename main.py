#Los Altos Hacks
import os
import sys
#quick options check
if len(sys.argv) > 1:
    if (str(sys.argv[1]) == "--opendatasets") or (str(sys.argv[1]) == "--showdatasets"):
        datasets_dir = str(os.getcwd()) + "/datasets/"
        print("The datasets directory is: "+datasets_dir)
        exit()
#quick options check over
import wget
import requests
import feedparser
import requests
import json
import feedparser
from pydub import AudioSegment
import pandas as pd
import re
from datasets import load_dataset
from textblob import TextBlob
import language_tool_python
from vosk import Model, KaldiRecognizer
import wave
import random

def printLogo():
    print("██████╗  ██████╗ ██████╗ ████████╗███████╗██╗  ██╗████████╗██╗███████╗██╗   ██╗")
    print("██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝██║██╔════╝╚██╗ ██╔╝")
    print("██████╔╝██║   ██║██║  ██║   ██║   █████╗   ╚███╔╝    ██║   ██║█████╗   ╚████╔╝ ")
    print("██╔═══╝ ██║   ██║██║  ██║   ██║   ██╔══╝   ██╔██╗    ██║   ██║██╔══╝    ╚██╔╝  ")
    print("██║     ╚██████╔╝██████╔╝   ██║   ███████╗██╔╝ ██╗   ██║   ██║██║        ██║   ")
    print("╚═╝      ╚═════╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝        ╚═╝   ")
    print("                                            by Sean, Max, Aarushi, and Vaughn ")

def howToGuide():
    print("\nusage: main.py --name='(name of podcast, or 'random' for random)' --number=(number of episodes to download) ")
    print("example: --name='Talk Python To Me' --number='5' ")
    print("output: a .parquet file for training models")

#custom function to get datasets directory

#validity checks!
if not len(sys.argv) >= 3:
    #no arguments, or malformed arguments, were passed; therefore we should exit and print help
    print("missing or malformed arguments detected.")
    howToGuide()
    exit()
elif not '--name=' == str(str(sys.argv[1])[0:7]):
    #there is no name, or the argument is malformed.
    print("Missing or malformed name. Please use --name='example search' format.")
    howToGuide()
    exit()
elif not '--number=' == str(sys.argv[2])[0:9]:
    #there is no number, or the argument is malformed
    print("Missing or malformed number. Please use --name='42' format.")
    howToGuide()
    exit()
#jank way of checking if there is a valid int number.
try:
    int(str(sys.argv[2])[9:(len(sys.argv[2]))]) + 1
except:
    print("(mode 2) Missing or malformed number. Please use --name='42' format.")
    howToGuide()
    exit()

name = str(str(sys.argv[1])[7:])
number = int(str(sys.argv[2])[9:(len(sys.argv[2]))])

#welcome to the program.
printLogo()

#check if apple podcasts is up
def is_website_reachable(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False
if not is_website_reachable("https://itunes.apple.com/search"):
    print("\n\nLooks like either Apple or you is offline. Exiting program.")
    exit()

#create a directory for podcasts
if not os.path.exists('podcasts'):
    os.makedirs('podcasts')
    print("making temporary directory for podcasts...")
if not os.path.exists('datasets'):
    os.makedirs('datasets')
    print("making a directory for datasets...")

#finding and download podcasts
def search_podcasts(term):
    base_url = "https://itunes.apple.com/search"
    params = {
        "term": term,
        "media": "podcast",
        "limit": 1
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
def get_podcast_feed_url(podcast_id):
    base_url = "https://itunes.apple.com/lookup"
    params = {
        "id": podcast_id
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['resultCount'] > 0:
            return data['results'][0]['feedUrl']
    return None
def get_episode_download_urls(feed_url):
    feed = feedparser.parse(feed_url)
    download_urls = []
    for entry in feed.entries:
        download_urls.append(entry.enclosures[0].href)
    return download_urls

podcasts = search_podcasts(name)

if podcasts:
    for podcast in podcasts['results']:
        print(f"Podcast Name: {podcast['collectionName']}")
        feed_url = get_podcast_feed_url(podcast['collectionId'])
        if feed_url:
            download_urls = get_episode_download_urls(feed_url)
else:
    print("No podcasts found.")

#check if the length of the podcasts fetched is less than the amount we want.
if len(download_urls) < number:
    print(f"Warning: the number of episodes ({len(download_urls)}) is shorter than the number requested ({number}) ")
    number = download_urls

sources = list()
for item in range(0,number):
    sources.append(download_urls[item])

file_locations = list()
for source in sources:
    file_name = source.split('/')[-1]
    new_file_name = f'{name}-{file_name}'
    file_path = os.path.join("podcasts", new_file_name)
    wget.download(source, out=file_path)
    #print(f'\nDownloaded {source} as {new_file_name}')
    input_file = "podcasts/"+str(new_file_name)
    output_file = "podcasts/"+str(new_file_name)[:(len(new_file_name)-4)]+".wav"
    print(f"\nConverting {new_file_name} to WAV...")
    audio = AudioSegment.from_file(input_file)
    print(f"Converting {new_file_name} to 16 kHz...")
    audio = audio.set_frame_rate(16000)
    audio.set_channels(1)
    audio.export(output_file, format="wav")
    #delete old .mp3 file
    if os.path.isfile(input_file):
        # Delete the file
        os.remove(input_file)
    else:
        print(f"could not remove {input_file}.")
    file_locations.append("\'"+str(output_file)+"\'")


download_directory = str(os.getcwd()) + "/datasets/"
tool = language_tool_python.LanguageTool('en-US')


def txt_to_parquet(txt_file, parquet_file):
    # Read each line as a separate record
    with open(txt_file, 'r') as file:
        lines = file.readlines()

    # Create a DataFrame with one column, each line is a row in the DataFrame
    df = pd.DataFrame(lines, columns=['Data'])

    # Save the DataFrame to a Parquet file
    df.to_parquet(parquet_file)



for i in range(len(file_locations)):
    text = ""
    #load text using AI
    command = str(str(os.getcwd()) + "/../whisper/whisper.cpp/main -otxt -of output" + " -m ../whisper/whisper.cpp/models/ggml-tiny.en.bin -f " + str(file_locations[i]))
    print("running whisper...")
    #print(command)
    os.system(command)
    print("whisper ran!")
    #load text from file
    with open("output.txt", "r+") as file:
        text = file.read()
        text = tool.correct(text)
        file.write(text)
    #write text to parqet
    name = str(random.randint(1111111,9999999))
    txt_to_parquet('output.txt', f'{name}.parquet')
    os.system("rm output.txt")
    os.system(f"mv *.parquet datasets/")

print("Done! Dataset directory is ",str(os.getcwd()) + "/datasets/")
