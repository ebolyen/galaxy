import ast
import unittest

from galaxy.datatypes.qiime2 import PredicateRemover, ReconstructExpression


# Note: Not all the expressions here are completely valid types they are just
# representative examples
class TestStripProperties(unittest.TestCase):
    def test_simple(self):
        simple_expression = 'Taxonomy % Properties("SILVIA")'
        stripped_expression = 'Taxonomy'

        simple_tree = ast.parse(simple_expression)
        PredicateRemover().visit(simple_tree)

        reconstruct = ReconstructExpression()
        reconstruct.visit(simple_tree)
        self.assertEqual(reconstruct.expression, stripped_expression)

    def test_single(self):
        single_expression = 'FeatureData[Taxonomy % Properties("SILVIA")]'
        stripped_expression = 'FeatureData[Taxonomy]'

        single_tree = ast.parse(single_expression)
        PredicateRemover().visit(single_tree)

        reconstruct = ReconstructExpression()
        reconstruct.visit(single_tree)
        self.assertEqual(reconstruct.expression, stripped_expression)

    def test_double(self):
        double_expression = ('FeatureData[Taxonomy % Properties("SILVIA"), '
                             'DistanceMatrix % Axes("ASV", "ASV")]')
        stripped_expression = 'FeatureData[Taxonomy, DistanceMatrix]'

        double_tree = ast.parse(double_expression)
        PredicateRemover().visit(double_tree)

        reconstruct = ReconstructExpression()
        reconstruct.visit(double_tree)
        self.assertEquals(reconstruct.expression, stripped_expression)

    def test_nested(self):
        nested_expression = ('Tuple[FeatureData[Taxonomy % '
                             'Properties("SILVIA")] % Axes("ASV", "ASV")]')
        stripped_expression = 'Tuple[FeatureData[Taxonomy]]'

        nested_tree = ast.parse(nested_expression)
        PredicateRemover().visit(nested_tree)

        reconstruct = ReconstructExpression()
        reconstruct.visit(nested_tree)
        self.assertEqual(reconstruct.expression, stripped_expression)

    def test_complex(self):
        complex_expression = \
            ('Tuple[FeatureData[Taxonomy % Properties("SILVA")] % Axis("ASV") '
             ',DistanceMatrix % Axes("ASV", "ASV")] % Unique')
        stripped_expression = 'Tuple[FeatureData[Taxonomy], DistanceMatrix]'

        complex_tree = ast.parse(complex_expression)
        PredicateRemover().visit(complex_tree)

        reconstruct = ReconstructExpression()
        reconstruct.visit(complex_tree)
        self.assertEqual(reconstruct.expression, stripped_expression)
