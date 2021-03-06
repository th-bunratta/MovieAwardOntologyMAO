import unittest
from pathlib import Path
import os
from unittest import TestCase
from dirs import ROOT_DIR

from ontogen import Ontology, OwlIndividual
from ontogen.actualizers.owlready2 import cleanup
from ontogen.converter import OntogenConverter
from ontogen.primitives import OwlClass, OwlObjectProperty, OwlAnnotationProperty
from ontogen.primitives.datatypes import Datatype
from ontogen.utils.classexp import ClassExpToConstruct

from settings import OWL_FILEPATH, OUT_PATH, OUT_FILENAME


def count_files(directory: str) -> int:
    return len([name for name in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, name))])


SPEC_VERSION = 'v2.1.0'


class TestOntogen(TestCase):
    def setUp(self):
        self.converter: OntogenConverter = OntogenConverter.load_from_spec(ROOT_DIR / "mao.yaml")
        self.i: OwlClass = self.converter.get_entity("mao:Film")
        self.parasite_film = OwlIndividual("mao:Parasite")
        self.parasite_film.be_type_of(self.i)
        self.onto = self.converter.sync_with_ontology()

    def test_add_rule(self):
        self.test_realization()
        self.onto.add_rule("mao:ActingSituation(?p) ^ mao:hasActor(?p, ?a) -> mao:actsIn(?a, ?p)", "ActsIn")

    def test_assertion(self):
        self.test_instantiation()
        self.parasite_film.add_property_assertion("mao:hasTitle", "Parasite")
#        self.parasite_film.actualize(self.onto)
      #  self.assertListEqual(['Parasite', 'Parasite'], self.parasite_film.properties_values["mao:hasTitle"])

    def test_instantiation(self):
        film: OwlClass = OwlClass("mao:Film")

        self.parasite_film.be_type_of(film)
        self.parasite_film.add_label("Parasite^^rdfs:Literal@en")
        self.parasite_film.add_property_assertion("mao:hasTitle", "Parasite")
#        self.parasite_film.actualize(self.onto)
#        self.assertEqual(len(self.parasite_film._imp.hasTitle), 1)

    def test_sparql_query(self):
        self.test_assertion()
        lst = self.onto.sparql_query("""SELECT ?individual WHERE { ?individual rdf:type mao:Film }""")
        self.assertEqual("http://www.semanticweb.org/movie-ontology/ontologies/2020/9/mao#Parasite", str(lst[0][0]))
        answer = self.onto.sparql_query("""ASK { mao:Parasite rdf:type mao:Film }""")
        self.assertTrue(answer)

    def test_realization(self):
        self.converter.sync_with_ontology(self.onto)

    # Create an OWL ontology from scratch
    def test_create_ontology(self):
        self.test_assertion()
        self.converter.sync_with_ontology(self.onto)
        self.onto.save_to_file(str(Path(OUT_PATH) / OUT_FILENAME))
        self.onto.save_to_file(str(Path(OUT_PATH) / "out.ttl"), "ttl")

    def test_super_classes(self):
        film_making = self.converter.get_entity("mao:FilmMakingSituation")
        event = self.converter.get_entity("mao:Event")
        sit = self.converter.get_entity("mao:Situation")
        self.assertListEqual([event.actualized_entity, sit.actualized_entity], film_making.actualized_entity.is_a)

    def test_annotation_property(self):
        prop = OwlAnnotationProperty("mao:someProp")
        event = self.converter.get_entity("mao:Event")
        self.test_instantiation()
        self.parasite_film.add_property_assertion("mao:someProp", "Parasite")
        # self.parasite_film.actualize(self.onto)
        self.converter.sync_with_ontology(self.onto)
        self.onto.save_to_file(str(Path(OUT_PATH) / OUT_FILENAME))

    def test_write_yaml(self):
        c = OntogenConverter()
        c.write_yaml(str(ROOT_DIR / 'tests' / Path(OUT_PATH) / OUT_FILENAME), ROOT_DIR / "out/out.yaml")

    def tearDown(self):
        cleanup(self.onto)


class TestOntogenFamily(TestCase):
    def test_family_ontology(self):
        converter = OntogenConverter.load_from_spec(ROOT_DIR / f"tests/specs/{SPEC_VERSION}/test_case2.yaml")
        onto = converter.sync_with_ontology()
        father1 = onto.get_entity("family:Father1")
        aunt1 = onto.get_entity("family:Aunt1")
        self.assertListEqual([father1.actualized_entity], aunt1.actualized_entity.isSiblingOf)
        onto.add_license("MIT License")
        self.assertEqual("http://www.co-ode.org/roberts/family-tree.owl#", onto.base_iri)
        onto.save_to_file("out/family.owl")

    def test_pizza_ontology(self):
        converter = OntogenConverter.load_from_spec(ROOT_DIR / f"tests/specs/{SPEC_VERSION}/test_case1.yaml")
        onto = converter.sync_with_ontology()
        named_pizza = onto.get_entity("pizza:NamedPizza")
        margherita = onto.get_entity("pizza:Margherita")
        cls_exp = ClassExpToConstruct(onto)
        self.assertListEqual(margherita.actualized_entity.is_a,
                             [named_pizza.actualized_entity,
                              cls_exp.to_construct("hasTopping only (MozzarellaTopping or TomatoTopping)"),
                              cls_exp.to_construct("hasTopping some MozzarellaTopping"),
                              cls_exp.to_construct("hasTopping some TomatoTopping")])
        self.assertEqual("http://www.co-ode.org/ontologies/pizza/pizza.owl#", onto.base_iri)
        onto.save_to_file("out/pizza.owl")

    # def test_movie_ontology(self):
    #     o = Ontology.load_from_file(OWL_FILEPATH)
    #     print(o.implementation.metadata.deprecated)


FIXTURES = (
    ("(Mo) and (Ding)", "mao.Mo & mao.Ding"),
    ("{Male, Female, NonBinary}", "OneOf([mao.Male, mao.Female, mao.NonBinary])"),
    ("Ding and (hasPet some (Cat or Dog))", "mao.Ding & mao.hasPet.some(mao.Cat | mao.Dog)"),
    ("Mai and (hasPet some Cat)", "mao.Mai & mao.hasPet.some(mao.Cat)"),
    ("Mai and (hasPet exactly 2 Cat)", "mao.Mai & mao.hasPet.exactly(2, mao.Cat)"),
    ("(Mai and (hasPet exactly 2 Cat)) or (hasPet min 1 Cat)",
     "(mao.Mai & mao.hasPet.exactly(2, mao.Cat)) | mao.hasPet.min(1, mao.Cat)"),
    ("Mo or Ding or Bank", "mao.Mo | mao.Ding | mao.Bank"),
    ("(mao:Mai and mao:Student) or mao:SPP",
     "(mao.Mai & mao.Student) | mao.SPP"),
    ("(not(Dog or Cat)) and (Horse)",
     "Not(mao.Dog | mao.Cat) & mao.Horse"),
    ("(mao:Dog and not(mao:Croc or not(mao:Cat))) "
     "or mao:Cat or (mao:Person and mao:Film)",
     "(mao.Dog & Not(mao.Croc | Not(mao.Cat))) | mao.Cat | (mao.Person & mao.Film)"),
    ("(Horse) and (not(Dog or Cat))", "mao.Horse & Not(mao.Dog | mao.Cat)"),
    ("(Cat and Horse and Dog) and Chicken", "mao.Cat & mao.Horse & mao.Dog & mao.Chicken"),
    ("(mao:Dog and (mao:Done or (mao:Film and mao:Croc))) or mao:Cat or (mao:Person and mao:Film)",
     "(mao.Dog & (mao.Done | (mao.Film & mao.Croc))) | mao.Cat | (mao.Person & mao.Film)")
)


class OntogenClassExpressionTestCase(TestCase):
    def setUp(self):
        self.onto = Ontology("http://www.semanticweb.org/movie-ontology/ontologies/2020/9/mao#")
        self.onto.create()
        obj_prop = OwlObjectProperty("mao:hasPet")
        obj_prop.actualize(self.onto)

    def test_basic(self):
        c = OwlClass("mao:Gender")
        i = OwlIndividual("mao:Male")
        i.be_type_of(c)
       # i.actualize(self.onto)
        i = OwlIndividual("mao:Female")
        i.be_type_of(c)
        #i.actualize(self.onto)
        i = OwlIndividual("mao:NonBinary")
        i.be_type_of(c)
        # i.actualize(self.onto)
        cls = ClassExpToConstruct(self.onto)
        for fixture in FIXTURES:
            exp, expected = fixture
            with self.subTest(exp=exp, expected=expected):
                construct = cls.to_construct(exp)
                self.assertEqual(expected, str(construct))


if __name__ == '__main__':
    unittest.main()
