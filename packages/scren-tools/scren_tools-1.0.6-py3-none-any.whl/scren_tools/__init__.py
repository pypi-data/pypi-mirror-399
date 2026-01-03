import requests
import concurrent.futures
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io
import time

class AdvancedScreenCapture:
    def __init__(self, url, name="screen", fmt="png", width=1920, zoom=2, delay=5000,
                 device="desktop", quality=100, text_below=True, custom_text=None,
                 enhance_quality=True, adjust_brightness=True, contrast_factor=1.2,
                 sharpness_factor=2.0, dpi=300, super_sample=2):
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
        if self.fmt not in ("png","jpg","jpeg"):
            raise ValueError("Format must be png/jpg/jpeg")
        self._capture()

    def _enhance_image_quality(self, image):
        if self.fmt in ("jpg","jpeg"):
            image = image.convert("RGB")
        original_size = image.size
        enhanced_size = (original_size[0]*self.super_sample, original_size[1]*self.super_sample)
        enhanced_image = image.resize(enhanced_size, Image.Resampling.LANCZOS)
        if self.adjust_brightness:
            enhanced_image = ImageEnhance.Brightness(enhanced_image).enhance(1.1)
            enhanced_image = ImageEnhance.Contrast(enhanced_image).enhance(self.contrast_factor)
            enhanced_image = ImageEnhance.Sharpness(enhanced_image).enhance(self.sharpness_factor)
        final_image = enhanced_image.resize(original_size, Image.Resampling.LANCZOS)
        return final_image

    def _capture(self):
        api_base = f"https://image.thum.io/get/fullpage/width/{self.width}/zoom/{self.zoom}/delay/{self.delay}/"
        if self.device == "mobile":
            api_base += "mobile/3/"
        api_url = api_base + self.url
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept":"image/webp,image/apng,image/*,*/*;q=0.8"
        }
        max_retries = 6
        for attempt in range(max_retries):
            try:
                response = requests.get(api_url, headers=headers, timeout=180, stream=True)
                if response.status_code == 200:
                    data = response.content
                    if len(data) < 50000:
                        if attempt < max_retries-1:
                            time.sleep(4)
                            continue
                        raise RuntimeError("Image data too small")
                    image = Image.open(io.BytesIO(data)).convert("RGBA")
                    if self.enhance_quality:
                        image = self._enhance_image_quality(image)
                    if self.text_below:
                        image = self._add_text_below(image)
                    save_params={}
                    if self.fmt in ("jpg","jpeg"):
                        image = image.convert("RGB")
                        save_params={"quality":100,"optimize":True,"progressive":True}
                    elif self.fmt=="png":
                        save_params={"optimize":True,"compress_level":0}
                    image.save(f"{self.name}.{self.fmt}", **save_params)
                    if attempt < max_retries:
                        return
                else:
                    if attempt < max_retries-1:
                        time.sleep(3)
            except Exception as e:
                if attempt == max_retries-1:
                    raise RuntimeError(f"Screenshot capture failed: {str(e)}")
                time.sleep(3)
        raise RuntimeError("Failed to capture screenshot after multiple attempts")

    def _add_text_below(self, image):
        w,h = image.size
        new_h = h+60
        bg_color=(245,245,245)
        new_image = Image.new("RGBA",(w,new_h),(*bg_color,255))
        new_image.paste(image,(0,0),image)
        draw = ImageDraw.Draw(new_image)
        try:
            font = ImageFont.truetype("arialbd.ttf",28)
        except:
            font = ImageFont.load_default()
        text = self.custom_text if self.custom_text else self.url
        bbox = draw.textbbox((0,0), text, font=font)
        tw = bbox[2]-bbox[0]
        th = bbox[3]-bbox[1]
        draw.text(((w-tw)//2,h+(60-th)//2), text, fill=(30,30,30), font=font)
        draw.line([(0,h),(w,h)], fill=(200,200,200), width=2)
        return new_image

class MultiScreenCapture:
    def __init__(self, url_list, name_list=None, fmt="png", width=1920, zoom=2, delay=5000,
                 device="desktop", quality=100, max_workers=3, enhance_quality=True):
        self.urls=url_list
        self.names=name_list if name_list else [f"screen_{i}" for i in range(len(url_list))]
        self.fmt=fmt
        self.width=width
        self.zoom=zoom
        self.delay=delay
        self.device=device
        self.quality=quality
        self.max_workers=max_workers
        self.enhance_quality=enhance_quality
        self._parallel_capture()

    def _parallel_capture(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures=[executor.submit(self._capture_single,url,name) for url,name in zip(self.urls,self.names)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing a URL: {str(e)}")

    def _capture_single(self,url,name):
        AdvancedScreenCapture(
            url=url,name=name,fmt=self.fmt,width=self.width,zoom=self.zoom,
            delay=self.delay,device=self.device,quality=self.quality,
            text_below=True,enhance_quality=self.enhance_quality,
            adjust_brightness=True,contrast_factor=1.2,sharpness_factor=2.0,
            dpi=300,super_sample=2
        )

def screen(url, name="screen", fmt="png", width=1920, zoom=2, delay=5000, device="desktop"):
    return AdvancedScreenCapture(url,name,fmt,width,zoom,delay,device)

def multi_screens(url_list, name_list=None, fmt="png", width=1920, zoom=2, delay=5000, device="desktop"):
    return MultiScreenCapture(url_list,name_list,fmt,width,zoom,delay,device)
