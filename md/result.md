**V. EXPERIMENTAL SETUP**

The simulation framework was developed using a MATLAB-based environment to evaluate the performance of a 2x2 MIMO-OFDM system. The proposed system models the transmission of a random bit stream through a multipath Rayleigh fading channel with Additive White Gaussian Noise (AWGN). The transmitter uses 16-QAM modulation, Alamouti Space-Time Block Coding (STBC), and OFDM modulation. At the receiver, OFDM demodulation, Alamouti STBC decoding, 16-QAM demodulation, and error-rate calculation are performed. The system performance is evaluated in terms of Bit Error Rate (BER) and Symbol Error Rate (SER) over a range of ![](data:image/x-wmf;base64...) values.

**1. Simulation Parameters**

To ensure reproducibility and clarity, the main parameters used in the simulation are summarized in Table I.

**Table I: Simulation Parameters**

| **Parameter** | **Value** |
| --- | --- |
| Number of Transmit Antennas | 2 |
| Number of Receive Antennas | 2 |
| MIMO Scheme | Alamouti STBC |
| FFT Size (N) | 64 |
| Cyclic Prefix (CP) | 16 |
| Modulation Scheme | 16-QAM |
| Bits per Symbol | 4 |
| Channel Type | Multipath Rayleigh Fading |
| Number of Channel Taps | 6 |
| Noise Model | AWGN |
| ![](data:image/x-wmf;base64...) Range | 0 dB to 30 dB |
| Performance Metrics | BER and SER |
| Channel State Information | Perfect CSI assumed at receiver |

**2. Processing Methodology**

The simulation follows the complete baseband transmission and reception chain of a 2x2 MIMO-OFDM system. The processing workflow consists of the following steps:

a) **Random Bit Generation:** A random binary bit stream is generated at the transmitter. The bit stream represents the digital information to be transmitted through the wireless channel.

b) **16-QAM Modulation:** The generated bits are grouped into sets of four bits and mapped into 16-QAM symbols. Since each 16-QAM symbol carries four bits, this modulation scheme provides higher spectral efficiency than lower-order schemes such as BPSK or QPSK.

c) **Alamouti STBC Encoding:** The modulated symbols are encoded using the Alamouti space-time block code for two transmit antennas. For each pair of symbols ![](data:image/x-wmf;base64...) and ![](data:image/x-wmf;base64...), the two antennas transmit the following structure over two consecutive time slots:

![](data:image/x-wmf;base64...)

This coding structure provides transmit diversity and improves the reliability of the received signal in fading channels.

d) **OFDM Modulation:** After STBC encoding, each antenna branch is processed using OFDM modulation. The frequency-domain symbols are converted into time-domain signals by applying the Inverse Fast Fourier Transform (IFFT). A cyclic prefix is then inserted to reduce inter-symbol interference caused by the multipath Rayleigh fading channel.

e) **Channel Modeling:** The transmitted signals pass through a 2x2 multipath Rayleigh fading channel. Each transmit-receive antenna pair has an independent Rayleigh channel response modeled using complex Gaussian random variables. AWGN is then added to the received signals according to the selected ![](data:image/x-wmf;base64...) value.

f) **OFDM Demodulation:** At the receiver, the cyclic prefix is removed and the Fast Fourier Transform (FFT) is applied to convert the received signals back into the frequency domain.

g) **Alamouti STBC Decoding:** The receiver combines the signals from the two receive antennas using the Alamouti decoding rule. Perfect channel state information is assumed at the receiver, allowing the received symbols to be combined and equalized accurately.

h) **16-QAM Demodulation:** The estimated QAM symbols are demapped back into binary bits using the 16-QAM decision boundaries.

i) **BER and SER Calculation:** The recovered bits and symbols are compared with the originally transmitted data. The Bit Error Rate (BER) is calculated as the ratio between the number of incorrectly detected bits and the total number of transmitted bits. The Symbol Error Rate (SER) is calculated as the ratio between the number of incorrectly detected symbols and the total number of transmitted symbols.

**3. Evaluation Scenario**

The simulation is repeated for ![](data:image/x-wmf;base64...)values from 0 dB to 30 dB. For each ![](data:image/x-wmf;base64...)value, a large number of random bits are transmitted through the 2x2 MIMO-OFDM system. The corresponding BER and SER values are collected and plotted on a logarithmic scale. These curves are then used to evaluate how the system performance changes as the signal-to-noise ratio increases.

The expected result is that both BER and SER decrease as ![](data:image/x-wmf;base64...)increases. The use of Alamouti STBC is expected to improve system reliability by providing spatial diversity, while OFDM helps reduce the effect of multipath propagation by converting the frequency-selective channel into multiple narrowband subchannels.

**VI.RESULTS AND DISCUSSION**

The performance of the 2x2 MIMO-OFDM system utilizing Alamouti Space-Time Block Coding (STBC) and 16-QAM modulation over a Rayleigh fading channel with additive white Gaussian noise (AWGN) is evaluated by measuring the Bit Error Rate (BER) and Symbol Error Rate (SER) across various Signal-to-Noise Ratio (SNR) levels. The performance is evaluated over different ![](data:image/x-wmf;base64...)values, which represent the bit-energy-to-noise-density ratio.

**1. Simulation Results**

The obtained simulation results illustrate the variations of BER and SER as functions of ![](data:image/x-wmf;base64...)

To provide quantitative precision, specific performance data points extracted from the simulation with a step size of 2 dB are presented in Table 1.

Table 1: BER and SER Performance Data of the 16-QAM MIMO-OFDM System

| **Eb/N0 (dB)** | **BER** | **SER** |
| --- | --- | --- |
| 0 | 9.11283e-02 | 3.19521e-01 |
| 2 | 5.59388e-02 | 2.03760e-01 |
| 4 | 2.97852e-02 | 1.11914e-01 |
| 6 | 1.36120e-02 | 5.18828e-02 |
| 8 | 4.64779e-03 | 1.80755e-02 |
| 10 | 1.39518e-03 | 5.45573e-03 |
| 12 | 4.33594e-04 | 1.69792e-03 |
| 14 | 7.42187e-05 | 2.96875e-04 |
| 16 | 1.75781e-05 | 6.77083e-05 |
| 18 | 6.51042e-07 | 2.60417e-06 |
| 20 | 6.51042e-07 | 2.60417e-06 |
| 22 | 6.51042e-07 | 2.60417e-06 |
| 24 | 0.00000e+00 | 0.00000e+00 |
| 26 | 0.00000e+00 | 0.00000e+00 |
| 28 | 0.00000e+00 | 0.00000e+00 |
| 30 | 0.00000e+00 | 0.00000e+00 |

![](data:image/jpeg;base64...)

**2. Discussion**

2.1. General Performance Trend

The simulation results show that both BER and SER decrease as ![](data:image/x-wmf;base64...) increases. At low ![](data:image/x-wmf;base64...), the received signal is strongly affected by Rayleigh fading and AWGN, resulting in relatively high error rates. As ![](data:image/x-wmf;base64...) increases, the noise effect becomes weaker, so the detection accuracy improves and the BER/SER values decrease significantly.

2.2. BER and SER Comparison

The SER values are higher than the BER values because each 16-QAM symbol carries 4 bits. A symbol error occurs when at least one bit in the symbol is detected incorrectly. However, the use of Gray coding helps reduce the number of bit errors when the received symbol is mistaken for a neighboring constellation point.

2.3. Diversity Gain from Alamouti STBC

The use of Alamouti STBC in the 2x2 MIMO system provides spatial diversity. By transmitting coded symbols through two transmit antennas and combining the received signals from two receive antennas, the system reduces the impact of deep fading. This explains the rapid decrease of BER and SER as ![](data:image/x-wmf;base64...) increases.

2.4. Effect of OFDM in Multipath Channel

OFDM improves system performance in the multipath Rayleigh channel. The IFFT/FFT structure divides the frequency-selective channel into multiple narrowband subchannels, while the cyclic prefix helps reduce inter-symbol interference. In this simulation, the cyclic prefix length is sufficient for the 6-tap channel, so most ISI effects are mitigated.

2.5. High - ![](data:image/x-wmf;base64...) Region and Error Floor

In the high - ![](data:image/x-wmf;base64...) region, a short flattening of the BER and SER curves can be observed. However, this should not be considered a true error floor because the simulation assumes perfect channel state information at the receiver. The flattening is mainly caused by the limited number of transmitted bits in the simulation. When the error probability becomes very small, only a few errors occur, so the measured BER and SER may remain unchanged over several ![](data:image/x-wmf;base64...) values.

2.6. Overall Evaluation

Overall, the results confirm that the 2x2 MIMO-OFDM system using Alamouti STBC and 16-QAM achieves good performance over a multipath Rayleigh fading channel. The performance improvement mainly comes from the diversity gain of STBC and the ability of OFDM to handle multipath propagation.