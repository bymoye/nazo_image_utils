# -*- coding: utf-8 -*-
# @Author: bymoye
# @Date:   2022-03-20 20:38:54
# @Last Modified by:   bymoye
# @Last Modified time: 2022-03-20 21:01:05
import ujson,random
from blacksheep import Application, ContentDispositionType,file
app = Application()

@app.router.get('/')
async def index():
    with open('manifest.json') as f:
        temp = ujson.load(f)
        with open('webp/' + random.choice(list(temp.keys())) + '.source.webp',mode='rb') as f:
            return file(
                f.read(),"image/webp",content_disposition=ContentDispositionType.INLINE,
            )