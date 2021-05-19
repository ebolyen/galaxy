import ast
import unittest

from galaxy.datatypes.qiime2 import strip_properties


# Note: Not all the expressions here are completely valid types they are just
# representative examples
class TestStripProperties(unittest.TestCase):
    def test_simple(self):
        simple_expression = 'Taxonomy % Properties("SILVIA")'
        stripped_expression = 'Taxonomy'

        reconstructed_expression = strip_properties(simple_expression)
        self.assertEqual(reconstructed_expression, stripped_expression)

    def test_single(self):
        single_expression = 'FeatureData[Taxonomy % Properties("SILVIA")]'
        stripped_expression = 'FeatureData[Taxonomy]'

        reconstructed_expression = strip_properties(single_expression)
        self.assertEqual(reconstructed_expression, stripped_expression)

    def test_double(self):
        double_expression = ('FeatureData[Taxonomy % Properties("SILVIA"), '
                             'DistanceMatrix % Axes("ASV", "ASV")]')
        stripped_expression = 'FeatureData[Taxonomy, DistanceMatrix]'

        reconstructed_expression = strip_properties(double_expression)
        self.assertEquals(reconstructed_expression, stripped_expression)

    def test_nested(self):
        nested_expression = ('Tuple[FeatureData[Taxonomy % '
                             'Properties("SILVIA")] % Axes("ASV", "ASV")]')
        stripped_expression = 'Tuple[FeatureData[Taxonomy]]'

        reconstructed_expression = strip_properties(nested_expression)
        self.assertEqual(reconstructed_expression, stripped_expression)

    def test_complex(self):
        complex_expression = \
            ('Tuple[FeatureData[Taxonomy % Properties("SILVA")] % Axis("ASV") '
             ',DistanceMatrix % Axes("ASV", "ASV")] % Unique')
        stripped_expression = 'Tuple[FeatureData[Taxonomy], DistanceMatrix]'

        reconstructed_expression = strip_properties(complex_expression)
        self.assertEqual(reconstructed_expression, stripped_expression)
