import requests
import concurrent.futures
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import time

class AdvancedScreenCapture:
    def __init__(self, url, name="screen", fmt="png", width=3840, zoom=3, delay=4000,
                 device="desktop", quality=100, text_below=True, custom_text=None):
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
        if self.fmt not in ("png", "jpg", "jpeg"):
            raise ValueError("Format must be png/jpg/jpeg")
        self._enhanced_capture()

    def _enhanced_capture(self):
        api_base = f"https://image.thum.io/get/fullpage/width/{self.width}/zoom/{self.zoom}/delay/{self.delay}/"
        if self.device == "mobile":
            api_base += "mobile/2/"
        api_url = api_base + self.url
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(api_url, headers=headers, timeout=120, stream=True)
                if response.status_code == 200:
                    image_data = response.content
                    if len(image_data) < 15000:
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                        raise RuntimeError("Image quality is too low")
                    image = Image.open(io.BytesIO(image_data))
                    if self.fmt in ("jpg", "jpeg"):
                        image = image.convert("RGB")
                    image = self._apply_filters(image)
                    if self.text_below:
                        image = self._add_text_below(image)
                    save_params = {}
                    if self.fmt in ("jpg", "jpeg"):
                        save_params['quality'] = self.quality
                        save_params['optimize'] = True
                        save_params['progressive'] = True
                    elif self.fmt == "png":
                        save_params['optimize'] = True
                        save_params['compress_level'] = 1
                    output_path = f"{self.name}.{self.fmt}"
                    image.save(output_path, **save_params)
                    return
                else:
                    if attempt < max_retries - 1:
                        time.sleep(2)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Screenshot capture failed: {str(e)}")
                time.sleep(2)
        raise RuntimeError("Failed to capture screenshot after multiple attempts")

    def _apply_filters(self, image):
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.15)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.25)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        image = image.filter(ImageFilter.DETAIL)
        image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=2))
        return image

    def _add_text_below(self, image):
        original_width, original_height = image.size
        new_height = original_height + 60
        new_image = Image.new("RGB" if self.fmt in ("jpg", "jpeg") else "RGBA", (original_width, new_height), (255, 255, 255))
        new_image.paste(image, (0, 0))
        try:
            draw = ImageDraw.Draw(new_image)
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
                except:
                    font = ImageFont.load_default()
            text_content = self.custom_text if self.custom_text else f"Screen Shot - {self.url}"
            text_width = draw.textlength(text_content, font=font)
            text_position = ((original_width - text_width) // 2, original_height + 20)
            draw.text(text_position, text_content, fill=(0, 0, 0), font=font)
        except:
            pass
        return new_image

class MultiScreenCapture:
    def __init__(self, url_list, name_list=None, fmt="png", width=3840, zoom=3, delay=4000, device="desktop", quality=100, max_workers=5):
        self.urls = url_list
        self.names = name_list if name_list else [f"screen_{i}" for i in range(len(url_list))]
        self.fmt = fmt
        self.width = width
        self.zoom = zoom
        self.delay = delay
        self.device = device
        self.quality = quality
        self.max_workers = max_workers
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
        AdvancedScreenCapture(url=url, name=name, fmt=self.fmt, width=self.width, zoom=self.zoom, delay=self.delay, device=self.device, quality=self.quality, text_below=True)

def screen(url, name="screen", fmt="png", width=3840, zoom=3, delay=4000, device="desktop"):
    return AdvancedScreenCapture(url, name, fmt, width, zoom, delay, device)

def multi_screens(url_list, name_list=None, fmt="png", width=3840, zoom=3, delay=4000, device="desktop"):
    return MultiScreenCapture(url_list, name_list, fmt, width, zoom, delay, device)
