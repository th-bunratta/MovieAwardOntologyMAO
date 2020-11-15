from typing import List, Type

from owlready2 import Ontology, Thing


GENERATED_TYPES = {}


class OntologyEntity:
    prefix = "owl"
    name = "any"
    _internal_dict = {}
    _parent_class = object
    parent_class_names: List[str] = []
    _parent_classes: List["OntologyEntity"] = []
    _disjoint_classes: List["OntologyEntity"] = []

    def __init__(self, entity_qualifier: str):
        pre, n = entity_qualifier.split(":")
        self.prefix = pre
        self.name = n
        self.dependencies = []
        self._parent_classes = []
        self._disjoint_classes = []

    @classmethod
    def get_entity_name(cls) -> str:
        return f"{cls.prefix}:{cls.name}"

    # owlready2-related implementation
    def instantiate(self, onto: Ontology):
        pass

    def get_generated_class(self, onto: Ontology, **attrs) -> Type[Thing]:
        if self.name in GENERATED_TYPES:
            return GENERATED_TYPES[self.name]
        attrs['namespace'] = onto
        default = True
        if len(self._parent_classes) > 0:
            gen = [x.get_generated_class(onto=onto) for x in self._parent_classes if x is not None]
            if len(gen) > 0:
                GENERATED_TYPES[self.name] = type(self.name, tuple(gen), attrs)
                default = False
        if default:
            GENERATED_TYPES[self.name] = type(self.name, (self._parent_class,), attrs)
        return GENERATED_TYPES[self.name]

    def add_superclass(self, superclass: "OntologyEntity"):
        """
        Adds a superclass of this Class.
        This Class will then be a `rdfs:subclassOf` a given superclass
        :param superclass: A given Superclass
        """
        self._parent_classes.append(superclass)

    def add_disjoint_classes(self, cls: "OntologyEntity"):
        self._disjoint_classes.append(cls)
