from datetime import datetime
from config import CHILD_PHOTO_MALE, CHILD_PHOTO_FEMALE
from utils import fmt_time, format_child_age


class FamilyMixin:

    # ========== ДЕТИ: СТАТИСТИКА ==========
    def update_child_stats(self, child_id):
        try:
            if child_id not in self.children:
                return False
            data = self.children[child_id]
            last = datetime.fromisoformat(data["last_update"])
            now = datetime.now()
            diff = (now - last).total_seconds() // 3600
            if diff > 0:
                dec = int(diff) * 3
                data["hunger"] = max(0, data["hunger"] - dec)
                data["sleep"]  = max(0, data["sleep"]  - dec)
                data["mood"]   = max(0, data["mood"]   - dec)
                data["health"] = max(0, data["health"] - dec)
                data["last_update"] = now.isoformat()
                self.children[child_id] = data
                self.save_all()
                return True
            return False
        except:
            return False

    def update_all_children(self):
        try:
            if not self.children:
                return 0
            updated = 0
            for child_id in list(self.children.keys()):
                if self.update_child_stats(child_id):
                    updated += 1
            if updated > 0:
                print(f"🔄 Обновлены статусы {updated} детей")
                self.save_all()
            return updated
        except:
            return 0

    # ========== БРАКИ ==========
    def marriage_add(self, u1, u2, date=None):
        try:
            u1s, u2s = str(u1), str(u2)
            if u1s in self.marriages or u2s in self.marriages:
                return False, "❌ Кто-то уже в браке"
            ts = date.isoformat() if date else datetime.now().isoformat()
            self.marriages[u1s] = {"partner": u2, "since": ts}
            self.marriages[u2s] = {"partner": u1, "since": ts}
            self.save_all()
            return True, "✅"
        except Exception as e:
            return False, f"❌ Ошибка: {e}"

    def marriage_remove(self, uid):
        try:
            u = str(uid)
            if u not in self.marriages:
                return False, "❌ Не в браке"
            p = self.marriages[u]["partner"]
            del self.marriages[u], self.marriages[str(p)]
            self.save_all()
            return True, "✅"
        except Exception as e:
            return False, f"❌ Ошибка: {e}"

    def marriage_status(self, uid):
        try:
            u = str(uid)
            if u not in self.marriages:
                return None
            d = self.marriages[u]
            partner = d["partner"]
            children = self.get_children_in_marriage(uid, partner)
            status = f"💕 В браке с {self.user_link(partner)} уже {fmt_time(d['since'])}"
            if children:
                status += "\n\n👶 Дети в браке:"
                for child in children:
                    gender = "👦" if child.get("gender", "male") == "male" else "👧"
                    age = format_child_age(child['birthday'])
                    status += f"\n{gender} {child['name']} ({age})"
            return status
        except:
            return "❌ Ошибка получения статуса"

    def get_children_in_marriage(self, user_id, partner_id):
        children_list = []
        for child_id, data in self.children.items():
            if (data["parent1"] == user_id and data["parent2"] == partner_id) or \
               (data["parent1"] == partner_id and data["parent2"] == user_id):
                children_list.append(data)
        return children_list

    # ========== ДЕТИ ==========
    def get_child(self, user_id, partner_id=None):
        try:
            if partner_id:
                for child_id, data in self.children.items():
                    if (data["parent1"] == user_id and data["parent2"] == partner_id) or \
                       (data["parent1"] == partner_id and data["parent2"] == user_id):
                        return child_id, data
                return None, None
            for child_id, data in self.children.items():
                if data["parent1"] == user_id or data["parent2"] == user_id:
                    return child_id, data
            return None, None
        except:
            return None, None

    def feed_child(self, user_id):
        try:
            child_id, data = self.get_child(user_id)
            if not data:
                return "У вас нет ребенка!"
            self.update_child_stats(child_id)
            if data["hunger"] >= 100:
                return f"{data['name']} уже сыт!"
            data["hunger"] = min(100, data["hunger"] + 30)
            data["mood"] = min(100, data["mood"] + 5)
            self.children[child_id] = data
            self.save_all()
            return f"🍼 {data['name']} покормлен! Голод: {data['hunger']}%"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def play_with_child(self, user_id):
        try:
            child_id, data = self.get_child(user_id)
            if not data:
                return "У вас нет ребенка!"
            self.update_child_stats(child_id)
            if data["mood"] >= 100:
                return f"{data['name']} уже весел!"
            data["mood"] = min(100, data["mood"] + 25)
            data["sleep"] = max(0, data["sleep"] - 10)
            self.children[child_id] = data
            self.save_all()
            return f"🎮 {data['name']} поиграл! Настроение: {data['mood']}%"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def sleep_child(self, user_id):
        try:
            child_id, data = self.get_child(user_id)
            if not data:
                return "У вас нет ребенка!"
            self.update_child_stats(child_id)
            if data["sleep"] >= 100:
                return f"{data['name']} уже выспался!"
            data["sleep"] = min(100, data["sleep"] + 30)
            data["mood"] = min(100, data["mood"] + 5)
            self.children[child_id] = data
            self.save_all()
            return f"😴 {data['name']} уложен спать! Сон: {data['sleep']}%"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def treat_child(self, user_id):
        try:
            child_id, data = self.get_child(user_id)
            if not data:
                return "У вас нет ребенка!"
            self.update_child_stats(child_id)
            if data["health"] >= 100:
                return f"{data['name']} уже здоров!"
            data["health"] = min(100, data["health"] + 30)
            data["mood"] = max(0, data["mood"] - 10)
            data["sleep"] = max(0, data["sleep"] - 10)
            self.children[child_id] = data
            self.save_all()
            return f"💊 {data['name']} вылечен! Здоровье: {data['health']}%"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def get_child_status(self, user_id):
        try:
            child_id, data = self.get_child(user_id)
            if not data:
                return None, None
            self.update_child_stats(child_id)
            gender = "👦" if data.get("gender", "male") == "male" else "👧"
            p1 = self.user_link(data["parent1"])
            p2 = self.user_link(data["parent2"])
            age = format_child_age(data.get('birthday', ''))
            status = f"👶 {data['name']} {gender} | {age}\n"
            status += f"👨‍👩‍👦 Родители: {p1} и {p2}\n"
            status += f"🍼 Голод: {data['hunger']}%"
            status += f" | 😴 Сон: {data['sleep']}%"
            status += f" | 😊 Настроение: {data['mood']}%\n"
            status += f"❤️ Здоровье: {data['health']}%\n\n"
            if data["health"] < 30:
                status += "⚠️ Ребенок болен!"
            elif data["hunger"] < 20:
                status += "🍽️ Ребенок голоден! Покормите!"
            elif data["sleep"] < 20:
                status += "😴 Ребенок хочет спать!"
            elif data["mood"] < 20:
                status += "😢 Ребенок грустный! Поиграйте!"
            else:
                status += "😊 Ребенок счастлив!"
            return status, child_id
        except:
            return "❌ Ошибка получения статуса", None

    def get_children_list(self):
        try:
            if not self.children:
                return "Детей нет"
            result = "👶 Список детей:\n\n"
            for child_id, data in self.children.items():
                p1 = self.user_link(data["parent1"])
                p2 = self.user_link(data["parent2"])
                gender = "👦" if data.get("gender", "male") == "male" else "👧"
                age = format_child_age(data.get('birthday', ''))
                result += f"{gender} {data['name']} ({p1} и {p2}) — {age}\n"
            return result
        except:
            return "❌ Ошибка получения списка"

    # ========== БЕРЕМЕННОСТЬ ==========
    def confirm_pregnancy(self, partner_id, user_id, action):
        try:
            if user_id not in self.pregnancies:
                return False, "Нет активной беременности"
            preg = self.pregnancies[user_id]
            if preg["partner"] != partner_id:
                return False, "Не та пара"
            if action == "no":
                del self.pregnancies[user_id]
                self.save_all()
                return False, "Отказ"
            preg["status"] = "pending"
            self.pregnancies[user_id] = preg
            self.save_all()
            return True, "ok"
        except Exception as e:
            return False, f"Ошибка: {e}"

    def create_child_from_pregnancy(self, user_id, name, gender):
        try:
            if user_id not in self.pregnancies:
                return False, "Нет беременности"
            preg = self.pregnancies[user_id]
            if preg["status"] != "pending":
                return False, "Статус не pending"
            partner = preg["partner"]
            self.child_counter += 1
            child_id = f"child_{self.child_counter}"
            now = datetime.now().isoformat()
            self.children[child_id] = {
                "name": name, "gender": gender,
                "parent1": user_id, "parent2": partner,
                "birthday": now,
                "hunger": 70, "sleep": 70, "mood": 70, "health": 90,
                "last_update": now
            }
            del self.pregnancies[user_id]
            self.save_all()
            self.update_all_children()
            return True, f"Ребенок {name} родился! 🎉"
        except Exception as e:
            return False, f"Ошибка: {e}"

    # ========== ОТПРАВКА СТАТУСА ==========
    def send_child_status(self, user_id, peer_id, edit=False, conv_msg_id=None):
        status, child_id = self.get_child_status(user_id)
        if not status:
            self.send(peer_id, "❌ У вас нет ребенка!")
            return
        keyboard = self.get_child_status_keyboard(user_id)

        attachment = None
        if child_id:
            data = self.children.get(child_id, {})
            gender = data.get('gender', 'male')
            if gender == 'male' and CHILD_PHOTO_MALE:
                attachment = CHILD_PHOTO_MALE
            elif gender == 'female' and CHILD_PHOTO_FEMALE:
                attachment = CHILD_PHOTO_FEMALE

        if edit:
            if not conv_msg_id and user_id in self.status_messages:
                saved = self.status_messages[user_id]
                conv_msg_id = saved.get("conv_msg_id")
                peer_id = saved.get("peer_id", peer_id)
                if not attachment:
                    attachment = saved.get("attachment")
            if conv_msg_id:
                try:
                    params = {'peer_id': peer_id, 'message': status,
                              'conversation_message_id': conv_msg_id, 'keyboard': keyboard}
                    if attachment:
                        params['attachment'] = attachment
                    self.vk.method('messages.edit', params)
                    self.status_messages[user_id] = {"peer_id": peer_id, "conv_msg_id": conv_msg_id, "attachment": attachment}
                    return
                except Exception as e:
                    print(f"❌ Ошибка редактирования статуса: {e}")
                    edit = False

        try:
            params = {'peer_id': peer_id, 'message': status, 'keyboard': keyboard,
                      'random_id': __import__('random').randint(1, 10**9)}
            if attachment:
                params['attachment'] = attachment
            result = self.vk.method('messages.send', params)
            if isinstance(result, dict):
                conv_id = result.get('conversation_message_id')
                if conv_id:
                    self.status_messages[user_id] = {"peer_id": peer_id, "conv_msg_id": conv_id, "attachment": attachment}
        except Exception as e:
            print(f"❌ Ошибка отправки статуса с фото: {e}")
            self.send(peer_id, status, keyboard=keyboard)

    def get_family_help(self):
        return """👶 Семья и дети

забеременеть от @юз — начать беременность
ребенок имя — дать имя ребенку
ребенок пол мальчик/девочка — выбрать пол
статус — состояние ребенка (с кнопками)
дети — список детей
обновить детей — обновить статусы всех детей
помощь семья — помощь по семье"""