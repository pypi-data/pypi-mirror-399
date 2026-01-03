import requests
from PIL import Image, ImageEnhance, ImageFilter
import io
import os
import random
import time

class ScreenCapture:
    def __init__(self, url, name="screen", fmt="png", width=1920, super_sample=3,
                 quality=100, dpi=300, enhance=True, contrast=1.3,
                 sharpness=2.5, color_boost=1.15, noise_reduce=True, edge_enhance=True,
                 max_retries=8, timeout=60):
        self.url = url
        self.name = name
        self.fmt = fmt.lower()
        self.width = width
        self.super_sample = super_sample
        self.quality = quality
        self.dpi = dpi
        self.enhance = enhance
        self.contrast = contrast
        self.sharpness = sharpness
        self.color_boost = color_boost
        self.noise_reduce = noise_reduce
        self.edge_enhance = edge_enhance
        self.max_retries = max_retries
        self.timeout = timeout
        self._capture()

    def _get_image(self):
        apis = [
            f"https://image.thum.io/get/fullpage/width/{self.width}/{self.url}",
            f"https://s0.wp.com/mshots/v1/{self.url}?w={self.width}"
        ]
        for attempt in range(self.max_retries):
            random.shuffle(apis)
            for api in apis:
                try:
                    headers = {
                        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    }
                    r = requests.get(api, headers=headers, timeout=self.timeout, stream=True)
                    if r.status_code == 200:
                        img = Image.open(io.BytesIO(r.content))
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        return img
                except:
                    time.sleep(random.uniform(1,2))
        return None

    def _enhance_image(self, img):
        orig_size = img.size
        if self.super_sample > 1:
            img = img.resize((orig_size[0]*self.super_sample, orig_size[1]*self.super_sample), Image.Resampling.LANCZOS)
        if self.enhance:
            img = ImageEnhance.Brightness(img).enhance(1.08)
            img = ImageEnhance.Contrast(img).enhance(self.contrast)
            img = ImageEnhance.Color(img).enhance(self.color_boost)
            img = ImageEnhance.Sharpness(img).enhance(self.sharpness)
        if self.noise_reduce:
            img = img.filter(ImageFilter.SMOOTH_MORE)
        if self.edge_enhance:
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE).filter(ImageFilter.DETAIL)
        if self.super_sample > 1:
            img = img.resize(orig_size, Image.Resampling.LANCZOS)
        return img

    def _capture(self):
        img = self._get_image()
        if not img:
            raise RuntimeError(f"Failed to capture {self.url}")
        img = self._enhance_image(img)
        save_params={}
        if self.fmt in ("jpg","jpeg"):
            img = img.convert("RGB")
            save_params={"quality":self.quality,"optimize":True,"progressive":True,"subsampling":0,"dpi":(self.dpi,self.dpi)}
        elif self.fmt=="png":
            save_params={"optimize":True,"compress_level":0,"dpi":(self.dpi,self.dpi)}
        elif self.fmt=="webp":
            save_params={"quality":self.quality,"lossless":True,"method":6}
        os.makedirs(os.path.dirname(self.name) if os.path.dirname(self.name) else ".",exist_ok=True)
        output_name = f"{self.name}.{self.fmt}" if "."+self.fmt not in self.name else self.name
        img.save(output_name, **save_params)

def screen(url, name="screen", fmt="png", width=1920, super_sample=3, quality=100):
    return ScreenCapture(url=url, name=name, fmt=fmt, width=width, super_sample=super_sample, quality=quality)
