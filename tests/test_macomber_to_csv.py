import os

from scripts.macomber_to_csv import MacomberToCSV


class TestMacomberToCSV:

    test_dir = os.path.dirname(__file__)
    data_dir = os.path.join(test_dir, '..', 'data')

    @classmethod
    def setup_class(cls):
        cls.mac = MacomberToCSV()

    def test_init(self):
        # schema should be set
        assert self.mac.schema
        # sanity check contents
        assert self.mac.schema['sheets']
        assert self.mac.schema['sheets'][0]['name'] == 'Story Instance'

    incipit_start = 'በእንተ፡ ዘከመ፡ አስተርአየቶ፡ ለቴዎፍሎስ፡ ሊቀ፡'

    def test_load_incipits(self):
        self.mac.load_incipits(os.path.join(self.data_dir, 'incipits.csv'))
        assert self.mac.incipits
        assert '1-A' in self.mac.incipits
        assert 'EMML' in self.mac.incipits['1-A']
        assert '6938' in self.mac.incipits['1-A']['EMML']
        assert self.mac.incipits['1-A']['EMML']['6938'] \
            .startswith(self.incipit_start)

    def test_get_incipit(self):
        incipit = self.mac.get_incipit('1-A', 'EMML', '6938')
        assert incipit.startswith(self.incipit_start)
        # missing
        assert self.mac.get_incipit('1-A', 'EMML', 'foo') == ''
