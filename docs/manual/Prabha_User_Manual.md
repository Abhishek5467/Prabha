---
title: "Prabha"
subtitle: "User manual, mathematical reference and evaluation guide"
author: "Abhishek Singh · Electronics and Communication Engineering · IIT Patna"
date: "30 September 2026 · preview.3 / components-1 · clarity revision"
---

# Reading this manual

Prabha is a research software prototype for photonic–electronic behavioural simulation. It connects explicit signal descriptions and validation rules to component calculations, a visual Designer, and a fixed small neural-network inference example. Use it to study the assumptions of a computation chain, reproduce numerical results and develop additional models with tests.

This manual describes the supplied preview.3 implementation and the accompanying clarity patch. It distinguishes a **simulated physical model** from a physical experiment. No fabricated Prabha processor, measured accelerator energy, trained classification benchmark or implemented transformer is reported here.

If you are preparing for an evaluation, first read the worked neuron and ANN chapters. Then run the demonstrations, read the model catalogue and practise the questions. If you are changing the software, begin with the architecture and reproducibility chapters. The catalogue is generated from the actual `spec/blocks/model_*.json` definitions; their limits and descriptions are also used by the Inspector.

## What changed in this review

The source labels now follow their connections: a source feeding an input command displays **x**, and one feeding a signed-weight command displays **w**. The Inspector states that these are dimensionless controls. The optical phase selector is enabled only for optical probes; selecting an electrical probe restores its ordinary value view. Results name their actual component/legacy profile. A digital source now starts with valid integer codes. These changes clarify use; they do not add new optical physics or alter the reference ANN mathematics.

The Windows log supplied for this review reports 43 passing Python tests and successful asset and frontend builds. A missing browser favicon is cosmetic. The MkDocs link notice and the Starlette test-client deprecation warning are distinct from numerical simulation failures.

# What runs where

## The three scientific paths

| Path | Purpose | Important boundary |
|:--|:--|:--|
| Current Designer, `model_*` | Connect the established Python component classes in a sampled graph | 19 definitions; compact and expanded neuron examples |
| Legacy PEMAN | Reproduce original saved graphs and fixtures | Original converter/activation semantics remain intact |
| Standalone ANN | Run the fixed 4–3–2 behavioural inference regression | Independent of arbitrary Designer graph execution |

The current Designer and standalone experiments share component classes, but they can organize time and accumulation differently. A shared class is not a proof that two entire experiments have equal timing or architecture. The C++17 engine covers the original conformance fixtures; it does not execute the new current-model kernels or the ANN operation.

## The software layers

1. **Specification:** JSON schemas describe signals, ports, blocks and netlists. Block definitions provide parameters, ports and implementation identifiers.
2. **Validation:** structural checks are followed by semantic rules for graph references, connections, kinds, domains, channels and cycles.
3. **Execution:** the Python engine schedules a valid directed acyclic graph and invokes registered kernels. Adapters call the established component classes.
4. **Product interface:** a shared Python dispatcher exposes graph, component, perceptron and ANN operations.
5. **Transport and interface:** React/Vite Studio and the Designer call the dispatcher through FastAPI locally, through Python/Pyodide in a browser worker on static hosting, or through a Python sidecar in the desktop scaffold.

The frontend displays and configures results. It does not replace the numerical core with a separate JavaScript implementation. Static hosting serves files; the visitor's browser performs the current Python simulation. This is why the present Pages prototype does not need an AWS simulation server.

## Important folders

| Relative path under Prabha | What it contains |
|:--|:--|
| `spec/blocks/` | Machine-readable block interfaces and defaults |
| `spec/examples/` | Current runnable Designer graphs |
| `core-py/prabha/blocks/` | Component classes and graph adapters |
| `core-py/prabha/blocks/component_kernels.py` | Current `model_*` adapter implementations |
| `core-py/prabha/product.py` | Shared product operations and bounded requests |
| `core-py/experiments/` | Research experiments and their protocols |
| `core-py/ann_batch_validation.csv` | Archived 100-input ANN evidence |
| `frontend/web/index.html` | Editable Designer source |
| `frontend/studio/` | Studio source, build and browser tests |
| `docs/site/` | Documentation website source |
| `desktop/` | Tauri wrapper and sidecar configuration |
| `tests/` | Product and current-model integration checks |

Do not edit generated `dist`, `public/designer.html` or the contents of `prabha-python.zip`. Change the corresponding source, then rebuild.

# First successful local run and GitHub push

## Apply the clarity patch

Your preview.3 updater has already completed. Extract the new review package outside your repository. Open Command Prompt in its `Prabha-Clarity-Update` directory and run:

```bat
py apply_update.py "C:\Users\samay\OneDrive\Documents\Research_Works\Prabha" --check
py apply_update.py "C:\Users\samay\OneDrive\Documents\Research_Works\Prabha"
```

The updater checks that edited files match the expected preview.3 baseline, backs up replacements, creates the listed documentation files and verifies the written bytes. It skips files already current. If it reports conflicts, preserve your local changes and merge the named files using the complete supplied versions. It does not commit or push.

## Rebuild and inspect

From Windows Command Prompt:

```bat
cd /d "C:\Users\samay\OneDrive\Documents\Research_Works\Prabha"
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm.cmd ci --prefix frontend/studio
.\.venv\Scripts\python.exe scripts/build_web_assets.py
npm.cmd run build --prefix frontend/studio
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe frontend/web/server.py
```

Use the existing project environment. If it is missing, first create it with `py -3.12 -m venv .venv`. The source project's Node configuration is the build reference. Open `http://127.0.0.1:8000`, choose **Component designer**, and run the default neuron. The expected final ADC code is 2616 and reconstructed voltage is 0.6388278388278388 V. Read it numerically as a normalized output on the 1 V scale.

Stop the server with Ctrl+C before entering the Git commands. From the same Prabha root:

```bat
git status
git diff --stat
git remote -v
git branch --show-current
git add .
git diff --cached --stat
git commit -m "Clarify Designer signals and add model mathematics manual"
git push
```

Review the staged file list before committing. The supplied `.gitignore` excludes environments, dependencies, build outputs and common secret files; retain it. Do not stage unrelated personal data. These commands include the earlier preview.3 changes if you have not yet committed them. `git push` uses your existing branch and upstream. If Git explicitly says that the current branch has no upstream, use `git push -u origin YOUR_BRANCH`, replacing `YOUR_BRANCH` with the output of `git branch --show-current`. Do not rename your branch or force-push just to deploy.

If the remote has new commits, fetch and review them before merging or rebasing; do not overwrite them. Authentication, a rejected push and a failed GitHub build are separate problems. Keep the exact error if one occurs.

## Publish the new commit

In the repository's Actions tab, check **Validate prototype** for the new commit. Start a **new Publish web preview** run on the branch you just pushed. Re-running an older workflow run uses that older commit. Wait for a successful Pages deployment, then refresh the site and inspect the source labels and Documentation link. The patch retains preview.3 and the `components-1` model revision because the numerical model is unchanged.

Project: <https://github.com/Abhishek5467/Prabha>

Web app: <https://abhishek5467.github.io/Prabha/>

Documentation: <https://abhishek5467.github.io/Prabha/docs/>

These are the configured project addresses, not a claim that this review has pushed your Windows files or published the patch.

# A guided Designer session

## Controls and a first experiment

Choose **Component neuron · B22 reference**. The reference uses duration 4 ns, seed 1 and noise off. The compact graph has x, w, laser, MAC, capacitor, amplifier, activation and ADC blocks. Select a block to inspect parameters. Drag or double-click a palette item to add it, join compatible output and input ports, press `F` to focus a selection, and `.` to fit the graph. **Show theory** changes explanations only.

Run the model. The output cards show final values from the complete simulation. The probe selector changes which stage is plotted. A displayed trace is sampled down to at most 1,200 points, with original sample indices retained; this does not change the final value. The default graph has 64 samples at 16 GHz.

Change MAC `dac_bits` from 12 to 3. The old results should clear. Run again and compare the final output. This experiment demonstrates finite input-converter resolution, not random noise. Restore 12 bits before quoting the reference result.

Choose **Expanded component chain** to expose inverse encoding, DAC, MZM, splitting, weight encoding, attenuation, two detectors and subtraction separately. It should reproduce the compact example's final output. The graph is wide; zoom and use its stage probes. The compact MAC is a current-model primitive internally calling the component classes, even though the palette groups it as a compound convenience block.

## Why both sources had an x and a voltage port

Previously, both blocks used the same generic `model_source` definition. Its body renderer selected x for every source whose definition name did not contain “weight”. Thus the displayed letter was wrong on the w block; its numerical values and connection to the weight input were still distinct.

Four transport kinds exist in the present schema: optical, voltage, current and digital. There is no separate dimensionless-control kind. Consequently the normalized x and signed w arrays travel through voltage-kind ports by convention. They are **not both physical drive voltages**.

| Quantity | Meaning in B22 | Unit or range |
|:--|:--|:--|
| x | Desired normalized optical intensity | Dimensionless, 0 to 1 |
| w | Signed multiplication coefficient | Dimensionless, −1 to 1 |
| Encoder output | Requested MZM drive | V |
| DAC output / MAC `drive` | Quantized MZM drive | V |
| Weight encoder output | Upper/lower power transmission | Dimensionless, 0 to 1 |
| Detector output | Photocurrent | A |
| Capacitor / amplifier output | Electrical state | V |
| ADC `code` | Integer code | 0 to $2^b-1$ |
| ADC `voltage` | Reconstructed readout | V, interpreted on the stated normalization scale |

The patch infers display roles from consumers, not from instance names. A generic or mixed-use source retains a generic label. Raw exported graph signal kinds remain unchanged for compatibility; source-control meaning must still accompany the recorded graph. A future schema revision could introduce explicit dimensionless quantities, but doing so requires migration and conformance work.

## Optical power and phase views

The optical signal is a sampled complex envelope:

$$E_k=\sqrt{P_k}\exp(j\phi_k),\qquad P_k=|E_k|^2.$$

Its amplitude has units $\sqrt{\mathrm W}$; the ordinary scope displays power in watts. The phase view displays `unwrap(arg(E))` in radians. Unwrapping removes numerical jumps of $2\pi$ between adjacent phase samples. It does not reconstruct phase changes larger than the sampling can resolve, and phase has no physical meaning at zero amplitude.

The optical carrier itself is not sampled at hundreds of terahertz. Wavelength identifies the carrier in metadata; sample rate resolves the envelope variations. In the current MZM adapter, a nonnegative square-root power factor scales the envelope while preserving its incident phase. There is no chirp or coherent arm-field model.

Direct detection uses $|E|^2$, so a common phase rotation cancels. With laser RIN disabled and linewidth enabled, the phase trace can wander while optical power remains constant. That is expected behaviour. Phase-to-intensity conversion would require an appropriate interferometric or coherent detection model; selecting the phase view does not create one.

The patch disables the phase selector for electrical probes. It no longer allows an ADC voltage plot to appear as though it were an optical phase measurement.

# Mathematics of the complete neuron

## Ideal target

A mathematical neuron computes

$$s=\sum_{i=1}^{N}x_iw_i+b,\qquad y=\sigma(s),\qquad \sigma(s)=\frac{1}{1+e^{-s}}.$$

For B22,

$$x=[0.9,0.3,0.7,0.5],\qquad w=[0.8,-0.6,0.4,-0.9],\qquad b=0.2.$$

The products are $[0.72,-0.18,0.28,-0.45]$, their sum is 0.37, the pre-activation is 0.57 and the ideal output is 0.638763175149. x here is already a nonnegative normalized input. Earlier signed optical-link experiments instead mapped a signed input through $u=(x+1)/2$; do not apply that mapping a second time to the B22 input.

## Inverse MZM encoding and the DAC

Let $V_\pi$ be the half-wave voltage and $\phi_b$ the differential bias phase. With insertion loss $L$ in dB, the implemented MZM power transfer is

$$T(V)=10^{-L/10}\cos^2\left(\frac{\pi V}{2V_\pi}+\frac{\phi_b}{2}\right).$$

The factor $\phi_b/2$ is essential. The inverse encoder chooses one branch of the *lossless normalized* transfer:

$$V_i^*=\frac{2V_\pi}{\pi}\left[\arccos(\sqrt{x_i})-\frac{\phi_b}{2}\right].$$

For $V_\pi=1$ V and $\phi_b=\pi/2$, x from 0 to 1 maps into +0.5 to −0.5 V. Matching the encoder and MZM parameters is a calibration assumption. Insertion loss remains after this inversion; the encoder does not automatically compensate it.

For an endpoint-inclusive converter with b bits,

$$\Delta=\frac{V_{\max}-V_{\min}}{2^b-1},\quad c=\operatorname{rint}\left(\frac{V^*-V_{\min}}{\Delta}\right),\quad \widehat V=V_{\min}+c\Delta.$$

`rint` rounds to nearest, with ties to even. The reference DAC uses 12 bits and −0.5 to +0.5 V, giving a step of approximately 0.2442 mV. Commands outside the range are rejected unless explicit clipping is enabled. The reconstructed voltage enters the nonlinear transfer, producing $P_i=P_0T(\widehat V_i)$.

## Signed optical weighting

The ideal signed weight encoder makes two nonnegative power transmissions:

$$t_i^+=\frac{1+w_i}{2},\qquad t_i^-=\frac{1-w_i}{2}.$$

An equal optical splitter sends half the MZM power to each branch. After attenuation and detection with responsivity $\mathcal R$,

$$I_i^+=\frac{\mathcal R P_i}{2}t_i^+,\quad I_i^-=\frac{\mathcal R P_i}{2}t_i^-,\quad I_i^\Delta=I_i^+-I_i^-=\frac{\mathcal R P_iw_i}{2}.$$

The optical powers never need to become negative. The signed result is the difference between two nonnegative detector currents. Equal deterministic dark currents cancel under ideal subtraction, but independent detector shot fluctuations do not cancel sample by sample.

If the upper split fraction is r instead of 1/2, the mean becomes $\mathcal R P_i[r(1+w_i)/2-(1-r)(1-w_i)/2]=\mathcal R P_i[(2r-1)+w_i]/2$. Thus splitter imbalance introduces an input-dependent offset in this ideal weighting construction. Do not change r and continue quoting the equal-split formula.

## Charge accumulation, gain and bias

For constant current over an interval $\tau$, the capacitor increment is $I\tau/C$. In the no-leakage reference,

$$V_C=\frac{\tau}{C}\sum_i I_i^\Delta.$$

With $P_0=1$ mW, $\mathcal R=1$ A/W, $\tau=1$ ns and $C=1$ pF, the ideal scaling is

$$V_C=(0.5\,\mathrm V)\sum_i x_iw_i.$$

The amplifier applies gain 2 and offset 0.2 V. Dividing by the chosen 1 V normalization gives the dimensionless sigmoid argument. This scaling connects the physical-model units to the mathematical neuron; it is not an assertion that volts are dimensionless.

The standalone B22 experiment adds four parallel currents and integrates for 1 ns. The Designer instead sends four sequential symbols, each held for 1 ns, and integrates for 4 ns. The final charge agrees when leakage is off and scaling matches. Their latency and architecture are different. With leakage, earlier sequential contributions decay more, so the final-value equivalence need not survive.

## Activation and ADC readout

The activation receives the gain/bias voltage. In the reference it applies a sigmoid on the normalized 1 V scale, represented again as a voltage between 0 and 1 V. The final ADC quantizes that voltage:

$$c_A=\operatorname{rint}[(2^{12}-1)y_a],\qquad \widehat y=\frac{c_A}{4095}.$$

Current B22 ordering is **analog activation then ADC**. The legacy PEMAN fixture's ADC/digital-activation ordering differs. Neither ordering should be silently substituted for the other.

| Stage | Reference result |
|:--|--:|
| Ideal dot product | 0.37 |
| Ideal pre-activation | 0.57 |
| Ideal sigmoid | 0.638763175149 |
| Model capacitor voltage | 0.185083940444 V |
| Model gain and bias voltage | 0.570167880888 V |
| Model analog sigmoid on 1 V scale | 0.638801911885 V |
| ADC code | 2616 |
| Reconstructed normalized output | 0.638827838828 |
| Absolute output difference from ideal | $6.46637\times10^{-5}$ |

The small discrepancy is expected from finite converter precision in this deterministic baseline. It does not mean every other input or physical device will have the same error.

# Noise, nonlinearity and memory

## The noise switch has a specific meaning

A stochastic contribution requires both the global Noise switch and its block-specific switch. Noise off leaves deterministic transfer functions active: MZM nonlinearity, insertion loss, DAC/ADC quantization, dark current, TIA filtering, leakage, clipping and activation do not disappear.

Random streams combine a run seed, block seed and CRC32 of the instance identifier, modulo $2^{32}$. Repeating the graph and settings reproduces a stream; renaming a block changes it. The compact MAC uses internal detector names consistent with the expanded reference. A seed is a reproducibility control, not an experimental replicate count by itself.

## Laser intensity and linewidth

For one-sided RIN density $S_{\mathrm{RIN}}=10^{\mathrm{RIN}_{dB/Hz}/10}$ and sample rate $f_s$, the linearized power perturbation uses

$$\sigma_P=P_0\sqrt{S_{\mathrm{RIN}} f_s/2}.$$

It is a Gaussian white-sample approximation. Large fluctuations can make sampled power negative; the model rejects such realizations instead of taking an invalid square root. It is not a general low-photon-count laser statistics model.

The phase diffusion increment obeys

$$\Delta\phi_k\sim\mathcal N(0,2\pi\Delta\nu/f_s),\qquad \phi_k=\phi_0+\sum_{j\leq k}\Delta\phi_j.$$

Here $\Delta\nu$ is linewidth in Hz. The first generated noisy phase sample includes the first increment. At zero linewidth the envelope phase is fixed. Separately toggling RIN and linewidth allows you to observe intensity and phase effects without conflating them.

## Photodetection and receiver noise

The current mean is $I_{\mathrm{mean}}=\mathcal R|E|^2+I_d$ when dark current is enabled. The white Gaussian shot approximation uses

$$\sigma_I^2=2qI_{\mathrm{mean}}\frac{f_s}{2}.$$

$q$ is electron charge. This implementation applies Gaussian fluctuations around the mean; instantaneous samples can be negative even though mean photocurrent is nonnegative. Use the model within the regime where the approximation is meaningful. It is not a discrete photon-arrival simulation.

The current-model detector does **not** silently add the old legacy load-thermal term. The TIA accepts an explicit input-referred current-noise density $i_n$ in A/$\sqrt{\mathrm{Hz}}$ and adds white noise of standard deviation $i_n\sqrt{f_s/2}$ before gain/filtering. This parameter may represent a measured receiver noise budget; document its source and avoid double counting thermal noise.

## TIA bandwidth

For resistance $R_f$ and bandwidth B, define $\tau_f=1/(2\pi B)$, $\Delta t=1/f_s$ and $\alpha=\Delta t/(\tau_f+\Delta t)$. The backward-Euler update is

$$v_k=\alpha R_f i_k+(1-\alpha)v_{k-1}.$$

The first output is initialized to the first current sample times $R_f$. It is not a zero-state startup transient. The discrete response depends on $f_s$, so a nominal analog bandwidth does not guarantee an exact digital −3 dB frequency. This TIA has no saturation or slew-rate model; use the separate amplifier rails only where that abstraction is appropriate.

## Capacitor leakage and sample timing

Without leakage, $V_{k+1}=V_k+I_k\Delta t/C$. With finite leakage resistance $R_L$ and constant current during each interval, the adapter uses the exact interval update

$$V_{k+1}=V_ke^{-\Delta t/(R_LC)}+I_kR_L\left(1-e^{-\Delta t/(R_LC)}\right).$$

The stored output at array index k is the state **after** integrating interval k, including one step at index zero. The scope's common time labels use k/$f_s$; account for this interval-end convention when interpreting capacitor startup. Each run resets the state to `initial_V`. No reset switch, kT/C noise or inter-run retained charge is modeled.

## Amplifier rails and activation

The amplifier computes gain × input + offset and applies whichever lower/upper rails are enabled. This is deterministic clipping. The activation computes a shifted/scaled argument and applies sigmoid, tanh, ReLU or linear transfer. Sigmoid arguments are clipped to ±60 for numerical stability. These are behavioural functions, not transistor-level activation circuits. A negative tanh or unbounded ReLU output can exceed the default ADC's 0–1 V range; change the intended readout range or explicitly enable clipping.

# ANN inference and the meaning of validation

## Fixed network and separate reference paths

The current network has four inputs, three hidden neurons and two output neurons:

$$h=\sigma(W_1x+b_1),\qquad y=\sigma(W_2h+b_2),$$

$$W_1=\begin{bmatrix}.8&-.6&.4&-.9\\-.3&.7&.5&.2\\.6&.1&-.8&.7\end{bmatrix},\quad b_1=\begin{bmatrix}.2\\-.1\\.05\end{bmatrix},$$

$$W_2=\begin{bmatrix}.7&-.5&.6\\-.4&.9&-.7\end{bmatrix},\quad b_2=\begin{bmatrix}.1\\-.05\end{bmatrix}.$$

Every model neuron includes the converter-aware optical/electronic chain. Quantized model hidden outputs feed the model output layer. Ideal hidden outputs independently feed the analytical output layer. Reusing ideal hidden values in the model path would hide part of the accumulated error.

The coefficients are fixed; no training occurred in this validation. The inputs are synthetic numerical test vectors rather than a labelled classification dataset.

## The 100-input protocol

The experiment uses NumPy `default_rng(12345)` to generate 100 four-dimensional vectors uniformly from [0.05,0.95]. The first vector is replaced with the B22 reference input. The stored CSV has 100 rows and two output-error columns, giving 200 comparisons. For errors $e_{nj}=\widehat y_{nj}-y_{nj}$,

$$\mathrm{RMS}=\sqrt{\frac{1}{200}\sum_{n=1}^{100}\sum_{j=1}^{2}e_{nj}^2},\qquad e_{\max}=\max_{n,j}|e_{nj}|.$$

Recomputation from the supplied CSV gives RMS $7.864411795585\times10^{-5}$, maximum $1.782838135357\times10^{-4}$ and mean signed error $1.518043206350\times10^{-6}$. The larger output's index agrees with the analytical reference for all 100 vectors.

**0/100 ordering mismatches is not 100% classification accuracy.** There are no labels to classify. It shows agreement of the two-output ordering for this fixed network and input sample. The two sigmoid outputs are not a softmax probability distribution and need not sum to one.

## Separate optical-link noise evidence

The archived `full_chain_monte_carlo.csv` contains 200 runs per case, 800 rows total. Mean *per-run recovery RMS* values are approximately:

| Link case | Mean recovery RMS |
|:--|--:|
| Laser RIN | 0.00562061 |
| PD dark + shot | 0.00483002 |
| TIA noise | 0.00366789 |
| Full link | 0.00636798 |

These values were recomputed from the stored CSV in this review. They were not generated by a new hardware measurement or by injecting noise into the 4–3–2 ANN. They describe a different link, normalization and converter setup. An average of trial RMS values is not automatically the same statistic as a pooled RMS over all samples. Do not add these RMS values to the deterministic ANN RMS or call the result noisy ANN accuracy.

## What the tests establish

The original 14 fixtures exercise golden outputs and graph errors in Python and C++17. Current Python integration tests cover adapters, compact/expanded correspondence, controls and request errors. UI tests check interaction and transport. These are useful engineering evidence at different layers; passing them does not prove every physical assumption.

The strongest present claim is: **the implemented fixed small-network model reproduces an independently computed analytical reference with the reported finite-precision deviations on the stated sample set.** It supports further controlled modelling work. Generalization to deeper trained networks, physical devices, tasks and serving performance requires additional evidence.

# Four demonstrations for a professor

## Demonstration 1: explain every number

Run the reference neuron with noise off. Show x and w and their ranges. Read MAC drive to distinguish normalized commands from volts. Explain the factor 1/2 from the optical split, the capacitor scaling, gain 2 and bias 0.2. Show analog activation and ADC code separately. Compare the final output with the worked table.

Expected explanation: the small difference comes from the modeled finite converters; the ideal target is a separate calculation. Save the run JSON before changing anything.

## Demonstration 2: show a controlled precision change

Reduce only DAC bits to 3, run, then restore 12. Keep input, weights, duration, ADC, noise and seed unchanged. Compare the result and drive trace. Do not call a single input an entire precision benchmark. If making a plot for a paper, repeat a documented sweep and preserve all settings and errors.

## Demonstration 3: distinguish phase and intensity

Load the noisy receiver. Turn laser RIN off, leave linewidth on and inspect `laser.out` power and phase. Disable detector shot and TIA noise if you want to isolate phase-only behaviour in the receiver. Power remains constant while phase varies. Turn linewidth off to remove phase diffusion, then enable RIN to see intensity fluctuations. Explain why no direct-detection phase-to-intensity conversion appears.

Restore the example before quoting its defaults. A changed seed should change the realization; the original seed should reproduce it.

## Demonstration 4: connect a neuron to an ANN

In Studio's ANN workspace, run the reference vector, inspect ideal/model hidden and output values, then choose **Validate 100 inputs**. Read RMS, maximum error and mismatch count with their definitions. Export the CSV. Explain the fixed weights, absence of training and distinction between numerical agreement and task accuracy.

A useful 10-minute sequence is: question and scope (1 minute), component chain and equations (3), live neuron/phase demo (2), ANN evidence (2), contribution and next experiment (2). Keep screenshots and exported runs as a fallback if the browser runtime cannot load during the evaluation.

# Saving, replay and common problems

## Save the experiment, not just a picture

**Save Designer project** stores graph, positions, model revision and run settings in `.prabha.json`. **Export engine netlist** preserves the original plain netlist format; settings are supplied separately. **Export reproducible run** includes request, result, metadata, warnings, sampled probes and full-simulation final values. A graph run can be replayed by supplying its recorded `request` to the shared dispatcher. Large plots alone do not preserve enough context.

**Plot ZIP** depends on its optional JSZip CDN. JSON export remains useful if that dependency is unavailable. Record the Git commit, Python/NumPy versions, operating environment, model revision, graph, parameter values, seeds and any comparison tolerance with an experiment.

## Troubleshooting table

| Observation | Interpretation and next check |
|:--|:--|
| Both x and w used to show x | Display renderer reused a generic source symbol; apply this patch |
| Phase control disabled on ADC | Correct: choose an optical probe to inspect phase |
| Phase wanders; power is constant | Expected for phase-only noise and direct detection |
| ADC range error | Inspect upstream range; change intended range or explicitly enable clipping |
| Digital source error | Codes must be nonnegative integers within the receiving DAC's bit range |
| Source/laser size or fs mismatch | Match rate × samples/symbol to laser fs and check duration |
| Run has unused-output warnings | Probe outputs may legitimately be unused; read errors separately |
| Results disappear after editing | Correct: stale results are invalidated |
| A saved old graph differs from B22 | Check legacy/current profile and activation/converter ordering |
| Negative laser power error | Gaussian RIN regime is invalid for that realization; inspect density, fs and model suitability |
| Docs/frontend show old content | Rebuild Python/web assets before Vite; deploy the new commit and refresh |
| No favicon / test-client warning | Cosmetic or dependency warning; distinguish from failed tests |

The graph is feed-forward; a feedback loop is rejected. Do not connect a capacitor output back into the graph and expect a general circuit differential-equation solver. The present sample/state models operate within a directed acyclic block schedule.

# Research contribution, novelty and next evidence

## Defensible contribution now

Prabha's implemented contribution is a specification-first, inspectable workflow linking mixed optical/electrical models to a numerical neuron and ANN reference, with saved experiments and a shared Python execution path. The current Designer integration makes the established component models accessible through explicit blocks. This is substantive software engineering and reproducibility work.

That does not establish priority for optical neural computation, photonic circuit simulation, component libraries, balanced detection, converter-aware models or graphical composition. Simphony, Photontorch and SAX provide important related simulation capabilities. Lightening-Transformer and LightCode establish prior photonic transformer and hybrid compilation work. The accompanying research paper compares these scopes without claiming a performance win over them.

A targeted public literature review was performed on 30 September 2026. It is not an exhaustive priority or patent search. No published head-to-head simulator benchmark, external user study or calibrated hardware validation was found in the supplied Prabha evidence. Absence of those results should not be replaced by an unsupported “first” claim.

## A useful claim table

| Claim | Present assessment | Evidence still needed |
|:--|:--|:--|
| Reproducible small-network simulation | Supported within stated scope | Broader boundary/seed/size coverage |
| Common current component logic across UI transports | Implemented and tested in the prototype | Continued cross-environment regression |
| General C++/Python equivalence | Not established | Port and test all current kernels and ANN |
| New photonic device or activation physics | Not established | A distinct model, calibration and comparison |
| Faster or more accurate simulator than prior tools | Not established | Matched model/workload/tolerance benchmarks |
| Token-friendly LLM accelerator advantage | Research hypothesis | Transformer mapping, traces, full costs, quality and baselines |

For a software-introduction publication, organize the manuscript around the research need, design, implementation, illustrative use, reproducibility, validation and limitations. A software paper can be valuable without inventing new optics. JOSS is a short software-article venue with explicit software maturity and research-use requirements; check its current author guidance and eligibility before adapting the longer manuscript. The supplied full paper is a journal-neutral working draft, not a claim of submission readiness or acceptance.

## Priority after this pause

First reproduce the manual's examples and explain every conversion. Then freeze a reviewed release with a commit/tag and archived evidence. Add calibrated models or a carefully scoped CNN primitive only after this baseline is understood. A token-level accelerator study is a separate research project: define a transformer workload, model conversions/memory/residency/calibration, compare an optimized electronic baseline, and report conditions where optical placement loses as well as where it helps.

# Open-source distribution and possible services

The repository includes an MIT licence. Retain its notices in distributed source and verify provenance/licensing of additional assets before adding them. The public research prototype can use its configured GitHub Pages address initially. Its community links are the forum <https://prabhacommunity5701.flarum.cloud/> and Discord <https://discord.gg/RUdRMHBFp>.

Use the forum for reproducible questions, model discussions and showcase write-ups; use Discord for quick conversation, with durable conclusions moved into documentation or issues. A helpful bug report contains a minimal saved graph, settings, expected/actual result and version. Label evidence as simulation, archived experiment or hardware measurement.

The desktop wrapper is scaffolded; native Windows, macOS and Linux installer builds and installation checks are still release gates. A working Python sidecar alone is insufficient to advertise all three desktop applications as verified releases. A custom domain is optional; it does not improve scientific validation or require a change of compute architecture.

Possible services after the prototype is stable are guided setup for a lab/course, teaching workshops, model integration with documented tests, reproducibility audits and maintenance/support arrangements. These are proposed offerings, not existing customers or capabilities already delivered. Begin with one clearly bounded pilot and publish its acceptance criteria. A calibrated device-model service needs measured data and expertise; an accelerator-performance service needs system benchmarks. Avoid promising hardware speedups or reliability guarantees from the current ANN regression.

# Questions to rehearse

**What exactly did you build?** A specification-driven behavioural simulator workflow, original cross-engine conformance tests, Python component/neuronal experiments, a fixed ANN regression and an accessible interface exposing current models and reproducible runs.

**Where is the optical computation?** Intensity encoding, optical power splitting and ideal signed weight transmissions form the products. Balanced photodetection converts the branch difference to a signed current. Integration, gain/bias, activation and conversion complete the electronic path.

**Why inverse encoding?** The MZM's cosine-squared transfer is nonlinear. Inverting a chosen ideal branch makes requested normalized intensity approximately linear in x before quantization and loss. It does not remove every physical nonideality.

**Why are there two detectors?** Each optical power is nonnegative. Their difference represents a signed product without assigning negative optical intensity.

**What makes the neuron nonlinear?** MZM transfer is nonlinear physically in its drive; inverse encoding compensates its intended encoding. The separate activation supplies the neural nonlinearity. Converter steps and clipping are other nonlinear effects with different purposes.

**Can phase noise change the output?** It can in a coherent/interferometric system, but this current direct-detection chain does not implement that coupling. Its phase display must not be mistaken for proof of coherent computation.

**Does 43 passing tests prove the model?** It supports the tested software behaviours. Physical validity needs appropriate assumptions and comparisons with measured or trusted reference data.

**Is zero winner mismatch an accuracy result?** It is agreement of the two-output ordering with a fixed mathematical reference across 100 synthetic vectors, not a labelled task score.

**Why call the result validated?** Because the defined implementation was compared with explicit references under a documented protocol. Always state that boundary rather than implying universal validation.

**Is Prabha novel?** The demonstrated contribution is the concrete integrated software workflow and its reproducible validation. Broad optics/simulator concepts have prior art. A strong scientific novelty claim requires a sharper comparison and additional evidence.

**Did the internship already implement the later ANN?** Keep the chronology explicit: the internship presentation covers device studies and simulator foundations; later component integration and ANN validation belong to subsequent BTP progress.

**What would make the next paper stronger?** A released version with independent reproduction, a clear related-work comparison, calibrated model evidence, more systematic coverage and a demonstration of a research question enabled by the software.

# References and source record

The project source, supplied BTP master report, internship foundation report, microring study, architecture decisions and archived CSVs are the primary sources for Prabha-specific claims in this manual. The revised manuscripts include fuller bibliographies.

- Ploeg, Gunther and Camacho. *Simphony: An open-source photonic integrated circuit simulation framework*. <https://arxiv.org/abs/2009.05146>.
- Laporte, Dambre and Bienstman. *Highly parallel simulation and optimization of photonic circuits in time and frequency domain based on the deep-learning framework PyTorch*. Scientific Reports 9, 5918 (2019). <https://doi.org/10.1038/s41598-019-42408-2>.
- SAX project documentation. <https://gdsfactory.github.io/sax/>.
- Zhu et al. *Lightening-Transformer*. <https://arxiv.org/abs/2305.19533>.
- Tomich, Zhong and Englund. *LightCode: Compiling LLM Inference for Photonic-Electronic Systems*. <https://arxiv.org/abs/2509.16443>.
- JOSS author guidance. <https://joss.readthedocs.io/en/latest/submitting.html> (checked 30 September 2026).

This revision used AI assistance for source inspection, drafting, literature retrieval, code clarification and document preparation. The project author should verify the text, figures, authorship, acknowledgements and venue-specific disclosure before submission. No paper has been submitted by this review.

# Current block catalogue

The following interfaces/defaults are extracted from the reviewed block definitions. Values are defaults for a newly added block, not a guarantee that every example uses them. The earlier mathematics chapters explain the model equations and approximations. Ports labelled voltage can carry normalized controls where explicitly stated. All current blocks operate on sampled time-domain signals.

## Nonlinear activation

`model_activation` · `ComponentActivation`

Uses Activation.activate. Sigmoid, tanh, ReLU and linear; sigmoid argument clipped to ±60 for numerical stability. Behavioral output is represented on a normalized 1 V scale; this is not a transistor-level device model. B22 places activation BEFORE ADC.

Inputs: `in` (voltage). Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `kind` | sigmoid  | Behavioral transfer function. Options: sigmoid, tanh, relu, linear. |
| `gain` | 1.0  | Pre-activation scaling. Allowed: -1e+06 to 1e+06. |
| `threshold_V` | 0.0 V | Shift: z=gain × (Vin−threshold). Allowed: -1e+06 to 1e+06. |

## ADC

`model_adc` · `ComponentADC`

Uses ADC.convert/code_to_voltage. code is the actual integer code; voltage is the reconstructed quantized value. Range errors are visible unless clipping is explicitly enabled. No jitter, INL or DNL model.

Inputs: `in` (voltage). Outputs: `code` (digital), `voltage` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `bits` | 12  | Integer resolution; nearest code, NumPy ties-to-even. Allowed: 1 to 16. |
| `v_min` | 0.0 V | Lower conversion endpoint. Allowed: -1e+06 to 1e+06. |
| `v_max` | 1.0 V | Upper conversion endpoint. Allowed: -1e+06 to 1e+06. |
| `clip` | false  | False rejects out-of-range commands; true explicitly clips to converter rails. |

## Voltage amplifier

`model_amplifier` · `ComponentAmplifier`

Uses Amplifier.amplify: gain × Vin + offset, followed by enabled rail limits. No bandwidth, slew-rate or amplifier noise beyond the separately modeled TIA.

Inputs: `in` (voltage). Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `gain` | 2.0  | Voltage gain. Allowed: -1e+06 to 1e+06. |
| `offset_V` | 0.2 V | Additive bias after gain. Allowed: -1e+06 to 1e+06. |
| `lower_rail_enabled` | false  | Enable lower-rail saturation. |
| `v_min` | -1.0 V | Lower output rail; must be below upper rail if both enabled. Allowed: -1e+06 to 1e+06. |
| `upper_rail_enabled` | false  | Enable upper-rail saturation. |
| `v_max` | 1.0 V | Upper output rail. Allowed: -1e+06 to 1e+06. |

## Balanced current subtraction

`model_balance` · `ComponentBalance`

Iout=Iupper−Ilower. Each photodetector has its own noise stream. No extra subtractor noise or hidden gain.

Inputs: `upper` (current), `lower` (current). Outputs: `out` (current).

No editable parameters.

## Capacitor integrator

`model_capacitor` · `ComponentCapacitor`

Uses Capacitor.integrate_current with dt=1/fs. Output sample k is voltage AFTER interval k; first sample includes one integration step. Without leakage: V+=I dt/C. With leakage: Vnew=Vold exp(−dt/RC)+IR(1−exp(−dt/RC)). No kT/C reset noise.

Inputs: `in` (current). Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `capacitance_pF` | 1.0 pF | Charge storage capacitance. Allowed: 1e-12 to 1e+12. |
| `initial_V` | 0.0 V | Initial voltage; resets at start of every run. Allowed: -1e+06 to 1e+06. |
| `leakage_enabled` | false  | Use finite RC leakage; deterministic even with noise off. |
| `leakage_ohm` | 1000000.0 ohm | Leakage resistance; exact constant-current RC solution per sample. Allowed: 1e-09 to 1e+20. |

## Digital code source

`model_code_source` · `ComponentSource`

Time-domain sequence of nonnegative integer codes. Connect to a code-to-voltage DAC with sufficient resolution. No source noise is invented.

Inputs: none. Outputs: `out` (digital).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `values` | 0,1024,2048,4095  | Comma-separated samples held for sps steps; final value is held until run end. |
| `rate` | 1.0 GHz | Symbol rate. fs = rate × 10^9 × sps. Set all connected sources to the same fs. Allowed: 1e-12 to 1e+06. |
| `sps` | 16  | Integer samples per symbol. Allowed: 1 to 256. |
| `kind` | digital  | Fixed port type for this source definition. Options: digital. |

## Current source

`model_current_source` · `ComponentSource`

Time-domain current sequence in amperes. Connect to a capacitor or TIA. No source noise is invented.

Inputs: none. Outputs: `out` (current).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `values` | 0.9,0.3,0.7,0.5  | Comma-separated samples held for sps steps; final value is held until run end. |
| `rate` | 1.0 GHz | Symbol rate. fs = rate × 10^9 × sps. Set all connected sources to the same fs. Allowed: 1e-12 to 1e+06. |
| `sps` | 16  | Integer samples per symbol. Allowed: 1 to 256. |
| `kind` | current  | Fixed port type for this source definition. Options: current. |

## DAC: codes to voltage

`model_dac` · `ComponentDAC`

Uses DAC.code_to_voltage. Input must contain integer codes in [0,2^bits−1]; output is volts. Use the command quantizer when starting from a requested analog voltage.

Inputs: `code` (digital). Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `bits` | 12  | Integer converter resolution. Allowed: 1 to 16. |
| `v_min` | -0.5 V | Converter lower endpoint. Must be less than v_max. Allowed: -1e+06 to 1e+06. |
| `v_max` | 0.5 V | Converter upper endpoint. Allowed: -1e+06 to 1e+06. |

## DAC command quantizer

`model_dac_quantizer` · `ComponentDACQuantizer`

Uses DAC.quantize from converter experiments: requested analog command → integer code and quantized voltage. LSB=(v_max−v_min)/(2^bits−1). No jitter, DNL or INL model.

Inputs: `in` (voltage). Outputs: `out` (voltage), `code` (digital).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `bits` | 12  | Integer resolution; rounds to nearest code with NumPy ties-to-even. Allowed: 1 to 16. |
| `v_min` | -0.5 V | Converter lower endpoint. Must be less than v_max. Allowed: -1e+06 to 1e+06. |
| `v_max` | 0.5 V | Converter upper endpoint. Allowed: -1e+06 to 1e+06. |
| `clip` | false  | False rejects out-of-range commands; true explicitly clips to converter rails. |

## Inverse MZM encoder

`model_encoder` · `ComponentEncoder`

Calibration helper: x in [0,1] → V=(2Vpi/π)[acos(sqrt(x))−bias/2]. It inverts ideal normalized transmission before insertion loss. Match its parameters to the MZM.

Inputs: `x` (voltage). Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `v_pi` | 1.0 V | MZM half-wave voltage. Allowed: 1e-09 to 1000. |
| `bias_rad` | 1.5707963268 rad | Differential bias phase; transfer uses bias_rad / 2. Allowed: -100 to 100. |

## CW laser

`model_laser` · `ComponentLaser`

Uses experiments’ CWLaser complex envelope. RIN and phase noise have separate switches. Optical probes include power and unwrapped phase; no phase-to-intensity conversion is assumed.

Inputs: none. Outputs: `out` (optical).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `power_mW` | 1.0 mW | Mean optical power. Allowed: 0 to 10000. |
| `wavelength_nm` | 1550.0 nm | Carrier wavelength; optical metadata, not sampled carrier oscillation. Allowed: 1 to 1e+06. |
| `fs` | 16000000000.0 Hz | Sample rate; match rate × 10^9 × sps of electrical sources. Allowed: 1e-06 to 1e+15. |
| `phase_rad` | 0.0 rad | Initial envelope phase. Allowed: -1e+06 to 1e+06. |
| `rin_enabled` | true  | Enables laser intensity fluctuations only with global noise on. |
| `rin_db_hz` | -150.0 dB/Hz | One-sided RIN density. Linearized Gaussian power model; invalid negative-power realizations are rejected. Allowed: -300 to -60. |
| `linewidth_enabled` | true  | Enables phase diffusion only with global noise on. |
| `linewidth_hz` | 1000000.0 Hz | Lorentzian linewidth: phase-increment variance 2π linewidth/fs. Direct power detection is phase insensitive. Allowed: 0 to 1e+12. |
| `seed` | 0  | Block seed offset. Combined with run seed and instance ID; integer 0..2^32-1. Allowed: 0 to 4.29497e+09. |

## Photonic MAC (component models)

`model_mac` · `ComponentMAC`

Compact encoder → DAC → nonlinear MZM → split → ideal signed weight transmissions → independent photodetectors → current subtraction. External laser preserves explicit power/noise wiring. x∈[0,1], w∈[−1,1] use dimensionless values on voltage ports. Outputs are time samples, not an automatic vector sum; integrate over the intended symbol duration. Expand using the component-chain example to inspect every stage.

Inputs: `light` (optical), `x` (voltage), `w` (voltage). Outputs: `out` (current), `drive` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `v_pi` | 1.0 V | MZM half-wave voltage. Allowed: 1e-09 to 1000. |
| `bias_rad` | 1.5707963268 rad | Differential bias phase; transfer uses bias_rad / 2. Allowed: -100 to 100. |
| `loss_dB` | 0.0 dB | Deterministic insertion loss; remains active with noise off. Allowed: 0 to 200. |
| `dac_bits` | 12  | Input DAC integer resolution. Allowed: 1 to 16. |
| `v_min` | -0.5 V | Converter lower endpoint. Must be less than v_max. Allowed: -1e+06 to 1e+06. |
| `v_max` | 0.5 V | Converter upper endpoint. Allowed: -1e+06 to 1e+06. |
| `clip` | false  | False rejects out-of-range commands; true explicitly clips to converter rails. |
| `ratio` | 0.5  | Fraction of incident power in upper arm. Allowed: 0 to 1. |
| `responsivity` | 1.0 A/W | Photocurrent per watt of incident optical power. Allowed: 0 to 100. |
| `dark_enabled` | true  | Adds deterministic dark current even when global noise is off. |
| `dark_current_A` | 0.0 A | Mean dark current, included in shot-noise variance when enabled. Allowed: 0 to 1. |
| `shot_enabled` | true  | Global noise AND this switch enable white Gaussian shot noise, variance 2 q Imean fs/2. |
| `seed` | 0  | Block seed offset. Combined with run seed and instance ID; integer 0..2^32-1. Allowed: 0 to 4.29497e+09. |

## Mach–Zehnder modulator

`model_mzm` · `ComponentMZM`

Nonlinear power transfer T=cos²(πV/(2Vpi)+bias/2) × 10^(−loss/10). Uses MachZehnderModulator.transfer. Envelope phase is passed through; modulator chirp and coherent field sign are not modeled.

Inputs: `light` (optical), `drive` (voltage). Outputs: `out` (optical).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `v_pi` | 1.0 V | MZM half-wave voltage. Allowed: 1e-09 to 1000. |
| `bias_rad` | 1.5707963268 rad | Differential bias phase; transfer uses bias_rad / 2. Allowed: -100 to 100. |
| `loss_dB` | 0.0 dB | Deterministic insertion loss; remains active with noise off. Allowed: 0 to 200. |

## Photodetector

`model_pd` · `ComponentPD`

Uses Photodetector.detect_white_shot: I=R|E|²+Idark, white-shot variance=2q Imean fs/2. Single optical channel. Receiver filtering/noise is handled explicitly by TIA; no automatic load-thermal term is added.

Inputs: `in` (optical). Outputs: `out` (current).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `responsivity` | 1.0 A/W | Photocurrent per watt of incident optical power. Allowed: 0 to 100. |
| `dark_enabled` | true  | Adds deterministic dark current even when global noise is off. |
| `dark_current_A` | 0.0 A | Mean dark current, included in shot-noise variance when enabled. Allowed: 0 to 1. |
| `shot_enabled` | true  | Global noise AND this switch enable white Gaussian shot noise, variance 2 q Imean fs/2. |
| `seed` | 0  | Block seed offset. Combined with run seed and instance ID; integer 0..2^32-1. Allowed: 0 to 4.29497e+09. |

## Voltage / normalized source

`model_source` · `ComponentSource`

Time-domain voltage sequence. Normalized x and signed w may use the voltage transport; these control values are dimensionless by convention. No source noise is invented.

Inputs: none. Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `values` | 0.9,0.3,0.7,0.5  | Comma-separated samples held for sps steps; final value is held until run end. |
| `rate` | 1.0 GHz | Symbol rate. fs = rate × 10^9 × sps. Set all connected sources to the same fs. Allowed: 1e-12 to 1e+06. |
| `sps` | 16  | Integer samples per symbol. Allowed: 1 to 256. |
| `kind` | voltage  | Fixed port type for this source definition. Options: voltage. |

## Optical splitter

`model_splitter` · `ComponentSplitter`

Power-conserving split before explicit insertion loss. Envelopes scale by square roots of branch power ratios. No additional fabrication or coupling model.

Inputs: `in` (optical). Outputs: `upper` (optical), `lower` (optical).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `ratio` | 0.5  | Fraction of incident power in upper arm. Allowed: 0 to 1. |
| `loss_dB` | 0.0 dB | Deterministic insertion loss; remains active with noise off. Allowed: 0 to 200. |

## Transimpedance amplifier

`model_tia` · `ComponentTIA`

Uses TIA.amplify. Noise is added before gain and finite-bandwidth filtering. Density can represent the measured receiver noise budget; no implicit second thermal-noise source. No TIA saturation model.

Inputs: `in` (current). Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `resistance_ohm` | 1000.0 ohm | Transimpedance gain. Allowed: 1e-09 to 1e+12. |
| `bandwidth_enabled` | true  | Apply the established first-order backward-Euler low-pass. |
| `bandwidth_Hz` | 1000000000.0 Hz | Nominal analog −3 dB bandwidth; discrete response depends on fs. First output equals first input × gain. Allowed: 1e-09 to 1e+15. |
| `noise_enabled` | true  | Global noise AND this switch enable input-referred white current noise. |
| `noise_A_sqrtHz` | 1e-12 A/√Hz | User-specified total input current noise density; variance before filtering is density² fs/2. Allowed: 0 to 1. |
| `seed` | 0  | Block seed offset. Combined with run seed and instance ID; integer 0..2^32-1. Allowed: 0 to 4.29497e+09. |

## Power transmission control

`model_transmission` · `ComponentTransmission`

Ideal weight attenuation: Eout=Ein sqrt(t), 0≤t≤1. Control uses a voltage-kind port as a dimensionless transmission command. This is not a voltage-driven nonlinear MZM.

Inputs: `light` (optical), `transmission` (voltage). Outputs: `out` (optical).

No editable parameters.

## Signed weight encoder

`model_weights` · `ComponentWeights`

Dimensionless signed w in [−1,1] becomes t+=(1+w)/2 and t−=(1−w)/2. Ideal weight settings; no weight DAC or drift model has been validated.

Inputs: `in` (voltage). Outputs: `upper` (voltage), `lower` (voltage).

No editable parameters.
