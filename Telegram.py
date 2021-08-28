import requests


def enviarMensagem(mensagem):
    token = '1945616969:AAE7nuXekkJ-x1UbvmfjHCfwoXD-E_uhtZo'
    chatId = -573458699

    try:
        data = {"chat_id": chatId, "text": mensagem}
        url = "https://api.telegram.org/bot{}/sendMessage".format(token)
        requests.post(url, data)
    except Exception as e:
        print("Erro no sendMessage:", e)
