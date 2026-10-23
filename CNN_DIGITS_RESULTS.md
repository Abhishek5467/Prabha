# Trained CNN: complete labelled benchmark

Date:15 October2026. The four-filter CNN is trained and evaluated; this
supersedes the earlier two-image untrained smoke as the application milestone.

| Item | Measured result |
|---|---:|
| Train / validation / test | 1,149 / 288 / 360 |
| Parameters | 410 |
| Epochs / selected epoch | 160 / 155 |
| Conventional correct / accuracy | 354 / 360;98.3333% |
| Prabha correct / accuracy | 354 / 360;98.3333% |
| Prediction disagreements | 0 / 360 |
| Logit RMS / maximum error | .00299290906 / .01030958826 |
| MAC calls / device passes | 55,440 / 55,440 |
| Waveform samples | 9,538,560 |
| NumPy full-test median7 warm runtime | .001563205 s |
| Shared operators + DigitalMAC, one full run | .097523242 s |
| Prabha one full pass,12 batches | 7.346462795 s |

Dataset:scikit-learn bundled8x8 digits,not MNIST. Pixel intensities/16,
image-stratified split,not writer-disjoint. Architecture:Conv(1,4,3 valid),
ReLU,MaxPool2,flatten36,Linear(36,10). All convolution and dense parameters
are trained digitally with NumPy Adam; frozen weights transfer unchanged.
Selection uses minimum validation cross-entropy,not test performance.

The full test set is processed using the existing PhysicalMAC and CNN
operators. A separate vectorised NumPy reference agrees with DigitalMAC
operators to1.7763568394e-14. Physical inference uses12-bit lower-at-tie input
DAC,100 dB extinction,noise off,output ADC off,automatic scaling and explicit
digital bias/ReLU/pooling. Native full-CNN dynamics and hardware timing are
not established. The native stationary noise ledger remains68 pass/1
inconclusive; the CNN result does not alter it. CPU timing is machine-specific
software inference with resident inputs/weights and one physical pass.

Artifacts are in `results/cnn_digits/`; run commands and full continuation
context are in `START_HERE_CHATGPT_GO.md` and `handoff/`.

Dataset SHA256:3b0a4a80fedd50b3b5ecfb380cbef32ebb23b1e2306c310b73898a69f14c9e21

Model SHA256:f023ab9dddcb6a0d56e2448e5a6cfe2d171c961d50e11028dcbff6e4b7ce0a6e
