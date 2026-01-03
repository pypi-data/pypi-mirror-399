import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import os
import random
import time

class ScreenCapture:
    def __init__(self, url, name="screen", fmt="png", width=1920, zoom=2, delay=5000,
                 device="desktop", quality=100, text_below=True, custom_text=None,
                 enhance_quality=True, adjust_brightness=True, contrast_factor=1.3,
                 sharpness_factor=2.5, dpi=300, super_sample=3, color_boost=1.15,
                 noise_reduction=True, edge_enhance=True, max_retries=10, timeout=60):
        self.url = url
        self.name = name
        self.fmt = fmt.lower()
        self.width = width
        self.zoom = zoom
        self.delay = delay
        self.device = device
        self.quality = max(1, min(100, quality))
        self.text_below = text_below
        self.custom_text = custom_text
        self.enhance_quality = enhance_quality
        self.adjust_brightness = adjust_brightness
        self.contrast_factor = contrast_factor
        self.sharpness_factor = sharpness_factor
        self.dpi = dpi
        self.super_sample = super_sample
        self.color_boost = color_boost
        self.noise_reduction = noise_reduction
        self.edge_enhance = edge_enhance
        self.max_retries = max_retries
        self.timeout = timeout
        self._capture_ultra()

    def _get_screenshot(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        for _ in range(self.max_retries):
            try:
                resp = requests.get(f"https://api.screenshotapi.net/screenshot?url={self.url}&width={self.width}", headers=headers, timeout=self.timeout, stream=True)
                if resp.status_code == 200:
                    img = Image.open(io.BytesIO(resp.content))
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    return img
            except:
                time.sleep(random.uniform(1,3))
        return None

    def _enhance_image(self, img):
        orig_size = img.size
        if self.super_sample > 1:
            img = img.resize((orig_size[0]*self.super_sample, orig_size[1]*self.super_sample), Image.Resampling.LANCZOS)
        if self.adjust_brightness:
            img = ImageEnhance.Brightness(img).enhance(1.08)
            img = ImageEnhance.Contrast(img).enhance(self.contrast_factor)
            img = ImageEnhance.Color(img).enhance(self.color_boost)
            img = ImageEnhance.Sharpness(img).enhance(self.sharpness_factor)
        if self.noise_reduction:
            img = img.filter(ImageFilter.SMOOTH_MORE)
        if self.edge_enhance:
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE).filter(ImageFilter.DETAIL)
        if self.super_sample > 1:
            img = img.resize(orig_size, Image.Resampling.LANCZOS)
        return img

    def _add_text_below(self, img):
        w,h = img.size
        new_h = h+80
        new_img = Image.new("RGBA",(w,new_h),(250,250,250,255))
        new_img.paste(img,(0,0),img if img.mode=='RGBA' else None)
        draw = ImageDraw.Draw(new_img)
        font_paths=["arialbd.ttf","Arial Bold.ttf","/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/System/Library/Fonts/Supplemental/Arial Bold.ttf","C:\\Windows\\Fonts\\arialbd.ttf"]
        font=None
        for p in font_paths:
            try:
                font = ImageFont.truetype(p,32)
                break
            except:
                continue
        if not font:
            font = ImageFont.load_default()
        text = self.custom_text if self.custom_text else self.url
        bbox = draw.textbbox((0,0),text,font=font)
        tw,th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text(((w-tw)//2+2,h+(80-th)//2+2),text,(180,180,180),font=font)
        draw.text(((w-tw)//2,h+(80-th)//2),text,(40,40,40),font=font)
        for i in range(4):
            draw.line([(0,h+i),(w,h+i)],fill=(220,220,220, int(255*(1-i/4))),width=1)
        return new_img

    def _capture_ultra(self):
        img = self._get_screenshot()
        if not img:
            raise RuntimeError(f"Failed to capture {self.url}")
        if self.enhance_quality:
            img = self._enhance_image(img)
        if self.text_below:
            img = self._add_text_below(img)
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
        img.save(output_name,**save_params)

def screen(url, name="screen", fmt="png", width=1920, zoom=2, delay=5000,
           device="desktop", quality=100):
    return ScreenCapture(url=url, name=name, fmt=fmt, width=width, zoom=zoom,
                         delay=delay, device=device, quality=quality)
