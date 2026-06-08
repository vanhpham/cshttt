III. Theoretical Background

1. MIMO(Multiple Input Multiple Output)

MIMO (Multiple-Input Multiple-Output) is a technique that uses multiple antennas on both the input and output sides to transmit and receive signals simultaneously on the same frequency band.The 2x2 MIMO (Multiple-Input Multiple-Output) system is fundamental to analyzing the data transmission capabilities and reliability of modern radio systems. This system uses two antennas at the transmitter (NT>=2) and two antennas at the receiver (NR=2) to create independent interfacial communication channels.

* **Mathematical Model (**2×2 **MIMO):** The relationship between the transmitted and received signals in a flat-fading environment is represented by the matrix equation:

**y**=**Hs**+*η*

* Where:
  + **y**=[*y*1 ,*y*2] *T* is the received signal vector.
  + **s**=[*s*1 ,*s*2 ] *T* is the transmitted symbol vector.
  + **H** is the 2×2 channel matrix containing complex path gains *hij* between transmit antenna *j* and receive antenna *i*.
  + *η* is the additive white Gaussian noise (AWGN) vector.

In the first time slot, it transmits the symbols s1, s2 on antenna 1 and antenna 2, in the next time slot it transmits -s2\*, s1\* on antenna 1 and antenna 2.

Time slot 1: Antenna 1 transmits x1Antenna 2 transmits x2

. The received signal is:

![](data:image/png;base64...)

Time slot 2: Antenna 1 transmits −x 2\* , Antenna 2 transmits x 1\*. The received signal is:

![](data:image/png;base64...)

In which:

This is the signal received in the first time slot at the two receiving antennas. y

This is the signal received in the second time slot at the two receiving antennas. Y

hij is the channel gain, j is the transmitting antenna number, and i is the receiving antenna

This is noise interference from the receiver

1. MIMO-OFDM System

The receiver and transmitter structure of a MIMO-OFDM system includes the MIMO system Transmit and Nr receiving antennas are combined with OFDM technology using Nc subcarriers.

![](data:image/png;base64...)

The signal received from the i-th receiving antenna, at the subcarrier, is represented as follows:

……………………………………………………………………

is the symbol broadcast on the k-th carrier wave in the symbol OFDM

) is Gaussian interference at the i-th receiving antenna

is the channel factor from the j-th transmitting antenna to the i-th receiving antenna.

The MIMO-OFDM system channel can be described through the matrix H as follows

In this case, the channel matrix H is estimated at the receiver.

the transmitter: The signal to be transmitted will be passed through a channel encoder for encoding Error detection and correction codes, combined with the inexpensive IL(interleaved) interleaver to avoid displaying errors city statue Group 6 Large Assignment Report 19 Radio information cluster. Continuing the above sequence of bits will be passed through an S/P converter and arranged to form bit groups for M-PSK or M-QAM modulation, which will then become complex number sequences:

With

Q: the number of bits of a group used for preparation Q = log 2 M .

i: is the i-th complex character number of the M-PSK or M-QAM modulation.

Distributed on the complex plane as follows:

![](data:image/png;base64...)

The modulated string will be converted from serial to 2N characters parallel relative corresponding to N subcarriers as follows:

Where m: is the m-th character of OFDM. Next, we feed the modulated string Dk into the STC encoder. The STC encoder works as follows: It will split the OFDM Dk character string into a group of 2 characters parallel ] relative D1, D2 respectively, then through The STC encoder produces the characters s1,s2,-s2\*,s1\*

![](data:image/png;base64...)

Mathematical description

Where

m: is the mth block of OFDM (1 block corresponds to 2 OFDM characters)

n: is the number of nth characters modulated on the subcarrier n

J: is the transmitting antenna sequence number J=1.2

T: is the corresponding time slot t=1.2

Considering the k-th block with 2 OFDM characters:

We have the following signal after passing through the STC.

Xm is then IFFT-transformed to modulate the carrier wave and insert CP into the winter. It is transmitted via two antennas as analyzed above

![](data:image/png;base64...)

At the receiver: The signal is transmitted through an AWGN (additive white gausian) channel and fading

Where rJ,m(t),xJ,m(t),nj,m(t) la received signal،transmitted signal،and interference act at antenna J (J=1,2) in the time slot t (t=1,2) of the corresponding OFDM m. hj,k,m are the channel coefficients from the transmitting antennas to the antennas OFDM m-th , it remains unchanged across 2 time slots. obtain the corresponding character Here, for simplicity, we consider the OFDM character with a flat fading environment. At the CP splitter receiver, we get:

In this case: n=0,…,N-1 is equivalent to the subcarriers. Then, using the FFT system, we get

After CP removal and Fast Fourier Transform (FFT) processing for subcarrier de-multiplexing, the signal is fed into the STC decoder. Here, the decoder performs decoding across two time slots to estimate the transmitted symbols

At the receiver using the maximum likelihood detection (ML) method, M-PSK or M-QAM complex symbols can be recovered and subsequently decoded to find the required information bits.

With $ and $ being complex numbers in the complex plane that are sequentially substituted to find the closest value, the above system model can be utilized with receive antennas