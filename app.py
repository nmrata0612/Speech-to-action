import requests
from pywikihow import search_wikihow
from bs4 import BeautifulSoup
import os
import time
import datetime
import wikipedia
import pyautogui
import pyttsx3
import sqlite3
import speech_recognition as sr
import webbrowser
import PIL
import pyaudio
from PIL import Image
import sys

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id)


def create_table():
    connection = sqlite3.connect("queries.db")
    connect = connection.cursor()
    connect.execute("""CREATE TABLE IF NOT EXISTS queries(
                command text,
                path text
                )""")
    connection.commit()
    connection.close()


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wish_me():
    hour = int(datetime.datetime.now().hour)
    tt = time.strftime("%I:%M %p")
    if (hour >= 0) and (hour < 12):
        speak(f'good morning,its {tt}')
    elif(hour >= 12) and (hour < 18):
        speak(f'good afternoon, {tt}')
    else:
        speak(f'good evening,its {tt}')
    speak("its your assistant, is there any thing i can do?")


def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('listening...')

        audio = r.listen(source)
    try:
        print('recognize')
        queries = r.recognize_google(audio, language='en-IN')
        print(f'user said {queries}')
        speak('user said')
        speak(queries)
    except Exception:
        print('say again')
        speak("say again")
        return 'none'
    return queries


conn = sqlite3.connect("queries.db")
c = conn.cursor()


def task_execution():
    while True:
        query = take_command().lower()

        if 'sleep' in query:
            speak('i am on sleep but, you can call me anytime')
            break

        elif "goodbye" in query:
            sys.exit()

        elif 'wikipedia' in query:
            try:
                query = query.replace('wikipedia ', "")
                print(query)
                results = wikipedia.summary(query, sentences=2)
                print(results)
                speak(results)
            except Exception:
                print("didn't get you, please say again")
                speak("didn't get you, please say again")
                continue

        elif "temperature" in query:
            url = f"https://www.google.com/search?q={query}"
            r = requests.get(url)
            data = BeautifulSoup(r.text, "html.parser")
            temp = data.find('div', class_="BNeawe").text
            speak(f"current{query} is {temp}")

        elif 'learn mode' in query:
            while True:
                speak('what you want to learn')
                how = take_command()
                try:
                    if 'exit' in how or 'close' in how:
                        speak('closing learn mode')
                        break
                    else:
                        how_to = search_wikihow(how, 1)
                        assert len(how_to) == 1
                        print(how_to[0])
                        speak(how_to[0].summary)
                except Exception as e:
                    print("sorry, not able to find this.")
                    speak('sorry, not able to find this.')

        elif 'open' in query:
            try:
                query = query.replace('open ', "")
                if 'google' in query:
                    speak('what you want to search on google')
                    cmd = take_command().lower()
                    webbrowser.open(f"{cmd}")
                else:
                    str1 = f"SELECT path FROM queries WHERE command='{query}'"
                    c.execute(str1)
                    webbrowser.open(c.fetchone()[0])
            except Exception:
                print("didn't get you, please say again")
                speak("didn't get you, please say again")
                continue

        elif "close" in query:
            print(query)
            query = query.replace('close ', "")
            print(query)
            speak(f"closing {query}")
            str2 = f"SELECT path FROM queries WHERE command='{query}'"
            c.execute(str2)
            os.system(f'taskkill /im {query}.exe /f')

        elif 'switch window' in query:
            pyautogui.keyDown('alt')
            pyautogui.press("tab")
            time.sleep(1)
            pyautogui.keyUp('alt')

        elif 'screenshot' in query:
            speak('what should be the name of the screenshot?')
            name = take_command().lower()
            if name == 'none':
                speak("I beg your pardon, what should be the name of the screenshot?")
                name = take_command().lower()
            speak('open the window you want to take screenshot and wait for few seconds')
            time.sleep(5)
            img = pyautogui.screenshot()
            img.save(f'{name}.png')
            speak('done, screenshot saved in main folder')


if __name__ == '__main__':
    # wish_me()
    speak("you need to wake up the system first!")
    while True:
        permission = take_command()
        if "wake up" in permission:
            wish_me()
            task_execution()
        elif "goodbye" in permission:
            sys.exit()

conn.commit()
conn.close()
