# В данном файле будет реализован телеграм-бот
import emoji
from moviepy.editor import VideoFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import pygame
from mutagen.mp3 import MP3
from moviepy.editor import *
import moviepy.editor as mpe
import os
from pydub import AudioSegment
import json
import time
import base64
import re  # для split
import requests
import telebot  # - модуль  с помощью, которого делать бота, как его установить смотри статью, которую я скинул в гайде


def movies_builder(TEXT1, images):
    kol = 0
    for i in TEXT1:
        image = Image.open(images[kol])

        # КОНВЕРТИРУЕМ ИЗОБРАЖЕНИЕ ИЗ RGBA В RGB
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        font = ImageFont.truetype("arial.ttf", 50)
        drawer = ImageDraw.Draw(image)
        drawer.text((200, 750), i, font=font, fill='black')

        image.save(str(kol) + '2.jpg')
        kol += 1
    time = []
    for i in range(0, len(TEXT1)):
        tts = gTTS(TEXT1[i], lang='ru')
        # ИСПРАВЛЕНИЕ: используем уникальное имя для каждого MP3 файла
        mp3_filename = f"output_{i}.mp3"
        tts.save(mp3_filename)
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_filename)
        pygame.mixer.music.play()
        f = MP3(mp3_filename)
        f1 = int(f.info.length)
        time.append(f1)
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    clips = {}
    for i in range(0, len(TEXT1)):
        clips1 = ImageClip(str(i) + "2.jpg").set_duration(int(time[i]))
        clips["var" + str(i)] = clips1
    l = list(clips.values())
    finalcl = concatenate_videoclips([*l], method="compose")
    finalcl.write_videofile('video.mp4', fps=24)

    # ИСПРАВЛЕНИЕ: используем правильные имена MP3 файлов
    sound = AudioSegment.from_mp3("output_0.mp3")
    for i in range(1, len(TEXT1)):
        sound1 = AudioSegment.from_mp3(f"output_{i}.mp3")  # !!!!
        sound += sound1
    # ЗАМЕНА ПУТИ: убираем длинный путь
    sound.export("Result.mp3", format="mp3")

    vidos = VideoFileClip("video.mp4")
    video_length = vidos.duration

    # ЗАМЕНА ПУТЕЙ: убираем длинные пути
    audio_background = mpe.AudioFileClip("Result.mp3")
    my_clip = mpe.VideoFileClip("video.mp4")
    filename, file_extension = os.path.splitext("video.mp4")

    new_audioclip = mpe.CompositeAudioClip([audio_background])
    my_clip.audio = new_audioclip
    output_path = f"{filename}_with_audio{file_extension}"
    my_clip.write_videofile(output_path, codec="libx264", fps=24, audio_codec='aac')
    clip1 = VideoFileClip("LOGO.mp4")
    clip2 = VideoFileClip("video_with_audio.mp4")
    final_clip = concatenate_videoclips([clip1, clip2], method="compose")
    final_clip.write_videofile("ready.mp4")
    return 0

    pass


# ЗАМЕНА НАЧИНАЕТСЯ ЗДЕСЬ - старый класс заменяем на новый рабочий
class FusionBrainAPI:
    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline_id, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'pipeline_id': (None, pipeline_id),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['result']['files']
            attempts -= 1
            time.sleep(delay)


# ЗАМЕНА ЗАКОНЧИЛАСЬ

# токен для получения доступа к боту которого ты создал в BotFather
# Вставь его в значение этой переменной. Он будет похож на 6776320160:AAHVZ4oYR3Tqа_-g0gBwR2HPPXn89fwhHKр

TOKEN = '7196021874:AAGuQphQ9G-MpqcYC432qSJiXjAFTHcA2Js'

bot = telebot.TeleBot(TOKEN)


# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id,
                     'Привет! ' + '\U0001F603' + '\nЯ бот, который генерирует видеоряд с озвучкой по тексту' + '\U0001F60E')


# Получение сообщений от юзера
@bot.message_handler(content_types=['text'])
def draw(message):
    delet2 = bot.send_message(message.chat.id, "Генерация картинок..." + '\U0001F914')
    IMAGES = []
    po_zaprosu = re.split(r'[;.!?]\s', message.text)
    for i in po_zaprosu:
        if i == "":
            po_zaprosu.remove(i)
    with open("STIX.txt", "w+") as file:  # все это я пишу, чтобы поместить текст стихотворный  в одну длинную строчку
        file.write(message.text)
    text = " "
    with open('STIX.txt', 'r') as file:
        for line in file:
            text += line
    text = re.split('[\n]', text)
    stroka = ' '.join(text)
    mess_text = re.split(r'[;.!?]\s', stroka)  # разделение текста
    for i in mess_text:
        if i == "":
            mess_text.remove(i)
    krt = 1
    for i in mess_text:
        if __name__ == '__main__':  # генерация картинки
            # ИСПОЛЬЗУЕМ НОВЫЙ РАБОЧИЙ API
            api = FusionBrainAPI('https://api-key.fusionbrain.ai/', '8DC462F982203BD6F6F118ECE5CB8273',
                                 '4E2200683B7F3A5DF8C7E1CA530D0C65')
            pipeline_id = api.get_pipeline()
            i = "картинка, которое обозначает " + " ' " + i + " ' "
            uuid = api.generate(i.lower(), pipeline_id)
            files = api.check_generation(uuid)
            if files:
                image_base64 = files[0]
                image_data = base64.b64decode(image_base64)
                with open(str(krt) + ".jpg", "wb") as file:
                    file.write(image_data)
                IMAGES.append(str(krt) + ".jpg")
        krt += 1
    delet1 = bot.send_message(message.chat.id, "Сборка видео..." + '\U0001F9D0')
    movies_builder(po_zaprosu, IMAGES)
    bot.delete_message(message.chat.id, delet2.message_id)
    bot.delete_message(message.chat.id, delet1.message_id)
    # ЗАМЕНА ПУТИ: убираем длинный путь
    video_ = open("ready.mp4", 'rb')
    bot.send_video(message.chat.id, video_)
    bot.send_message(message.chat.id, "Видео готово!" + '\U0001F4AA')


def image_generator(request):
    """
      Эта функция для генерации изображений на вход она принимает параметр request - это будет наш текстовый запрос
      Если появились вопросы - пиши
    """
    pass

    pass


# Запускаем бота
bot.polling(none_stop=True, interval=0)

