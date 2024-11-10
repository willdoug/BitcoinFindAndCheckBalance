# BitcoinFindAndCheckBalance
Este pequeno artefato de software criado em python faz a geração de chaves privadas randomicas de bitcoin e verifica se possui saldo.
Salva todos os resultados positivos em um arquivo e emite um som quando acha alguma wallet com saldo.
Ele roda em loop infinito e você pode configurar a quantidade de vcpu's que deseja utilizar.

Dependências:
instale as seguintes bibliotecas:
 os, time, random, asyncio, requests, aiohttp, BIP32, hashlib, concurrent.futures, psutil

 Softwares para executar:
 Pycharm Community para rodar o script:
 https://www.jetbrains.com/pycharm/download/other.html
 
 Electrum wallet para importar a wif com balance:
 https://electrum.org/#download
