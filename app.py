from pytube import YouTube
from flask import Flask, send_file
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import threading
import time
import os
app = Flask(__name__)
api = Api(app)
CORS(app)


@app.route('/info/')
def info():
    parser = reqparse.RequestParser()
    parser.add_argument('url', required=True)
    args = parser.parse_args()
    return getinfo(args["url"])


@app.route('/download/')
def download_route():
    parser = reqparse.RequestParser()
    parser.add_argument('url', required=True)
    parser.add_argument('res', required=True)
    args = parser.parse_args()
    filename = os.path.abspath(download(args["url"], args["res"]))
    threading.Thread(target=remove_file, name="Remove File",
                     args=(filename,)).start()
    return send_file(filename, attachment_filename=filename)


def remove_file(path):
    time.sleep(10 * 60)
    os.remove(path)


def getinfo(url):
    try:
        yt = YouTube(url)
        return {
            "title": yt.title,
            "description": yt.description,
            "thumbnail": yt.thumbnail_url,
            "views": yt.views,
            "res": list(getres(yt)[1])}
    except:
        return {
            "title": "Hata",
            "description": "Lütfen düzgün bir URL girdiğinizden emin olun",
            "thumbnail": "Hata",
            "views": "Hata",
            "res": "Hata"}


def getres(video):
    # DEAL WITH FIRST - NO
    try:
        res_list = [144, 240, 360, 480, 720,
                    1080, 1440, 2160, 4320, 8640]
        res_dict = {}
        streams = video.streams
        for res in res_list:
            filtered_streams = streams.filter(
                res=f"{res}p")  # , progressive=True)
            if len(filtered_streams) > 0:
                res_dict[res] = filtered_streams.first()
        info_arr = []
        for key, value in res_dict.items():
            info_arr.append([key, value.is_progressive, value.filesize_approx])
        return res_dict, info_arr
    except Exception as e:
        return {}, {}


def download(url, res):
    yt = YouTube(url)
    resolutions = getres(yt)[0]
    selected_video = resolutions[int(res)]
    selected_video.download()
    return selected_video.default_filename


# download("https://www.youtube.com/watch?v=CLGzSBcIVlE")

if __name__ == "__main__":
    app.run()
