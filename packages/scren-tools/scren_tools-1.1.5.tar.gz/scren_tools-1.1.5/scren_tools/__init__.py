import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import io, os, random, time
import concurrent.futures

class ScreenCapture:
    def __init__(self, url, name="screen", fmt="png", width=1920, super_sample=3,
                 quality=100, dpi=300, enhance=True, contrast=1.3, sharpness=2.5,
                 color_boost=1.15, noise_reduce=True, edge_enhance=True,
                 max_retries=8, timeout=60, text_below=True, custom_text="Zeus",
                 font_size=36):
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
        self.text_below = text_below
        self.custom_text = custom_text
        self.font_size = font_size
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
                    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                    r = requests.get(api, headers=headers, timeout=self.timeout, stream=True)
                    if r.status_code == 200:
                        img = Image.open(io.BytesIO(r.content))
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        return img
                except:
                    time.sleep(random.uniform(0.5,1.5))
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

    def _add_text(self, img):
        w,h = img.size
        new_h = h + self.font_size + 20
        new_img = Image.new("RGBA",(w,new_h),(255,255,255,255))
        new_img.paste(img,(0,0),img if img.mode=='RGBA' else None)
        draw = ImageDraw.Draw(new_img)
        font_paths=["arialbd.ttf","Arial Bold.ttf","/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/System/Library/Fonts/Supplemental/Arial Bold.ttf","C:\\Windows\\Fonts\\arialbd.ttf"]
        font=None
        for p in font_paths:
            try:
                font = ImageFont.truetype(p,self.font_size)
                break
            except:
                continue
        if not font:
            font = ImageFont.load_default()
        text = self.custom_text
        bbox = draw.textbbox((0,0),text,font=font)
        tw,th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        shadow_color = (180,180,180)
        main_color = (20,20,20)
        draw.text(((w-tw)//2+2,h+(self.font_size+20-th)//2+2),text,shadow_color,font=font)
        draw.text(((w-tw)//2,h+(self.font_size+20-th)//2),text,main_color,font=font)
        for i in range(4):
            draw.line([(0,h+i),(w,h+i)],fill=(220,220,220,int(255*(1-i/4))),width=1)
        return new_img

    def _capture(self):
        img = self._get_image()
        if not img:
            raise RuntimeError(f"Failed to capture {self.url}")
        img = self._enhance_image(img)
        if self.text_below:
            img = self._add_text(img)
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

class MultiScreenCapture:
    def __init__(self, url_list, name_list=None, fmt="png", width=1920, super_sample=3, max_workers=5):
        self.urls = url_list
        self.names = name_list if name_list else [f"screen_{i}" for i in range(len(url_list))]
        self.fmt = fmt
        self.width = width
        self.super_sample = super_sample
        self.max_workers = max_workers
        self._parallel_capture()

    def _capture_single(self,url,name):
        ScreenCapture(url,name,fmt=self.fmt,width=self.width,super_sample=self.super_sample)

    def _parallel_capture(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for url,name in zip(self.urls,self.names):
                futures.append(executor.submit(self._capture_single,url,name))
            for f in concurrent.futures.as_completed(futures):
                try:
                    f.result()
                except:
                    pass

def screen(url, name="screen", fmt="png", width=1920, super_sample=3):
    return ScreenCapture(url=url, name=name, fmt=fmt, width=width, super_sample=super_sample)

def multi_screens(url_list, name_list=None, fmt="png", width=1920, super_sample=3, max_workers=5):
    return MultiScreenCapture(url_list,name_list,fmt,width,super_sample,max_workers)
