import numpy as np
import scipy.signal as signal
from sklearn.cross_decomposition import CCA
import matplotlib.pyplot as plt


# === STEP 1: Simulate or Load EEG Data ===
def generate_synthetic_ssvep(freqs, fs=256, duration=3, num_channels=9):
    """
    Generates synthetic SSVEP EEG signals with noise.

    Parameters:
        freqs (list): List of target stimulation frequencies.
        fs (int): Sampling frequency in Hz.
        duration (int): Signal duration in seconds.
        num_channels (int): Number of EEG channels.

    Returns:
        eeg_data (np.array): Simulated EEG data of shape (num_channels, samples).
        labels (list): Corresponding labels for each frequency.
    """
    t = np.linspace(0, duration, fs * duration)
    eeg_data = np.zeros((num_channels, len(t)))

    for i, f in enumerate(freqs):
        eeg_data[i] = np.sin(2 * np.pi * f * t)  # Simulated SSVEP signal
        eeg_data[i] += 0.2 * np.random.randn(len(t))  # Add noise

    return eeg_data, t


# Define SSVEP stimulation frequencies (e.g., 8Hz, 10Hz, 12Hz, etc.)
ssvep_freqs = [8, 10, 12, 15]
fs = 256  # Sampling rate in Hz
duration = 3  # Signal duration in seconds

# Generate simulated EEG data
eeg_data, time_axis = generate_synthetic_ssvep(ssvep_freqs)


# === STEP 2: Apply Recursive Least Squares (RLS) Adaptive Filtering ===
class RLSFilter:
    def __init__(self, num_channels, lambda_=0.99, delta=1.0):
        self.num_channels = num_channels
        self.lambda_ = lambda_  # Forgetting factor
        self.delta = delta  # Regularization
        self.P = np.eye(num_channels) / delta  # Inverse correlation matrix
        self.W = np.zeros((num_channels, 1))  # Filter weights

    def update(self, u, d):
        """
        Update the RLS filter with new input (u) and desired output (d).
        """
        u = u.reshape(-1, 1)  # Ensure column vector
        d = np.array([[d]])  # Ensure scalar

        k = self.P @ u / (self.lambda_ + u.T @ self.P @ u)  # Gain vector
        e = d - u.T @ self.W  # Error signal
        self.W += k * e  # Update weights
        self.P = (self.P - k @ u.T @ self.P) / self.lambda_  # Update correlation matrix

        return self.W.T @ u  # Filtered output


# Apply RLS filtering to EEG data
rls_filter = RLSFilter(num_channels=eeg_data.shape[0])
filtered_eeg = np.zeros_like(eeg_data)

for i in range(eeg_data.shape[1]):
    filtered_eeg[:, i] = rls_filter.update(eeg_data[:, i], np.mean(eeg_data[:, i]))


# === STEP 3: Perform Canonical Correlation Analysis (CCA) ===
def generate_reference_signals(freqs, time_axis, fs):
    """
    Generate sine-cosine reference signals for CCA.

    Returns:
        reference_signals: Dictionary mapping frequencies to reference signal matrices.
    """
    reference_signals = {}
    for f in freqs:
        ref_sin = np.sin(2 * np.pi * f * time_axis)
        ref_cos = np.cos(2 * np.pi * f * time_axis)
        reference_signals[f] = np.array([ref_sin, ref_cos])  # 2D array
    return reference_signals


# Generate reference signals
reference_signals = generate_reference_signals(ssvep_freqs, time_axis, fs)


def perform_cca(eeg_data, reference_signals):
    """
    Perform CCA to determine the frequency with the highest correlation.

    Returns:
        best_freq: Frequency with the highest CCA correlation.
        max_corr: Maximum correlation value.
    """
    cca = CCA(n_components=1)
    max_corr = 0
    best_freq = None

    for freq, ref in reference_signals.items():
        cca.fit(eeg_data.T, ref.T)
        X_c, Y_c = cca.transform(eeg_data.T, ref.T)
        corr = np.corrcoef(X_c[:, 0], Y_c[:, 0])[0, 1]

        if corr > max_corr:
            max_corr = corr
            best_freq = freq

    return best_freq, max_corr


# Identify the most likely SSVEP frequency
identified_freq, max_correlation = perform_cca(filtered_eeg, reference_signals)
print(f"Identified SSVEP Frequency: {identified_freq} Hz (Correlation: {max_correlation:.2f})")


# === STEP 4: Evaluate Performance ===
def compute_snr(signal, noise):
    """
    Compute the signal-to-noise ratio (SNR) in dB.
    """
    power_signal = np.mean(signal ** 2)
    power_noise = np.mean(noise ** 2)
    return 10 * np.log10(power_signal / power_noise)


# Compute SNR before and after RLS filtering
snr_before = compute_snr(eeg_data, eeg_data - np.mean(eeg_data, axis=0))
snr_after = compute_snr(filtered_eeg, filtered_eeg - np.mean(filtered_eeg, axis=0))

print(f"SNR Before RLS: {snr_before:.2f} dB")
print(f"SNR After RLS: {snr_after:.2f} dB")

# === STEP 5: Visualization ===
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(time_axis, eeg_data[0, :], label="Raw EEG (Channel 1)")
plt.plot(time_axis, filtered_eeg[0, :], label="Filtered EEG (RLS)", alpha=0.7)
plt.legend()
plt.title("EEG Signals Before and After RLS Filtering")

plt.subplot(2, 1, 2)
plt.bar(["Before RLS", "After RLS"], [snr_before, snr_after], color=['red', 'green'])
plt.ylabel("SNR (dB)")
plt.title("SNR Improvement After RLS Filtering")

plt.tight_layout()
plt.show()
