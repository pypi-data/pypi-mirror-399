import asyncio
import os
from PIL import Image, ImageEnhance, ImageFilter
from pyppeteer import launch

class ScreenCapture:
    def __init__(self, url, name="screen", fmt="png", width=1920, height=1080,
                 scale=2, quality=100, dpi=300,
                 enhance=True, contrast=1.3, sharpness=2.5,
                 color_boost=1.15, noise_reduce=True, edge_enhance=True):
        self.url = url
        self.name = name
        self.fmt = fmt.lower()
        self.width = width
        self.height = height
        self.scale = scale
        self.quality = quality
        self.dpi = dpi
        self.enhance = enhance
        self.contrast = contrast
        self.sharpness = sharpness
        self.color_boost = color_boost
        self.noise_reduce = noise_reduce
        self.edge_enhance = edge_enhance
        asyncio.get_event_loop().run_until_complete(self._capture())

    async def _capture(self):
        browser = await launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        page = await browser.newPage()
        await page.setViewport({
            "width": self.width,
            "height": self.height,
            "deviceScaleFactor": self.scale
        })
        await page.goto(self.url, {"waitUntil": "networkidle2", "timeout": 0})
        await asyncio.sleep(2)
        tmp_path = "__raw_screen.png"
        await page.screenshot({
            "path": tmp_path,
            "fullPage": True
        })
        await browser.close()
        img = Image.open(tmp_path)
        if self.enhance:
            img = self._enhance_image(img)
        if self.fmt in ("jpg", "jpeg"):
            img = img.convert("RGB")
            img.save(
                f"{self.name}.{self.fmt}",
                quality=self.quality,
                optimize=True,
                progressive=True,
                subsampling=0,
                dpi=(self.dpi, self.dpi)
            )
        elif self.fmt == "png":
            img.save(
                f"{self.name}.{self.fmt}",
                optimize=True,
                compress_level=0,
                dpi=(self.dpi, self.dpi)
            )
        elif self.fmt == "webp":
            img.save(
                f"{self.name}.{self.fmt}",
                quality=self.quality,
                lossless=True,
                method=6
            )
        os.remove(tmp_path)

    def _enhance_image(self, img):
        img = ImageEnhance.Brightness(img).enhance(1.05)
        img = ImageEnhance.Contrast(img).enhance(self.contrast)
        img = ImageEnhance.Color(img).enhance(self.color_boost)
        img = ImageEnhance.Sharpness(img).enhance(self.sharpness)
        if self.noise_reduce:
            img = img.filter(ImageFilter.SMOOTH_MORE)
        if self.edge_enhance:
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE).filter(ImageFilter.DETAIL)
        return img

def screen(url, name="screen", fmt="png", width=1920, height=1080,
           scale=2, quality=100):
    return ScreenCapture(
        url=url,
        name=name,
        fmt=fmt,
        width=width,
        height=height,
        scale=scale,
        quality=quality
    )
