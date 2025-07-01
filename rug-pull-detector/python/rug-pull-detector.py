from web3 import Web3
import datetime
import io
import sys
import os
from decimal import Decimal

uniswap_v2_factory_abi = [  # Minimal ABI for Factory contract
    {
        "constant": True,
        "inputs": [{"name": "tokenA", "type": "address"}, {"name": "tokenB", "type": "address"}],
        "name": "getPair",
        "outputs": [{"name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "allPairsLength",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "uint", "type": "uint256"}],
        "name": "allPairs",
        "outputs": [{"name": "pair", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

pair_abi = [
    {"constant": True, "inputs": [], "name": "token0", "outputs": [{"name": "", "type": "address"}],
     "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [], "name": "token1", "outputs": [{"name": "", "type": "address"}],
     "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [], "name": "getReserves",
     "outputs": [{"name": "reserve0", "type": "uint112"}, {"name": "reserve1", "type": "uint112"},
                 {"name": "blockTimestampLast", "type": "uint32"}], "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}],
     "stateMutability": "view", "type": "function"}
]

token_abi = [
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}],
     "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}],
     "stateMutability": "view", "type": "function"},
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}],
     "stateMutability": "view", "type": "function"}
]

BASE_RPC_URL = "https://base.drpc.org"  # Base RPC URL
web3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))

# Ensure the connection to the Base chain
if web3.is_connected():
    print("Connected to Base Chain")

# Input token address 
#SKI MASK DOG - 0x768BE13e1680b5ebE0024C42c896E3dB59ec0149
#WALL STREET PEPE -  0x00006955ab0269a2ebf21702740536f6af139bc1
#GG TOKEN - 0x000000000000a59351f61b598e8da953b9e041ec

input_token_address = "0x000000000000a59351f61b598e8da953b9e041ec"

# Uniswap V2 Factory contract address 
uniswap_v2_factory_address = "0x8909Dc15e40173Ff4699343b6eB8132c65e18eC6"

# Do not change these. Will be used to find the pair with USDC or WETH
USDC_contract = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
WETH_contract = '0x4200000000000000000000000000000000000006'
ZERO_address = '0x0000000000000000000000000000000000000000'
WETH_USDC_PAIR = '0x88A43bbDF9D098eEC7bCEda4e2494615dfD9bB9C'

# Create contract instance for the Uniswap V2 Factory
factory_contract = web3.eth.contract(address=web3.to_checksum_address(uniswap_v2_factory_address),
                                     abi=uniswap_v2_factory_abi)


def get_price_per_eth():
    pair_contract = web3.eth.contract(address=web3.to_checksum_address(WETH_USDC_PAIR), abi=pair_abi)
    reserves = pair_contract.functions.getReserves().call()
    token0 = pair_contract.functions.token0().call()
    token1 = pair_contract.functions.token1().call()

    reserve0 = Decimal(reserves[0])
    reserve1 = Decimal(reserves[1])

    decimals0 = Decimal(10 ** get_token_decimals(token0))
    decimals1 = Decimal(10 ** get_token_decimals(token1))

    if token0 == WETH_contract:
        price = (reserve1 / decimals1) / (reserve0 / decimals0)
    elif token1 == WETH_contract:
        price = (reserve0 / decimals0) / (reserve1 / decimals1)
    else:
        raise Exception("WETH not found in this pair")

    return price

def get_token_decimals(token_address):
    if token_address == USDC_contract:
        return 6
    if token_address == WETH_contract:
        return 18
    
    token_contract = web3.eth.contract(address=web3.to_checksum_address(token_address), abi=token_abi)
    return token_contract.functions.decimals().call()

def get_token_total_supply(token_address):
    token_contract = web3.eth.contract(address=web3.to_checksum_address(token_address), abi=token_abi)
    return token_contract.functions.totalSupply().call()

def check_minting_ability(token_contract):
    try:
        token_contract.functions.mint().call()
        return {"mintable": True, "supplyStatus": "NOT FIXED"}
    except:
        return {"mintable": False, "supplyStatus": "FIXED"}

def find_pair_by_token(token_address):
    pair_address_usdc = factory_contract.functions.getPair(
        web3.to_checksum_address(token_address),
        web3.to_checksum_address(USDC_contract)
    ).call()
    
    if pair_address_usdc != ZERO_address:
        return {"pairAddress": pair_address_usdc, "quoteToken": "USDC"}
    
    pair_address_weth = factory_contract.functions.getPair(
        web3.to_checksum_address(token_address),
        web3.to_checksum_address(WETH_contract)
    ).call()
    
    if pair_address_weth != ZERO_address:
        return {"pairAddress": pair_address_weth, "quoteToken": "WETH"}
    
    return None

def calculate_market_cap(pair_contract):
    try:
        reserves = pair_contract.functions.getReserves().call()
        token0 = pair_contract.functions.token0().call()
        token1 = pair_contract.functions.token1().call()
        pricePerEth = get_price_per_eth()        
        token_total_supply = get_token_total_supply(token0)
        
        # Normalize values using decimals
        reserve0_normalized = Decimal(reserves[0]) / Decimal(10 ** get_token_decimals(token0))
        reserve1_normalized = Decimal(reserves[1]) / Decimal(10 ** get_token_decimals(token1))
        if(token1 == USDC_contract):
            price_per_token = reserve1_normalized / reserve0_normalized
        else:
            price_per_token = reserve1_normalized / reserve0_normalized * pricePerEth

        total_supply_normalized = Decimal(token_total_supply) / Decimal(10 ** get_token_decimals(token0))
        if(token1 == USDC_contract):
            market_cap = total_supply_normalized * price_per_token
        else:
            market_cap = total_supply_normalized * price_per_token * pricePerEth
        
        return {
            "reserves": reserves,
            "token0": token0,
            "token1": token1,
            "pricePerToken": str(price_per_token),
            "totalSupplyNormalized": str(total_supply_normalized),
            "marketCap": str(market_cap)
        }
    except Exception as e:
        print(f"Error calculating market cap: {e}")
        return None

# Main execution
pair_info = find_pair_by_token(input_token_address)
if pair_info is None:
    print("Pair could not be found! Quit execution of the algorithm...")
    quit()

pair_address = pair_info["pairAddress"]
pair_contract = web3.eth.contract(address=web3.to_checksum_address(pair_address), abi=pair_abi)

# Get token addresses
token0 = pair_contract.functions.token0().call()
token1 = pair_contract.functions.token1().call()
input_token = token0 if token0 != USDC_contract and token0 != WETH_contract else token1
pair_token = token0 if token0 == USDC_contract or token0 == WETH_contract else token1

# Create contract instances
token_contract = web3.eth.contract(address=input_token, abi=token_abi)
pair_token_contract = web3.eth.contract(address=pair_token, abi=token_abi)

buffer = io.StringIO()
sys.stdout = buffer

print("=" * 80)
print("🔍 TOKEN ANALYSIS REPORT")
print("=" * 80)
print(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 80)

# Token Information
print("\n📊 TOKEN INFORMATION")
print("-" * 40)
print(f"Token Address: {input_token}")
token_name = token_contract.functions.name().call()
token_symbol = token_contract.functions.symbol().call()
print(f"Token Name: {token_name}")
print(f"Token Symbol: {token_symbol}")

# Pair Token Information
print("\n🔄 PAIR TOKEN INFORMATION")
print("-" * 40)
print(f"Pair Token Address: {pair_token}")
pair_token_name = pair_token_contract.functions.name().call()
pair_token_symbol = pair_token_contract.functions.symbol().call()
print(f"Pair Token Name: {pair_token_name}")
print(f"Pair Token Symbol: {pair_token_symbol}")

# Liquidity Information
print("\n💧 LIQUIDITY INFORMATION")
print("-" * 40)
print(f"Liquidity Pair Address: {pair_address}")
total_lp_tokens = pair_contract.functions.totalSupply().call()
print(f"Total Supply of LP Tokens: {total_lp_tokens}")

# Market Analysis
print("\n💰 MARKET ANALYSIS")
print("-" * 40)
market_cap_data = calculate_market_cap(pair_contract)
if market_cap_data:
    print(f"Reserve {token_symbol}: {market_cap_data['reserves'][0]}")
    print(f"Reserve {pair_token_symbol}: {market_cap_data['reserves'][1]}")
    print(f"Price per {token_symbol}: {market_cap_data['pricePerToken']} USDC")
    print(f"Total Supply: {market_cap_data['totalSupplyNormalized']}")
    print(f"Market Cap: {market_cap_data['marketCap']} USDC")

# Supply Analysis
print("\n🪄 SUPPLY ANALYSIS")
print("-" * 40)
minting_status = check_minting_ability(token_contract)
print(f"Mint Status: {'MINTABLE' if minting_status['mintable'] else 'NOT MINTABLE'}")
print(f"Total Supply Status: {minting_status['supplyStatus']}")

print("\n" + "=" * 80)
print("End of Report")
print("=" * 80)

sys.stdout = sys.__stdout__

output_text = buffer.getvalue()

# Save to text file
txt_filename = './data/outputs/report.txt'
os.makedirs(os.path.dirname(txt_filename), exist_ok=True)
with open(txt_filename, 'w') as f:
    f.write(output_text)

print(f"✅ Output saved to {txt_filename} \n")
print(output_text)
