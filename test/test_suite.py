"""Run all tests."""
import os
import unittest

import test_lml_optimizer as lo

from common import get_data

wkdir = os.getcwd()


class ConfigTestCase(unittest.TestCase):
    """Test suite for AtoML code base."""

    def test_lml_optimizer(self):
        """Test log_marginal_likelihood optimization."""
        train_features, train_targets, test_features, \
            test_targets = get_data()
        lo.lml_test(train_features, train_targets, test_features, test_targets)


if __name__ == '__main__':
    unittest.main()
