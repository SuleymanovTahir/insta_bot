import httpx
from config import PAGE_ACCESS_TOKEN

async def send_message(recipient_id: str, message: str):
    """Отправить сообщение в Instagram"""
    url = "https://graph.facebook.com/v18.0/me/messages"
    
    params = {"access_token": PAGE_ACCESS_TOKEN}
    
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, params=params, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Ошибка отправки в Instagram: {e}")
            return {"error": str(e)}

async def send_typing_indicator(recipient_id: str):
    """Показать индикатор печати (опционально)"""
    url = "https://graph.facebook.com/v18.0/me/messages"
    
    params = {"access_token": PAGE_ACCESS_TOKEN}
    
    data = {
        "recipient": {"id": recipient_id},
        "sender_action": "typing_on"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            await client.post(url, params=params, json=data)
        except Exception as e:
            print(f"⚠️ Не удалось показать typing: {e}")
