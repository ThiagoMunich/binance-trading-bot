import requests


def mensagemTelegram(mensagem):
    token = '2023637583:AAGwMc7TNgHK4iUnEmWCJuNqvNPEfoV8wDU'
    chatId = -566210839

    try:
        data = {"chat_id": chatId, "text": mensagem}
        url = "https://api.telegram.org/bot{}/sendMessage".format(token)
        requests.post(url, data)
    except Exception as e:
        print("Erro no sendMessage:", e)
