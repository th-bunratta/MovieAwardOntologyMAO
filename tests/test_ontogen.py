from pathlib import Path
import os
from unittest import TestCase

from ontogen.owlready_converter import YamlToOwlConverter
from ontogen.wrapper import OwlClass


def count_files(directory: str) -> int:
    return len([name for name in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, name))])


class TestOntogen(TestCase):
    converter: YamlToOwlConverter

    def setUp(self):
        self.converter = YamlToOwlConverter("data/mao.yaml")

    def test_mao_to_owl_model_scripts(self):
        p = os.path.dirname(__file__)
        self.converter.to_python_scripts(p)

        c = count_files(Path(p) / "generated" / "mao")
        self.assertEqual(42, c)

    def test_assertion(self):
        i: OwlClass = self.converter.get_entity("mao:Film")
        i.add_property_assertion("mao:hasTitle", "Parasite")
        self.assertEqual("Parasite", i.properties_values["mao:hasTitle"])
        print(i)
