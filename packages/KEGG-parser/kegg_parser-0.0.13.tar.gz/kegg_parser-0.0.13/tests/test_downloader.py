import pytest

from KEGG_parser.downloader import get_from_kegg_flat_file, get_kegg_record_dict, \
    get_kegg_link_from_api
from KEGG_parser.parsers import parse_ko
from test_fixtures import ko_raw_record, list_of_kos


@pytest.fixture()
def ko_flat_file(tmpdir_factory, ko_raw_record):
    fn = tmpdir_factory.mktemp("data").join("ko")
    fn.write('%s///\n' % '///\n'.join([ko_raw_record] * 3))
    return str(fn)


def test_get_from_kegg_flat_file(ko_flat_file):
    organism_records = get_from_kegg_flat_file(ko_flat_file)
    assert len(organism_records) == 3


def test_get_kegg_record_dict(list_of_kos, ko_flat_file):
    ko_dict_web = get_kegg_record_dict(list_of_kos, parse_ko)
    assert len(ko_dict_web) == 2
    ko_dict_local = get_kegg_record_dict(list_of_kos, parse_ko, ko_flat_file)
    assert len(ko_dict_local) == 1


def test_get_kegg_link_from_api():
    link_dict = get_kegg_link_from_api('ko', 'hsa')
    assert tuple(link_dict.keys())[0].startswith('K')
