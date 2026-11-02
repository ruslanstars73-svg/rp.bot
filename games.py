import random
import time
import json


class GamesMixin:

    # ========== КОСТИ ==========
    def start_dice_game(self, peer_id, user_id, target_id):
        try:
            if peer_id in self.dice_games and self.dice_games[peer_id].get("active", False):
                return "❌ В этом чате уже идет игра в кости!"
            if target_id == user_id:
                return "❌ Нельзя играть с самим собой!"
            self.dice_games[peer_id] = {
                "player1": user_id, "player2": target_id, "turn": user_id,
                "move1": None, "move2": None, "active": True
            }
            text = f"🎲 Игра: Кости\n\n👤 {self.user_link(user_id)} vs {self.user_link(target_id)}\n\n🟢 Ход: {self.user_link(user_id)}"
            self.vk.method('messages.send', {
                'peer_id': peer_id, 'message': text,
                'keyboard': self.get_dice_keyboard(),
                'random_id': random.randint(1, 10**9)
            })
            return "✅ Игра в кости начата!"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def handle_dice_turn(self, peer_id, user_id):
        try:
            if peer_id not in self.dice_games or not self.dice_games[peer_id].get("active", False):
                return "❌ Игра уже завершена!"
            game = self.dice_games[peer_id]
            if user_id not in (game["player1"], game["player2"]):
                return "❌ Вы не участвуете в этой игре!"
            if game["turn"] != user_id:
                return f"❌ Не ваш ход! Сейчас ходит {self.user_link(game['turn'])}"
            dice1 = random.randint(1, 6); dice2 = random.randint(1, 6)
            total = dice1 + dice2
            emojis = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
            result = f"🎲 {self.user_link(user_id)} бросил кости!\n{emojis[dice1-1]} + {emojis[dice2-1]} = **{total}**"
            if user_id == game["player1"]:
                game["move1"] = total
            else:
                game["move2"] = total
            self.dice_games[peer_id] = game
            if game["move1"] is not None and game["move2"] is not None:
                return result + "\n\n" + self.finish_dice_game(peer_id)
            next_player = game["player2"] if user_id == game["player1"] else game["player1"]
            game["turn"] = next_player
            self.dice_games[peer_id] = game
            text = f"🎲 Игра: Кости\n\n👤 {self.user_link(game['player1'])} vs {self.user_link(game['player2'])}\n\n🟢 Ход: {self.user_link(next_player)}"
            self.vk.method('messages.send', {
                'peer_id': peer_id, 'message': text,
                'keyboard': self.get_dice_keyboard(),
                'random_id': random.randint(1, 10**9)
            })
            return result + f"\n\n🟢 Теперь ход: {self.user_link(next_player)}"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def finish_dice_game(self, peer_id):
        try:
            game = self.dice_games[peer_id]
            user1, user2 = game["player1"], game["player2"]
            move1, move2 = game["move1"], game["move2"]
            if move1 == move2:
                emoji, rt = "🤝", "Ничья!"
            elif move1 > move2:
                emoji, rt = "🎉", f"Победил: {self.user_link(user1)}!"
            else:
                emoji, rt = "🎉", f"Победил: {self.user_link(user2)}!"
            text = f"🎲 Игра: Кости (ЗАВЕРШЕНА)\n\n👤 {self.user_link(user1)} vs {self.user_link(user2)}\n\n⚀ {self.user_link(user1)}: {move1}\n⚁ {self.user_link(user2)}: {move2}\n\n{emoji} {rt}"
            game["active"] = False
            self.dice_games[peer_id] = game
            self.vk.method('messages.send', {
                'peer_id': peer_id, 'message': text,
                'keyboard': json.dumps({"buttons": []}, ensure_ascii=False),
                'random_id': random.randint(1, 10**9)
            })
            time.sleep(3)
            if peer_id in self.dice_games:
                del self.dice_games[peer_id]
            return text
        except:
            return "❌ Ошибка завершения игры"

    # ========== КРЕСТИКИ-НОЛИКИ ==========
    def start_ttt_game(self, peer_id, user1, user2):
        try:
            if user1 == user2:
                return "❌ Нельзя играть с самим собой!"
            if peer_id in self.tic_tac_toe_games:
                return "❌ В этом чате уже идет игра! Дождись окончания."
            game_id = f"ttt_{peer_id}_{int(time.time())}"
            board = [""] * 9
            self.tic_tac_toe_games[peer_id] = {
                "game_id": game_id, "board": board, "players": [user1, user2],
                "turn": user1, "active": True, "winner": None, "message_ids": []
            }
            text = f"🎮 Крестики-нолики!\n\n❌ {self.user_link(user1)} (X) vs ⭕ {self.user_link(user2)} (O)\n🟢 Ход: {self.user_link(user1)} (X)"
            result = self.vk.method('messages.send', {
                'peer_id': peer_id, 'message': text,
                'keyboard': self.get_ttt_keyboard(board, game_id),
                'random_id': random.randint(1, 10**9)
            })
            msg_id = result.get('message_id') if isinstance(result, dict) else result
            self.tic_tac_toe_games[peer_id]["message_ids"].append(msg_id)
            return "✅ Игра начата!"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def handle_ttt_move(self, peer_id, user_id, pos, game_id):
        try:
            if peer_id not in self.tic_tac_toe_games:
                return
            game = self.tic_tac_toe_games[peer_id]
            if not game.get("active", False) or game["turn"] != user_id or game["board"][pos] != "":
                return
            player1 = game["players"][0]
            symbol = "X" if user_id == player1 else "O"
            game["board"][pos] = symbol

            winner = self.check_ttt_winner(game["board"])
            if winner:
                game["active"] = False
                game["winner"] = winner
                winner_id = player1 if winner == "X" else game["players"][1]
                text = f"🎮 Крестики-нолики! 🏆\n\n❌ {self.user_link(game['players'][0])} (X) vs ⭕ {self.user_link(game['players'][1])} (O)\n🎉 Победил: {self.user_link(winner_id)}!"
                self.vk.method('messages.send', {'peer_id': peer_id, 'message': text, 'random_id': random.randint(1, 10**9)})
                for msg_id in game.get("message_ids", []):
                    try:
                        self.vk.method('messages.delete', {'peer_id': peer_id, 'message_ids': [msg_id], 'delete_for_all': 1})
                    except: pass
                time.sleep(5)
                if peer_id in self.tic_tac_toe_games:
                    del self.tic_tac_toe_games[peer_id]
                return

            if all(cell != "" for cell in game["board"]):
                game["active"] = False
                text = f"🎮 Крестики-нолики! 🤝\n\n❌ {self.user_link(game['players'][0])} (X) vs ⭕ {self.user_link(game['players'][1])} (O)\n🤝 Ничья!"
                self.vk.method('messages.send', {'peer_id': peer_id, 'message': text, 'random_id': random.randint(1, 10**9)})
                for msg_id in game.get("message_ids", []):
                    try:
                        self.vk.method('messages.delete', {'peer_id': peer_id, 'message_ids': [msg_id], 'delete_for_all': 1})
                    except: pass
                time.sleep(5)
                if peer_id in self.tic_tac_toe_games:
                    del self.tic_tac_toe_games[peer_id]
                return

            next_player = game["players"][1] if user_id == game["players"][0] else game["players"][0]
            game["turn"] = next_player
            self.tic_tac_toe_games[peer_id] = game

            text = f"🎮 Крестики-нолики!\n\n❌ {self.user_link(game['players'][0])} (X) vs ⭕ {self.user_link(game['players'][1])} (O)\n🟢 Ход: {self.user_link(next_player)} ({'X' if next_player == game['players'][0] else 'O'})"
            old_ids = game.get("message_ids", [])
            if old_ids:
                last_id = old_ids[-1]
                try:
                    self.vk.method('messages.delete', {'peer_id': peer_id, 'message_ids': [last_id], 'delete_for_all': 1})
                except: pass
                game["message_ids"] = old_ids[:-1]
            result = self.vk.method('messages.send', {
                'peer_id': peer_id, 'message': text,
                'keyboard': self.get_ttt_keyboard(game["board"], game.get("game_id")),
                'random_id': random.randint(1, 10**9)
            })
            new_msg_id = result.get('message_id') if isinstance(result, dict) else result
            game["message_ids"].append(new_msg_id)
            self.tic_tac_toe_games[peer_id] = game
        except Exception as e:
            print(f"❌ Ошибка TTT move: {e}")

    def check_ttt_winner(self, board):
        wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
        for c in wins:
            if board[c[0]] and board[c[0]] == board[c[1]] == board[c[2]]:
                return board[c[0]]
        return None