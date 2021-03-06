import datetime
import re

import owlready2
from rdflib import Graph, Namespace
from owlready2 import Imp, get_ontology, sync_reasoner_pellet
from typing import Any, Dict, List, Optional, Union, Type, Set, Tuple

from . import OwlEntity
from .namespaces import lookup_iri, lookup_prefix, build_prefixes, WELL_KNOWN_PREFIXES
from .assertable import OwlAssertable
from ontogen.primitives.classes import OwlClass, OwlIndividual
from ontogen.primitives.properties import OwlObjectProperty
from ..primitives import OwlDataProperty
from ..utils.basics import absolutize_entity_name


def get_ontology_from_prefix(prefix: str, ld: dict):
    return get_ontology(lookup_iri(prefix, ld))


FREE_DOMAIN = "http://www.semanticweb.org"
ANNOTATION_FUNCTION_MAP = {
    'license': 'add_license',
    'label': 'add_label',
    'comment': 'add_comment'
}


class Ontology(OwlAssertable):
    """
    TODO: A proxy for the real implementation in `owlready2`
    """
    license: str
    seeAlso: str
    contributor: str
    comment: str

    def __init__(self, base_iri: str = "", base_prefix: str = ""):
        super(Ontology, self).__init__()
        self._internal_onto: owlready2.Ontology or None = None
        self.base_iri = base_iri
        self.base_prefix = base_prefix
        self.iris: Dict[str, str] = {}
        self.annotations: Dict[str, List[Union["OwlAnnotationProperty", Any]]] = {}
        self.entities: Dict[str, Union[OwlEntity, OwlIndividual]] = {}
        self.disjoint_sets: List[Tuple['OwlEntity']] = []

    def _get_with_type(self, t: Type[Union['OwlEntity', 'OwlIndividual']]):
        return {x: self.entities[x] for x in self.entities if isinstance(self.entities[x], t)}

    @property
    def individuals(self) -> Dict[str, OwlIndividual]:
        """Returns all the Individuals of this Ontology"""
        return self._get_with_type(OwlIndividual)

    @property
    def classes(self) -> Dict[str, OwlClass]:
        """Returns all the Classes of this Ontology"""
        return self._get_with_type(OwlClass)

    @property
    def object_properties(self) -> Dict[str, OwlObjectProperty]:
        """Returns all the Object Properties of this Ontology"""
        return self._get_with_type(OwlObjectProperty)

    @property
    def data_properties(self) -> Dict[str, OwlDataProperty]:
        """Returns all the Data Properties of this Ontology"""
        return self._get_with_type(OwlDataProperty)

    def get_entity(self, relative_name: str) -> Union[OwlEntity, None]:
        name = absolutize_entity_name(relative_name, self.base_prefix)
        return self.entities.get(name, None)

    def generate_base_iri_from_prefix(self, developer: str = "nomad"):
        now = datetime.datetime.now()
        if not self.base_iri:
            self.base_iri = f"{FREE_DOMAIN}/{developer}/ontologies/{now.year}/{now.month}/{self.base_prefix}#"

    def _get_onto_from_prefix(self, prefix: str) -> owlready2.Ontology:
        return get_ontology_from_prefix(prefix, self.iris)

    def lookup_iri(self, prefix: str) -> str:
        """Returns a fully qualified IRI from a given prefix

        Args:
            prefix: A given prefix

        """
        return lookup_iri(prefix, self.iris)

    def lookup_prefix(self, iri: str) -> str:
        """Returns a fully qualified prefix from a given IRI

        Args:
            iri: A given IRI
        """
        return lookup_prefix(iri, self.iri_to_prefixes)

    def update_base_prefix(self):
        b = self.lookup_prefix(self.base_iri)
        self.base_prefix = b

    @property
    def iri_to_prefixes(self):
        return {v: k for k, v in self.iris.items()}

    def create(self, namespace_iri: str = ""):
        """Newly creates an Ontology from an existing namespace

        Args:
            namespace_iri: A given namespace

        Returns:
            None
        """
        if not (self.base_iri == "" or namespace_iri == ""):
            raise AssertionError("Namespace must be set before creation")
        self.base_iri = self.base_iri if self.base_iri != "" else namespace_iri
        self._internal_onto = get_ontology(self.base_iri)
        if not self.base_prefix:
            self.base_prefix = self.implementation.name
        self.implementation.name = self.base_prefix
        self.define_prefix()

    def define_prefix(self, prefix: Optional[str] = None, iri: Optional[str] = None,
                      allow_update: Optional[bool] = True):
        """Associate a prefix with an IRI in this Ontology

        Args:
            prefix: A given prefix shorthand
            iri: A given IRI
            allow_update: Checks whether the given prefix is already defined for an IRI

        Returns:
            None
        """
        if prefix is None:
            prefix = self.base_prefix
        if iri is None:
            iri = self.base_iri
        if not allow_update and prefix in self.iris:
            raise AssertionError(f"Prefix {prefix} is already associated with IRI {self.iris[prefix]}")
        if iri in self.iri_to_prefixes:
            return
        self.iris[prefix] = iri

    @classmethod
    def load_from_file(cls, filename: str) -> "Ontology":
        """Loads an Ontology from an existing file

        Args:
            filename: The name of a given file

        Returns: An Ontology object
        """
        inst = cls()
        inst._internal_onto = get_ontology(f"file://{filename}")
        internal = inst._internal_onto
        internal.load()
        for k in ANNOTATION_FUNCTION_MAP:
            if hasattr(internal.metadata, k):
                [getattr(inst, ANNOTATION_FUNCTION_MAP[k])(prop)
                 for prop in getattr(internal.metadata, k)]
        inst.base_iri, inst.base_prefix = inst.implementation.base_iri, inst.implementation.name
        inst.define_prefix()
        return inst

    def save_to_file(self, filename: str, file_format: str = "xml"):
        """Saves an Ontology with a given filename

        Args:
            filename: The name of a given file
            file_format: The file format of given filename. Only `xml` is supported by `owlready2`
        """

        with self.implementation:
            g: Graph = self.rdflib_graph
            self.iris.update(WELL_KNOWN_PREFIXES)
            if len(self.iris) > 0:
                for prefix in self.iris:
                    #self.implementation.graph.add_ontology_alias(prefix, self.iris[prefix])
                    g.namespace_manager.bind(prefix, Namespace(self.iris[prefix]))
            with open(filename, mode="wb") as file:
                file.write(g.serialize(format=file_format))

    def add_rule(self, swrl_rule: str, rule_name: str = None, comment: str = None):
        """Adds a SWRL rule to the Ontology

        Args:
            swrl_rule: A rule definition in SWRL
            rule_name: The name of the given rule in `rdfs:label`
            comment: An `rdfs:comment` on the given rule
        """
        rule = Imp(namespace=self.implementation)
        if rule_name is not None:
            rule.label = rule_name
        if comment is not None:
            rule.comment = comment
        rule.set_as_rule(swrl_rule.replace(f"swrlb:", "").replace(f"{self.base_name}:", "").replace("^ ", ", "))

    @property
    def implementation(self) -> owlready2.Ontology:
        if self._internal_onto is None:
            self.create()  # lazy creation
        return self._internal_onto

    @property
    def base_name(self):
        return self.implementation.name

    def add_label(self, label: Union[str, int]):
        self.add_annotation("rdfs:label", label)

    def add_license(self, label: Union[str, int]):
        self.add_annotation("dcterms:licence", label)

    def add_annotation(self, annotation: str, value: Any):
        self.add_property_assertion(annotation, value)

    def actualize(self):
        self.actualize_assertions(self.implementation.metadata)

    def add_disjoint_set(self, owl_class_set: Tuple['OwlEntity', ...]):
        """Adds a tuple of disjoint classes to this Ontology. The given class will be lazy loaded.

        Args:
            owl_class_set: an OntologyEntity
        """
        if owl_class_set is None:
            return TypeError(f"owl_class must not be None")
        self.disjoint_sets.append(owl_class_set)

    @property
    def rdflib_graph(self) -> Graph:
        return self.implementation.world.as_rdflib_graph()

    def sparql_query(self, query: str, with_prefixes=True, sync_reasoner=False) -> list or bool:
        """Queries the Ontology in SPARQL

        Args:
            query: A query in SPARQL
            with_prefixes: Whether the prefixes will be included prior to the query
            sync_reasoner: Whether to sync the Pellet reasoner or not

        Returns:
            A result
        """
        if sync_reasoner:
            sync_reasoner_pellet()
        if with_prefixes:
            #q = self.rdflib_graph.query(query, initNs=self.iris)
            m = re.match(r"PREFIX (.+): <(.+)>", query)
            if m is not None:
                raise AssertionError("Prefixes are already included.")
            query = build_prefixes(self.iris) + query
            q = self.rdflib_graph.query(query)
        else:
            q = self.rdflib_graph.query(query)
        if q.type == 'ASK':
            return q.askAnswer
        else:
            return list(q)

    def add_entity(self, entity: 'OwlEntity'):
        """Adds a given Entity into this Ontology

        Args:
            entity: A given Entity

        Returns:
            None
        """
        self.entities[absolutize_entity_name(entity.name, self.base_prefix)] = entity

    def sync_iri(self):
        self.base_prefix = self.lookup_prefix(self.base_iri)
