import requests
from datetime import datetime


class Client:
    DEFAULT_URL = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'

    COMMON_PREFIXES = [
        'PREFIX wd: <http://www.wikidata.org/entity/>',
        'PREFIX wdt: <http://www.wikidata.org/prop/direct/>',
        'PREFIX wikibase: <http://wikiba.se/ontology#>',
        'PREFIX p: <http://www.wikidata.org/prop/>',
        'PREFIX v: <http://www.wikidata.org/prop/statement/>',
        'PREFIX q: <http://www.wikidata.org/prop/qualifier/>',
        'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>',
    ]

    def __init__(self, uri=DEFAULT_URL, useragent='Python WDQS Client (v1.0)'):
        self.uri = uri
        self.useragent = useragent

    def raw_query(self, query, add_common_prefixes=True):
        if add_common_prefixes:
            query = '\n'.join(Client.COMMON_PREFIXES) + '\n' + query
        resp = requests.get(
            self.uri,
            params={'query': query, 'format': 'json'},
            headers={'User-Agent': self.useragent}
        )
        return resp.json()

    def query(self, query):
        return self._parse_response(self.raw_query(query))

    def _parse_value(self, item):
        if 'datatype' not in item:
            return item['value']
        elif item['datatype'] == 'http://www.w3.org/2001/XMLSchema#dateTime':
            # This is ok, since we assume WDQS returns only UTC timestamps
            return datetime.strptime(item['value'], '%Y-%m-%dT%H:%M:%SZ')

    def _parse_response(self, response):
        parsed = []
        for item in response['results']['bindings']:
            parsed.append({k: self._parse_value(v) for k, v in item.items()})
        return parsed
