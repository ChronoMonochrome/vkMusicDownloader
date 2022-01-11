#!/usr/bin/python3
#-*- coding: utf-8 -*-

import re
import os
import sys
import asyncio
import getopt
import pickle
from time import time
import vk_api
from vk_api import audio

class vkMusicDownloader():
    CONFIG_DIR = "config"
    USERDATA_FILE = "{}/UserData.datab".format(CONFIG_DIR) #файл хранит логин, пароль и id
    REQUEST_STATUS_CODE = 200 
    path = 'music/'

    def __init__(self):
        self.logger = open("log.txt", "wb+")

    def log(self, msg):
        print(msg)
        msg += "\n"
        self.logger.write(msg.encode("u8"))

    def __exit__(self):
        self.logger.close()

    def auth_handler(self, remember_device=None):
        code = input("Введите код подтверждения\n> ")
        if (remember_device == None):
            remember_device = True
        return code, remember_device

    def saveUserData(self):
        SaveData = [self.login, self.password, self.user_id]

        with open(self.USERDATA_FILE, 'wb') as dataFile:
            pickle.dump(SaveData, dataFile)

    def auth(self, new=False):
        try:
            if (os.path.exists(self.USERDATA_FILE) and new == False):
                with open(self.USERDATA_FILE, 'rb') as DataFile:
                    LoadedData = pickle.load(DataFile)

                self.login = LoadedData[0]
                self.password = LoadedData[1]
                self.user_id = LoadedData[2]
            else:
                if (os.path.exists(self.USERDATA_FILE) and new == True):
                    os.remove(self.USERDATA_FILE)

                self.login = str(input("Введите логин\n> ")) 
                self.password = str(input("Введите пароль\n> ")) 
                self.user_id = str(input("Введите id профиля\n> "))
                self.saveUserData()

            SaveData = [self.login, self.password, self.user_id]
            with open(self.USERDATA_FILE, 'wb') as dataFile:
                pickle.dump(SaveData, dataFile)

            vk_session = vk_api.VkApi(login=self.login, password=self.password)
            try:
                vk_session.auth()
            except:
                vk_session = vk_api.VkApi(login=self.login, password=self.password, auth_handler=self.auth_handler)
                vk_session.auth()
            self.log('Вы успешно авторизовались.')
            self.vk = vk_session.get_api()
            self.vk_audio = audio.VkAudio(vk_session)
        except KeyboardInterrupt:
            self.log('Вы завершили выполнение программы.')

    async def downloadTrack(self, trackId):
        # собственно загружаем нашу музыку
        if trackId >= len(self.tracks):
            return
        track = self.tracks[trackId]
        fileMP3 = "{} - {}.mp3".format(track["artist"], track["title"])
        fileMP3 = fileMP3.replace("/", "_").replace("*", "＊").replace("|", "।")
        self.log("ffmpeg -i {} -c copy -map a \"{}\"".format(track['url'], fileMP3))
        proc = None

        try:
            if os.path.isfile(fileMP3) :
                self.log("{} Уже скачен: {}.".format(trackId, fileMP3))
            else :
                self.log("{} Скачивается: {}.".format(trackId, fileMP3))

                self.log("ffmpeg -i {} -c copy -map a \"{}\"".format(track['url'], fileMP3))
                proc = await asyncio.create_subprocess_exec("ffmpeg", "-i", track['url'], "-c", "copy", "-map", "a", fileMP3)
        except OSError:
            if not os.path.isfile(fileMP3) :
                self.log("{} Не удалось скачать аудиозапись: {}".format(trackId, fileMP3))

        self.log("[%d / %d] %s" % (trackId + 1, len(self.tracks), fileMP3))
        return proc

    async def downloadTracks(self, numThreads = 4):
        start = 0
        while start < len(self.tracks):
            tasks = [asyncio.ensure_future(self.awaitProc(t)) for t in await self.runProcs(start, numThreads) if t]
            if tasks:
                await asyncio.wait(tasks)

            start += numThreads

    async def runProcs(self, start, numThreads):
        tasks = [await self.downloadTrack(i) for i in range(start, start + numThreads)]
        return tasks

    async def awaitProc(self, proc):
        await proc.wait()

    async def main(self, auth_dialog = 'yes'):
        try:
            if (not os.path.exists(self.CONFIG_DIR)):
                os.mkdir(self.CONFIG_DIR)
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            
            if (auth_dialog == 'yes') :
                auth_dialog = str(input("Авторизоваться заново? yes/no\n> "))
                if (auth_dialog == "yes"):
                    self.auth(new=True)
                elif (auth_dialog == "no"):
                    self.auth(new=False)
                else:
                    self.log('Ошибка, неверный ответ.')
                    self.main()
            elif (auth_dialog == 'no') :
                self.auth(new=False)
            
            self.log('Подготовка к скачиванию...')
            
            # В папке music создаем папку с именем пользователя, которого скачиваем.
            info = self.vk.users.get(user_id=self.user_id)
            music_path = "{}/{} {}".format(self.path, info[0]['first_name'], info[0]['last_name'])
            if not os.path.exists(music_path):
                os.makedirs(music_path)

            time_start = time() # сохраняем время начала скачивания
            self.log("Скачивание началось...\n")
            
            os.chdir(music_path) #меняем текущую директорию
            self.tracks = self.vk_audio.get(owner_id=self.user_id)
            self.log('Будет скачано: {} аудиозаписей с Вашей страницы.'.format(len(self.tracks)))
            await self.downloadTracks(numThreads = 4)

            os.chdir("../..")
            albums = self.vk_audio.get_albums(owner_id=self.user_id)
            self.log('У Вас {} альбома.'.format(len(albums)))
            for album in albums:
                self.tracks = self.vk_audio.get(owner_id=self.user_id, album_id=album['id'])
                
                self.log('Будет скачано: {} аудиозаписей из альбома {}.'.format(len(self.tracks), album['title']))
                
                album_path = "{}/{}".format(music_path, album['title'])
                self.log(album_path)
                if not os.path.exists(album_path):
                    os.makedirs(album_path)
                    
                os.chdir(album_path) #меняем текущую директорию
                
                await self.downloadTracks(numThreads = 4)
                
                os.chdir("../../..")
                
            time_finish = time()
            self.log("" + str(len(self.tracks)) + " аудиозаписей скачано за: " + str(time_finish - time_start) + " сек.")
        except KeyboardInterrupt:
            self.log('Вы завершили выполнение программы.')

if __name__ == '__main__':
    vkMD = vkMusicDownloader()

    try:
        opts, args = getopt.getopt(sys.argv, "hn")
    except getopt.GetoptError:
        print('./main.py [-n] [-h]')
        sys.exit(2)
    
    if len(args) == 1 :
        asyncio.run(vkMD.main(auth_dialog = 'yes'))
    else :
        for arg in args:    
            if arg == '-h':
                print('./main.py [-n] [-h]')
                sys.exit()
            elif arg == '-n':
                asyncio.run(vkMD.main(auth_dialog = 'no'))


