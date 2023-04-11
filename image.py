# -*- coding: utf-8 -*-
# @Author: bymoye
# @Date:   2021-06-02 12:13:43
# @Last Modified by:   bymoye
# @Last Modified time: 2023-04-12 00:11:23
import os, ujson
from tqdm import tqdm
from enum import Enum
from PIL import Image
from multiprocessing import Pool
from dataclasses import dataclass
from hashlib import md5
from typing import Union


@dataclass(frozen=True)
class Size:
    width: int
    height: int

    # 转tuple
    def to_tuple(self):
        return (self.width, self.height)


@dataclass
class SizeShortCode:
    name: str
    size: Size = None


FORMAT = {"webp", "jpeg"}
# SIZE_NAME = {"source", "th", "md"}
# 过滤尺寸 要开设置
PC_SIZE = Size(1920, 1080)
MOBILE_SIZE = Size(1080, 1920)
# FILTER_TYPE = (PC, MOBILE)
PC = "pc"
MOBILE = "mobile"


class SizeEnum(Enum):
    SOURCE = SizeShortCode("source")
    TH = SizeShortCode("th", Size(900, 600))
    MD = SizeShortCode("md", Size(50, 30))

    @property
    def value(self) -> SizeShortCode:
        return super().value


class ProcessImage:
    pc = dict()
    mobile = dict()
    md5_set = set()
    fail_files = list()
    repeat_files = list()
    unqualified_files = list()
    allow = 0

    def __init__(self, flush: bool, filter: bool) -> None:
        if not os.path.exists("./jpeg"):
            os.mkdir("./jpeg")
        if not os.path.exists("./webp"):
            os.mkdir("./webp")
        self.flush = flush
        self.filter = filter

    def process_image(self, file) -> Union[int, dict]:
        try:
            source = open(f"gallary/{file}", "rb")
            _hash = md5(source.read()).hexdigest()
            if _hash in self.md5_set:
                source.close()
                return 1
            image = Image.open(source).convert("RGB")
        except Exception as e:
            print(f"error : {e}")
            return 0
        width, height = image.size
        platform = MOBILE if width < height else PC

        if self.filter:
            filter_size = PC_SIZE if platform == PC else MOBILE_SIZE
            if width < filter_size.width or height < filter_size.height:
                source.close()
                image.close()
                return 2

        for format in FORMAT:
            _image = image.copy()
            for size_enum in SizeEnum:
                if size_enum.value.size:
                    _image.thumbnail(size_enum.value.size.to_tuple())
                _image.save(
                    f"{format}/{_hash}.{size_enum.value.name}.{format}",
                    format.upper(),
                    quality=90,
                    subsampling=0,
                    progressive=format == "jpeg",
                )
        source.close()
        image.close()
        _image.close()
        self.md5_set.add(_hash)
        return {platform: {_hash: {"source": file}}}

    def try_process(self):
        if not os.path.exists("./gallary"):
            os.mkdir("./gallary")
            print("gallary文件夹不存在,已自动创建,请在该文件夹下放图片,再运行此程序")
            return False
        file_names = [
            file
            for file in os.listdir("gallary")
            if os.path.isfile(os.path.join("gallary", file))
        ]
        if not self.flush:
            if os.path.exists("manifest.json"):
                with open("manifest.json", "r") as f:
                    manifest: dict = ujson.load(f)
                    _manifest = [i["source"] for i in list(manifest.values())]
                    self.md5_set = self.md5_set | {i for i in manifest.keys()}
                    file_names = list(set(file_names) - set(_manifest))
                    self.pc = manifest
            if os.path.exists("manifest_mobile.json"):
                with open("manifest_mobile.json", "r") as f:
                    manifest: dict = ujson.load(f)
                    _manifest = [i["source"] for i in manifest.values()]
                    self.md5_set = self.md5_set | {i for i in manifest.keys()}
                    file_names = list(set(file_names) - set(_manifest))
                    self.mobile = manifest
        files_len = len(file_names)
        # progress = 0
        with Pool(processes=8) as pool:
            results = []
            for filename in file_names:
                results.append(pool.apply_async(self.process_image, args=(filename,)))
            processed_files = 0
            for r in tqdm(results, total=files_len, desc="Processing images"):
                img_process = r.get()
                filename = file_names[processed_files]
                processed_files += 1
                if isinstance(img_process, int):
                    if img_process == 0:
                        self.fail_files.append(filename)
                        # print(f"\n出现错误文件:{filename}")
                    elif img_process == 1:
                        self.repeat_files.append(filename)
                        # print(f"\n{filename} 已存在")
                    elif img_process == 2:
                        self.unqualified_files.append(filename)
                        # print(f"\n{filename} 尺寸不达标")
                else:
                    self.allow += 1
                    if PC in img_process:
                        self.pc.update(img_process[PC])
                    elif MOBILE in img_process:
                        self.mobile.update(img_process[MOBILE])
                print(
                    f"\rProcessing images: {filename} ({processed_files}/{files_len})",
                    end="",
                    flush=True,
                )

        with open("manifest.json", "w+") as json_file:
            ujson.dump(self.pc, json_file)

        with open("manifest_mobile.json", "w+") as json_file:
            ujson.dump(self.mobile, json_file)
        print(
            f"""
            任务已完成
            总计数量：{files_len}
            成功数量：{self.allow}
            
            失败数量：{len(self.fail_files)}
            失败文件：{self.fail_files}
            
            重复数量：{len(self.repeat_files)}
            重复文件：{self.repeat_files}
            
            不合格数量：{len(self.unqualified_files)}
            不合格文件：{self.unqualified_files}
            
            当前总计   pc   图片数量：{len(self.pc)}
            当前总计 mobile 图片数量：{len(self.mobile)}
            """
        )


if __name__ == "__main__":
    # 如果 flush 为True 将会清空原有的manifest.json文件
    # 如果 flush 为False 将会追加新的manifest.json文件
    # 如果filter 为True 将会过滤掉不合格的图片
    temp = ProcessImage(flush=False, filter=True)
    temp.try_process()
