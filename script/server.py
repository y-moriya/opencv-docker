#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import http.server as s
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib.parse import unquote
import requests
import cv2
import numpy as np
from PIL import Image

class MyHandler(s.BaseHTTPRequestHandler):
    def do_POST(self):
        self.make_data()
    def do_GET(self):
        self.make_data()
    def hasWashitsu(self, filepath):
        Image.open(filepath).convert("RGB").save("./images/converted.jpg")
        img = cv2.imread("./images/converted.jpg")
        temp = cv2.imread("./images/washitsu_template.jpg")

        # グレースケール変換
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        temp = cv2.cvtColor(temp, cv2.COLOR_RGB2GRAY)

        # テンプレート画像の高さ・幅
        h, w = temp.shape

        res = cv2.matchTemplate(gray, temp, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.7)
        if (len(loc[0]) + len(loc[1])) > 0:
            return "true"
        else:
            return "false"
    def make_data(self):
        # urlパラメータを取得
        parsed = urlparse(self.path)
        # urlパラメータを解析
        params = parse_qs(parsed.query)

        try:
            url = unquote(params['url'][0])
            path = urlparse(url)
            filepath = "./images/" + os.path.basename(path.path)
            response = requests.get(url)
            if response.status_code != 200:
                self.send_error(400, "requests.get(url) failed. status code: " + str(response.status_code))
                self.end_headers()
                return

            data = response.content
            with open(filepath, mode = "wb") as f:
                f.write(data)
                
            result = self.hasWashitsu(filepath)

            body = '{ "hasWashitsu": ' + result + ' }'
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Content-length', len(body.encode()))
            self.end_headers()
            self.wfile.write(body.encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
            self.end_headers()
            return

host = '0.0.0.0'
port = 8000
httpd = s.HTTPServer((host, port), MyHandler)
print('サーバを起動しました。ポート:%s' % port)
httpd.serve_forever()
