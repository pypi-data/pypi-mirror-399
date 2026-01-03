from pathlib import Path
import numpy as np
from breesy.load import load_recording
from breesy.features import get_mean_power, get_mean_power_per_channel, get_normalized_covariance_matrix, \
    get_spatial_filter_from_covariances, get_csp_features
from breesy.recording import split_by_window_duration

REPO_ROOT = Path(__file__).parent.parent


def test_mean_power_alpha_band():
    # Arrange
    datapath = REPO_ROOT / "tests" / "data" / "alpha" / "subject_01.mat"
    rec = load_recording(str(datapath))
    epochs = split_by_window_duration(rec, window_duration=5.0)
    epoch_data = np.array([epoch.data for epoch in epochs])
    n_epochs, n_channels, _ = epoch_data.shape

    # Act
    alpha_power = get_mean_power(epoch_data, freq_range='alpha', sample_rate=rec.sample_rate)

    # Assert
    assert alpha_power.ndim == 1
    assert alpha_power.shape[0] == len(epochs)
    assert np.all(alpha_power > 0)
    assert np.all(np.isfinite(alpha_power))


def test_mean_power_per_channel_alpha_band():
    # Arrange
    datapath = REPO_ROOT / "tests" / "data" / "alpha" / "subject_01.mat"
    rec = load_recording(str(datapath))
    epochs = split_by_window_duration(rec, window_duration=5.0)
    epoch_data = np.array([epoch.data for epoch in epochs])
    n_epochs, n_channels, _ = epoch_data.shape

    # Act
    alpha_power_per_channel = get_mean_power_per_channel(epoch_data, freq_range='alpha', sample_rate=rec.sample_rate)

    # Assert
    assert alpha_power_per_channel.ndim == 2
    assert alpha_power_per_channel.shape == (n_epochs, n_channels)
    assert np.all(alpha_power_per_channel > 0)
    assert np.all(np.isfinite(alpha_power_per_channel))
    assert not np.allclose(alpha_power_per_channel[:, 0], alpha_power_per_channel[:, 1])


def test_mean_power_custom_range():
    # Arrange
    datapath = REPO_ROOT / "tests" / "data" / "alpha" / "subject_01.mat"
    rec = load_recording(str(datapath))
    epochs = split_by_window_duration(rec, window_duration=5.0)
    epoch_data = np.array([epoch.data for epoch in epochs])

    # Act
    power = get_mean_power(epoch_data, freq_range=(10, 15), sample_rate=rec.sample_rate)

    # Assert
    assert power.ndim == 1
    assert power.shape[0] == len(epochs)
    assert np.all(power > 0)
    assert np.all(np.isfinite(power))


def test_frequency_bands():
    # Arrange
    datapath = REPO_ROOT / "tests" / "data" / "alpha" / "subject_01.mat"
    rec = load_recording(str(datapath))
    epochs = split_by_window_duration(rec, window_duration=5.0)
    epoch_data = np.array([epoch.data for epoch in epochs])
    bands = ['delta', 'theta', 'alpha', 'beta', 'gamma']

    # Act & Assert
    for band in bands:
        power = get_mean_power(epoch_data, freq_range=band, sample_rate=rec.sample_rate)

        assert power.ndim == 1
        assert power.shape[0] == len(epochs)
        assert np.all(power > 0)
        assert np.all(np.isfinite(power))


def test_csp_workflow():
    # Arrange
    datapath = REPO_ROOT / "tests" / "data" / "alpha" / "subject_01.mat"
    rec = load_recording(str(datapath))
    all_epochs = split_by_window_duration(rec, window_duration=2.0)

    # split into two classes
    n_total = len(all_epochs)
    class1_epochs = all_epochs[:n_total // 2]
    class2_epochs = all_epochs[n_total // 2:n_total]

    # Act
    cov1 = get_normalized_covariance_matrix(class1_epochs)
    cov2 = get_normalized_covariance_matrix(class2_epochs)

    spatial_filter = get_spatial_filter_from_covariances(cov1, cov2)

    n_components = 2
    features1 = get_csp_features(spatial_filter, class1_epochs, n_components=n_components)
    features2 = get_csp_features(spatial_filter, class2_epochs, n_components=n_components)

    # Assert
    n_channels = rec.number_of_channels
    assert cov1.shape == (n_channels, n_channels)
    assert cov2.shape == (n_channels, n_channels)
    assert spatial_filter.shape == (n_channels, n_channels)
    assert features1.shape == (len(class1_epochs), 2 * n_components)
    assert features2.shape == (len(class2_epochs), 2 * n_components)

    # finite (no NaN or inf)
    assert np.all(np.isfinite(cov1))
    assert np.all(np.isfinite(cov2))
    assert np.all(np.isfinite(spatial_filter))
    assert np.all(np.isfinite(features1))
    assert np.all(np.isfinite(features2))

    # symmetric
    assert np.allclose(cov1, cov1.T)
    assert np.allclose(cov2, cov2.T)