# Reference:
# https://gist.github.com/kgriffs/c20084db6686fee2b363fdc1a8998792#file-uuid_regex-py-L7-L17


import re

# RFC 4122 states that the characters should be output as lowercase, but
#   that input is case-insensitive. When validating input strings,
#   include re.I or re.IGNORECASE per below:


def _create_pattern(version="[1-5]"):
    return re.compile(
        (
            "[a-f0-9]{8}-"
            + "[a-f0-9]{4}-"
            + version
            + "[a-f0-9]{3}-"
            + "[89ab][a-f0-9]{3}-"
            + "[a-f0-9]{12}"
        ),
        re.IGNORECASE,
    )


UUID_ALL_PATTERN = _create_pattern()
UUID_V4_PATTERN = _create_pattern("4")
