#!/usr/bin/env python3
"""生成社交分享卡片图 (og-image.png, 1200x630)。

用法: conda activate mkdocs-site && python scripts/make_og_image.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
OUT = "docs/assets/images/og-image.png"

# 与站点主题一致的靛蓝渐变
TOP = (79, 70, 229)      # indigo-600
BOTTOM = (124, 58, 237)  # violet-600


def load_font(size):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def main():
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # 垂直渐变
    for y in range(H):
        t = y / (H - 1)
        color = tuple(round(a + (b - a) * t) for a, b in zip(TOP, BOTTOM))
        draw.line([(0, y), (W, y)], fill=color)

    # 装饰：散落的白色半透明几何图形（呼应站点的蓝色插画 logo）
    confetti = Image.open("docs/assets/images/favicon.png").convert("RGBA")
    confetti = confetti.resize((360, 360))
    alpha = confetti.getchannel("A").point(lambda a: int(a * 0.16))
    confetti.putalpha(alpha)
    img.paste(confetti, (880, 290), confetti)
    confetti_small = confetti.resize((190, 190))
    img.paste(confetti_small, (-40, -50), confetti_small)

    # 文字
    f_title = load_font(96)
    f_sub = load_font(40)
    f_url = load_font(30)

    cx = W // 2
    draw.text((cx, 215), "超级课程表", font=f_title, fill="white", anchor="mm")
    draw.text((cx, 345), "香港树仁大学课程评价平台", font=f_sub,
              fill=(255, 255, 255, 230), anchor="mm")
    draw.text((cx, 455), "真实课程评价 · 选课参考 · 学生共建",
              font=f_url, fill=(224, 224, 255), anchor="mm")
    draw.text((cx, 530), "www.pass3exceed4.com", font=f_url,
              fill=(255, 255, 255), anchor="mm")

    img.save(OUT, "PNG", optimize=True)
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
