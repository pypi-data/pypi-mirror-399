import requests
import concurrent.futures
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import time
import os
import random
import socket
import ssl
from urllib.parse import urlparse
from http.client import HTTPSConnection
import gzip

class AdvancedScreenCapture:
    def __init__(self, url, name="screen", fmt="png", width=1920, zoom=1, delay=3000,
                 device="desktop", quality=100, text_below=True, custom_text=None,
                 enhance_quality=True, adjust_brightness=True, contrast_factor=1.3,
                 sharpness_factor=2.0, dpi=300, super_sample=2, max_retries=5,
                 timeout=30, verify_ssl=False, compress_image=True):
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
        self.max_retries = max_retries
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.compress_image = compress_image
        
        if self.fmt not in ("png","jpg","jpeg","webp"):
            raise ValueError("Format must be png/jpg/jpeg/webp")
        
        if not self.url.startswith(('http://', 'https://')):
            self.url = 'https://' + self.url
        
        self._capture()

    def _create_custom_headers(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
        ]
        
        accept_encodings = [
            "gzip, deflate, br",
            "gzip, deflate",
            "br",
            ""
        ]
        
        accept_languages = [
            "en-US,en;q=0.9",
            "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
            "en-GB,en;q=0.9",
            "en-CA,en;q=0.9"
        ]
        
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": random.choice(accept_encodings),
            "Accept-Language": random.choice(accept_languages),
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
            "DNT": "1"
        }

    def _get_website_preview(self):
        for attempt in range(self.max_retries):
            try:
                headers = self._create_custom_headers()
                
                session = requests.Session()
                session.verify = self.verify_ssl
                
                if not self.verify_ssl:
                    requests.packages.urllib3.disable_warnings()
                    session.verify = False
                
                response = session.get(
                    self.url,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=True,
                    stream=True
                )
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'image' in content_type:
                        image_data = response.content
                        if len(image_data) > 10000:
                            return Image.open(io.BytesIO(image_data))
                    
                    time.sleep(self.delay / 1000)
                    
                    parsed_url = urlparse(self.url)
                    domain = parsed_url.netloc
                    
                    screenshot_urls = [
                        f"https://{domain}/screenshot.png",
                        f"https://{domain}/preview.png",
                        f"https://{domain}/thumbnail.png",
                        f"https://{domain}/og-image.png",
                        f"https://{domain}/assets/screenshot.png",
                        f"https://{domain}/images/preview.jpg",
                        f"https://{domain}/static/og-image.png",
                    ]
                    
                    for screenshot_url in screenshot_urls:
                        try:
                            img_response = session.get(
                                screenshot_url,
                                headers=headers,
                                timeout=10,
                                stream=True
                            )
                            if img_response.status_code == 200:
                                img_data = img_response.content
                                if len(img_data) > 50000:
                                    image = Image.open(io.BytesIO(img_data))
                                    return self._resize_image(image)
                        except:
                            continue
                    
                    favicon_url = f"https://{domain}/favicon.ico"
                    try:
                        fav_response = session.get(favicon_url, timeout=10)
                        if fav_response.status_code == 200:
                            fav_data = fav_response.content
                            if len(fav_data) > 1000:
                                favicon = Image.open(io.BytesIO(fav_data))
                                return self._create_placeholder(favicon)
                    except:
                        pass
                    
                    return self._create_fallback_image()
                
                time.sleep(2)
                
            except (requests.exceptions.Timeout, 
                    requests.exceptions.ConnectionError,
                    socket.timeout,
                    ssl.SSLError) as e:
                time.sleep(random.uniform(2, 4))
                continue
            except Exception as e:
                time.sleep(random.uniform(1, 3))
                continue
        
        return self._create_fallback_image()

    def _create_placeholder(self, favicon):
        width = self.width
        height = int(width * 0.6)
        
        image = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(image)
        
        try:
            font_large = ImageFont.truetype("arialbd.ttf", 48)
            font_medium = ImageFont.truetype("arial.ttf", 24)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        parsed_url = urlparse(self.url)
        domain = parsed_url.netloc
        
        draw.text((width//2, height//3), "🌐", fill=(100, 100, 100), 
                 font=font_large, anchor="mm")
        
        draw.text((width//2, height//2), domain, fill=(50, 50, 50), 
                 font=font_medium, anchor="mm")
        
        draw.text((width//2, height//2 + 40), self.url, fill=(100, 100, 100), 
                 font=font_medium, anchor="mm")
        
        if favicon:
            favicon_resized = favicon.resize((64, 64), Image.Resampling.LANCZOS)
            image.paste(favicon_resized, (width//2 - 32, height//3 - 80), 
                       favicon_resized if favicon.mode == 'RGBA' else None)
        
        return image

    def _create_fallback_image(self):
        width = self.width
        height = int(width * 0.6)
        
        image = Image.new('RGB', (width, height), color=(230, 230, 230))
        draw = ImageDraw.Draw(image)
        
        try:
            font_large = ImageFont.truetype("arialbd.ttf", 40)
            font_small = ImageFont.truetype("arial.ttf", 20)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        title = "Website Preview"
        url_text = self.url
        
        draw.text((width//2, height//2 - 30), title, fill=(80, 80, 80), 
                 font=font_large, anchor="mm")
        
        draw.text((width//2, height//2 + 30), url_text, fill=(120, 120, 120), 
                 font=font_small, anchor="mm")
        
        draw.rectangle([width//4, height//2 + 60, 3*width//4, height//2 + 100], 
                      outline=(180, 180, 180), width=2)
        draw.text((width//2, height//2 + 80), "Live Preview", fill=(100, 100, 100), 
                 font=font_small, anchor="mm")
        
        return image

    def _resize_image(self, image):
        original_width, original_height = image.size
        
        if self.device == "mobile":
            target_width = min(self.width, 480)
        else:
            target_width = min(self.width, 1920)
        
        if original_width > target_width:
            ratio = target_width / original_width
            target_height = int(original_height * ratio)
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        return image

    def _enhance_image_quality(self, image):
        if self.fmt in ("jpg","jpeg"):
            image = image.convert("RGB")
        
        original_size = image.size
        
        if self.super_sample > 1:
            enhanced_size = (original_size[0] * self.super_sample, 
                           original_size[1] * self.super_sample)
            image = image.resize(enhanced_size, Image.Resampling.LANCZOS)
        
        if self.adjust_brightness:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
            
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.contrast_factor)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(self.sharpness_factor)
            
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.05)
        
        if self.enhance_quality:
            image = image.filter(ImageFilter.DETAIL)
            image = image.filter(ImageFilter.SMOOTH_MORE)
            image = image.filter(ImageFilter.EDGE_ENHANCE)
        
        if self.super_sample > 1:
            image = image.resize(original_size, Image.Resampling.LANCZOS)
        
        return image

    def _add_text_below(self, image):
        w, h = image.size
        new_h = h + 60
        bg_color = (245, 245, 245)
        new_image = Image.new("RGBA", (w, new_h), (*bg_color, 255))
        new_image.paste(image, (0, 0), image if image.mode == 'RGBA' else None)
        
        draw = ImageDraw.Draw(new_image)
        
        font = None
        font_paths = [
            "arialbd.ttf",
            "Arial Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf"
        ]
        
        for path in font_paths:
            try:
                font = ImageFont.truetype(path, 28)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        text = self.custom_text if self.custom_text else self.url
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        draw.text(((w - tw)//2, h + (60 - th)//2), text, fill=(30, 30, 30), font=font)
        
        for i in range(3):
            y_pos = h + i
            alpha = int(255 * (1 - i/3))
            line_color = (200, 200, 200, alpha)
            draw.line([(0, y_pos), (w, y_pos)], fill=line_color, width=1)
        
        return new_image

    def _capture(self):
        image = self._get_website_preview()
        
        if self.enhance_quality:
            image = self._enhance_image_quality(image)
        
        if self.text_below:
            image = self._add_text_below(image)
        
        os.makedirs(os.path.dirname(self.name) if os.path.dirname(self.name) else ".", 
                   exist_ok=True)
        
        save_params = {}
        if self.fmt in ("jpg","jpeg"):
            image = image.convert("RGB")
            save_params = {
                "quality": self.quality,
                "optimize": True,
                "progressive": True,
                "subsampling": 0,
                "dpi": (self.dpi, self.dpi)
            }
        elif self.fmt == "png":
            if self.compress_image:
                save_params = {
                    "optimize": True,
                    "compress_level": 9 if self.quality > 90 else 6
                }
            else:
                save_params = {
                    "optimize": True,
                    "compress_level": 0
                }
        elif self.fmt == "webp":
            save_params = {
                "quality": self.quality,
                "lossless": self.quality == 100,
                "method": 6
            }
        
        if "." + self.fmt not in self.name:
            output_name = f"{self.name}.{self.fmt}"
        else:
            output_name = self.name
        
        image.save(output_name, **save_params)

class MultiScreenCapture:
    def __init__(self, url_list, name_list=None, fmt="png", width=1920, zoom=1, delay=3000,
                 device="desktop", quality=100, max_workers=3, enhance_quality=True,
                 timeout=30, verify_ssl=False):
        self.urls = url_list
        self.names = name_list if name_list else [f"screen_{i}" for i in range(len(url_list))]
        self.fmt = fmt
        self.width = width
        self.zoom = zoom
        self.delay = delay
        self.device = device
        self.quality = quality
        self.max_workers = max_workers
        self.enhance_quality = enhance_quality
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._parallel_capture()

    def _parallel_capture(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._capture_single, url, name) 
                      for url, name in zip(self.urls, self.names)]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result(timeout=self.timeout * 2)
                except:
                    pass

    def _capture_single(self, url, name):
        AdvancedScreenCapture(
            url=url,
            name=name,
            fmt=self.fmt,
            width=self.width,
            zoom=self.zoom,
            delay=self.delay,
            device=self.device,
            quality=self.quality,
            text_below=True,
            enhance_quality=self.enhance_quality,
            adjust_brightness=True,
            contrast_factor=1.3,
            sharpness_factor=2.0,
            dpi=300,
            super_sample=2,
            max_retries=3,
            timeout=self.timeout,
            verify_ssl=self.verify_ssl
        )

def screen(url, name="screen", fmt="png", width=1920, zoom=1, delay=3000, device="desktop", quality=100):
    return AdvancedScreenCapture(
        url=url,
        name=name,
        fmt=fmt,
        width=width,
        zoom=zoom,
        delay=delay,
        device=device,
        quality=quality
    )

def multi_screens(url_list, name_list=None, fmt="png", width=1920, zoom=1, delay=3000, 
                  device="desktop", max_workers=3):
    return MultiScreenCapture(
        url_list=url_list,
        name_list=name_list,
        fmt=fmt,
        width=width,
        zoom=zoom,
        delay=delay,
        device=device,
        max_workers=max_workers
    )

def quick_capture(url, output="screen.png", width=1366):
    return AdvancedScreenCapture(
        url=url,
        name=output,
        width=width,
        zoom=1,
        delay=2000,
        enhance_quality=False,
        max_retries=2,
        timeout=15
    )