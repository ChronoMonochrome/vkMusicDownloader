#!/usr/bin/python3
#-*- coding: utf-8 -*-

import re
import os
import sys
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
            print('Вы успешно авторизовались.')
            self.vk = vk_session.get_api()
            self.vk_audio = audio.VkAudio(vk_session)
        except KeyboardInterrupt:
            print('Вы завершили выполнение программы.')

    def downloadTracks(self, tracks):
        for index, track in enumerate(tracks, start = 1):
            fileMP3 = "{} - {}.mp3".format(track["artist"], track["title"])
            fileMP3 = fileMP3.replace("/", "_").replace("*", "＊").replace("|", "।")
            try:
                if os.path.isfile(fileMP3) :
                    print("{} Уже скачен: {}.".format(index, fileMP3))
                else :
                    print("{} Скачивается: {}.".format(index, fileMP3), end = "")

                    os.system("ffmpeg -i {} -c copy -map a \"{}\"".format(track['url'], fileMP3))
            except OSError:
                if not os.path.isfile(fileMP3) :
                    print("{} Не удалось скачать аудиозапись: {}".format(index, fileMP3))

    def main(self, auth_dialog = 'yes'):
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
                    print('Ошибка, неверный ответ.')
                    self.main()
            elif (auth_dialog == 'no') :
                self.auth(new=False)
            
            print('Подготовка к скачиванию...')
            
            # В папке music создаем папку с именем пользователя, которого скачиваем.
            info = self.vk.users.get(user_id=self.user_id)
            music_path = "{}/{} {}".format(self.path, info[0]['first_name'], info[0]['last_name'])
            if not os.path.exists(music_path):
                os.makedirs(music_path)

            time_start = time() # сохраняем время начала скачивания
            print("Скачивание началось...\n")
            
            os.chdir(music_path) #меняем текущую директорию
            tracks = self.vk_audio.get(owner_id=self.user_id)
            print('Будет скачано: {} аудиозаписей с Вашей страницы.'.format(len(tracks)))
            
            # собственно циклом загружаем нашу музыку 
            self.downloadTracks(tracks)

            os.chdir("../..")
            albums = self.vk_audio.get_albums(owner_id=self.user_id)
            print('У Вас {} альбома.'.format(len(albums)))
            for album in albums:
                tracks = self.vk_audio.get(owner_id=self.user_id, album_id=album['id'])
                
                print('Будет скачано: {} аудиозаписей из альбома {}.'.format(len(tracks), album['title']))
                
                album_path = "{}/{}".format(music_path, album['title'])
                print(album_path)
                if not os.path.exists(album_path):
                    os.makedirs(album_path)
                    
                os.chdir(album_path) #меняем текущую директорию
                
                self.downloadTracks(tracks)
                
                os.chdir("../../..")
                
            time_finish = time()
            print("" + str(len(tracks)) + " аудиозаписей скачано за: " + str(time_finish - time_start) + " сек.")
        except KeyboardInterrupt:
            print('Вы завершили выполнение программы.')

if __name__ == '__main__':
    vkMD = vkMusicDownloader()

    try:
        opts, args = getopt.getopt(sys.argv, "hn")
    except getopt.GetoptError:
        print('./main.py [-n] [-h]')
        sys.exit(2)
    
    if len(args) == 1 :
        vkMD.main(auth_dialog = 'yes')
    else :
        for arg in args:    
            if arg == '-h':
                print('./main.py [-n] [-h]')
                sys.exit()
            elif arg == '-n':
                vkMD.main(auth_dialog = 'no')


