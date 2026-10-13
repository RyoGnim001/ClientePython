import base64
import binascii
import subprocess
import tempfile


def abrir_imagem_recebida(resposta):
    if not resposta.startswith("OK;"):
        print(f"[Servidor] {resposta}")
        return

    dados_base64 = resposta[len("OK;"):]
    try:
        imagem = base64.b64decode(dados_base64, validate=True)
        with tempfile.NamedTemporaryFile(
            prefix="imagem-servidor-", suffix=".jpg", delete=False
        ) as arquivo:
            arquivo.write(imagem)
            caminho = arquivo.name

        processo_chrome = subprocess.Popen(
            ["google-chrome", caminho],
            stdout=subprocess.DEVNULL,  # Opcional: silencia a saída padrão
            stderr=subprocess.DEVNULL  # Opcional: silencia as mensagens de erro
        )
        print("Imagem aberta no Chrome.")
    except (ValueError, binascii.Error):
        print("O servidor enviou dados Base64 inválidos.")
    except OSError as e:
        print(f"Não foi possível salvar a imagem ou iniciar o Firefox: {e}")