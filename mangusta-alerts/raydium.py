import requests
from requests.models import parse_header_links 

RAYDIUM_ENDPOINT = 'https://api.raydium.io'

def get_raydium_pool_info(pool: str) -> dict():
    """
    Returns info of the specified pool
    """
    url = f'{RAYDIUM_ENDPOINT}/pairs'
    data = requests.get(url).json()

    for pair in data:
        if pair['name'] == pool:
            return pair

    """
    {
        'name': 'CWAR-USDC',
        'amm_id': '13uCPybNakXHGVd2DDVB7o2uwXuf9GqPFkvJMVgKy6UJ',
        'lp_mint': 'HjR23bxn2gtRDB2P1Tm3DLepAPPZgazsWJpLG9wqjnYR',
        'lp_price': 0.43111626266505687,
        'liquidity': 1399358.474798,
        'price': 1.5888860374747904,
        'token_amount_coin': 440358.352264834,
        'token_amount_lp': 3245895.819720423,
        'token_amount_pc': 699679.237399,
        'apy': 178.72,
        'volume_24h': 651549.325233,
        'volume_24h_quote': 651549.325233,
        'volume_7d': 12247049.515687,
        'volume_7d_quote': 12247049.515687
        'fee_24h': 1628.8733130825,
        'fee_24h_quote': 1628.8733130825,
        'fee_7d': 30617.6237892175,
        'fee_7d_quote': 30617.6237892175,
        'market': 'CDYafmdHXtfZadhuXYiR7QaqmK9Ffgk2TA8otUWj9SWz',
        'official': true,
        'pair_id': 'HfYFjMKNZygfMC8LsQ8LtpPsPxEJoXJx4M6tqi75Hajo-EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    }
    """

    return 'Pool not found!'

def get_raydium_pool_tvl(pool: str) -> float:
    """
    Returns the current TVL value (float) for the specified pool
    """
    url = f'{RAYDIUM_ENDPOINT}/pairs'
    data = requests.get(url).json()

    for pair in data:
        if pair['name'] == pool:
            return float(pair['liquidity'])

    return 'Pool not found!'

def get_raydium_pools_list() -> list():
    """
    Returns a list of tuples: (Pool Name, Pool token)
    """
    url = f'{RAYDIUM_ENDPOINT}/pairs'
    data = requests.get(url).json()

    pools_list = [(pool['name'], pool['name']) for pool in data]

    return pools_list

def get_token_price(token: str) -> float:
    """
    Returns the current price of the specified token
    """
    url = f'{RAYDIUM_ENDPOINT}/coin/price'
    data = requests.get(url).json()

    try:
        return data[token]
    except Exception:
        return 'Token not found!'
