import requests
import concurrent.futures
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import time
import random
import os

class SuperScreenCapture:
    def __init__(self, url, name="screen", fmt="png", width=1920, zoom=2, delay=5000,
                 device="desktop", quality=100, text_below=True, custom_text=None,
                 enhance_quality=True, adjust_brightness=True, contrast_factor=1.3,
                 sharpness_factor=2.5, dpi=300, super_sample=3, color_boost=1.15,
                 noise_reduction=True, edge_enhance=True, use_proxy=True,
                 max_retries=10, timeout=60):
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
        self.use_proxy = use_proxy
        self.max_retries = max_retries
        self.timeout = timeout
        
        if self.fmt not in ("png","jpg","jpeg","webp"):
            raise ValueError("Format must be png/jpg/jpeg/webp")
        
        self._setup_proxies()
        self._capture_ultra()

    def _setup_proxies(self):
        self.proxies = []
        if self.use_proxy:
            proxy_sources = [
                {"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"},
                {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"},
                {"http": "http://127.0.0.1:8118", "https": "http://127.0.0.1:8118"},
                {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"},
                {"http": "socks5://telegram.drw.tw:5566", "https": "socks5://telegram.drw.tw:5566"}
            ]
            for proxy in proxy_sources:
                try:
                    test = requests.get("https://httpbin.org/ip", proxies=proxy, timeout=5)
                    if test.status_code == 200:
                        self.proxies.append(proxy)
                except:
                    continue
        
        if not self.proxies:
            self.proxies.append(None)

    def _get_apis(self):
        apis = [
            f"https://image.thum.io/get/fullpage/width/{self.width}/zoom/{self.zoom}/delay/{self.delay}/",
            f"https://api.screenshotmachine.com?key=demo&url={self.url}&dimension={self.width}xfull&device={self.device}",
            f"https://s0.wp.com/mshots/v1/{self.url}?w={self.width}&zoom={self.zoom}",
            f"https://api.pagepeeker.com/v2/thumbs.php?size=x&url={self.url}",
            f"https://api.miniature.io/?width={self.width}&height=1080&url={self.url}",
            f"https://www.screenshotmaster.com/api/v1/screenshot?url={self.url}&width={self.width}",
            f"https://api.url2png.com/v6/P4A4F5A5C5D5/screenshot/?url={self.url}&thumbnail_max_width={self.width}",
            f"https://capture.heartrails.com/{self.width}x0/shorten?{self.url}",
            f"https://api.screenshotlayer.com/api/capture?access_key=7a2d8e0a2f&url={self.url}&viewport={self.width}x1080",
            f"https://api.screenshotapi.net/screenshot?url={self.url}&width={self.width}"
        ]
        
        if self.device == "mobile":
            apis[0] += "mobile/3/"
            apis[1] = apis[1].replace("device=desktop", "device=mobile")
        
        return apis

    def _super_enhance_image(self, image):
        if self.fmt in ("jpg","jpeg"):
            image = image.convert("RGB")
        
        original_size = image.size
        if self.super_sample > 1:
            enhanced_size = (original_size[0] * self.super_sample, original_size[1] * self.super_sample)
            image = image.resize(enhanced_size, Image.Resampling.LANCZOS)
        
        if self.adjust_brightness:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.08)
            
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.contrast_factor)
            
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(self.color_boost)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(self.sharpness_factor)
        
        if self.noise_reduction:
            image = image.filter(ImageFilter.SMOOTH_MORE)
        
        if self.edge_enhance:
            image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            image = image.filter(ImageFilter.DETAIL)
        
        if self.super_sample > 1:
            image = image.resize(original_size, Image.Resampling.LANCZOS)
        
        return image

    def _add_text_below(self, image):
        w, h = image.size
        new_h = h + 80
        bg_color = (250, 250, 250)
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
                font = ImageFont.truetype(path, 32)
                break
            except:
                continue
        
        if font is None:
            try:
                font = ImageFont.load_default()
                font = ImageFont.truetype(font.path, 32)
            except:
                font = ImageFont.load_default()
        
        text = self.custom_text if self.custom_text else self.url
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        shadow_color = (180, 180, 180)
        main_color = (40, 40, 40)
        
        draw.text(((w - tw) // 2 + 2, h + (80 - th) // 2 + 2), text, fill=shadow_color, font=font)
        draw.text(((w - tw) // 2, h + (80 - th) // 2), text, fill=main_color, font=font)
        
        gradient_height = 4
        for i in range(gradient_height):
            alpha = int(255 * (1 - i / gradient_height))
            line_color = (220, 220, 220, alpha)
            draw.line([(0, h + i), (w, h + i)], fill=line_color, width=1)
        
        return new_image

    def _download_with_retry(self, api_url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site"
        }
        
        for attempt in range(self.max_retries):
            proxy = random.choice(self.proxies)
            try:
                response = requests.get(
                    api_url,
                    headers=headers,
                    proxies=proxy,
                    timeout=self.timeout,
                    stream=True,
                    verify=False
                )
                
                if response.status_code == 200:
                    data = response.content
                    if len(data) < 10000:
                        continue
                    
                    image = Image.open(io.BytesIO(data))
                    
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                    
                    return image
            except Exception as e:
                time.sleep(random.uniform(1, 3))
        
        return None

    def _capture_ultra(self):
        apis = self._get_apis()
        
        for attempt in range(self.max_retries * 2):
            random.shuffle(apis)
            
            for api_base in apis:
                try:
                    if "thum.io" in api_base:
                        api_url = api_base + self.url
                    elif "screenshotmachine" in api_base:
                        api_url = api_base
                    else:
                        api_url = api_base.replace("{self.url}", self.url) if "{self.url}" in api_base else api_base
                    
                    image = self._download_with_retry(api_url)
                    
                    if image:
                        if self.enhance_quality:
                            image = self._super_enhance_image(image)
                        
                        if self.text_below:
                            image = self._add_text_below(image)
                        
                        save_params = {}
                        if self.fmt in ("jpg", "jpeg"):
                            image = image.convert("RGB")
                            save_params = {
                                "quality": self.quality,
                                "optimize": True,
                                "progressive": True,
                                "subsampling": 0,
                                "dpi": (self.dpi, self.dpi)
                            }
                        elif self.fmt == "png":
                            save_params = {
                                "optimize": True,
                                "compress_level": 0,
                                "dpi": (self.dpi, self.dpi)
                            }
                        elif self.fmt == "webp":
                            save_params = {
                                "quality": self.quality,
                                "lossless": True,
                                "method": 6
                            }
                        
                        os.makedirs(os.path.dirname(self.name) if os.path.dirname(self.name) else ".", exist_ok=True)
                        
                        if "." + self.fmt not in self.name:
                            output_name = f"{self.name}.{self.fmt}"
                        else:
                            output_name = self.name
                        
                        image.save(output_name, **save_params)
                        
                        final_size = os.path.getsize(output_name) / 1024
                        if final_size < 50:
                            continue
                        
                        return
                except Exception as e:
                    time.sleep(random.uniform(0.5, 2))
            
            time.sleep(random.uniform(2, 5))
        
        raise RuntimeError(f"Failed to capture screenshot for {self.url} after maximum retries")

class UltraMultiScreenCapture:
    def __init__(self, url_list, name_list=None, fmt="png", width=1920, zoom=2, delay=5000,
                 device="desktop", quality=100, max_workers=5, enhance_quality=True,
                 use_proxy=True, timeout=90, retry_count=8):
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
        self.use_proxy = use_proxy
        self.timeout = timeout
        self.retry_count = retry_count
        self._parallel_capture_ultra()

    def _parallel_capture_ultra(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for url, name in zip(self.urls, self.names):
                future = executor.submit(self._capture_single_ultra, url, name)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result(timeout=self.timeout * 2)
                except Exception as e:
                    pass

    def _capture_single_ultra(self, url, name):
        SuperScreenCapture(
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
            sharpness_factor=2.5,
            dpi=300,
            super_sample=3,
            color_boost=1.15,
            noise_reduction=True,
            edge_enhance=True,
            use_proxy=self.use_proxy,
            max_retries=self.retry_count,
            timeout=self.timeout
        )

def super_screen(url, name="screen", fmt="png", width=1920, zoom=2, delay=5000, 
                 device="desktop", quality=100, use_proxy=True):
    return SuperScreenCapture(
        url=url,
        name=name,
        fmt=fmt,
        width=width,
        zoom=zoom,
        delay=delay,
        device=device,
        quality=quality,
        use_proxy=use_proxy
    )

def ultra_multi_screens(url_list, name_list=None, fmt="png", width=1920, zoom=2, 
                        delay=5000, device="desktop", max_workers=5, use_proxy=True):
    return UltraMultiScreenCapture(
        url_list=url_list,
        name_list=name_list,
        fmt=fmt,
        width=width,
        zoom=zoom,
        delay=delay,
        device=device,
        max_workers=max_workers,
        use_proxy=use_proxy
    )

def quick_capture(url, output="quick.png", width=1366):
    return SuperScreenCapture(
        url=url,
        name=output,
        width=width,
        zoom=1,
        delay=2000,
        enhance_quality=False,
        use_proxy=True
    )