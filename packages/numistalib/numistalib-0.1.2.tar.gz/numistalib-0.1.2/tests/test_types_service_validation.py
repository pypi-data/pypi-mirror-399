"""Unit test for TypeBasicService validation error path.

Ensures a `ValueError` is raised when no search criteria are provided.
"""

import pytest

from numistalib.services.types.service import SearchParams, TypeBasicService


class NoopClient:
    # Not invoked in this test because validation fails before network
    def get(self, *args, **kwargs):  # pragma: no cover
        raise AssertionError("Should not be called")


def test_type_search_raises_without_criteria() -> None:
    service = TypeBasicService(NoopClient())
    params = SearchParams()
    with pytest.raises(ValueError):
        service.search_types(params)
