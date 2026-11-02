class StatsMixin:

    def get_user_stats(self, user_id):
        stats = self.chat_stats.get(str(user_id), {})
        return {k: stats.get(k, 0) for k in
                ["text","sticker","voice","video","photo","doc","other","total"]}

    def get_top_by_type(self, stat_type, limit=10):
        return sorted(self.chat_stats.items(), key=lambda x: x[1].get(stat_type, 0), reverse=True)[:limit]

    def format_top(self, sorted_items, stat_type, label):
        if not sorted_items:
            return f"📭 Нет данных по {label}"
        medals = ['1.','2.','3.','4.','5.','6.','7.','8.','9.','10.']
        result = f"🏆 Топ по {label}:\n\n"
        for i, (uid, data) in enumerate(sorted_items):
            medal = medals[i] if i < len(medals) else f"{i+1}."
            result += f"{medal} {self.user_link(int(uid))} — {data.get(stat_type, 0)} сообщений\n"
        return result