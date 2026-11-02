from config import GIGACHAT_AUTH_KEY, GIGACHAT_CLIENT_ID
from utils import session

ai_contexts = {}
gigachat_token = None


def get_gigachat_token():
    global gigachat_token
    try:
        r = session.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': GIGACHAT_CLIENT_ID,
                'Authorization': f'Basic {GIGACHAT_AUTH_KEY}'
            },
            data="scope=GIGACHAT_API_PERS",
            timeout=30, verify=False
        )
        if r.status_code == 200:
            gigachat_token = r.json().get('access_token')
            return gigachat_token
    except Exception:
        pass
    return None


def get_ai(user_id, prompt):
    try:
        ai_contexts.setdefault(user_id, []).append({"role": "user", "content": prompt})
        token = get_gigachat_token()
        if not token:
            return "❌ Ошибка токена"
        r = session.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json={"model": "GigaChat:latest", "messages": ai_contexts[user_id][-10:], "temperature": 0.7, "max_tokens": 500},
            timeout=45, verify=False
        )
        if r.status_code == 200:
            ans = r.json()['choices'][0]['message']['content']
            if ans:
                ai_contexts[user_id].append({"role": "assistant", "content": ans})
                return ans
    except Exception as e:
        print(f"❌ Ошибка GigaChat: {e}")
    return "❌ Ошибка GigaChat"