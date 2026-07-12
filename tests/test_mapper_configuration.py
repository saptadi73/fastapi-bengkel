from sqlalchemy.orm import configure_mappers


def test_all_mappers_are_valid():
    configure_mappers()