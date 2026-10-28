# Editable trained CNN

The **Trained CNN** workspace compares a trained 8 x 8 digit classifier in NumPy and the Prabha physical MAC backend. It uses native React panels inside Studio, with the same engine, busy state, exports and desktop Save bridge as ANN. Settings and results survive navigation between workspaces.

With the supplied built application, Windows users can double-click `RUN_PRABHA_STUDIO.bat`; Linux/macOS users can run `bash RUN_PRABHA_STUDIO.sh`. Keep its terminal open and visit `http://127.0.0.1:8000/#cnn`. Source-only checkouts need the normal web build first. The original standalone demo remains available through `RUN_CNN_DEMO.bat` at port 8765.

## Controls

Choose a range of held-out digits, or select an editable image. The custom image accepts an 8-by-8 JSON matrix with pixel values from 0 to 16. Click a pixel or focus it and press Enter to paint with the brush value, or load a held-out digit for editing. Leave the optional true label blank to show predictions without claiming accuracy. **Run CNN inference** uses the current input; **Validate 360 images** switches to the full held-out set with your current weights and converters.

Expand the weight editor to modify convolution/dense weights and biases. Shapes stay fixed: `[4,1,3,3]`, `[4]`, `[10,36]` and `[10]`. Parameters must be finite and between -100 and 100. Restore the checkpoint weights independently, or restore the entire reference experiment.

DAC and MAC-output ADC controls accept Off or 1 to 24 bits. Set the ADC's positive/negative voltage range and select lower-at-tie or nearest-even DAC rounding. ADC output is converted back to voltage before inverse scaling and digital bias. Out-of-range values raise an error; they are not silently clipped.

## Reproduction and inspection

Validate and export settings before a run, or export a completed run with its exact settings and fresh results. Import settings or a run file to restore settings; stored predictions are ignored. Editing inputs, weights or converter controls clears old results.

Select an image number in the predictions table to inspect normalized input, convolution with bias, ReLU, max pooling, flattened features and logits. Click a network stage or use the Stage selector, then choose a feature channel and compare NumPy/Prabha tensor maps, numerical differences and exact values. Export settings, run JSON, prediction CSV or layer inspection JSON. Run exports retain engine/version, timestamp, exact settings and model/data hashes. A failed run leaves no exportable old results.

## Scope

The supplied checkpoint reaches 354/360 (98.33%) in both backends with zero prediction disagreements. The fixed split has 1,149 training / 288 validation / 360 test images. Edited settings do not inherit the recorded accuracy. This is the small digits dataset, not MNIST or a writer-disjoint evaluation.

The reference uses a 12-bit lower-at-tie DAC, 100 dB input/weight MZM extinction, noise off and output ADC off. Bias, activation, pooling and scaling include digital/software operations. The interface measures warm software inference, with validation, loading, warmup, inspection and exports excluded. Prabha's detailed waveform computation is slower than vectorised NumPy in the recorded experiment; no physical hardware speedup follows from this. Complete noisy-CNN and native CNN dynamic validation remain separate work.


Read [CNN operators and execution](execution.md) for the cross-correlation convention, three execution choices and repeated benchmark. [Next validation steps](next-steps.md) distinguish completed stationary evidence from planned dynamic and noisy-network experiments.
