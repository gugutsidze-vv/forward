from datetime import datetime, timedelta
import os
import time
import cv2
import settings
import json


def round_up_time(dt, delta):
    return dt + (datetime.min-dt) % delta


def creatingCacheFile(path):
    listdir = os.listdir(path)
    cacheList = {}
    array = []
    for file in listdir:
        cacheList = ({'name': file, 'size': os.path.getsize(
            path+"/"+file), 'date': datetime.fromtimestamp(os.path.getctime(path+"/"+file)).strftime("%Y%m%d_%H%M%S")})
        array.append(cacheList)
    return array


def writeLog(text):
    datetime_today = time.strftime("%Y-%m-%d %H:%M:%S")
    date_today = time.strftime("%Y-%m-%d")
    f = open(settings.log_folder+"/"+str(date_today)+"_log.log", "a+")
    f.write(str(datetime_today)+" - "+text+"\n")
    f.close()


def creatingPlaylist():
    listdir = os.listdir(settings.soucre_path)
    # работаем с файлами из списка расширений
    data = "<wait start='follow' title='* * * * *' />\n"
    for file in listdir:
        # Если файл является видео, то готовим строку для добавления в плейлист
        if file.endswith(settings.extensions_videos):
            # Считаем длинну видео
            video = cv2.VideoCapture(settings.soucre_path+"/"+file)
            frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = int(video.get(cv2.CAP_PROP_FPS))
            seconds = int(frames/fps)
            videoTime = str(timedelta(seconds=seconds))
            data += '<movie file="'+str(settings.soucre_path+'/' + file).replace(
                "/", "\\") + '" duration="0'+str(videoTime)+'" file_duration="'+str(videoTime)+'"/>\n'
        elif file.endswith(settings.extensions_pictures):
            # Проверяем на вхождение в имя параметра длительности воспроизведения
            if "time_" in file:
                # Пытаемся получить значение в секундах, если попытка неудачна, то выводим значение в 10 секунд
                try:
                    # если подстрока находится в конце строки
                    if "_" not in file.split('time_')[1]:
                        duration = int(file.split('time_')[1].split('.')[0])
                    # если подстрока находится в середине строки
                    else:
                        duration = int(file.split('time_')[1].split('_')[0])
                        # если возникла какая-то ошибка, то принудительно ставим продолжительность 10 сек
                except BaseException:
                    duration = 10
            # если не указана длина в имени файла, то по-умолчанию продолжительность ставим 10 сек
            else:
                duration = 10
            duration = str(timedelta(seconds=duration))
            data += '<picture file="' + \
                str(settings.soucre_path+'/'+file).replace("/", "\\") + \
                '" duration="0'+duration+'.00" />\n'
    data += '<jump value="repeat script" />'
    now = datetime.now()
    time = round_up_time(now, timedelta(minutes=10))
    date_today = time.strftime("%Y%m%d_%H%M%S")
    # for i in os.listdir(settings.config_folder):
    # os.remove(settings.config_folder+"/"+i)
    f = open(settings.config_folder+"/Autoload_"+str(date_today)+".airx", "w")
    f.write(data)
    f.close()


# Проверяем наличие файла предыдущей конфигурации
# cache={}
if os.path.exists(settings.config_folder+'/old_cache.json'):
    # Если файл уже создан, то считываем его и сверяем папку с придыдущим слепком файлов
    with open(settings.config_folder+'/old_cache.json') as f:
        lastVersion = json.load(f)
    newVersion = json.dumps(creatingCacheFile(settings.soucre_path))
    newVersion = json.loads(newVersion)
    if newVersion == lastVersion:
        writeLog("Изменений нет")
    else:
        creatingPlaylist()
        writeLog("Создан файл - Autoload_"+str(round_up_time(datetime.now(), timedelta(minutes=10)).strftime("%Y%m%d_%H%M%S")))
else:
    # Если файла нет, то сканируем папку, создаем файл и файл расписания
    jsonString = json.dumps(creatingCacheFile(settings.soucre_path))
    jsonFile = open(settings.config_folder+"/old_cache.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()
