import os
import time
import random
import asyncio
import requests
import aiohttp
from mnemonic import Mnemonic
from bip32 import BIP32
import hashlib
import concurrent.futures
import psutil

mnemo = Mnemonic("english")

# Lista de fontes de consulta
sources = [
    "blockstream",
    "blockchain_info",
    "blockcypher",
    "blockchair",
    #"btccom",
    "blockonomics",
    "bitcore",
    "bitcoin_average",
    "nownodes",
]

# Variáveis globais para contagem
total_generated = 0
total_checked = 0
total_vcpus = psutil.cpu_count(logical=True)  # Obtém o número total de vCPUs
max_workers = max(1, int(total_vcpus * 0.6))  # Usa 60% dos vCPUs

# Funções de consulta a várias APIs

async def fetch_balance(session, address, source):
    urls = {
        "blockstream": f"https://blockstream.info/api/address/{address}",
        "blockchain_info": f"https://blockchain.info/rawaddr/{address}",
        "blockcypher": f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance",
        "blockchair": f"https://api.blockchair.com/bitcoin/dashboards/address/{address}",
        #"btccom": f"https://chain.api.btc.com/v3/address/{address}",
        "blockonomics": f"https://www.blockonomics.co/api/addr/{address}",
        "bitcore": f"https://api.bitcore.io/api/BTC/main/addr/{address}/balance",
        "bitcoin_average": f"https://api.bitcoinaverage.com/ticker/global/BTCTUSD/",
        "nownodes": f"https://nownodes.io/api/v1/addresses/{address}",
    }

    try:
        async with session.get(urls[source], timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                balance = None

                if source == "blockstream":
                    balance = data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
                elif source == "blockchain_info":
                    balance = data['final_balance']
                elif source == "blockcypher":
                    balance = data['balance']
                elif source == "blockchair":
                    balance = data['data'][address]['address']['balance']
                #elif source == "btccom":
                #    balance = data['data']['balance']
                elif source == "blockonomics":
                    balance = data['response']['balance']
                elif source == "bitcore":
                    balance = data['balance']
                elif source == "bitcoin_average":
                    balance = 0  # Placeholder
                elif source == "nownodes":
                    balance = data['balance']

                print(f"Consultado {address} na {source}: Saldo = {balance}")
                return balance
    except Exception as e:
        print(f"Erro na API {source}: {e}")
    return None

async def check_balance(address):
    random_sources = random.sample(sources, len(sources))  # Embaralha a lista de fontes
    async with aiohttp.ClientSession() as session:
        for source in random_sources:
            balance = await fetch_balance(session, address, source)
            if balance is not None:
                return balance
    return None

def generate_mnemonics(count):
    return [mnemo.generate(256) for _ in range(count)]

def get_keys_from_mnemonic(mnemonic):
    seed = mnemo.to_seed(mnemonic)
    bip32 = BIP32.from_seed(seed)
    private_key = bip32.get_privkey_from_path("m/0'/0'/0'")
    public_key = bip32.get_pubkey_from_path("m/0'/0'/0'")
    return private_key, public_key

def private_key_to_wif(private_key):
    extended_key = b'\x80' + private_key
    first_sha = hashlib.sha256(extended_key).digest()
    second_sha = hashlib.sha256(first_sha).digest()
    final_key = extended_key + second_sha[:4]
    return base58_encode(final_key)

def base58_encode(b):
    base58_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = int.from_bytes(b, 'big')
    res = []
    while n > 0:
        n, r = divmod(n, 58)
        res.append(base58_chars[r])
    res = ''.join(res[::-1])
    pad = 0
    for byte in b:
        if byte == 0:
            pad += 1
        else:
            break
    return '1' * pad + res

def public_key_to_address(public_key):
    sha256 = hashlib.sha256(public_key).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256)
    public_key_hash = ripemd160.digest()
    prefix_and_pubkey_hash = b'\x00' + public_key_hash
    first_sha = hashlib.sha256(prefix_and_pubkey_hash).digest()
    second_sha = hashlib.sha256(first_sha).digest()
    address_with_checksum = prefix_and_pubkey_hash + second_sha[:4]
    return base58_encode(address_with_checksum)

def process_mnemonic(mnemonic):
    private_key, public_key = get_keys_from_mnemonic(mnemonic)
    wif = private_key_to_wif(private_key)
    bitcoin_address = public_key_to_address(public_key)
    return {
        'seed': mnemonic,
        'wif': wif,
        'address': bitcoin_address
    }

def tocar_sirene():
    if os.name == 'nt':  # Windows
        import winsound
        winsound.Beep(1000, 3000)  # Frequência 1000 Hz por 3000 ms
    else:  # Linux e macOS
        os.system('echo -e "\a"')  # Emite um beep longo

async def report_progress():
    global total_generated, total_checked
    start_time = time.time()

    while True:
        await asyncio.sleep(60)  # Espera por 1 minuto
        elapsed_time = time.time() - start_time  # Calcula o tempo decorrido
        rate_generated = total_generated / elapsed_time if elapsed_time > 0 else 0
        rate_checked = total_checked / elapsed_time if elapsed_time > 0 else 0
        print(f"Total gerados: {total_generated}, Total checados: {total_checked}")
        print(f"Taxa de geração: {rate_generated:.2f} endereços/seg, Taxa de verificação: {rate_checked:.2f} endereços/seg")
        print(f"vCPUs usadas: {max_workers} de {total_vcpus} disponíveis")  # Mostra a quantidade de vCPUs usadas

async def main():
    global total_generated, total_checked
    total_generated = 0
    total_checked = 0

    # Exibe a quantidade de vCPUs usadas no início da execução
    print(f"Usando {max_workers} vCPUs de {total_vcpus} disponíveis")

    # Inicia a tarefa de relatório de progresso
    asyncio.create_task(report_progress())

    while True:
        batch_size = 100  # Número de mnemonics por lote
        mnemonics_batch = generate_mnemonics(batch_size)  # Gerar um lote de mnemonics

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_mnemonic, mnemonics_batch))

        # Criar uma lista de tarefas assíncronas para checar os saldos
        tasks = []
        for result in results:
            tasks.append(check_balance(result['address']))

        balances = await asyncio.gather(*tasks)  # Executa todas as tarefas

        for result, balance in zip(results, balances):
            total_generated += 1
            if balance and balance > 0:  # Se houver saldo
                # Salva as informações em um arquivo
                with open("wallets_com_saldo.txt", "a") as balance_file:
                    balance_file.write(
                        f"Seed: {result['seed']}, WIF: {result['wif']}, Address: {result['address']}, Balance: {balance}\n"
                    )
                tocar_sirene()  # Toca a sirene ao encontrar um saldo
            total_checked += 1

if __name__ == "__main__":
    asyncio.run(main())
