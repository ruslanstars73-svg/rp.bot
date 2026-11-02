import random
import json
import re
import lyricsgenius
from config import MOODS, GENIUS_TOKEN


class MusicMixin:

    def music_search(self, uid, q=None, mood=None):
        if not self.vk_user:
            return None, "❌ Музыка недоступна"
        try:
            if q:
                search_query = q
                if mood and mood in MOODS:
                    search_query += f" {MOODS[mood]}"
                r = self.vk_user.method("audio.search", {"q": search_query, "count": 50, "sort": 2, "auto_complete": 0})
                if not r or not r.get('items'):
                    return None, "❌ Не найдено"
                q_lower = q.lower()
                filtered = []
                for track in r['items']:
                    title = track.get('title', '').lower()
                    artist = track.get('artist', '').lower()
                    if q_lower == artist: filtered.insert(0, track)
                    elif q_lower == title: filtered.insert(0, track)
                    elif q_lower in artist or q_lower in title: filtered.append(track)
                if not filtered:
                    filtered = r['items'][:5]
                random.shuffle(filtered)
                return filtered[:3], None
            else:
                t = self.vk_user.method("audio.get", {"owner_id": uid, "count": 200})
                if not t or not t.get('items'):
                    return None, "❌ Нет твоих треков"
                tr = random.choice(t['items'])
                r = self.vk_user.method("audio.getRecommendations", {
                    "target_audio": f"{tr['owner_id']}_{tr['id']}", "count": 20, "shuffle": 1
                })
                if not r or not r.get('items'):
                    return None, "❌ Не найдено"
                random.shuffle(r['items'])
                return r['items'][:3], None
        except Exception as e:
            return None, f"❌ Ошибка музыки: {e}"

    def send_music(self, peer, uid, q=None, mood=None, edit_conv_msg_id=None, owner_id=None):
        if owner_id is None:
            owner_id = uid
        tracks, err = self.music_search(uid, q, mood)
        keyboard = self.get_music_keyboard(owner_id)
        if err:
            if edit_conv_msg_id:
                try:
                    self.vk.method('messages.edit', {
                        'peer_id': peer, 'message': err,
                        'keyboard': json.dumps({"buttons": []}, ensure_ascii=False),
                        'conversation_message_id': edit_conv_msg_id
                    })
                except Exception as e:
                    if "Flood control" not in str(e):
                        self.send(peer, err)
            else:
                self.send(peer, err)
            return
        if not tracks:
            self.send(peer, "❌ Нет треков")
            return
        att = ','.join([f"audio{t['owner_id']}_{t['id']}" for t in tracks])
        msg = f"{self.user_link(uid)}, ваши результаты{f' по запросу «{q}»' if q else ''}:"
        try:
            if edit_conv_msg_id:
                self.vk.method('messages.edit', {
                    'peer_id': peer, 'message': msg, 'attachment': att,
                    'keyboard': keyboard, 'conversation_message_id': edit_conv_msg_id
                })
            else:
                self.vk.method('messages.send', {
                    'peer_id': peer, 'message': msg, 'attachment': att,
                    'keyboard': keyboard, 'random_id': random.randint(1, 10**9)
                })
        except Exception as e:
            print(f"⚠️ Ошибка отправки музыки: {e}")

    def lyrics(self, artist, title):
        try:
            s = lyricsgenius.Genius(GENIUS_TOKEN)
            s.verbose = False
            song = s.search_song(title, artist)
            if song:
                lyrics = re.sub(r'\[.*?\]', '', song.lyrics).strip()
                return f"🎵 {song.title} — {song.artist}\n\n{lyrics}", None
            return None, f"❌ Не найдено: {artist} — {title}"
        except Exception as e:
            return None, f"❌ Ошибка: {e}"