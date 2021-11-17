import requests 

LLAMA_ENDPOINT = 'http://api.llama.fi/'

def get_llama_tvl(protocol: str) -> float:
    """
    Returns the current TVL value (float) for the specified protocol slug
    """
    url = f'{LLAMA_ENDPOINT}/tvl/{protocol}'
    return float(requests.get(url).text)

def get_llama_projects_list() -> list():
    """
    Returns a list of tuples: (Project Name, Slug)
    """
    url = f'{LLAMA_ENDPOINT}/protocols'
    protocols = requests.get(url).json()
    protocols_list = [(protocol['name'], protocol['slug']) for protocol in protocols]
    return protocols_list