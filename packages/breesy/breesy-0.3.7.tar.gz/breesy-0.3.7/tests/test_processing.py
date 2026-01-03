from pathlib import Path
import numpy as np
from breesy.load import load_recording
from breesy.processing import get_frequency_spectrum_channel, get_frequency_spectrum

REPO_ROOT = Path(__file__).parent.parent


def test_get_frequency_spectrum_channel():
    # Arrange
    datapath = REPO_ROOT / "tests" / "data" / "alpha" / "subject_01.mat"
    rec = load_recording(str(datapath))
    first_channel_name = rec.channel_names[0]

    # Act
    f, spectrum = get_frequency_spectrum_channel(rec, first_channel_name)

    # Assert
    assert f.ndim == 1
    assert spectrum.ndim == 1
    assert len(f) == len(spectrum)
    assert np.all(f >= 0)
    assert np.all(spectrum > 0)
    assert np.all(np.isfinite(spectrum))


def test_get_frequency_spectrum_channel_matches_full():
    # Arrange
    datapath = REPO_ROOT / "tests" / "data" / "alpha" / "subject_01.mat"
    rec = load_recording(str(datapath))
    first_channel_name = rec.channel_names[0]

    # Act
    f_full, spectrum_full = get_frequency_spectrum(rec)
    f_single, spectrum_single = get_frequency_spectrum_channel(rec, first_channel_name)

    # Assert
    assert np.array_equal(f_full, f_single)
    assert np.allclose(spectrum_full[0], spectrum_single)
