# test/unit/test_requirements.py
import unittest
from esf_pack.schema import BriefRequirements


class TestBriefRequirements(unittest.TestCase):
    def test_defaults_to_none(self):
        self.assertIsNone(BriefRequirements().ror_minimum)

    def test_holds_a_minimum(self):
        self.assertEqual(BriefRequirements(ror_minimum=3).ror_minimum, 3)

    def test_is_frozen(self):
        r = BriefRequirements(ror_minimum=3)
        with self.assertRaises(Exception):
            r.ror_minimum = 5  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
