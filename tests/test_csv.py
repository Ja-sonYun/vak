import pytest

import vak


@pytest.mark.parametrize(
    'config_type, audio_format, spect_format, annot_format, expected_result',
    [
        ("train", "cbin", None, "notmat", True),
        ("train", "wav", None, "birdsong-recognition-dataset", True),
        ("train", None, "mat", "yarden", True),
    ]
)
def test_has_unlabeled(config_type,
                       audio_format,
                       spect_format,
                       annot_format,
                       expected_result,
                       model,
                       specific_config_toml,
                       specific_csv_path):
    csv_path = specific_csv_path(config_type,
                                 model,
                                 annot_format,
                                 audio_format,
                                 spect_format)
    config_toml = specific_config_toml(config_type,
                                       model,
                                       annot_format,
                                       audio_format,
                                       spect_format)
    labelset = vak.converters.labelset_to_set(
        config_toml['PREP']['labelset']
    )

    has_unlabeled = vak.csv.has_unlabeled(csv_path, labelset)
    assert has_unlabeled == expected_result