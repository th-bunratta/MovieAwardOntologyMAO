import unittest
from io import StringIO

from dirs import ROOT_DIR
from extended_csv import read_xsv_file
from sa_autowrite.create import write_model


class TestAutowrite(unittest.TestCase):

    def test_write_model(self):
        args = [
            ('Nutrient', 'autowrite/nutrient.py', 'csv/nutrient-100.csv', 100, {'pk_cols': ['id']}),
            ('BrandedFood', 'autowrite/branded_food.py', 'csv/branded_food-10000.csv', 10000, {}),
        ]
        for name, out, in_, limit, options in args:
            # Commented out because PyCharm doesn't support auto show large diff in subTests yet
            # with self.subTest(f'{out=}{in_=}{limit=}{options=}'):
            with open(ROOT_DIR / f'tests/data/{out}', 'r', encoding='utf-8') as f:
                expected_result = f.read()

            output = StringIO()
            data = read_xsv_file(ROOT_DIR / f'tests/data/{in_}', dialect='excel', load_at_most=limit)
            write_model(output, name, data, **options)

            self.assertEqual(expected_result, output.getvalue())


if __name__ == '__main__':
    unittest.main()
