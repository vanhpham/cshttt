clc;
clear;
close all;

%% ============================================================
%  2x2 MIMO-OFDM with Alamouti STBC over multipath Rayleigh channel
%  Modulation: 16-QAM
%  Metrics: BER and SER versus Eb/N0
%  No Communications Toolbox required
%% ============================================================

rng(1);                         % For reproducible results

%% ---------------- Simulation parameters ----------------
Nt = 2;                          % Number of transmit antennas
Nr = 2;                          % Number of receive antennas

M = 16;                          % 16-QAM
k = log2(M);                     % Bits per QAM symbol = 4

Nfft = 64;                       % Number of OFDM subcarriers
Ncp = 16;                        % Cyclic prefix length
Lch = 6;                         % Number of Rayleigh multipath taps

EbN0_dB = 0:2:30;                % Eb/N0 range in dB

Nblocks = 3000;                  % Number of Alamouti-OFDM blocks per Eb/N0
                                 % Increase this for smoother curves

txScale = 1 / sqrt(Nt);          % Normalize total transmit power across antennas

BER = zeros(size(EbN0_dB));
SER = zeros(size(EbN0_dB));

%% ---------------- Multipath power delay profile ----------------
% Exponential power delay profile
pdp = exp(-(0:Lch-1));
pdp = pdp / sum(pdp);            % Normalize total channel power to 1

%% ============================================================
%                    Main Eb/N0 simulation loop
%% ============================================================

for isnr = 1:length(EbN0_dB)

    EbN0_linear = 10^(EbN0_dB(isnr)/10);

    % Since average QAM symbol energy Es = 1:
    % Eb = Es / k
    % Noise variance per complex sample:
    noiseVar = 1 / (k * EbN0_linear);

    totalBitErrors = 0;
    totalSymErrors = 0;
    totalBits = 0;
    totalSymbols = 0;

    for blk = 1:Nblocks

        %% ====================================================
        % 1. Generate random bits
        % Each Alamouti block transmits two QAM symbols per subcarrier:
        % s1 and s2
        %% ====================================================

        NsymPerBlock = 2 * Nfft;                 % s1 and s2 on each subcarrier
        NbitsPerBlock = NsymPerBlock * k;

        txBits = randi([0 1], NbitsPerBlock, 1);

        %% ====================================================
        % 2. 16-QAM mapping
        %% ====================================================

        txSymbols = qam16_mod(txBits);            % Column vector, average Es = 1

        s1 = txSymbols(1:Nfft).';                 % Row vector, 1 x Nfft
        s2 = txSymbols(Nfft+1:end).';             % Row vector, 1 x Nfft

        %% ====================================================
        % 3. Alamouti STBC encoding in frequency domain
        %
        % Time slot 1:
        %   Tx1 sends s1
        %   Tx2 sends s2
        %
        % Time slot 2:
        %   Tx1 sends -conj(s2)
        %   Tx2 sends  conj(s1)
        %% ====================================================

        X_tx1_slot1 = txScale * s1;
        X_tx2_slot1 = txScale * s2;

        X_tx1_slot2 = txScale * (-conj(s2));
        X_tx2_slot2 = txScale * ( conj(s1));

        %% ====================================================
        % 4. OFDM modulation: IFFT + cyclic prefix
        % Use sqrt(Nfft) normalization to preserve signal energy
        %% ====================================================

        x_tx1_slot1 = ofdm_mod(X_tx1_slot1, Nfft, Ncp);
        x_tx2_slot1 = ofdm_mod(X_tx2_slot1, Nfft, Ncp);

        x_tx1_slot2 = ofdm_mod(X_tx1_slot2, Nfft, Ncp);
        x_tx2_slot2 = ofdm_mod(X_tx2_slot2, Nfft, Ncp);

        %% ====================================================
        % 5. Generate 2x2 multipath Rayleigh channel
        % Channel is quasi-static over the two Alamouti time slots.
        % This assumption is required for Alamouti decoding.
        %% ====================================================

        h = zeros(Nr, Nt, Lch);

        for rx = 1:Nr
            for tx = 1:Nt
                h(rx, tx, :) = sqrt(pdp/2) .* ...
                    (randn(1, Lch) + 1j*randn(1, Lch));
            end
        end

        %% ====================================================
        % 6. Pass through Rayleigh channel + AWGN
        %% ====================================================

        y_slot1 = zeros(Nr, Nfft + Ncp + Lch - 1);
        y_slot2 = zeros(Nr, Nfft + Ncp + Lch - 1);

        for rx = 1:Nr

            h_rx_tx1 = squeeze(h(rx, 1, :)).';
            h_rx_tx2 = squeeze(h(rx, 2, :)).';

            y_slot1(rx, :) = conv(x_tx1_slot1, h_rx_tx1) + ...
                             conv(x_tx2_slot1, h_rx_tx2);

            y_slot2(rx, :) = conv(x_tx1_slot2, h_rx_tx1) + ...
                             conv(x_tx2_slot2, h_rx_tx2);
        end

        % Add complex AWGN
        noise1 = sqrt(noiseVar/2) * ...
            (randn(size(y_slot1)) + 1j*randn(size(y_slot1)));

        noise2 = sqrt(noiseVar/2) * ...
            (randn(size(y_slot2)) + 1j*randn(size(y_slot2)));

        y_slot1 = y_slot1 + noise1;
        y_slot2 = y_slot2 + noise2;

        %% ====================================================
        % 7. OFDM receiver: remove CP + FFT
        %% ====================================================

        Y1 = zeros(Nr, Nfft);
        Y2 = zeros(Nr, Nfft);

        for rx = 1:Nr
            Y1(rx, :) = ofdm_demod(y_slot1(rx, :), Nfft, Ncp);
            Y2(rx, :) = ofdm_demod(y_slot2(rx, :), Nfft, Ncp);
        end

        %% ====================================================
        % 8. Channel frequency response for each Tx-Rx pair
        %% ====================================================

        H = zeros(Nr, Nt, Nfft);

        for rx = 1:Nr
            for tx = 1:Nt
                h_temp = squeeze(h(rx, tx, :)).';
                H(rx, tx, :) = fft([h_temp zeros(1, Nfft - Lch)], Nfft);
            end
        end

        % Include transmit normalization in the equivalent channel
        G = txScale * H;

        %% ====================================================
        % 9. Alamouti STBC decoding with 2 receive antennas
        %% ====================================================

        s1_hat = zeros(1, Nfft);
        s2_hat = zeros(1, Nfft);

        for sc = 1:Nfft

            numerator_s1 = 0;
            numerator_s2 = 0;
            denominator = 0;

            for rx = 1:Nr

                g1 = G(rx, 1, sc);       % Channel Tx1 -> Rx
                g2 = G(rx, 2, sc);       % Channel Tx2 -> Rx

                y1 = Y1(rx, sc);         % Received signal in time slot 1
                y2 = Y2(rx, sc);         % Received signal in time slot 2

                numerator_s1 = numerator_s1 + conj(g1)*y1 + g2*conj(y2);
                numerator_s2 = numerator_s2 + conj(g2)*y1 - g1*conj(y2);

                denominator = denominator + abs(g1)^2 + abs(g2)^2;
            end

            s1_hat(sc) = numerator_s1 / denominator;
            s2_hat(sc) = numerator_s2 / denominator;
        end

        rxSymbols = [s1_hat.'; s2_hat.'];

        %% ====================================================
        % 10. 16-QAM demodulation
        %% ====================================================

        rxBits = qam16_demod(rxSymbols);

        %% ====================================================
        % 11. BER and SER calculation
        %% ====================================================

        bitErrors = sum(txBits ~= rxBits);

        txBitMatrix = reshape(txBits, k, []).';
        rxBitMatrix = reshape(rxBits, k, []).';
        symErrors = sum(any(txBitMatrix ~= rxBitMatrix, 2));

        totalBitErrors = totalBitErrors + bitErrors;
        totalSymErrors = totalSymErrors + symErrors;

        totalBits = totalBits + NbitsPerBlock;
        totalSymbols = totalSymbols + NsymPerBlock;

    end

    BER(isnr) = totalBitErrors / totalBits;
    SER(isnr) = totalSymErrors / totalSymbols;

    fprintf('Eb/N0 = %2d dB, BER = %.5e, SER = %.5e\n', ...
        EbN0_dB(isnr), BER(isnr), SER(isnr));

end

%% ============================================================
% 12. Plot BER and SER
%% ============================================================

figure;
semilogy(EbN0_dB, BER, 'o-', 'LineWidth', 1.5);
grid on;
xlabel('E_b/N_0 (dB)');
ylabel('Bit Error Rate (BER)');
title('BER Performance of 2x2 MIMO-OFDM with Alamouti STBC and 16-QAM');

figure;
semilogy(EbN0_dB, SER, 's-', 'LineWidth', 1.5);
grid on;
xlabel('E_b/N_0 (dB)');
ylabel('Symbol Error Rate (SER)');
title('SER Performance of 2x2 MIMO-OFDM with Alamouti STBC and 16-QAM');

figure;
semilogy(EbN0_dB, BER, 'o-', 'LineWidth', 1.5);
hold on;
semilogy(EbN0_dB, SER, 's-', 'LineWidth', 1.5);
grid on;
xlabel('E_b/N_0 (dB)');
ylabel('Error Rate');
title('BER and SER of 2x2 MIMO-OFDM with Alamouti STBC and 16-QAM');
legend('BER', 'SER', 'Location', 'southwest');

%% ============================================================
% Local functions
%% ============================================================

function symbols = qam16_mod(bits)
    % 16-QAM Gray mapping
    % Input: column vector of bits
    % Output: normalized complex symbols with average Es = 1

    bits = bits(:);

    if mod(length(bits), 4) ~= 0
        error('Number of bits must be a multiple of 4 for 16-QAM.');
    end

    bitGroups = reshape(bits, 4, []).';

    % First two bits for I, last two bits for Q
    bI = bitGroups(:, 1:2);
    bQ = bitGroups(:, 3:4);

    I = bits_to_gray_level(bI);
    Q = bits_to_gray_level(bQ);

    symbols = (I + 1j*Q) / sqrt(10);    % Normalize average energy to 1
end

function bits = qam16_demod(symbols)
    % 16-QAM Gray demapping
    % Input: complex symbols
    % Output: column vector of bits

    symbols = symbols(:) * sqrt(10);

    I = real(symbols);
    Q = imag(symbols);

    bitsI = gray_level_to_bits(I);
    bitsQ = gray_level_to_bits(Q);

    bitGroups = [bitsI bitsQ];

    bits = reshape(bitGroups.', [], 1);
end

function levels = bits_to_gray_level(bitPairs)
    % Gray mapping:
    % 00 -> -3
    % 01 -> -1
    % 11 -> +1
    % 10 -> +3

    levels = zeros(size(bitPairs, 1), 1);

    for i = 1:size(bitPairs, 1)
        b1 = bitPairs(i, 1);
        b2 = bitPairs(i, 2);

        if b1 == 0 && b2 == 0
            levels(i) = -3;
        elseif b1 == 0 && b2 == 1
            levels(i) = -1;
        elseif b1 == 1 && b2 == 1
            levels(i) = 1;
        elseif b1 == 1 && b2 == 0
            levels(i) = 3;
        end
    end
end

function bitPairs = gray_level_to_bits(values)
    % Decision thresholds for normalized 16-QAM before sqrt(10) scaling:
    % levels are -3, -1, +1, +3
    % thresholds are -2, 0, +2

    bitPairs = zeros(length(values), 2);

    for i = 1:length(values)

        v = values(i);

        if v < -2
            bitPairs(i, :) = [0 0];
        elseif v < 0
            bitPairs(i, :) = [0 1];
        elseif v < 2
            bitPairs(i, :) = [1 1];
        else
            bitPairs(i, :) = [1 0];
        end
    end
end

function txTime = ofdm_mod(X, Nfft, Ncp)
    % OFDM modulation with unitary IFFT normalization

    x = ifft(X, Nfft) * sqrt(Nfft);
    cp = x(end-Ncp+1:end);
    txTime = [cp x];
end

function X = ofdm_demod(rxTime, Nfft, Ncp)
    % OFDM demodulation with unitary FFT normalization

    rxUseful = rxTime(Ncp+1:Ncp+Nfft);
    X = fft(rxUseful, Nfft) / sqrt(Nfft);
end