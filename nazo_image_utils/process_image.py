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
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from hashlib import md5
from typing import Union, Optional


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
    size: Optional[Size] = None


PC_SIZE = Size(1920, 1080)
MOBILE_SIZE = Size(1080, 1920)
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
    md5_set = set()
    pc = dict()
    mobile = dict()
    fail_files = list()
    repeat_files = list()
    unqualified_files = list()
    file_names = list()
    allow = 0

    def __init__(
        self,
        flush: bool = False,
        filter: bool = True,
        gallery_path: str = "./gallary",
        pc_filter_size: Size = PC_SIZE,
        mobile_filter_size: Size = MOBILE_SIZE,
    ) -> None:
        """初始化处理图片程序

        Args:
            flush (bool): 是否清空缓存(重新处理所有图片) 默认 False
            filter (bool): 是否过滤尺寸不对的图片(小于过滤尺寸的图片不会被处理) 默认 True
            gallery_path (str, optional): 图片文件夹路径. 默认 "./gallary".
            pc_filter_size (Size, optional): PC端过滤尺寸. 默认 PC_SIZE(1920, 1080).
            mobile_filter_size (Size, optional): 移动端过滤尺寸. 默认 MOBILE_SIZE(1080, 1920).
        """
        self.pc_filter_size = pc_filter_size
        self.mobile_filter_size = mobile_filter_size
        self.gallery_path = Path(gallery_path)
        self.gallery_path.mkdir(exist_ok=True)

        jpeg_path = Path("./jpeg")
        jpeg_path.mkdir(exist_ok=True)

        webp_path = Path("./webp")
        webp_path.mkdir(exist_ok=True)

        self.flush = flush
        self.filter = filter

    def process_image(self, file: str) -> Union[int, dict]:
        """处理图片程序

        Args:
            file (str): 文件名

        Returns:
            Union[int, dict]: 处理结果 0: 失败 1: 重复 2: 不合格 dict: 处理成功
        """
        try:
            with open(os.path.join("gallary", file), "rb") as source:
                file_content = source.read()
                _hash = md5(file_content).hexdigest()

                if _hash in self.md5_set:
                    return 1

                image = Image.open(source).convert("RGB")
        except Exception as e:
            print(f"error : {e}")
            return 0

        width, height = image.size
        platform = MOBILE if width < height else PC

        if self.filter:
            filter_size = (
                self.pc_filter_size if platform == PC else self.mobile_filter_size
            )
            if width < filter_size.width or height < filter_size.height:
                with suppress(Exception):
                    image.close()
                return 2

        for format in {"webp", "jpeg"}:
            image_copy = image.copy()
            for size_enum in SizeEnum:
                if size_enum.value.size:
                    image_copy.thumbnail(size_enum.value.size.to_tuple())
                image_copy.save(
                    f"{format}/{_hash}.{size_enum.value.name}.{format}",
                    format.upper(),
                    quality=90,
                    subsampling=0,
                    progressive=format == "jpeg",
                )

        with suppress(Exception):
            image.close()
            image_copy.close()  # type: ignore

        self.md5_set.add(_hash)
        return {platform: {_hash: {"source": file}}}

    def load_manifest(self, file_path: str, attribute: str) -> None:
        """加载manifest文件

        Args:
            file_path (str): 文件路径
            attribute (str): 属性名
        """
        if not os.path.exists(file_path):
            return

        with open(file_path, "r") as f:
            manifest: dict = ujson.load(f)
            _manifest = [i["source"] for i in manifest.values()]
            self.md5_set |= {i for i in manifest.keys()}
            self.file_names = list(set(self.file_names) - set(_manifest))
            setattr(self, attribute, manifest)

    def try_process(self):
        if not list(self.gallery_path.iterdir()):
            print("gallary文件夹不存在,已自动创建,请在该文件夹下放图片,再运行此程序")
            return False

        self.file_names = [
            file.name for file in self.gallery_path.iterdir() if file.is_file()
        ]
        if not self.flush:
            self.load_manifest("manifest.json", "pc")
            self.load_manifest("manifest_mobile.json", "mobile")
        files_len = len(self.file_names)
        result_files = {
            0: self.fail_files,
            1: self.repeat_files,
            2: self.unqualified_files,
        }

        with Pool(processes=8) as pool:
            results = [
                pool.apply_async(self.process_image, args=(filename,))
                for filename in self.file_names
            ]

            t = tqdm(total=files_len, desc="Processing images")
            for i, result in enumerate(results):
                img_process = result.get()
                filename = self.file_names[i]
                t.set_description(f"Processing images: {filename}")
                t.update()

                if isinstance(img_process, int):
                    result_files[img_process].append(filename)
                else:
                    self.allow += 1
                    if PC in img_process:
                        self.pc.update(img_process[PC])
                    elif MOBILE in img_process:
                        self.mobile.update(img_process[MOBILE])

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
