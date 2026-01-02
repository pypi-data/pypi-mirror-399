import pytest

@pytest.fixture()
def ko_raw_record():
    return "ENTRY       K00001                      KO\n" \
           "NAME        E0.0.0.0\n" \
           "DEFINITION  a fake gene\n" \
           "PATHWAY     ko00000 a fake pathway\n" \
           "DISEASE     H00000 A bad one\n" \
           "CLASS       Metabolism; Carbohydrate Metabolism; Glycolysis / Gluconeogenesis[PATH:ko00010]\n" \
           "REACTION    R00623  primary_alcohol:NAD+ oxidoreductase\n" \
           "            R00754  ethanol:NAD+ oxidoreductase\n" \
           "DBLINKS     COG: COG0000\n" \
           "            GO: 0004022 0004023 0004024 0004025\n" \
           "GENES       HSA: hsa00000\n" \
           "REFERENCE\n" \
           "  AUTHORS   Fake G.\n" \
           "  TITLE     Not Real\n" \
           "  JOURNAL   Nurture (2001)\n" \
           "  SEQUENCE  [fke:FK_0000]"

@pytest.fixture()
def list_of_kos():
    return ['K00001', 'K00002']