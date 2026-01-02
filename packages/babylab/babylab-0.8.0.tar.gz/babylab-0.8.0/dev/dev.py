"""
Fixtures for testing.
"""

from babylab import api
from tests import conftest

records = api.Records()
data_dict = api.get_data_dict()
ppt = conftest.create_record_ppt()
apt = conftest.create_record_apt()
que = conftest.create_record_que()
