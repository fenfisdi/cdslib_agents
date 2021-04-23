from unittest import TestCase

from cdslib.models.population import BoxSize


class BoxSizeTestCase(TestCase):

    def test_box_size_instance(self):
        result = BoxSize(0, 100, 0, 100)

        self.assertEqual(result.left, 0)
        self.assertEqual(result.right, 100)
        self.assertEqual(result.bottom, 0)
        self.assertEqual(result.top, 100)
