"""
Unit test for GeoID lookup helper `lookup_listing_by_geoid` in `main.py`.

Run with:
    python3 test_get_listing_by_geoid.py
"""

import sys
import json
from types import SimpleNamespace

# Ensure package directory on path
sys.path.append('.')

from main import lookup_listing_by_geoid

class FakeRow:
    def __init__(self, mapping):
        self._mapping = mapping

class FakeResult:
    def __init__(self, row):
        self._row = row
    def fetchone(self):
        return self._row

class FakeConn:
    def __init__(self, scenario='exact'):
        self.scenario = scenario
        # sample listing mapping returned by v_current_listings
        self.sample = {
            'id': '11111111-1111-1111-1111-111111111111',
            'title': 'Test Listing',
            'full_geo_id': '29CG.0AB01',
            'price_monthly_vnd': 3500000
        }

    def execute(self, query, params=None):
        # For exact match scenario, return row when params match
        if self.scenario == 'exact':
            return FakeResult(FakeRow(self.sample))
        elif self.scenario == 'none':
            return FakeResult(None)
        else:
            return FakeResult(None)

class FakeEngine:
    def __init__(self, scenario='exact'):
        self.scenario = scenario
    def connect(self):
        # Return a context manager
        class CM:
            def __init__(self, scenario):
                self.scenario = scenario
            def __enter__(self):
                return FakeConn(self.scenario)
            def __exit__(self, exc_type, exc, tb):
                return False
        return CM(self.scenario)


def test_exact_match():
    engine = FakeEngine(scenario='exact')
    with engine.connect() as conn:
        listing = lookup_listing_by_geoid(conn, '29CG.0AB01')
        assert listing is not None, 'Expected listing for exact match'
        assert listing['full_geo_id'] == '29CG.0AB01'
        print('✓ Exact match returned listing')


def test_not_found():
    engine = FakeEngine(scenario='none')
    with engine.connect() as conn:
        listing = lookup_listing_by_geoid(conn, 'ZZZZ')
        assert listing is None, 'Expected None for not-found case'
        print('✓ Not-found returned None')


if __name__ == '__main__':
    try:
        test_exact_match()
        test_not_found()
        print('\n✅ ALL GeoID lookup tests passed')
        sys.exit(0)
    except AssertionError as e:
        print('\n❌ TEST FAILED:', e)
        sys.exit(1)
