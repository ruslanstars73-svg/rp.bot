import random
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


class DemotivatorMixin:

    def create_demotivator(self, peer_id, user_id, text, event):
        try:
            msg_id = event.message_id if hasattr(event, 'message_id') else event.message['id']
            msg_info = self.vk.method('messages.getById', {'message_ids': [msg_id]})['items'][0]
            photo_url = None

            for att in msg_info.get('attachments', []):
                if att['type'] == 'photo':
                    sizes = att['photo'].get('sizes', [])
                    if sizes:
                        photo_url = sizes[-1]['url']
                    break

            if not photo_url and 'reply_message' in msg_info:
                for att in msg_info['reply_message'].get('attachments', []):
                    if att['type'] == 'photo':
                        sizes = att['photo'].get('sizes', [])
                        if sizes:
                            photo_url = sizes[-1]['url']
                        break

            if not photo_url:
                self.send(peer_id, "❌ Прикрепите фото или ответьте на сообщение с фото!")
                return

            bottom_text = text.upper().strip() if text else "ТУТ ДОЛЖЕН БЫТЬ ТЕКСТ"

            resp = requests.get(photo_url, timeout=15)
            if resp.status_code != 200:
                self.send(peer_id, "❌ Не удалось загрузить фото")
                return

            original_img = Image.open(BytesIO(resp.content))
            img_width, img_height = original_img.size
            border_black = 40
            border_white = 10
            bottom_padding = 180

            new_width = img_width + (border_black + border_white) * 2
            new_height = img_height + (border_black + border_white) * 2 + bottom_padding

            result = Image.new('RGB', (new_width, new_height), color=(0, 0, 0))
            photo_x = border_black + border_white
            photo_y = border_black + border_white
            result.paste(original_img, (photo_x, photo_y))
            draw = ImageDraw.Draw(result)

            draw.rectangle([photo_x - border_white, photo_y - border_white,
                            photo_x + img_width + border_white, photo_y + img_height + border_white],
                           outline=(255, 255, 255), width=border_white)

            font_size = 52
            font = None
            for path in ["Arial.ttf", "DejaVuSans.ttf",
                         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                         "/system/fonts/Roboto-Regular.ttf", "arial.ttf"]:
                try:
                    font = ImageFont.truetype(path, font_size)
                    break
                except: continue

            if font is None:
                default_font = ImageFont.load_default()
                char_w, char_h = 16, 24
                max_chars = 18
                lines, cur = [], ""
                for word in bottom_text.split():
                    if len(cur) + len(word) + 1 <= max_chars:
                        cur = (cur + " " + word) if cur else word
                    else:
                        lines.append(cur); cur = word
                if cur: lines.append(cur)
                if not lines: lines = [bottom_text[:18]]
                lines = lines[:4]
                text_y = new_height - bottom_padding + 30
                for line in lines:
                    text_w = len(line) * char_w
                    text_x = (new_width - text_w) // 2
                    for i, ch in enumerate(line):
                        x = text_x + i * char_w
                        for dx, dy in [(0,0),(1,0),(0,1),(1,1)]:
                            draw.text((x+dx, text_y+dy), ch, fill=(255,255,255), font=default_font)
                        for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                            draw.text((x+dx, text_y+dy), ch, fill=(0,0,0), font=default_font)
                    text_y += char_h + 8
            else:
                max_chars = 25
                lines, cur = [], ""
                for word in bottom_text.split():
                    if len(cur) + len(word) + 1 <= max_chars:
                        cur = (cur + " " + word) if cur else word
                    else:
                        lines.append(cur); cur = word
                if cur: lines.append(cur)
                if not lines: lines = [bottom_text[:25]]
                lines = lines[:4]
                text_y = new_height - bottom_padding + 30
                line_spacing = font_size + 15
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_x = (new_width - (bbox[2] - bbox[0])) // 2
                    for dx, dy in [(-2,-2),(-2,0),(-2,2),(0,-2),(0,2),(2,-2),(2,0),(2,2)]:
                        draw.text((text_x+dx, text_y+dy), line, fill=(0,0,0), font=font)
                    draw.text((text_x, text_y), line, fill=(255,255,255), font=font)
                    text_y += line_spacing

            img_bytes = BytesIO()
            result.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            upload_server = self.vk.method('photos.getMessagesUploadServer', {})
            files = {'photo': ('demotivator.png', img_bytes, 'image/png')}
            upload_response = requests.post(upload_server['upload_url'], files=files).json()

            photo = self.vk.method('photos.saveMessagesPhoto', {
                'photo': upload_response['photo'],
                'server': upload_response['server'],
                'hash': upload_response['hash']
            })
            attachment = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"

            self.vk.method('messages.send', {
                'peer_id': peer_id,
                'message': '🖼 Демотиватор готов:',
                'attachment': attachment,
                'random_id': random.randint(1, 10**9)
            })
        except Exception as e:
            print(f"❌ Ошибка создания демотиватора: {e}")
            self.send(peer_id, f"⚠️ Ошибка: {str(e)[:100]}")