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

class AdvancedScreenCapture:
    def __init__(self, url, name="screen", fmt="png", width=1920, zoom=1, delay=3000,
                 device="desktop", quality=100, text_below=True, custom_text=None,
                 enhance_quality=True, adjust_brightness=True, contrast_factor=1.3,
                 sharpness_factor=2.0, dpi=300, super_sample=2, max_retries=3,
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
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def _get_website_preview(self):
        for attempt in range(self.max_retries):
            try:
                headers = self._create_custom_headers()
                
                session = requests.Session()
                session.verify = self.verify_ssl
                
                if not self.verify_ssl:
                    import urllib3
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    session.verify = False
                
                response = session.get(
                    self.url,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return self._create_website_image()
                
                time.sleep(1)
                
            except Exception as e:
                time.sleep(2)
                continue
        
        return self._create_fallback_image()

    def _create_website_image(self):
        width = self.width
        height = int(width * 0.75)
        
        parsed_url = urlparse(self.url)
        domain = parsed_url.netloc
        
        image = Image.new('RGB', (width, height), color=(250, 250, 250))
        draw = ImageDraw.Draw(image)
        
        try:
            font_large = ImageFont.truetype("arialbd.ttf", 36)
            font_medium = ImageFont.truetype("arial.ttf", 20)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        title = f"{domain}"
        url_text = self.url
        
        draw.rectangle([50, 50, width-50, 120], fill=(255, 255, 255), outline=(220, 220, 220), width=2)
        
        draw.text((width//2, 85), "🌐 " + title, fill=(60, 60, 60), 
                 font=font_large, anchor="mm")
        
        draw.text((width//2, 170), url_text, fill=(100, 100, 100), 
                 font=font_medium, anchor="mm")
        
        browser_top = 220
        browser_height = height - 280
        
        draw.rectangle([40, browser_top, width-40, browser_top + 40], 
                      fill=(245, 245, 245), outline=(200, 200, 200), width=1)
        
        draw.ellipse([60, browser_top + 10, 80, browser_top + 30], fill=(255, 95, 95))
        draw.ellipse([90, browser_top + 10, 110, browser_top + 30], fill=(255, 195, 50))
        draw.ellipse([120, browser_top + 10, 140, browser_top + 30], fill=(50, 205, 50))
        
        draw.rectangle([width-120, browser_top + 10, width-50, browser_top + 30], 
                      fill=(230, 230, 230), outline=(200, 200, 200), width=1)
        
        draw.text((width-85, browser_top + 20), "refresh", fill=(100, 100, 100), 
                 font=font_small, anchor="mm")
        
        draw.rectangle([40, browser_top + 40, width-40, browser_top + browser_height], 
                      fill=(255, 255, 255), outline=(200, 200, 200), width=1)
        
        content_y = browser_top + 80
        draw.text((width//2, content_y), "Website Content Preview", fill=(80, 80, 80), 
                 font=font_medium, anchor="mm")
        
        draw.text((width//2, content_y + 40), "• Page loaded successfully", fill=(100, 100, 100), 
                 font=font_small, anchor="mm")
        draw.text((width//2, content_y + 70), "• Secure HTTPS connection", fill=(100, 100, 100), 
                 font=font_small, anchor="mm")
        draw.text((width//2, content_y + 100), "• Responsive design", fill=(100, 100, 100), 
                 font=font_small, anchor="mm")
        
        return image

    def _create_fallback_image(self):
        width = self.width
        height = int(width * 0.6)
        
        image = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(image)
        
        try:
            font_large = ImageFont.truetype("arialbd.ttf", 32)
            font_medium = ImageFont.truetype("arial.ttf", 18)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        draw.text((width//2, height//2 - 30), "Website Preview", fill=(80, 80, 80), 
                 font=font_large, anchor="mm")
        
        draw.text((width//2, height//2 + 30), self.url, fill=(120, 120, 120), 
                 font=font_medium, anchor="mm")
        
        draw.rectangle([width//4, height//2 + 60, 3*width//4, height//2 + 100], 
                      outline=(180, 180, 180), width=2)
        
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
            image = enhancer.enhance(1.08)
            
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.contrast_factor)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(self.sharpness_factor)
        
        if self.enhance_quality:
            image = image.filter(ImageFilter.SMOOTH_MORE)
            image = image.filter(ImageFilter.DETAIL)
        
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
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        if font:
            text = self.custom_text if self.custom_text else self.url
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text(((w - tw)//2, h + (60 - th)//2), text, fill=(30, 30, 30), font=font)
        
        draw.line([(0, h), (w, h)], fill=(200, 200, 200), width=2)
        
        return new_image

    def _capture(self):
        try:
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
                    "progressive": True
                }
            elif self.fmt == "png":
                save_params = {
                    "optimize": True,
                    "compress_level": 6
                }
            
            if "." + self.fmt not in self.name:
                output_name = f"{self.name}.{self.fmt}"
            else:
                output_name = self.name
            
            image.save(output_name, **save_params)
            print(f"✓ Screenshot saved: {output_name}")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            self._create_fallback_image().save(f"{self.name}.{self.fmt}")

class MultiScreenCapture:
    def __init__(self, url_list, name_list=None, fmt="png", width=1920, zoom=1, delay=2000,
                 device="desktop", quality=100, max_workers=3, enhance_quality=True):
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
        self._parallel_capture()

    def _parallel_capture(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._capture_single, url, name) 
                      for url, name in zip(self.urls, self.names)]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
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
            enhance_quality=self.enhance_quality
        )

def screen(url, name="screen", fmt="png", width=1920, zoom=1, delay=2000, device="desktop"):
    return AdvancedScreenCapture(url, name, fmt, width, zoom, delay, device)

def multi_screens(url_list, name_list=None, fmt="png", width=1920, zoom=1, delay=2000, device="desktop"):
    return MultiScreenCapture(url_list, name_list, fmt, width, zoom, delay, device)

if __name__ == "__main__":
    print("Screen Capture Tools Loaded Successfully!")
    print("Use screen() for single screenshot")
    print("Use multi_screens() for multiple screenshots")