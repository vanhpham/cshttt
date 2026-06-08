# **QUESTION 1. 16-QAM MODULATION TECHNIQUE**

## **1.1 Theory of 16-QAM Modulation**

Quadrature Amplitude Modulation (QAM) is a digital modulation technique that transmits information by varying both the amplitude and phase of a carrier signal. The transmitted signal consists of two orthogonal components:

• In-phase component (I)

• Quadrature component (Q)

For a 16-QAM system, the modulation order is:

M = 16

The number of bits carried by each symbol is:

k = log₂(M)

Substituting M = 16:

k = log₂(16) = 4 bits/symbol

Therefore, each transmitted symbol carries 4 bits of information.

The passband signal is given by:

s(t) = I cos(2πfct) − Q sin(2πfct)

where:

I = In-phase component

Q = Quadrature component

fc = Carrier frequency

The amplitude levels used in both I and Q branches are:

I, Q ∈ {−3, −1, +1, +3}

Since each axis contains four amplitude levels, the total number of constellation points is:

N = 4 × 4 = 16

Thus, a 16-point constellation is obtained.

## **1.2 Average Symbol Energy Normalization**

The average energy of the in-phase component is calculated as:

E{I²} = [(-3)² + (-1)² + (+1)² + (+3)²] / 4

E{I²} = (9 + 1 + 1 + 9) / 4

E{I²} = 5

Similarly:

E{Q²} = 5

Therefore, the average symbol energy becomes:

Es = E{I²} + E{Q²}

Es = 5 + 5

Es = 10

To normalize the constellation such that:

Es = 1

all constellation points are multiplied by:

1/√10

Hence, the normalized transmitted symbol is:

s = (I + jQ)/√10

This normalization is used in the MATLAB implementation and simplifies BER and SER calculations.

## **1.3 16-QAM Constellation Diagram**

### **Constellation Coordinates**

| **Q \ I** | **-3** | **-1** | **+1** | **+3** |
| --- | --- | --- | --- | --- |
| +3 | (-3,+3) | (-1,+3) | (+1,+3) | (+3,+3) |
| +1 | (-3,+1) | (-1,+1) | (+1,+1) | (+3,+1) |
| -1 | (-3,-1) | (-1,-1) | (+1,-1) | (+3,-1) |
| -3 | (-3,-3) | (-1,-3) | (+1,-3) | (+3,-3) |

Constellation Diagram:

Q

+3 ● ● ● ●

+1 ● ● ● ●

-1 ● ● ● ●

-3 ● ● ● ●

-3 -1 +1 +3

I

After normalization, all coordinates are scaled by:

1/√10

## **1.4 Gray Bit Mapping Rule**

Gray coding is employed so that adjacent constellation points differ by only one bit.

### **Mapping Rule**

| **Bit Pair** | **Amplitude** |
| --- | --- |
| 00 | -3 |
| 01 | -1 |
| 11 | +1 |
| 10 | +3 |

The first two bits determine the I component, while the last two bits determine the Q component.

### **Example 1**

Input bits: 0000

I = −3

Q = −3

Transmitted symbol:

s = (−3 − j3)/√10

### **Example 2**

Input bits: 1111

I = +1

Q = +1

Transmitted symbol:

s = (1 + j1)/√10

### **Example 3**

Input bits: 1010

I = +3

Q = +3

Transmitted symbol:

s = (3 + j3)/√10

## **1.5 Euclidean Distance Demodulation**

After transmission through the Rayleigh fading channel and AWGN, the received symbol is represented as:

r = Ir + jQr

Let the m-th constellation point be:

Sm = Im + jQm

The Euclidean distance between the received symbol and the constellation point is:

dm = √[(Ir − Im)² + (Qr − Qm)²]

To reduce computational complexity, the receiver usually employs the squared Euclidean distance:

dm² = (Ir − Im)² + (Qr − Qm)²

The Maximum Likelihood (ML) decision rule is:

Ŝ = arg min{dm²}

or equivalently:

Ŝ = arg min[(Ir − Im)² + (Qr − Qm)²]

The constellation point with the minimum Euclidean distance is selected as the detected symbol and then converted back into the corresponding 4-bit sequence.

# **QUESTION 2. SYSTEM BLOCK DIAGRAM**

## **2.1 System Block Diagram**

TRANSMITTER

Input Bits

│

▼

16-QAM Mapper

│

▼

Alamouti STBC Encoder

│

▼

OFDM Modulator

(IFFT + Cyclic Prefix)

│

▼

Rayleigh Fading Channel

+

AWGN

│

▼

RECEIVER

OFDM Demodulator

(Remove CP + FFT)

│

▼

Alamouti STBC Decoder

│

▼

Euclidean Detector

│

▼

16-QAM Demapper

│

▼

Output Bits

## **2.2 Alamouti STBC Encoding**

The implemented system uses a 2 × 2 Alamouti Space-Time Block Code (STBC).

For two consecutive symbols s₁ and s₂, the Alamouti transmission matrix is:

X =

| **s₁ s₂** |
| --- |
| −s₂\* s₁\* |

where (\*) denotes complex conjugation.

### **First Time Slot**

Transmit Antenna 1:

s₁

Transmit Antenna 2:

s₂

### **Second Time Slot**

Transmit Antenna 1:

−s₂\*

Transmit Antenna 2:

s₁\*

This coding scheme provides transmit diversity and improves performance in fading environments.

## **2.3 System Operation**

### **Step 1 – Bit Generation**

A random binary bit stream is generated.

### **Step 2 – 16-QAM Mapping**

Every four bits are mapped into one normalized 16-QAM symbol according to the Gray coding rule.

### **Step 3 – Alamouti STBC Encoding**

The symbols are encoded using Alamouti STBC to exploit spatial diversity.

### **Step 4 – OFDM Modulation**

The encoded symbols are transformed into the time domain using an Inverse Fast Fourier Transform (IFFT). A Cyclic Prefix (CP) is added to mitigate inter-symbol interference.

### **Step 5 – Channel Transmission**

The OFDM signal propagates through a multipath Rayleigh fading channel and is corrupted by Additive White Gaussian Noise (AWGN).

### **Step 6 – OFDM Demodulation**

At the receiver, the cyclic prefix is removed and a Fast Fourier Transform (FFT) is performed.

### **Step 7 – Alamouti STBC Decoding**

The receiver combines signals from multiple antennas and estimates the transmitted symbols.

### **Step 8 – Euclidean Distance Detection**

The Euclidean distance between the received symbol and all possible constellation points is calculated. The constellation point with the minimum distance is selected.

### **Step 9 – 16-QAM Demapping**

The detected symbol is converted back into the corresponding binary sequence using the Gray mapping rule.

### **Step 10 – Performance Evaluation**

The recovered bit stream is compared with the transmitted bit stream to evaluate BER and SER performance.

## **2.4 Conclusion**

The implemented communication system combines 16-QAM modulation, OFDM transmission, and a 2 × 2 Alamouti STBC scheme operating over a Rayleigh fading channel with AWGN. Euclidean-distance-based Maximum Likelihood detection is employed at the receiver to recover the transmitted symbols accurately. This architecture improves spectral efficiency, provides diversity gain, and enhances communication reliability in wireless fading environments.