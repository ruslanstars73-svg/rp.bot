from config import DEFAULT_RP


class RPMixin:

    def rp_do(self, peer, uid, name, data, targets):
        try:
            t = targets[0]
            text = f"💫 {self.user_link(uid)} {data['description']} {self.user_link(t)}" if t != uid else f"😄 {self.user_link(uid)} {data['description']} сам(а) себя"
            # поддерживаем оба поля: vk_photo_id (дефолтные) и photo (кастомные)
            photo = data.get('vk_photo_id') or data.get('photo', '')
            self.send_photo(peer, text, photo)
            self.stats[name] = self.stats.get(name, 0) + 1
            self.save_all()
        except Exception as e:
            print(f"❌ Ошибка RP: {e}")
            self.send(peer, "⚠️ Ошибка выполнения RP")

    def rp_all(self):
        """Возвращает объединённый словарь RP (дефолтные + кастомные)."""
        all_rp = DEFAULT_RP.copy()
        all_rp.update(self.custom_rp)
        return all_rp

    def rp_top(self):
        all_actions = {}
        for u, acts in self.favorites_rp.items():
            for act, cnt in acts.items():
                all_actions[act] = all_actions.get(act, 0) + cnt
        return all_actions