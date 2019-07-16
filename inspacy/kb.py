import requests


class KnowledgeBase:

    TRANSLATION_CHAR_TABLE = {
        '\"': None
    }

    @classmethod
    def insee_rules(cls, builder):
        url = "http://rdf.insee.fr/sparql"
        headers = {"Accept": "application/json"}
        query = """
        PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
        SELECT ?concept ?libelle ?acronym WHERE {
            ?concept skos:inScheme ?conceptScheme .
            ?concept skos:prefLabel ?libelle .
            FILTER(regex(str(?conceptScheme),'/concepts/definitions/scheme'))
            FILTER(lang(?libelle) = 'fr')
            OPTIONAL {
                ?concept skos:altLabel ?acronym .
                FILTER(lang(?acronym) = 'fr')
            }
        }
        ORDER BY ?libelle
        """
        params = {"query": query}
        nes = []

        response = requests.get(url=url, headers=headers, params=params).json()
        for bind in response["results"]["bindings"]:
            entity = bind["libelle"]["value"].lower().translate(cls.TRANSLATION_CHAR_TABLE)
            id = bind["concept"]["value"].split('/')[-1]
            while entity[len(entity) - 1] == ' ' or entity[len(entity) - 1] == '\xa0':
                entity = entity[0:len(entity) - 1]
            ne = {
                'level': 'permis',
                'label': 'STAT-CPT',
                'entity': entity,
                'id': id
            }
            nes.append(ne)
            if "acronym" in bind:
                acronym = bind["acronym"]["value"].translate(cls.TRANSLATION_CHAR_TABLE)
                ne = {
                    'level': 'strict',
                    'label': 'STAT-CPT',
                    'entity': acronym,
                    'id': id
                }
                nes.append(ne)
        return builder(nes)
