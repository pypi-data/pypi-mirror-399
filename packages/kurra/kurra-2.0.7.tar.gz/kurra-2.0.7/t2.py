from kurra.shacl import validate
from pathlib import Path

data_file = Path(__file__).parent / "tests/test_shacl/vocab-invalid.ttl"


# print(validate(data_file, "https://linked.data.gov.au/def/vocpub/validator"))
# print(validate(data_file, "9"))

data_files = [
    Path(__file__).parent / "tests/test_shacl/vocab-invalid.ttl",
    Path(__file__).parent / "tests/test_shacl/vocab-invalid-additions.ttl",
]
print(validate(data_files, "https://linked.data.gov.au/def/vocpub/validator"))