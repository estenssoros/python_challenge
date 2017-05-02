import re


class MyUtil(object):
    def __init__(self):
        pass

    def extract_ips(self, fname):
        '''
        given filename or file object, extract ip addressses
        '''
        if isinstance(fname, str):
            with open(fname, 'r') as f:
                text = f.read()
        else:
            text = fname.read()
        return re.findall(r'[0-9]+(?:\.[0-9]+){3}', text)

    def parse_entities(self, entities):
        '''
        recursively pull entities from json
        '''
        handles = set()
        for ent in entities:
            if ent.get('entities'):
                handles.update(self.parse_entities(ent['entities']))
            else:
                handles.add(ent['handle'])
        return handles

    def camel_to_snake(self, name):
        '''
        convert string from camel case to snake case
        '''
        name = name.replace(' ', '_')
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def parse_rdap_json(self, resp):
        '''
        pasre json reponse from rdap api
        '''
        keys = ['ip', 'name', 'country', 'startAddress', 'endAddress', 'handle', 'ipVersion', 'lang', 'parentHandle', 'type', 'port43']
        parsed = {k: resp.get(k, None) for k in keys}
        parsed['status'] = None
        if resp.get('status'):
            parsed['status'] = resp['status'][0]
        parsed['last changed'] = None
        parsed['registration'] = None
        if resp.get('events'):
            for e in resp['events']:
                parsed[e['eventAction']] = e['eventDate']
        parsed['description'] = None
        # if resp.get('remarks'):
        #     parsed['description'] = '|'.join(resp['remarks'][0]['description'])
        parsed['entities'] = None
        if resp.get('entities'):
            parsed['entities'] = '|'.join(self.parse_entities(resp['entities']))
        return {self.camel_to_snake(k): v for k, v in parsed.iteritems()}
