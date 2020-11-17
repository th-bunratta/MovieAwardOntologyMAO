from owlready2 import (AllDisjoint, AnnotationProperty, AsymmetricProperty, DataProperty,
                       ObjectProperty, SymmetricProperty, FunctionalProperty, IrreflexiveProperty,
                       InverseFunctionalProperty, ReflexiveProperty,
                       Thing, ThingClass, TransitiveProperty)
from typing import Any, Dict, List, Type

from .base import Ontology, OntologyEntity, LABEL_ENTITY_NAME, COMMENT_ENTITY_NAME
from .wrapper import BaseOntologyClass
from .utils import ClassExpToConstruct

# __all__ = (B)

BUILTIN_DATATYPES = [str, int]
CHARACTERISTICS_MAPPING = {
    "owl:AsymmetricProperty": AsymmetricProperty,
    "owl:SymmetricProperty": SymmetricProperty,
    "owl:TransitiveProperty": TransitiveProperty,
    "owl:FunctionalProperty": FunctionalProperty,
    "owl:IrreflexiveProperty": IrreflexiveProperty,
    "owl:ReflexiveProperty": ReflexiveProperty,
    "owl:InverseFunctionalProperty": InverseFunctionalProperty
}
EXP_CONSTRUCTOR = ClassExpToConstruct()


def check_restrictions(prefix: str, str_types: List[str], value: Any) -> bool:
    t = type(value)
    # check for builtin types
    if t in BUILTIN_DATATYPES:
        return True
    p = set([f"{prefix}:{str_type}" for str_type in str_types]).intersection(ENTITIES.keys())
    return len(p) > 0


class OwlProperty(OntologyEntity):
    prefix = "owl"
    range = [Type[str]]

    # owlready-related implementation
    def actualize(self, onto: Ontology):
        """
        Instantiate a Property into a given Ontology

        :param individual_name: The name of an individual, creating an ontology Class if empty
        :param onto: An `owlready2` Ontology
        """
        if self.name in ["topObjectProperty", "topDataProperty"]:
            return
        apply_classes_from(onto)
        self.get_generated_class(onto, range=self.get_generated_range(onto))
        self._sync_internal(onto)

    def get_generated_range(self, onto: Ontology):
        return self.range

    def __repr__(self):
        str_obj = f"{self.name}" if len(self.range) > 0 or self.name == "ObjectProperty" else "<unk>"
        if "owl:Class" not in self.range:
            str_obj += f": {self.range[0]}"
        else:
            str_obj += f": Thing"
        return str_obj


class OwlDataProperty(OwlProperty):
    name = "DataProperty"
    range = [str]
    _parent_class = DataProperty


class OwlObjectProperty(OwlProperty):
    name = "ObjectProperty"
    _range = ["owl:Class"]
    _parent_class = ObjectProperty
    _characteristics = ["owl:SymmetricProperty"]

    def __init__(self, name: str):
        super().__init__(name)
        self._realised_parent_classes.append(ObjectProperty)
        self.inverse_prop: Type or None = None

    def get_generated_class(self, onto: Ontology, **attrs) -> Type[Thing]:
        u = [CHARACTERISTICS_MAPPING.get(c, None) for c in self._characteristics]
        if self.inverse_prop is not None:
            attrs['inverse_property'] = self.get_generated_inverse(onto)
        if len(u) > 0:
            self._realised_parent_classes.extend(u)
        return super(OwlObjectProperty, self).get_generated_class(onto, **attrs)

    def get_generated_range(self, onto: Ontology):
        return [x.get_generated_class(onto) for x in self.range if x is not None]

    def get_generated_inverse(self, onto: Ontology) -> Type:
        self.inverse_prop.inverse_prop = None
        return self.inverse_prop.get_generated_class(onto)

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, a):
        self._range = a
        self.dependencies.extend([b for b in a if not b == "Thing" and b != ""])


class OwlAnnotationProperty(OwlProperty):
    name = "AnnotationProperty"
    range = [str]
    _parent_class = AnnotationProperty

    # owlready-related implementation
    def actualize(self, onto: Ontology):
        """
        Instantiate a Datatype Property into a given Ontology

        :param onto: An `owlready2` Ontology
        """
        self.get_generated_class(onto, range=self.range)


class OwlClass(OntologyEntity):
    """
        A class for ontology classes of instances
    """

    def __repr__(self) -> str:
        return f"OwlClass<{self.prefix}:{self.name}>"

    prefix = "owl"
    name = "Class"
    parent_name = "BaseOntologyClass"
    _parent_class = Thing
    parent_class_names: List[str] = []
    disjoint_class_names: List[str] = []

    def __init__(self, entity_name: str):
        super(OwlClass, self).__init__(entity_qualifier=entity_name)
        self.defined_properties: Dict[str, "OwlProperty" or None] = dict(ENTITIES)

    # owlready-related implementation
    def instantiate(self, onto: Ontology, individual_name: str):
        """
        Instantiate Individuals into a given Ontology

        :param individual_name: The name of an individual, creating an ontology Class if empty
        :param onto: An `owlready2` Ontology
        """
        if not self.is_actualized:
            self.actualize(onto)
        apply_classes_from(onto)
        self._sync_internal(onto)
        inst = self.get_generated_class(onto)()
        inst.name = individual_name
        self._internal_imp_instance = inst

    def actualize(self, onto: Ontology):
        """
        Makes the entity concrete (saved) in a given Ontology

        Args:
            onto: a given Ontology
        """
        apply_classes_from(onto)
        # TODO: realise all equivalents
        [self.add_equivalent_class_expression(EXP_CONSTRUCTOR.to_construct(exp))
         for exp in self.equivalent_class_expressions]
        self._sync_internal(onto)
        self.get_generated_class(onto)
        disj = [x.get_generated_class(onto) for x in self._disjoint_classes if x is not None]
        if len(disj) > 0:
            AllDisjoint(disj)

    def add_property_assertion(self, property_name: str, value):
        """
            Adds property assertions with values
        """
        assert self.is_individual, \
            "Must be an Individual before adding any assertion. Please call instantiate() first"
        assert ":" in property_name and len(property_name.split(":")) == 2, "Please add prefix"
        self.properties_values[property_name] = value
        assert property_name in self.defined_properties, \
            "Must associate a subclass of OwlProperty with the given name before any assertion can be done"
        self._assert_restrictions(self.defined_properties[property_name].range, value)

    def _assert_restrictions(self, types: List[str], value):
        assert check_restrictions(self.prefix, types, value), \
            "The added value doesn't match the range restriction!"


class OwlThing(OwlClass):
    name = "Thing"
    parent_name = "BaseOwlThing"
    prefix = "owl"
    _internal_imp_instance = Thing

    def __init__(self):
        super().__init__(f"{self.prefix}:{self.name}")

    def get_generated_class(self, onto: Ontology, **attrs) -> Type[ThingClass]:
        return self._internal_imp_instance


def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]).union([cls])


def apply_classes_from(onto: Ontology):
    for s in all_subclasses(BaseOntologyClass):
        s.namespace = onto.implementation
        setattr(s, 'storid', onto.implementation.world._abbreviate(s.iri))


def get_match(identifier: str) -> Type[OntologyEntity]:
    for entity in BASE_ENTITIES:
        if identifier == entity.get_entity_qualifier():
            return entity


BASE_ENTITIES = [OwlAnnotationProperty, OwlDataProperty, OwlObjectProperty, OwlClass]
PROPERTY_ENTITIES = {"annotations": OwlAnnotationProperty,
                     "dataProperty": OwlDataProperty,
                     "objectProperty": OwlObjectProperty}
ENTITIES: Dict[str, OntologyEntity] = {

}
BUILTIN_ENTITIES = {
    LABEL_ENTITY_NAME: OwlAnnotationProperty(LABEL_ENTITY_NAME),
    COMMENT_ENTITY_NAME: OwlAnnotationProperty(COMMENT_ENTITY_NAME)
}
