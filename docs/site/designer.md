# Component Designer

The default Designer uses the component models from the supplied Prabha experiments. Choose **Component designer** in Studio. On Pages, loading Python can take a little time on the first visit; the browser runs the actual Python code through Pyodide.

## Start with an example

| Example | Purpose | Result to inspect |
|---|---|---|
| Component neuron · B22 reference | Compact current-model MAC with explicit laser and analog readout | `adc.voltage` final = **0.6388278388278388**, noise off |
| Expanded component chain | Separate encoder, DAC, MZM, splitter, weights and PDs | Same final output; inspect every stage |
| Noisy receiver · PD + TIA | Laser RIN/phase, dark/shot current and TIA bandwidth/noise | Optical phase/power, PD current, TIA voltage |
| Leakage, rails and activation | Finite RC leakage, ±0.4 V amplifier clipping and shifted sigmoid | Capacitor, amplifier, activation and ADC traces |
| Legacy PEMAN compatibility | Open or reproduce the earlier Designer | Original settings/semantics; not the B22 pipeline |

Drag a block from the palette (or double-click to add), connect an output to a matching input, then select the block. The Inspector displays **all parameters, units, model equations and limitations**. Press `F` to focus a selected block; `.` fits the whole graph. The expanded example is deliberately wide; zoom in to edit stages.

Set **Duration (ns)** and an integer **Run seed**. Electrical sources use `fs = rate (GHz) × 10^9 × sps`; match the laser sample rate. Source sequences hold their final value until the duration ends. The reference example uses 4 ns, 1 GHz symbol rate and 16 samples/symbol (16 GHz sample rate).

## Noise and nonlinearity

**Noise** is the master stochastic switch. Each laser has separate RIN and linewidth switches; PDs have a shot-noise switch; TIAs have an input-noise switch. A stochastic source needs both its own switch and the master switch enabled. A seed combines the run seed, the block seed and the instance ID, so renaming a block changes its random stream. Repeating unchanged settings reproduces the same samples.

Noise off does not disable nonlinear MZM transfer, converter quantization, insertion loss, dark current, TIA bandwidth, capacitor leakage, amplifier rails or activation thresholds. Their own parameters control them. **Show theory** changes explanations only.

The current PD does not add the old PEMAN load-thermal term. Use the explicit TIA noise-density parameter for the receiver noise budget. Avoid accounting for the same measured noise twice. Phase noise is visible in the phase scope; a direct detector does not turn phase into intensity by itself.

## Signals and outputs

Current component ADC `code` is an integer converter code carried in the signal's numeric array. `voltage` is its reconstructed voltage. Connect analog activation before the ADC to reproduce B22. The DAC offers a code-to-voltage block and a separate analog-command quantizer; neither silently reinterprets voltage as an integer code.

Normalized input and signed weight commands use voltage-kind transport ports with **dimensionless control semantics**, as identified in the block help. MZM drive and receiver/readout voltages are volts. Optical graph data is a complex envelope in √W; the default scope shows |E|² in W, with optional unwrapped phase in radians.

Graph outputs are time samples. The MAC does not automatically sum a vector; use the capacitor over the intended symbol duration. A capacitor output sample is the state after that sample's integration interval. Other waveform time labels use original indices `k/fs`.

## Save and reproduce

- **Save Designer project** creates `.prabha.json` with graph, layout, model revision and run settings. Open it in the Designer.
- **Export engine netlist** creates a plain `.prabha` graph for the existing Python netlist loader. Run settings are supplied separately; this format preserves the original schema.
- **Export reproducible run** creates JSON containing the exact request, settings, model revision, engine version, warnings and plotted probes. Replay its `request` using the `graph` action. Probes contain at most 1,200 plotted points and original sample indices; final values are computed from every simulation sample.
- **Plot ZIP** includes figures and the run record. It uses the existing JSZip CDN, so JSON export is the independent option if that optional dependency cannot load.

Changing the graph or run settings clears old results. A result returning after an edit is discarded. Parameter/connection errors are shown; unused-output warnings are allowed for probes. Run limits remain 64 top-level blocks, 256 connections and 20,000 samples/source.

## Compatibility and model revision

The palette shows 19 current component definitions by default. **Show legacy blocks** exposes older IDs for compatibility; imported old designs are not silently migrated, because modulator and ADC semantics differ. All current model calculations use Python in API, browser and desktop modes. C++ still covers the legacy fixtures only. See [model scope](model-scope.md).

## Model catalogue

The defaults below come from the current block definitions. Read the [extended user manual](user-manual.md) for the full mathematical derivation, demonstrations and interpretation.

### Nonlinear activation

`model_activation` · `ComponentActivation`

Uses Activation.activate. Sigmoid, tanh, ReLU and linear; sigmoid argument clipped to ±60 for numerical stability. Behavioral output is represented on a normalized 1 V scale; this is not a transistor-level device model. B22 places activation BEFORE ADC.

Inputs: `in` (voltage). Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `kind` | sigmoid  | Behavioral transfer function. Options: sigmoid, tanh, relu, linear. |
| `gain` | 1.0  | Pre-activation scaling. Allowed: -1e+06 to 1e+06. |
| `threshold_V` | 0.0 V | Shift: z=gain × (Vin−threshold). Allowed: -1e+06 to 1e+06. |

### ADC

`model_adc` · `ComponentADC`

Uses ADC.convert/code_to_voltage. code is the actual integer code; voltage is the reconstructed quantized value. Range errors are visible unless clipping is explicitly enabled. No jitter, INL or DNL model.

Inputs: `in` (voltage). Outputs: `code` (digital), `voltage` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `bits` | 12  | Integer resolution; nearest code, NumPy ties-to-even. Allowed: 1 to 16. |
| `v_min` | 0.0 V | Lower conversion endpoint. Allowed: -1e+06 to 1e+06. |
| `v_max` | 1.0 V | Upper conversion endpoint. Allowed: -1e+06 to 1e+06. |
| `clip` | false  | False rejects out-of-range commands; true explicitly clips to converter rails. |

### Voltage amplifier

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

### Balanced current subtraction

`model_balance` · `ComponentBalance`

Iout=Iupper−Ilower. Each photodetector has its own noise stream. No extra subtractor noise or hidden gain.

Inputs: `upper` (current), `lower` (current). Outputs: `out` (current).

No editable parameters.

### Capacitor integrator

`model_capacitor` · `ComponentCapacitor`

Uses Capacitor.integrate_current with dt=1/fs. Output sample k is voltage AFTER interval k; first sample includes one integration step. Without leakage: V+=I dt/C. With leakage: Vnew=Vold exp(−dt/RC)+IR(1−exp(−dt/RC)). No kT/C reset noise.

Inputs: `in` (current). Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `capacitance_pF` | 1.0 pF | Charge storage capacitance. Allowed: 1e-12 to 1e+12. |
| `initial_V` | 0.0 V | Initial voltage; resets at start of every run. Allowed: -1e+06 to 1e+06. |
| `leakage_enabled` | false  | Use finite RC leakage; deterministic even with noise off. |
| `leakage_ohm` | 1000000.0 ohm | Leakage resistance; exact constant-current RC solution per sample. Allowed: 1e-09 to 1e+20. |

### Digital code source

`model_code_source` · `ComponentSource`

Time-domain sequence of nonnegative integer codes. Connect to a code-to-voltage DAC with sufficient resolution. No source noise is invented.

Inputs: none. Outputs: `out` (digital).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `values` | 0,1024,2048,4095  | Comma-separated samples held for sps steps; final value is held until run end. |
| `rate` | 1.0 GHz | Symbol rate. fs = rate × 10^9 × sps. Set all connected sources to the same fs. Allowed: 1e-12 to 1e+06. |
| `sps` | 16  | Integer samples per symbol. Allowed: 1 to 256. |
| `kind` | digital  | Fixed port type for this source definition. Options: digital. |

### Current source

`model_current_source` · `ComponentSource`

Time-domain current sequence in amperes. Connect to a capacitor or TIA. No source noise is invented.

Inputs: none. Outputs: `out` (current).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `values` | 0.9,0.3,0.7,0.5  | Comma-separated samples held for sps steps; final value is held until run end. |
| `rate` | 1.0 GHz | Symbol rate. fs = rate × 10^9 × sps. Set all connected sources to the same fs. Allowed: 1e-12 to 1e+06. |
| `sps` | 16  | Integer samples per symbol. Allowed: 1 to 256. |
| `kind` | current  | Fixed port type for this source definition. Options: current. |

### DAC: codes to voltage

`model_dac` · `ComponentDAC`

Uses DAC.code_to_voltage. Input must contain integer codes in [0,2^bits−1]; output is volts. Use the command quantizer when starting from a requested analog voltage.

Inputs: `code` (digital). Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `bits` | 12  | Integer converter resolution. Allowed: 1 to 16. |
| `v_min` | -0.5 V | Converter lower endpoint. Must be less than v_max. Allowed: -1e+06 to 1e+06. |
| `v_max` | 0.5 V | Converter upper endpoint. Allowed: -1e+06 to 1e+06. |

### DAC command quantizer

`model_dac_quantizer` · `ComponentDACQuantizer`

Uses DAC.quantize from converter experiments: requested analog command → integer code and quantized voltage. LSB=(v_max−v_min)/(2^bits−1). No jitter, DNL or INL model.

Inputs: `in` (voltage). Outputs: `out` (voltage), `code` (digital).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `bits` | 12  | Integer resolution; rounds to nearest code with NumPy ties-to-even. Allowed: 1 to 16. |
| `v_min` | -0.5 V | Converter lower endpoint. Must be less than v_max. Allowed: -1e+06 to 1e+06. |
| `v_max` | 0.5 V | Converter upper endpoint. Allowed: -1e+06 to 1e+06. |
| `clip` | false  | False rejects out-of-range commands; true explicitly clips to converter rails. |

### Inverse MZM encoder

`model_encoder` · `ComponentEncoder`

Calibration helper: x in [0,1] → V=(2Vpi/π)[acos(sqrt(x))−bias/2]. It inverts ideal normalized transmission before insertion loss. Match its parameters to the MZM.

Inputs: `x` (voltage). Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `v_pi` | 1.0 V | MZM half-wave voltage. Allowed: 1e-09 to 1000. |
| `bias_rad` | 1.5707963268 rad | Differential bias phase; transfer uses bias_rad / 2. Allowed: -100 to 100. |

### CW laser

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

### Photonic MAC (component models)

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

### Mach–Zehnder modulator

`model_mzm` · `ComponentMZM`

Nonlinear power transfer T=cos²(πV/(2Vpi)+bias/2) × 10^(−loss/10). Uses MachZehnderModulator.transfer. Envelope phase is passed through; modulator chirp and coherent field sign are not modeled.

Inputs: `light` (optical), `drive` (voltage). Outputs: `out` (optical).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `v_pi` | 1.0 V | MZM half-wave voltage. Allowed: 1e-09 to 1000. |
| `bias_rad` | 1.5707963268 rad | Differential bias phase; transfer uses bias_rad / 2. Allowed: -100 to 100. |
| `loss_dB` | 0.0 dB | Deterministic insertion loss; remains active with noise off. Allowed: 0 to 200. |

### Photodetector

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

### Voltage / normalized source

`model_source` · `ComponentSource`

Time-domain voltage sequence. Normalized x and signed w may use the voltage transport; these control values are dimensionless by convention. No source noise is invented.

Inputs: none. Outputs: `out` (voltage).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `values` | 0.9,0.3,0.7,0.5  | Comma-separated samples held for sps steps; final value is held until run end. |
| `rate` | 1.0 GHz | Symbol rate. fs = rate × 10^9 × sps. Set all connected sources to the same fs. Allowed: 1e-12 to 1e+06. |
| `sps` | 16  | Integer samples per symbol. Allowed: 1 to 256. |
| `kind` | voltage  | Fixed port type for this source definition. Options: voltage. |

### Optical splitter

`model_splitter` · `ComponentSplitter`

Power-conserving split before explicit insertion loss. Envelopes scale by square roots of branch power ratios. No additional fabrication or coupling model.

Inputs: `in` (optical). Outputs: `upper` (optical), `lower` (optical).

| Parameter | Default / unit | Meaning |
|:--|:--|:--|
| `ratio` | 0.5  | Fraction of incident power in upper arm. Allowed: 0 to 1. |
| `loss_dB` | 0.0 dB | Deterministic insertion loss; remains active with noise off. Allowed: 0 to 200. |

### Transimpedance amplifier

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

### Power transmission control

`model_transmission` · `ComponentTransmission`

Ideal weight attenuation: Eout=Ein sqrt(t), 0≤t≤1. Control uses a voltage-kind port as a dimensionless transmission command. This is not a voltage-driven nonlinear MZM.

Inputs: `light` (optical), `transmission` (voltage). Outputs: `out` (optical).

No editable parameters.

### Signed weight encoder

`model_weights` · `ComponentWeights`

Dimensionless signed w in [−1,1] becomes t+=(1+w)/2 and t−=(1−w)/2. Ideal weight settings; no weight DAC or drift model has been validated.

Inputs: `in` (voltage). Outputs: `upper` (voltage), `lower` (voltage).

No editable parameters.
