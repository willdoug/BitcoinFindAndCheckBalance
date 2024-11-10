# BitcoinFindAndCheckBalance
Este pequeno artefato de software criado em python faz a geração de chaves privadas randomicas de bitcoin, gera um endereço a partir desta chave privada e chave publica, e então verifica se o endereço possui saldo.
Salva todos os resultados positivos em um arquivo e emite um som quando achar alguma wallet com saldo.
Ele roda em loop infinito e você pode configurar a quantidade de vcpu's que deseja utilizar.

DEPENDÊNCIAS:
instale as seguintes bibliotecas:
 os, time, random, asyncio, requests, aiohttp, BIP32, hashlib, concurrent.futures, psutil

 Softwares para executar:
 Pycharm Community para rodar o script:
 https://www.jetbrains.com/pycharm/download/other.html
 
 Electrum wallet para importar a wif com balance:
 https://electrum.org/#download

INSTRUÇÕES:
Baixe o pycharm community, instale e crie um novo projeto com o nome que preferir.
Baixe o arquivo main.py e coloque dentro da pasta do projeto criado.
Instale as bibliotecas dependentes.
Execute o código.
