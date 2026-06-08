III. Theoretical Background

1. Orthogonal Frequency Division Multiplexing

Orthogonal Frequency-Division Multiplexing (OFDM) is a special case of FDM (Frequency Division Multiplexing). In the FDM technique, the total bandwidth of the transmission link is divided into N non-overlapping frequency channels. The signal of each channel is modulated with a subcarrier, and the N channels are multiplexed using frequency division. This results in bandwidth inefficiency; to overcome this drawback of FDM, the OFDM technique was introduced. This technique divides the frequency band into numerous sub-bands with different carriers, each of which is modulated to transmit a low-rate data stream. The aggregate of these low-rate data streams constitutes the high-rate data stream required for transmission. Furthermore, the carriers employed are orthogonal to each other, allowing their spectra to overlap without causing interference. Consequently, bandwidth utilization becomes significantly more efficient.

1.1. Orthogonality Principle

The fundamental concept of OFDM relies on the mathematical

orthogonality of its subcarriers. Over a single symbol period, 𝑇𝑠

, two subcarriers with frequencies 𝑓𝑘and 𝑓𝑚 are orthogonal if the integral of their product over the symbol duration equals zero. Mathematically, this continuous-time condition is expressed as:

![](data:image/png;base64...)

To satisfy this condition, the subcarrier spacing 𝛥𝑓 is chosen to be

the reciprocal of the useful symbol duration 1/𝑇𝑠 , such that 𝛥𝑓 = 1/𝑇𝑠 . In the frequency domain, the spectrum of each subcarrier follows a sinc function shape. This precise spacing ensures that the peak of one subcarrier aligns with the nulls of all other subcarriers in the frequency domain. Consequently, crosstalk between subcarriers - known as InterCarrier Interference (ICI) is theoretically eliminated at the receiver's

sampling instants

1. Principles of using IFFT and FFT

In practical systems, using thousands of independent oscillators to generate orthogonal subcarriers is hardware-infeasible.

Therefore, the Fourier transform is used as an effective alternative.

At the transmitter (using IFFT):

Complex data symbols are mapped onto subcarriers in the frequency domain. The inverse fast Fourier transform (IFFT) is performed to convert these symbols to the time domain before transmission.The general formula for the discrete signal x(n) after IFFT is:

$$x(n)=\frac{1}{\sqrt{N}}\sum\_{k=0}^{N−1}X(k)e^{j\frac{2πkn}{N}}$$

where 𝑛 = 0, 1, … , 𝑁 − 1 is the time-domain sample index.

At the receiver (using FFT):

After receiving the time-domain signal, the receiver uses the Fast Fourier Transform (FFT) to convert the signal back to the frequency domain, thereby restoring the original data symbols.

Advantages: IFFT/FFT:

architecture significantly reduces computational complexity and makes system implementation hardware-feasible at a low cost.

1. **Cyclic Prefix(CP)**

**Cyclic Prefix (CP)** is a guard interval inserted before each symbol to ensure transmission quality in multipath environments. The CP is created by copying the end portion of an OFDM symbol (after the IFFT block) and prepending it to the beginning of that same symbol.

![](data:image/png;base64...)

* Inter-Symbol Interference (ISI) Mitigation: In a multipath propagation environment, delayed replicas of the signal cause ISI between successive symbols. The CP acts as a guard interval to absorb these delayed signal components.
* Maintaining Orthogonality and Preventing ICI: By converting the linear convolution of the transmission channel into a circular convolution, the CP helps maintain the orthogonality of the subcarriers, thereby eliminating Inter-Carrier Interference (ICI).
* Receiver Simplification: This conversion to circular convolution allows the receiver to perform channel equalization using a simple multiplication in the frequency domain (one-tap equalization), rather than employing complex equalizers in the time domain.