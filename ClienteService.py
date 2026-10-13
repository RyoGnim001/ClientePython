from Client import Client
from ImagemService import abrir_imagem_recebida
from MenuService import exibir_menu, preparar_mensagem
from SerializableService import tratar_objeto_serializado


def iniciar_cliente():
    client = Client("127.0.0.1", 12345)
    client.conectar()

    if not client.esta_conectado():
        return

    id_linha = client.receber_linha()
    if id_linha and id_linha.startswith("__ID__"):
        meu_id = id_linha.replace("__ID__", "").strip()
        print(f"Você é o client #{meu_id}")

    boas_vindas = client.receber_linha()
    if boas_vindas:
        print(f"[Servidor] {boas_vindas}")

    exibir_menu()

    while True:
        entrada = input("\n> ").strip()

        if entrada == "0":
            client.enviar_mensagem("0")
            break

        if not entrada:
            continue

        mensagem = preparar_mensagem(entrada)
        if client.enviar_mensagem(mensagem):
            resposta = client.receber_resposta()
            if resposta is None:
                break

            opcao = entrada.split(";", 1)[0].strip()

            if opcao == "4":
                abrir_imagem_recebida(resposta)
            elif resposta.startswith("SERIALIZED;"):
                tratar_objeto_serializado(resposta)
            else:
                print(f"[Servidor] {resposta}")
        else:
            break

    client.fechar()