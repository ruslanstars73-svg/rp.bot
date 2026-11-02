import random
import requests
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


class CertificateMixin:

    def generate_certificate(self, recipient_id, recipient_name, issuer_name):
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        for _ in range(6000):
            x, y = random.randint(0, width), random.randint(0, height)
            c = random.randint(20, 50)
            draw.point((x, y), fill=(c, c, c))

        for _ in range(15):
            x, y = random.randint(0, width), random.randint(0, height)
            r = random.randint(40, 130)
            draw.ellipse((x-r, y-r, x+r, y+r), outline=(80, 70, 40), width=2)

        for i in range(-height, width+height, 20):
            draw.line((i, 0, i+height, height), fill=(40, 40, 40), width=1)
            draw.line((i, height, i+height, 0), fill=(40, 40, 40), width=1)

        border = 30
        draw.rectangle([border, border, width-border, height-border], outline=(200, 170, 80), width=4)
        draw.rectangle([border+12, border+12, width-border-12, height-border-12], outline=(200, 170, 80), width=2)

        def corner(x, y, size=50):
            for r in range(size, 0, -10):
                draw.arc((x-r, y-r, x+r, y+r), 0, 90, fill=(200, 170, 80), width=2)
            draw.line((x, y, x+size, y), fill=(200, 170, 80), width=2)
            draw.line((x, y, x, y+size), fill=(200, 170, 80), width=2)
            for i in range(5, size, 10):
                draw.arc((x-i, y-i, x+i, y+i), 0, 90, fill=(150, 130, 60), width=1)
        corner(border+5, border+5, 55)
        corner(width-border-5, border+5, 55)
        corner(border+5, height-border-5, 55)
        corner(width-border-5, height-border-5, 55)

        for (x, y) in [(border+15, border+15), (border+15, height//2), (border+15, height-border-15),
                       (width-border-15, border+15), (width-border-15, height//2), (width-border-15, height-border-15),
                       (width//2, border+15), (width//2, height-border-15)]:
            draw.ellipse((x-5, y-5, x+5, y+5), fill=(200, 170, 80))
            draw.ellipse((x-3, y-3, x+3, y+3), fill=(255, 220, 140))

        def get_font(size):
            for p in ["DejaVuSans.ttf", "arial.ttf",
                      "/system/fonts/Roboto-Regular.ttf",
                      "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
                try: return ImageFont.truetype(p, size)
                except: continue
            return ImageFont.load_default()

        font_title = get_font(48)
        font_name = get_font(38)
        font_diagnosis = get_font(40)
        font_footer = get_font(28)
        font_date = get_font(26)
        font_small = get_font(20)

        def glow(text, x, y, font, color, glow_color=None, glow_size=2):
            if glow_color is None:
                glow_color = color
            for i in range(glow_size, 0, -1):
                alpha = int(30 * (1 - i/glow_size))
                for dx, dy in [(-i,-i),(i,-i),(-i,i),(i,i)]:
                    draw.text((x+dx, y+dy), text, font=font, fill=(*glow_color, alpha))
            draw.text((x, y), text, font=font, fill=color)

        title = "СЕРТИФИКАТ ВРУЧЕН"
        tw = draw.textlength(title, font=font_title)
        tx, ty = (width - tw) // 2, 40
        glow(title, tx, ty, font_title, (220, 180, 60), (200, 160, 40), 3)
        under_y = ty + font_title.getbbox(title)[3] + 5
        draw.line((tx, under_y, tx + tw, under_y), fill=(220, 180, 60), width=3)

        # Печать
        sc = (width - 90, height - 90)
        sr = 55
        for i in range(3, 0, -1):
            draw.ellipse((sc[0]-sr-i, sc[1]-sr-i, sc[0]+sr+i, sc[1]+sr+i), outline=(180, 60, 60), width=2)
        draw.ellipse((sc[0]-sr, sc[1]-sr, sc[0]+sr, sc[1]+sr), outline=(200, 80, 80), width=5)
        draw.ellipse((sc[0]-sr+8, sc[1]-sr+8, sc[0]+sr-8, sc[1]+sr-8), outline=(180, 60, 60), width=2)
        draw.text((sc[0]-35, sc[1]-10), "ПЕЧАТЬ", font=font_small, fill=(200, 80, 80))

        draw.text((40, height-50), f"№ {random.randint(100000, 999999)}", font=font_small, fill=(200, 170, 80))

        # Герб
        sc2 = (width//2, height-60); sr2 = 40
        for i in range(3, 0, -1):
            draw.ellipse((sc2[0]-sr2-i, sc2[1]-sr2-i, sc2[0]+sr2+i, sc2[1]+sr2+i), outline=(200, 170, 80), width=2)
        draw.ellipse((sc2[0]-sr2, sc2[1]-sr2, sc2[0]+sr2, sc2[1]+sr2), outline=(220, 190, 120), width=4)
        fw, fh = 30, 20
        fx, fy = sc2[0]-fw//2, sc2[1]-fh//2
        draw.rectangle((fx, fy, fx+fw//3, fy+fh), fill=(255, 255, 255))
        draw.rectangle((fx+fw//3, fy, fx+2*fw//3, fy+fh), fill=(0, 50, 255))
        draw.rectangle((fx+2*fw//3, fy, fx+fw, fy+fh), fill=(255, 0, 0))
        draw.rectangle((fx, fy, fx+fw, fy+fh), outline=(200, 170, 80), width=1)

        # Подпись
        sy = height - 100
        draw.line((width-250, sy, width-50, sy), fill=(200, 170, 80), width=3)
        draw.text((width-200, sy+5), "Подпись врача", font=font_small, fill=(200, 170, 80))

        # Аватар
        av_size = 120; av_x, av_y = 60, 130
        try:
            user_data = self.vk.method('users.get', {'user_ids': recipient_id, 'fields': 'photo_200'})
            if user_data and 'photo_200' in user_data[0]:
                resp = requests.get(user_data[0]['photo_200'], timeout=10)
                if resp.status_code == 200:
                    av = Image.open(BytesIO(resp.content)).resize((av_size, av_size), Image.Resampling.LANCZOS)
                    mask = Image.new('L', (av_size, av_size), 0)
                    ImageDraw.Draw(mask).ellipse((0, 0, av_size, av_size), fill=255)
                    img.paste(av, (av_x, av_y), mask)
                    for i in range(3, 0, -1):
                        draw.ellipse((av_x-i, av_y-i, av_x+av_size+i, av_y+av_size+i), outline=(200, 170, 80), width=2)
                    draw.ellipse((av_x, av_y, av_x+av_size, av_y+av_size), outline=(220, 190, 120), width=3)
        except Exception as e:
            print(f"⚠️ Аватарка: {e}")

        # Кому
        label = "КОМУ:"
        label_x = av_x + av_size + 40
        label_y = av_y + 15
        glow(label, label_x, label_y, font_name, (220, 180, 60), (200, 160, 40), 2)
        label_width = draw.textlength(label, font=font_name)

        name_text = recipient_name.upper()
        name_x = label_x + label_width + 15
        glow(name_text, name_x, label_y, font_name, (255, 255, 255), (200, 200, 220), 3)
        full_w = draw.textlength(label + " " + name_text, font=font_name)
        under_y2 = label_y + font_name.getbbox(name_text)[3] + 5
        draw.line((label_x, under_y2, label_x + full_w, under_y2), fill=(220, 180, 60), width=2)

        # Диагноз
        diagnosis = "ДИАГНОЗ: Редкостный Еблан"
        dw = draw.textlength(diagnosis, font=font_diagnosis)
        dx, dy = (width - dw) // 2, av_y + av_size + 50
        glow(diagnosis, dx, dy, font_diagnosis, (220, 60, 60), (180, 40, 40), 3)
        under_y3 = dy + font_diagnosis.getbbox(diagnosis)[3] + 5
        draw.line((dx, under_y3, dx + dw, under_y3), fill=(220, 60, 60), width=2)

        # От кого
        footer_label = "ВЫДАН ЛИЧНО ОТ:"
        issuer_text = issuer_name.upper()
        fl_w = draw.textlength(footer_label, font=font_footer)
        it_w = draw.textlength(issuer_text, font=font_footer)
        fx = (width - fl_w - 20 - it_w) // 2
        fy = dy + 60
        glow(footer_label, fx, fy, font_footer, (220, 180, 60), (200, 160, 40), 2)
        issuer_x = fx + fl_w + 15
        glow(issuer_text, issuer_x, fy, font_footer, (255, 255, 255), (200, 200, 220), 3)
        full_fw = draw.textlength(footer_label + " " + issuer_text, font=font_footer)
        under_y4 = fy + font_footer.getbbox(issuer_text)[3] + 5
        draw.line((fx, under_y4, fx + full_fw, under_y4), fill=(220, 180, 60), width=2)

        # Дата
        date_str = datetime.now().strftime("%d.%m.%Y")
        dtx, dty = width - 200, height - 60
        glow(date_str, dtx, dty, font_date, (220, 180, 60), (200, 160, 40), 2)
        dt_w = draw.textlength(date_str, font=font_date)
        under_y5 = dty + font_date.getbbox(date_str)[3] + 5
        draw.line((dtx, under_y5, dtx + dt_w, under_y5), fill=(220, 180, 60), width=2)

        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes