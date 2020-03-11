import requests
import os


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
        PREFIX xkos:<http://rdf-vocabulary.ddialliance.org/xkos#>

        SELECT ?concept ?libelle ?acronym ?definitionValue ?shortDefinitionValue WHERE {
            ?concept skos:inScheme ?conceptScheme;
                     skos:prefLabel ?libelle .
            FILTER(regex(str(?conceptScheme),'/concepts/definitions/scheme'))
            FILTER(lang(?libelle) = 'fr')
            OPTIONAL {
                ?concept skos:altLabel ?acronym .
                FILTER(lang(?acronym) = 'fr')
            }
            OPTIONAL {
                ?concept skos:definition ?definition ;
                         skos:scopeNote ?shortDefinition.
                ?definition xkos:plainText ?definitionValue .
                ?shortDefinition xkos:plainText ?shortDefinitionValue .
                FILTER(lang(?definitionValue) = 'fr')
                FILTER(lang(?shortDefinitionValue ) = 'fr')
            }
        }
        ORDER BY ?concept
        """
        params = {"query": query}
        nes = []
        definitions = {
            "short": {},
            "standard": {}
        }
        entities = {}
        proxies = {}

        # Yep, dirty...
        if 'HTTP_PROXY' in os.environ:
            proxies = {
                'http': os.environ['HTTP_PROXY']
            }

        response = requests.get(url=url, headers=headers, params=params, proxies=proxies).json()
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
            if "shortDefinitionValue" in bind:
                definitions["short"][id] = bind["shortDefinitionValue"]["value"]
            if "definitionValue" in bind:
                definitions["standard"][id] = bind["definitionValue"]["value"]
            entities[id] = entity
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
        return builder(nes), definitions, entities
