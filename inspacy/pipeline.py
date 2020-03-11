import json
import os

from spacy.pipeline import EntityRuler
from spacy import displacy
from pipe import EntityLinker
from pipe import RuleBuilder
from kb import KnowledgeBase


class Pipeline:
    """Spacy pipeline with an EntityRuler added before ner"""

    def __init__(self, cfg):
        """Init a pipeline running tagger & parser, then build entity rules from a knowledge base. Add an EntityRuler
        component with built-in rules to the pipeline."""
        builder = RuleBuilder(cfg['SpaCy'])
        self.nlp = builder.get_pipeline()
        self.debug = json.loads(cfg['InspaCy'].get('debug'))

        rules, self.definitions, self.entities = KnowledgeBase.insee_rules(builder)

        if self.debug:
            with open(os.environ['INSPACY_HOME'] + "/debug/rules.jsonl", mode="w") as file:
                for rule in rules:
                    file.write((json.dumps(rule, ensure_ascii=False) + '\n'))

        ruler = EntityRuler(self.nlp)
        ruler.add_patterns(rules)
        linker = EntityLinker(cfg)

        self.nlp.add_pipe(ruler)
        self.nlp.add_pipe(linker)

    def __call__(self, text, format=None):
        doc = self.nlp(text)
        if format == 'html':
            return displacy.render(doc, style='ent', minify=True), displacy.render(doc, style='dep', minify=True)
        elif format == 'json':
            return __class__.pipe_jsonify(self.definitions, self.entities, doc)
        else:
            return doc

    @staticmethod
    def pipe_jsonify(definitions, entities, doc):
        result = doc.to_json()
        result["ents"] = [{"start": ent.start_char, "end": ent.end_char,
                           "label": ent.label_, "link": ent._.link,
                           "entity": entities[ent.ent_id_],
                           "definition": definitions["standard"][ent.ent_id_] if (ent.ent_id_ in definitions["standard"]) else "",
                           "shortDefinition": definitions["short"][ent.ent_id_] if (ent.ent_id_ in definitions["short"]) else ""} for ent in doc.ents]
        return result
