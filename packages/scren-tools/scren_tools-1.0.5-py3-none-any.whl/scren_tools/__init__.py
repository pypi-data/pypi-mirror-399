import requests
import concurrent.futures
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import time
import hashlib

class AdvancedScreenCapture:
    def __init__(self, url, name="screen", fmt="png", width=3840, zoom=3, delay=8000,
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
        
        if self.fmt not in ("png", "jpg", "jpeg"):
            raise ValueError("Format must be png/jpg/jpeg")
        self._capture()

    def _enhance_image_quality(self, image):
        if self.fmt in ("jpg", "jpeg"):
            image = image.convert("RGB")
        
        original_size = image.size
        enhanced_size = (original_size[0] * self.super_sample, original_size[1] * self.super_sample)
        
        enhanced_image = image.resize(enhanced_size, Image.Resampling.LANCZOS)
        
        if self.adjust_brightness:
            from PIL import ImageEnhance
            brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
            enhanced_image = brightness_enhancer.enhance(1.1)
            
            contrast_enhancer = ImageEnhance.Contrast(enhanced_image)
            enhanced_image = contrast_enhancer.enhance(self.contrast_factor)
            
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
            enhanced_image = sharpness_enhancer.enhance(self.sharpness_factor)
        
        final_image = enhanced_image.resize(original_size, Image.Resampling.LANCZOS)
        
        return final_image

    def _capture(self):
        api_base = f"https://image.thum.io/get/fullpage/width/{self.width}/zoom/{self.zoom}/delay/{self.delay}/wait/{self.delay//2000}/"
        if self.device == "mobile":
            api_base += "mobile/3/"
        api_url = api_base + self.url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site'
        }
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.get(api_url, headers=headers, timeout=180, stream=True)
                if response.status_code == 200:
                    image_data = response.content
                    
                    if len(image_data) < 50000:
                        if attempt < max_retries - 1:
                            time.sleep(3)
                            continue
                        raise RuntimeError("Image quality is too low")
                    
                    image = Image.open(io.BytesIO(image_data))
                    
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    elif image.mode == 'LA':
                        image = image.convert('RGBA')
                    
                    if self.enhance_quality:
                        image = self._enhance_image_quality(image)
                    
                    if self.text_below:
                        image = self._add_text_below(image)
                    
                    save_params = {}
                    if self.fmt in ("jpg", "jpeg"):
                        save_params['quality'] = 100
                        save_params['optimize'] = True
                        save_params['progressive'] = True
                        save_params['subsampling'] = 0
                        save_params['qtables'] = 'web_high'
                        image = image.convert("RGB")
                    elif self.fmt == "png":
                        save_params['optimize'] = True
                        save_params['compress_level'] = 0
                        if image.mode == 'RGBA':
                            save_params['pnginfo'] = image.info
                    
                    image.info['dpi'] = (self.dpi, self.dpi)
                    
                    output_path = f"{self.name}.{self.fmt}"
                    image.save(output_path, **save_params)
                    
                    with open(output_path, 'rb') as f:
                        file_size = len(f.read())
                    
                    if file_size < 100000:
                        if attempt < max_retries - 1:
                            time.sleep(3)
                            continue
                    
                    return
                else:
                    if attempt < max_retries - 1:
                        time.sleep(3)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Screenshot capture failed: {str(e)}")
                time.sleep(3)
        raise RuntimeError("Failed to capture screenshot after multiple attempts")

    def _add_text_below(self, image):
        original_width, original_height = image.size
        new_height = original_height + 80
        background_color = (245, 245, 245)
        
        if image.mode == 'RGBA':
            new_image = Image.new("RGBA", (original_width, new_height), (*background_color, 255))
            new_image.paste(image, (0, 0), image if image.mode == 'RGBA' else None)
        else:
            new_image = Image.new("RGB", (original_width, new_height), background_color)
            new_image.paste(image, (0, 0))
        
        try:
            draw = ImageDraw.Draw(new_image)
            try:
                font = ImageFont.truetype("arialbd.ttf", 28)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", 28)
                except:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
                    except:
                        try:
                            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
                        except:
                            font = ImageFont.load_default(size=28)
            
            text_content = self.custom_text if self.custom_text else f"{self.url}"
            bbox = draw.textbbox((0, 0), text_content, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_position = ((original_width - text_width) // 2, original_height + (80 - text_height) // 2)
            
            draw.text(text_position, text_content, fill=(30, 30, 30), font=font)
            
            draw.line([(0, original_height), (original_width, original_height)], fill=(200, 200, 200), width=2)
            
        except:
            pass
        
        return new_image

class MultiScreenCapture:
    def __init__(self, url_list, name_list=None, fmt="png", width=3840, zoom=3, delay=8000, 
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
            futures = [executor.submit(self._capture_single, url, name) for url, name in zip(self.urls, self.names)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing a URL: {str(e)}")

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
            contrast_factor=1.2,
            sharpness_factor=2.0,
            dpi=300,
            super_sample=2
        )

def screen(url, name="screen", fmt="png", width=3840, zoom=3, delay=8000, device="desktop"):
    return AdvancedScreenCapture(
        url=url,
        name=name,
        fmt=fmt,
        width=width,
        zoom=zoom,
        delay=delay,
        device=device,
        quality=100,
        text_below=True,
        enhance_quality=True,
        adjust_brightness=True,
        contrast_factor=1.2,
        sharpness_factor=2.0,
        dpi=300,
        super_sample=2
    )

def multi_screens(url_list, name_list=None, fmt="png", width=3840, zoom=3, delay=8000, device="desktop"):
    return MultiScreenCapture(
        url_list=url_list,
        name_list=name_list,
        fmt=fmt,
        width=width,
        zoom=zoom,
        delay=delay,
        device=device,
        quality=100,
        max_workers=3,
        enhance_quality=True
    )