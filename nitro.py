#!/usr/bin/env python3.7

import getopt
from moviepy.editor import *
import re
import youtube_dl

MOVIE_NAME = "kononTMP.mp4"
OUPUT_MOVIE_NAME = "nitrorar.mp4"
SHORTEST_SILENCE = 0.1
SHORTEST_SOUND = 0.1
SOUND_LEVEL = 0.02

verbose = False


def makeRAR():
    global verbose, MOVIE_NAME, OUPUT_MOVIE_NAME, SOUND_LEVEL, SHORTEST_SOUND, SHORTEST_SILENCE
    video = VideoFileClip(MOVIE_NAME)
    audio = video.audio
    length = video.duration
    begin = 0
    end = 0
    prev_begin = 0
    prev_end = 0
    array = audio.to_soundarray()
    clipTimes = []
    clips = []
    for step in range(int(44100*length)):
        if abs(array[step][0]) > SOUND_LEVEL:
            end = step
        else:
            if begin != end:
                if begin - prev_end < 44100 * SHORTEST_SILENCE:
                    prev_end = end
                    begin = end = step
                else:
                    if prev_end - prev_begin > 44100 * SHORTEST_SOUND:
                        clipTimes.append((prev_begin / 44100, prev_end / 44100))
                        if verbose:
                            print("%f - %f" % (prev_begin / 44100, prev_end / 44100))
                    prev_begin = begin
                    prev_end = end
                    begin = end = step
            else:
                begin = end = step
    if begin != end:
        if begin - prev_end < 44100 * SHORTEST_SILENCE:
            clipTimes.append((prev_begin / 44100, end / 44100))
            if verbose:
                print("%f - %f" % (prev_begin / 44100, end / 44100))
        else:
            clipTimes.append((begin / 44100, end / 44100))
            if verbose:
                print("%f - %f" % (begin / 44100, end / 44100))
    for i, j in clipTimes:
        clips.append(video.subclip(i, j))
    nitrorar = concatenate_videoclips(clips)
    nitrorar.write_videofile(OUPUT_MOVIE_NAME, codec='libx264', audio_codec='aac')


def downloadMovie(link):
    global MOVIE_NAME
    ydl_opts = {
        'format': 'mp4',
        'nocheckcertificate': True,
        'outtmpl': MOVIE_NAME,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])


def main(argv):
    global verbose, MOVIE_NAME, OUPUT_MOVIE_NAME
    link = ''
    try:
        opts, args = getopt.getopt(argv, "vhl:", ["link="])
    except getopt.GetoptError:
        print('test.py (-v) -l <link>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py (-v) -l <link>')
            sys.exit()
        elif opt in ("-l", "--link"):
            link = arg
        elif opt in ("-v", "--verbose"):
            verbose = True
    if not re.search("https://.*youtube.*", link):
        print("Incorrect link")
        print(link)
        return
    downloadMovie(link)
    if os.path.isfile('./' + MOVIE_NAME):
        makeRAR()
        os.remove('./' + MOVIE_NAME)
    else:
        print("Error during download")

if __name__ == "__main__":
    main(sys.argv[1:])