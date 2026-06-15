clc;
clear;
close all;

%% ============================================================
%%                     System Parameters
%% ============================================================
Nt = 2;             % Number of transmit antennas
Nr = 2;             % Number of receive antennas
M = 16;             % Modulation order (16-QAM)
k = log2(M);        % Bits per symbol (4)

Nfft = 64;          % FFT size
Lch = 6;            % Channel memory length (6-tap Rayleigh)
txScale = 1/sqrt(2);% Normalize transmit power to 1 over 2 antennas

EbN0_dB = 0:2:30;   % Eb/N0 range in dB
Nblocks = 1500;     % Number of blocks for Monte Carlo simulation
P = 50;             % Number of symbol pairs per continuous block (100 OFDM symbols total)

% Exponential power delay profile (PDP)
pdp = exp(-(0:Lch-1));
pdp = pdp / sum(pdp); % Normalize total channel power to 1

% CP lengths to compare
CP_lengths = [16, 4, 0];
BER_results = zeros(length(CP_lengths), length(EbN0_dB));

fprintf('Starting Continuous Transmission Simulation...\n');

%% ============================================================
%%                 Simulation Loop for different CPs
%% ============================================================
for icp = 1:length(CP_lengths)
    Ncp = CP_lengths(icp);
    fprintf('\nSimulating with CP length = %d\n', Ncp);
    
    for isnr = 1:length(EbN0_dB)
        EbN0_linear = 10^(EbN0_dB(isnr)/10);
        noiseVar = 1 / (k * EbN0_linear); % Noise variance per complex sample
        
        totalBitErrors = 0;
        totalBits = 0;
        
        for blk = 1:Nblocks
            % 1. Generate random bits for P frames (continuous stream)
            NsymPerBlock = P * 2 * Nfft;
            NbitsPerBlock = NsymPerBlock * k;
            txBits = randi([0 1], NbitsPerBlock, 1);
            
            % 2. 16-QAM mapping
            txSymbols = qam16_mod(txBits);
            
            % 3. Serial-to-Parallel (S/P) into symbol streams s1 and s2
            s1 = reshape(txSymbols(1 : P*Nfft), Nfft, P).';
            s2 = reshape(txSymbols(P*Nfft + 1 : end), Nfft, P).';
            
            % 4. Alamouti STBC encoding
            X_tx1_slot1 = txScale * s1;
            X_tx2_slot1 = txScale * s2;
            X_tx1_slot2 = txScale * (-conj(s2));
            X_tx2_slot2 = txScale * (conj(s1));
            
            % 5. Continuous time domain signal generation (with CP)
            symbol_len = Nfft + Ncp;
            x1 = zeros(1, 2 * P * symbol_len);
            x2 = zeros(1, 2 * P * symbol_len);
            
            for p = 1:P
                % Slot 1
                x1_s1 = ofdm_mod(X_tx1_slot1(p, :), Nfft, Ncp);
                x2_s1 = ofdm_mod(X_tx2_slot1(p, :), Nfft, Ncp);
                % Slot 2
                x1_s2 = ofdm_mod(X_tx1_slot2(p, :), Nfft, Ncp);
                x2_s2 = ofdm_mod(X_tx2_slot2(p, :), Nfft, Ncp);
                
                idx1 = (2*p - 2) * symbol_len + 1;
                idx2 = (2*p - 1) * symbol_len + 1;
                
                x1(idx1 : idx1 + symbol_len - 1) = x1_s1;
                x1(idx2 : idx2 + symbol_len - 1) = x1_s2;
                x2(idx1 : idx1 + symbol_len - 1) = x2_s1;
                x2(idx2 : idx2 + symbol_len - 1) = x2_s2;
            end
            
            % 6. Generate 2x2 multipath Rayleigh channel (quasi-static over block)
            h = zeros(Nr, Nt, Lch);
            for rx = 1:Nr
                for tx = 1:Nt
                    h(rx, tx, :) = sqrt(pdp/2) .* (randn(1, Lch) + 1j*randn(1, Lch));
                end
            end
            
            % 7. Continuous transmission over the channels (conv generates ISI)
            y = zeros(Nr, length(x1) + Lch - 1);
            for rx = 1:Nr
                h_rx_tx1 = squeeze(h(rx, 1, :)).';
                h_rx_tx2 = squeeze(h(rx, 2, :)).';
                y(rx, :) = conv(x1, h_rx_tx1) + conv(x2, h_rx_tx2);
            end
            
            % Add AWGN noise
            noise = sqrt(noiseVar/2) * (randn(size(y)) + 1j*randn(size(y)));
            y = y + noise;
            
            % 8. Receiver CP removal and FFT (segmentation of received stream)
            Y1 = zeros(Nr, P, Nfft);
            Y2 = zeros(Nr, P, Nfft);
            for rx = 1:Nr
                for p = 1:P
                    idx1 = (2*p - 2) * symbol_len + 1;
                    idx2 = (2*p - 1) * symbol_len + 1;
                    
                    y_s1 = y(rx, idx1 : idx1 + symbol_len - 1);
                    y_s2 = y(rx, idx2 : idx2 + symbol_len - 1);
                    
                    Y1(rx, p, :) = ofdm_demod(y_s1, Nfft, Ncp);
                    Y2(rx, p, :) = ofdm_demod(y_s2, Nfft, Ncp);
                end
            end
            
            % 9. Channel Frequency Response
            H = zeros(Nr, Nt, Nfft);
            for rx = 1:Nr
                for tx = 1:Nt
                    h_temp = squeeze(h(rx, tx, :)).';
                    H(rx, tx, :) = fft([h_temp zeros(1, Nfft - Lch)], Nfft);
                end
            end
            G = txScale * H;
            
            % 10. Alamouti decoding for all P symbols and subcarriers
            s1_hat = zeros(P, Nfft);
            s2_hat = zeros(P, Nfft);
            for p = 1:P
                for sc = 1:Nfft
                    numerator_s1 = 0;
                    numerator_s2 = 0;
                    denominator = 0;
                    for rx = 1:Nr
                        g1 = G(rx, 1, sc);
                        g2 = G(rx, 2, sc);
                        y1 = Y1(rx, p, sc);
                        y2 = Y2(rx, p, sc);
                        
                        numerator_s1 = numerator_s1 + conj(g1)*y1 + g2*conj(y2);
                        numerator_s2 = numerator_s2 + conj(g2)*y1 - g1*conj(y2);
                        denominator = denominator + abs(g1)^2 + abs(g2)^2;
                    end
                    s1_hat(p, sc) = numerator_s1 / denominator;
                    s2_hat(p, sc) = numerator_s2 / denominator;
                end
            end
            
            % 11. Parallel-to-Serial symbol concatenation
            rxSymbols = [reshape(s1_hat.', [], 1); reshape(s2_hat.', [], 1)];
            
            % 12. 16-QAM demapping
            rxBits = qam16_demod(rxSymbols);
            
            % 13. Error metrics calculation
            bitErrors = sum(txBits ~= rxBits);
            totalBitErrors = totalBitErrors + bitErrors;
            totalBits = totalBits + NbitsPerBlock;
        end
        
        BER_results(icp, isnr) = totalBitErrors / totalBits;
        fprintf('  Eb/N0 = %2d dB, BER = %.5e\n', EbN0_dB(isnr), BER_results(icp, isnr));
    end
end

%% ============================================================
%%               Plot Comparison Results
%% ============================================================
fig = figure;
semilogy(EbN0_dB, BER_results(1, :), 'o-', 'LineWidth', 1.5, 'MarkerFaceColor', 'b', 'DisplayName', 'Sufficient CP (N_{cp}=16)');
hold on;
semilogy(EbN0_dB, BER_results(2, :), 's-', 'LineWidth', 1.5, 'MarkerFaceColor', 'r', 'DisplayName', 'Insufficient CP (N_{cp}=4)');
semilogy(EbN0_dB, BER_results(3, :), 'd-', 'LineWidth', 1.5, 'MarkerFaceColor', 'g', 'DisplayName', 'No CP (N_{cp}=0)');
grid on;
xlabel('E_b/N_0 (dB)');
ylabel('Bit Error Rate (BER)');
title('MIMO-OFDM CP Mitigation Performance under Continuous Transmission');
legend('show', 'Location', 'southwest');

% Ensure figure directory exists and save the plot
if ~exist('figure', 'dir')
    mkdir('figure');
end

% Set figure and axes background to white (avoiding black backgrounds or borders)
set(fig, 'Color', 'w');
set(gca, 'Color', 'w');

% Configure paper size and position for tight vector PDF export (no A4 white margins)
set(fig, 'Units', 'inches');
pos = get(fig, 'Position');
set(fig, 'PaperPositionMode', 'manual');
set(fig, 'PaperSize', [pos(3), pos(4)]);
set(fig, 'PaperPosition', [0, 0, pos(3), pos(4)]);

% Save figure
print(fig, 'figure/Figure_4.pdf', '-dpdf', '-r300');
fprintf('\nSimulation complete. Plot saved to figure/Figure_4.pdf\n');

%% ============================================================
%%                     Local Functions
%% ============================================================
function symbols = qam16_mod(bits)
    bits = bits(:);
    bitGroups = reshape(bits, 4, []).';
    bI = bitGroups(:, 1:2);
    bQ = bitGroups(:, 3:4);
    I = bits_to_gray_level(bI);
    Q = bits_to_gray_level(bQ);
    symbols = (I + 1j*Q) / sqrt(10);
end

function bits = qam16_demod(symbols)
    symbols = symbols(:) * sqrt(10);
    I = real(symbols);
    Q = imag(symbols);
    bitsI = gray_level_to_bits(I);
    bitsQ = gray_level_to_bits(Q);
    bitGroups = [bitsI bitsQ];
    bits = reshape(bitGroups.', [], 1);
end

function levels = bits_to_gray_level(bitPairs)
    levels = zeros(size(bitPairs, 1), 1);
    for i = 1:size(bitPairs, 1)
        b1 = bitPairs(i, 1);
        b2 = bitPairs(i, 2);
        if b1 == 0 && b2 == 0,     levels(i) = -3;
        elseif b1 == 0 && b2 == 1, levels(i) = -1;
        elseif b1 == 1 && b2 == 1, levels(i) = 1;
        elseif b1 == 1 && b2 == 0, levels(i) = 3;
        end
    end
end

function bitPairs = gray_level_to_bits(values)
    bitPairs = zeros(length(values), 2);
    for i = 1:length(values)
        v = values(i);
        if v < -2,     bitPairs(i, :) = [0 0];
        elseif v < 0,  bitPairs(i, :) = [0 1];
        elseif v < 2,  bitPairs(i, :) = [1 1];
        else,          bitPairs(i, :) = [1 0];
        end
    end
end

function txTime = ofdm_mod(X, Nfft, Ncp)
    x = ifft(X, Nfft) * sqrt(Nfft);
    if Ncp > 0
        txTime = [x(end-Ncp+1:end) x];
    else
        txTime = x;
    end
end

function X = ofdm_demod(rxTime, Nfft, Ncp)
    if Ncp > 0
        X = fft(rxTime(Ncp+1:Ncp+Nfft), Nfft) / sqrt(Nfft);
    else
        X = fft(rxTime(1:Nfft), Nfft) / sqrt(Nfft);
    end
end
