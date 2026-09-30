<!-- Generated from docs/manual/Prabha_User_Manual.md using pandoc --mathml. -->


<header id="title-block-header">
<h1 class="title">Prabha</h1>
<p class="subtitle">User manual, mathematical reference and evaluation
guide</p>
<p class="author">Abhishek Singh · Electronics and Communication
Engineering · IIT Patna</p>
<p class="date">30 September 2026 · preview.3 / components-1 · clarity
revision</p>
</header>
<nav id="TOC" role="doc-toc">
<ul>
<li><a href="#reading-this-manual" id="toc-reading-this-manual">Reading
this manual</a>
<ul>
<li><a href="#what-changed-in-this-review"
id="toc-what-changed-in-this-review">What changed in this
review</a></li>
</ul></li>
<li><a href="#what-runs-where" id="toc-what-runs-where">What runs
where</a>
<ul>
<li><a href="#the-three-scientific-paths"
id="toc-the-three-scientific-paths">The three scientific paths</a></li>
<li><a href="#the-software-layers" id="toc-the-software-layers">The
software layers</a></li>
<li><a href="#important-folders" id="toc-important-folders">Important
folders</a></li>
</ul></li>
<li><a href="#first-successful-local-run-and-github-push"
id="toc-first-successful-local-run-and-github-push">First successful
local run and GitHub push</a>
<ul>
<li><a href="#apply-the-clarity-patch"
id="toc-apply-the-clarity-patch">Apply the clarity patch</a></li>
<li><a href="#rebuild-and-inspect" id="toc-rebuild-and-inspect">Rebuild
and inspect</a></li>
<li><a href="#publish-the-new-commit"
id="toc-publish-the-new-commit">Publish the new commit</a></li>
</ul></li>
<li><a href="#a-guided-designer-session"
id="toc-a-guided-designer-session">A guided Designer session</a>
<ul>
<li><a href="#controls-and-a-first-experiment"
id="toc-controls-and-a-first-experiment">Controls and a first
experiment</a></li>
<li><a href="#why-both-sources-had-an-x-and-a-voltage-port"
id="toc-why-both-sources-had-an-x-and-a-voltage-port">Why both sources
had an x and a voltage port</a></li>
<li><a href="#optical-power-and-phase-views"
id="toc-optical-power-and-phase-views">Optical power and phase
views</a></li>
</ul></li>
<li><a href="#mathematics-of-the-complete-neuron"
id="toc-mathematics-of-the-complete-neuron">Mathematics of the complete
neuron</a>
<ul>
<li><a href="#ideal-target" id="toc-ideal-target">Ideal target</a></li>
<li><a href="#inverse-mzm-encoding-and-the-dac"
id="toc-inverse-mzm-encoding-and-the-dac">Inverse MZM encoding and the
DAC</a></li>
<li><a href="#signed-optical-weighting"
id="toc-signed-optical-weighting">Signed optical weighting</a></li>
<li><a href="#charge-accumulation-gain-and-bias"
id="toc-charge-accumulation-gain-and-bias">Charge accumulation, gain and
bias</a></li>
<li><a href="#activation-and-adc-readout"
id="toc-activation-and-adc-readout">Activation and ADC readout</a></li>
</ul></li>
<li><a href="#noise-nonlinearity-and-memory"
id="toc-noise-nonlinearity-and-memory">Noise, nonlinearity and
memory</a>
<ul>
<li><a href="#the-noise-switch-has-a-specific-meaning"
id="toc-the-noise-switch-has-a-specific-meaning">The noise switch has a
specific meaning</a></li>
<li><a href="#laser-intensity-and-linewidth"
id="toc-laser-intensity-and-linewidth">Laser intensity and
linewidth</a></li>
<li><a href="#photodetection-and-receiver-noise"
id="toc-photodetection-and-receiver-noise">Photodetection and receiver
noise</a></li>
<li><a href="#tia-bandwidth" id="toc-tia-bandwidth">TIA
bandwidth</a></li>
<li><a href="#capacitor-leakage-and-sample-timing"
id="toc-capacitor-leakage-and-sample-timing">Capacitor leakage and
sample timing</a></li>
<li><a href="#amplifier-rails-and-activation"
id="toc-amplifier-rails-and-activation">Amplifier rails and
activation</a></li>
</ul></li>
<li><a href="#ann-inference-and-the-meaning-of-validation"
id="toc-ann-inference-and-the-meaning-of-validation">ANN inference and
the meaning of validation</a>
<ul>
<li><a href="#fixed-network-and-separate-reference-paths"
id="toc-fixed-network-and-separate-reference-paths">Fixed network and
separate reference paths</a></li>
<li><a href="#the-100-input-protocol"
id="toc-the-100-input-protocol">The 100-input protocol</a></li>
<li><a href="#separate-optical-link-noise-evidence"
id="toc-separate-optical-link-noise-evidence">Separate optical-link
noise evidence</a></li>
<li><a href="#what-the-tests-establish"
id="toc-what-the-tests-establish">What the tests establish</a></li>
</ul></li>
<li><a href="#four-demonstrations-for-a-professor"
id="toc-four-demonstrations-for-a-professor">Four demonstrations for a
professor</a>
<ul>
<li><a href="#demonstration-1-explain-every-number"
id="toc-demonstration-1-explain-every-number">Demonstration 1: explain
every number</a></li>
<li><a href="#demonstration-2-show-a-controlled-precision-change"
id="toc-demonstration-2-show-a-controlled-precision-change">Demonstration
2: show a controlled precision change</a></li>
<li><a href="#demonstration-3-distinguish-phase-and-intensity"
id="toc-demonstration-3-distinguish-phase-and-intensity">Demonstration
3: distinguish phase and intensity</a></li>
<li><a href="#demonstration-4-connect-a-neuron-to-an-ann"
id="toc-demonstration-4-connect-a-neuron-to-an-ann">Demonstration 4:
connect a neuron to an ANN</a></li>
</ul></li>
<li><a href="#saving-replay-and-common-problems"
id="toc-saving-replay-and-common-problems">Saving, replay and common
problems</a>
<ul>
<li><a href="#save-the-experiment-not-just-a-picture"
id="toc-save-the-experiment-not-just-a-picture">Save the experiment, not
just a picture</a></li>
<li><a href="#troubleshooting-table"
id="toc-troubleshooting-table">Troubleshooting table</a></li>
</ul></li>
<li><a href="#research-contribution-novelty-and-next-evidence"
id="toc-research-contribution-novelty-and-next-evidence">Research
contribution, novelty and next evidence</a>
<ul>
<li><a href="#defensible-contribution-now"
id="toc-defensible-contribution-now">Defensible contribution
now</a></li>
<li><a href="#a-useful-claim-table" id="toc-a-useful-claim-table">A
useful claim table</a></li>
<li><a href="#priority-after-this-pause"
id="toc-priority-after-this-pause">Priority after this pause</a></li>
</ul></li>
<li><a href="#open-source-distribution-and-possible-services"
id="toc-open-source-distribution-and-possible-services">Open-source
distribution and possible services</a></li>
<li><a href="#questions-to-rehearse"
id="toc-questions-to-rehearse">Questions to rehearse</a></li>
<li><a href="#references-and-source-record"
id="toc-references-and-source-record">References and source
record</a></li>
<li><a href="#current-block-catalogue"
id="toc-current-block-catalogue">Current block catalogue</a>
<ul>
<li><a href="#nonlinear-activation"
id="toc-nonlinear-activation">Nonlinear activation</a></li>
<li><a href="#adc" id="toc-adc">ADC</a></li>
<li><a href="#voltage-amplifier" id="toc-voltage-amplifier">Voltage
amplifier</a></li>
<li><a href="#balanced-current-subtraction"
id="toc-balanced-current-subtraction">Balanced current
subtraction</a></li>
<li><a href="#capacitor-integrator"
id="toc-capacitor-integrator">Capacitor integrator</a></li>
<li><a href="#digital-code-source" id="toc-digital-code-source">Digital
code source</a></li>
<li><a href="#current-source" id="toc-current-source">Current
source</a></li>
<li><a href="#dac-codes-to-voltage" id="toc-dac-codes-to-voltage">DAC:
codes to voltage</a></li>
<li><a href="#dac-command-quantizer" id="toc-dac-command-quantizer">DAC
command quantizer</a></li>
<li><a href="#inverse-mzm-encoder" id="toc-inverse-mzm-encoder">Inverse
MZM encoder</a></li>
<li><a href="#cw-laser" id="toc-cw-laser">CW laser</a></li>
<li><a href="#photonic-mac-component-models"
id="toc-photonic-mac-component-models">Photonic MAC (component
models)</a></li>
<li><a href="#machzehnder-modulator"
id="toc-machzehnder-modulator">Mach–Zehnder modulator</a></li>
<li><a href="#photodetector"
id="toc-photodetector">Photodetector</a></li>
<li><a href="#voltage-normalized-source"
id="toc-voltage-normalized-source">Voltage / normalized source</a></li>
<li><a href="#optical-splitter" id="toc-optical-splitter">Optical
splitter</a></li>
<li><a href="#transimpedance-amplifier"
id="toc-transimpedance-amplifier">Transimpedance amplifier</a></li>
<li><a href="#power-transmission-control"
id="toc-power-transmission-control">Power transmission control</a></li>
<li><a href="#signed-weight-encoder"
id="toc-signed-weight-encoder">Signed weight encoder</a></li>
</ul></li>
</ul>
</nav>
<h1 id="reading-this-manual">Reading this manual</h1>
<p>Prabha is a research software prototype for photonic–electronic
behavioural simulation. It connects explicit signal descriptions and
validation rules to component calculations, a visual Designer, and a
fixed small neural-network inference example. Use it to study the
assumptions of a computation chain, reproduce numerical results and
develop additional models with tests.</p>
<p>This manual describes the supplied preview.3 implementation and the
accompanying clarity patch. It distinguishes a <strong>simulated
physical model</strong> from a physical experiment. No fabricated Prabha
processor, measured accelerator energy, trained classification benchmark
or implemented transformer is reported here.</p>
<p>If you are preparing for an evaluation, first read the worked neuron
and ANN chapters. Then run the demonstrations, read the model catalogue
and practise the questions. If you are changing the software, begin with
the architecture and reproducibility chapters. The catalogue is
generated from the actual <code>spec/blocks/model_*.json</code>
definitions; their limits and descriptions are also used by the
Inspector.</p>
<h2 id="what-changed-in-this-review">What changed in this review</h2>
<p>The source labels now follow their connections: a source feeding an
input command displays <strong>x</strong>, and one feeding a
signed-weight command displays <strong>w</strong>. The Inspector states
that these are dimensionless controls. The optical phase selector is
enabled only for optical probes; selecting an electrical probe restores
its ordinary value view. Results name their actual component/legacy
profile. A digital source now starts with valid integer codes. These
changes clarify use; they do not add new optical physics or alter the
reference ANN mathematics.</p>
<p>The Windows log supplied for this review reports 43 passing Python
tests and successful asset and frontend builds. A missing browser
favicon is cosmetic. The MkDocs link notice and the Starlette
test-client deprecation warning are distinct from numerical simulation
failures.</p>
<h1 id="what-runs-where">What runs where</h1>
<h2 id="the-three-scientific-paths">The three scientific paths</h2>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Path</th>
<th style="text-align: left;">Purpose</th>
<th style="text-align: left;">Important boundary</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">Current Designer,
<code>model_*</code></td>
<td style="text-align: left;">Connect the established Python component
classes in a sampled graph</td>
<td style="text-align: left;">19 definitions; compact and expanded
neuron examples</td>
</tr>
<tr class="even">
<td style="text-align: left;">Legacy PEMAN</td>
<td style="text-align: left;">Reproduce original saved graphs and
fixtures</td>
<td style="text-align: left;">Original converter/activation semantics
remain intact</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Standalone ANN</td>
<td style="text-align: left;">Run the fixed 4–3–2 behavioural inference
regression</td>
<td style="text-align: left;">Independent of arbitrary Designer graph
execution</td>
</tr>
</tbody>
</table>
<p>The current Designer and standalone experiments share component
classes, but they can organize time and accumulation differently. A
shared class is not a proof that two entire experiments have equal
timing or architecture. The C++17 engine covers the original conformance
fixtures; it does not execute the new current-model kernels or the ANN
operation.</p>
<h2 id="the-software-layers">The software layers</h2>
<ol type="1">
<li><strong>Specification:</strong> JSON schemas describe signals,
ports, blocks and netlists. Block definitions provide parameters, ports
and implementation identifiers.</li>
<li><strong>Validation:</strong> structural checks are followed by
semantic rules for graph references, connections, kinds, domains,
channels and cycles.</li>
<li><strong>Execution:</strong> the Python engine schedules a valid
directed acyclic graph and invokes registered kernels. Adapters call the
established component classes.</li>
<li><strong>Product interface:</strong> a shared Python dispatcher
exposes graph, component, perceptron and ANN operations.</li>
<li><strong>Transport and interface:</strong> React/Vite Studio and the
Designer call the dispatcher through FastAPI locally, through
Python/Pyodide in a browser worker on static hosting, or through a
Python sidecar in the desktop scaffold.</li>
</ol>
<p>The frontend displays and configures results. It does not replace the
numerical core with a separate JavaScript implementation. Static hosting
serves files; the visitor’s browser performs the current Python
simulation. This is why the present Pages prototype does not need an AWS
simulation server.</p>
<h2 id="important-folders">Important folders</h2>
<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Relative path under Prabha</th>
<th style="text-align: left;">What it contains</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>spec/blocks/</code></td>
<td style="text-align: left;">Machine-readable block interfaces and
defaults</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>spec/examples/</code></td>
<td style="text-align: left;">Current runnable Designer graphs</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>core-py/prabha/blocks/</code></td>
<td style="text-align: left;">Component classes and graph adapters</td>
</tr>
<tr class="even">
<td
style="text-align: left;"><code>core-py/prabha/blocks/component_kernels.py</code></td>
<td style="text-align: left;">Current <code>model_*</code> adapter
implementations</td>
</tr>
<tr class="odd">
<td
style="text-align: left;"><code>core-py/prabha/product.py</code></td>
<td style="text-align: left;">Shared product operations and bounded
requests</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>core-py/experiments/</code></td>
<td style="text-align: left;">Research experiments and their
protocols</td>
</tr>
<tr class="odd">
<td
style="text-align: left;"><code>core-py/ann_batch_validation.csv</code></td>
<td style="text-align: left;">Archived 100-input ANN evidence</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>frontend/web/index.html</code></td>
<td style="text-align: left;">Editable Designer source</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>frontend/studio/</code></td>
<td style="text-align: left;">Studio source, build and browser
tests</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>docs/site/</code></td>
<td style="text-align: left;">Documentation website source</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>desktop/</code></td>
<td style="text-align: left;">Tauri wrapper and sidecar
configuration</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>tests/</code></td>
<td style="text-align: left;">Product and current-model integration
checks</td>
</tr>
</tbody>
</table>
<p>Do not edit generated <code>dist</code>,
<code>public/designer.html</code> or the contents of
<code>prabha-python.zip</code>. Change the corresponding source, then
rebuild.</p>
<h1 id="first-successful-local-run-and-github-push">First successful
local run and GitHub push</h1>
<h2 id="apply-the-clarity-patch">Apply the clarity patch</h2>
<p>Your preview.3 updater has already completed. Extract the new review
package outside your repository. Open Command Prompt in its
<code>Prabha-Clarity-Update</code> directory and run:</p>
<div class="sourceCode" id="cb1"><pre
class="sourceCode bat"><code class="sourceCode dosbat"><span id="cb1-1"><a href="#cb1-1" aria-hidden="true" tabindex="-1"></a>py apply_update.py <span class="st">&quot;C:\Users\samay\OneDrive\Documents\Research_Works\Prabha&quot;</span> -<span class="at">-check</span></span>
<span id="cb1-2"><a href="#cb1-2" aria-hidden="true" tabindex="-1"></a>py apply_update.py <span class="st">&quot;C:\Users\samay\OneDrive\Documents\Research_Works\Prabha&quot;</span></span></code></pre></div>
<p>The updater checks that edited files match the expected preview.3
baseline, backs up replacements, creates the listed documentation files
and verifies the written bytes. It skips files already current. If it
reports conflicts, preserve your local changes and merge the named files
using the complete supplied versions. It does not commit or push.</p>
<h2 id="rebuild-and-inspect">Rebuild and inspect</h2>
<p>From Windows Command Prompt:</p>
<div class="sourceCode" id="cb2"><pre
class="sourceCode bat"><code class="sourceCode dosbat"><span id="cb2-1"><a href="#cb2-1" aria-hidden="true" tabindex="-1"></a><span class="bu">cd</span> <span class="at">/d</span> <span class="st">&quot;C:\Users\samay\OneDrive\Documents\Research_Works\Prabha&quot;</span></span>
<span id="cb2-2"><a href="#cb2-2" aria-hidden="true" tabindex="-1"></a>.\.venv\Scripts\python.exe <span class="at">-m</span> pip install <span class="at">-r</span> requirements<span class="at">-dev</span>.txt</span>
<span id="cb2-3"><a href="#cb2-3" aria-hidden="true" tabindex="-1"></a>npm.cmd ci -<span class="at">-prefix</span> frontend<span class="at">/studio</span></span>
<span id="cb2-4"><a href="#cb2-4" aria-hidden="true" tabindex="-1"></a>.\.venv\Scripts\python.exe scripts<span class="at">/build_web_assets</span>.py</span>
<span id="cb2-5"><a href="#cb2-5" aria-hidden="true" tabindex="-1"></a>npm.cmd run build -<span class="at">-prefix</span> frontend<span class="at">/studio</span></span>
<span id="cb2-6"><a href="#cb2-6" aria-hidden="true" tabindex="-1"></a>.\.venv\Scripts\python.exe <span class="at">-m</span> pytest tests <span class="at">-q</span></span>
<span id="cb2-7"><a href="#cb2-7" aria-hidden="true" tabindex="-1"></a>.\.venv\Scripts\python.exe frontend<span class="at">/web/server</span>.py</span></code></pre></div>
<p>Use the existing project environment. If it is missing, first create
it with <code>py -3.12 -m venv .venv</code>. The source project’s Node
configuration is the build reference. Open
<code>http://127.0.0.1:8000</code>, choose <strong>Component
designer</strong>, and run the default neuron. The expected final ADC
code is 2616 and reconstructed voltage is 0.6388278388278388 V. Read it
numerically as a normalized output on the 1 V scale.</p>
<p>Stop the server with Ctrl+C before entering the Git commands. From
the same Prabha root:</p>
<div class="sourceCode" id="cb3"><pre
class="sourceCode bat"><code class="sourceCode dosbat"><span id="cb3-1"><a href="#cb3-1" aria-hidden="true" tabindex="-1"></a>git status</span>
<span id="cb3-2"><a href="#cb3-2" aria-hidden="true" tabindex="-1"></a>git diff -<span class="at">-stat</span></span>
<span id="cb3-3"><a href="#cb3-3" aria-hidden="true" tabindex="-1"></a>git remote <span class="at">-v</span></span>
<span id="cb3-4"><a href="#cb3-4" aria-hidden="true" tabindex="-1"></a>git branch -<span class="at">-show-current</span></span>
<span id="cb3-5"><a href="#cb3-5" aria-hidden="true" tabindex="-1"></a>git add .</span>
<span id="cb3-6"><a href="#cb3-6" aria-hidden="true" tabindex="-1"></a>git diff -<span class="at">-cached</span> -<span class="at">-stat</span></span>
<span id="cb3-7"><a href="#cb3-7" aria-hidden="true" tabindex="-1"></a>git commit <span class="at">-m</span> <span class="st">&quot;Clarify Designer signals and add model mathematics manual&quot;</span></span>
<span id="cb3-8"><a href="#cb3-8" aria-hidden="true" tabindex="-1"></a>git push</span></code></pre></div>
<p>Review the staged file list before committing. The supplied
<code>.gitignore</code> excludes environments, dependencies, build
outputs and common secret files; retain it. Do not stage unrelated
personal data. These commands include the earlier preview.3 changes if
you have not yet committed them. <code>git push</code> uses your
existing branch and upstream. If Git explicitly says that the current
branch has no upstream, use <code>git push -u origin YOUR_BRANCH</code>,
replacing <code>YOUR_BRANCH</code> with the output of
<code>git branch --show-current</code>. Do not rename your branch or
force-push just to deploy.</p>
<p>If the remote has new commits, fetch and review them before merging
or rebasing; do not overwrite them. Authentication, a rejected push and
a failed GitHub build are separate problems. Keep the exact error if one
occurs.</p>
<h2 id="publish-the-new-commit">Publish the new commit</h2>
<p>In the repository’s Actions tab, check <strong>Validate
prototype</strong> for the new commit. Start a <strong>new Publish web
preview</strong> run on the branch you just pushed. Re-running an older
workflow run uses that older commit. Wait for a successful Pages
deployment, then refresh the site and inspect the source labels and
Documentation link. The patch retains preview.3 and the
<code>components-1</code> model revision because the numerical model is
unchanged.</p>
<p>Project: <a href="https://github.com/Abhishek5467/Prabha"
class="uri">https://github.com/Abhishek5467/Prabha</a></p>
<p>Web app: <a href="https://abhishek5467.github.io/Prabha/"
class="uri">https://abhishek5467.github.io/Prabha/</a></p>
<p>Documentation: <a href="https://abhishek5467.github.io/Prabha/docs/"
class="uri">https://abhishek5467.github.io/Prabha/docs/</a></p>
<p>These are the configured project addresses, not a claim that this
review has pushed your Windows files or published the patch.</p>
<h1 id="a-guided-designer-session">A guided Designer session</h1>
<h2 id="controls-and-a-first-experiment">Controls and a first
experiment</h2>
<p>Choose <strong>Component neuron · B22 reference</strong>. The
reference uses duration 4 ns, seed 1 and noise off. The compact graph
has x, w, laser, MAC, capacitor, amplifier, activation and ADC blocks.
Select a block to inspect parameters. Drag or double-click a palette
item to add it, join compatible output and input ports, press
<code>F</code> to focus a selection, and <code>.</code> to fit the
graph. <strong>Show theory</strong> changes explanations only.</p>
<p>Run the model. The output cards show final values from the complete
simulation. The probe selector changes which stage is plotted. A
displayed trace is sampled down to at most 1,200 points, with original
sample indices retained; this does not change the final value. The
default graph has 64 samples at 16 GHz.</p>
<p>Change MAC <code>dac_bits</code> from 12 to 3. The old results should
clear. Run again and compare the final output. This experiment
demonstrates finite input-converter resolution, not random noise.
Restore 12 bits before quoting the reference result.</p>
<p>Choose <strong>Expanded component chain</strong> to expose inverse
encoding, DAC, MZM, splitting, weight encoding, attenuation, two
detectors and subtraction separately. It should reproduce the compact
example’s final output. The graph is wide; zoom and use its stage
probes. The compact MAC is a current-model primitive internally calling
the component classes, even though the palette groups it as a compound
convenience block.</p>
<h2 id="why-both-sources-had-an-x-and-a-voltage-port">Why both sources
had an x and a voltage port</h2>
<p>Previously, both blocks used the same generic
<code>model_source</code> definition. Its body renderer selected x for
every source whose definition name did not contain “weight”. Thus the
displayed letter was wrong on the w block; its numerical values and
connection to the weight input were still distinct.</p>
<p>Four transport kinds exist in the present schema: optical, voltage,
current and digital. There is no separate dimensionless-control kind.
Consequently the normalized x and signed w arrays travel through
voltage-kind ports by convention. They are <strong>not both physical
drive voltages</strong>.</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Quantity</th>
<th style="text-align: left;">Meaning in B22</th>
<th style="text-align: left;">Unit or range</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">x</td>
<td style="text-align: left;">Desired normalized optical intensity</td>
<td style="text-align: left;">Dimensionless, 0 to 1</td>
</tr>
<tr class="even">
<td style="text-align: left;">w</td>
<td style="text-align: left;">Signed multiplication coefficient</td>
<td style="text-align: left;">Dimensionless, −1 to 1</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Encoder output</td>
<td style="text-align: left;">Requested MZM drive</td>
<td style="text-align: left;">V</td>
</tr>
<tr class="even">
<td style="text-align: left;">DAC output / MAC <code>drive</code></td>
<td style="text-align: left;">Quantized MZM drive</td>
<td style="text-align: left;">V</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Weight encoder output</td>
<td style="text-align: left;">Upper/lower power transmission</td>
<td style="text-align: left;">Dimensionless, 0 to 1</td>
</tr>
<tr class="even">
<td style="text-align: left;">Detector output</td>
<td style="text-align: left;">Photocurrent</td>
<td style="text-align: left;">A</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Capacitor / amplifier output</td>
<td style="text-align: left;">Electrical state</td>
<td style="text-align: left;">V</td>
</tr>
<tr class="even">
<td style="text-align: left;">ADC <code>code</code></td>
<td style="text-align: left;">Integer code</td>
<td style="text-align: left;">0 to
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msup><mn>2</mn><mi>b</mi></msup><mo>−</mo><mn>1</mn></mrow><annotation encoding="application/x-tex">2^b-1</annotation></semantics></math></td>
</tr>
<tr class="odd">
<td style="text-align: left;">ADC <code>voltage</code></td>
<td style="text-align: left;">Reconstructed readout</td>
<td style="text-align: left;">V, interpreted on the stated normalization
scale</td>
</tr>
</tbody>
</table>
<p>The patch infers display roles from consumers, not from instance
names. A generic or mixed-use source retains a generic label. Raw
exported graph signal kinds remain unchanged for compatibility;
source-control meaning must still accompany the recorded graph. A future
schema revision could introduce explicit dimensionless quantities, but
doing so requires migration and conformance work.</p>
<h2 id="optical-power-and-phase-views">Optical power and phase
views</h2>
<p>The optical signal is a sampled complex envelope:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>E</mi><mi>k</mi></msub><mo>=</mo><msqrt><msub><mi>P</mi><mi>k</mi></msub></msqrt><mo>exp</mo><mrow><mo stretchy="true" form="prefix">(</mo><mi>j</mi><msub><mi>ϕ</mi><mi>k</mi></msub><mo stretchy="true" form="postfix">)</mo></mrow><mo>,</mo><mspace width="2.0em"></mspace><msub><mi>P</mi><mi>k</mi></msub><mo>=</mo><msup><mrow><mo stretchy="true" form="prefix">|</mo><msub><mi>E</mi><mi>k</mi></msub><mo stretchy="true" form="postfix">|</mo></mrow><mn>2</mn></msup><mi>.</mi></mrow><annotation encoding="application/x-tex">E_k=\sqrt{P_k}\exp(j\phi_k),\qquad P_k=|E_k|^2.</annotation></semantics></math></p>
<p>Its amplitude has units
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msqrt><mi mathvariant="normal">W</mi></msqrt><annotation encoding="application/x-tex">\sqrt{\mathrm W}</annotation></semantics></math>;
the ordinary scope displays power in watts. The phase view displays
<code>unwrap(arg(E))</code> in radians. Unwrapping removes numerical
jumps of
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>2</mn><mi>π</mi></mrow><annotation encoding="application/x-tex">2\pi</annotation></semantics></math>
between adjacent phase samples. It does not reconstruct phase changes
larger than the sampling can resolve, and phase has no physical meaning
at zero amplitude.</p>
<p>The optical carrier itself is not sampled at hundreds of terahertz.
Wavelength identifies the carrier in metadata; sample rate resolves the
envelope variations. In the current MZM adapter, a nonnegative
square-root power factor scales the envelope while preserving its
incident phase. There is no chirp or coherent arm-field model.</p>
<p>Direct detection uses
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msup><mrow><mo stretchy="true" form="prefix">|</mo><mi>E</mi><mo stretchy="true" form="postfix">|</mo></mrow><mn>2</mn></msup><annotation encoding="application/x-tex">|E|^2</annotation></semantics></math>,
so a common phase rotation cancels. With laser RIN disabled and
linewidth enabled, the phase trace can wander while optical power
remains constant. That is expected behaviour. Phase-to-intensity
conversion would require an appropriate interferometric or coherent
detection model; selecting the phase view does not create one.</p>
<p>The patch disables the phase selector for electrical probes. It no
longer allows an ADC voltage plot to appear as though it were an optical
phase measurement.</p>
<h1 id="mathematics-of-the-complete-neuron">Mathematics of the complete
neuron</h1>
<h2 id="ideal-target">Ideal target</h2>
<p>A mathematical neuron computes</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>s</mi><mo>=</mo><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>N</mi></munderover><msub><mi>x</mi><mi>i</mi></msub><msub><mi>w</mi><mi>i</mi></msub><mo>+</mo><mi>b</mi><mo>,</mo><mspace width="2.0em"></mspace><mi>y</mi><mo>=</mo><mi>σ</mi><mrow><mo stretchy="true" form="prefix">(</mo><mi>s</mi><mo stretchy="true" form="postfix">)</mo></mrow><mo>,</mo><mspace width="2.0em"></mspace><mi>σ</mi><mrow><mo stretchy="true" form="prefix">(</mo><mi>s</mi><mo stretchy="true" form="postfix">)</mo></mrow><mo>=</mo><mfrac><mn>1</mn><mrow><mn>1</mn><mo>+</mo><msup><mi>e</mi><mrow><mo>−</mo><mi>s</mi></mrow></msup></mrow></mfrac><mi>.</mi></mrow><annotation encoding="application/x-tex">s=\sum_{i=1}^{N}x_iw_i+b,\qquad y=\sigma(s),\qquad \sigma(s)=\frac{1}{1+e^{-s}}.</annotation></semantics></math></p>
<p>For B22,</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>x</mi><mo>=</mo><mrow><mo stretchy="true" form="prefix">[</mo><mn>0.9</mn><mo>,</mo><mn>0.3</mn><mo>,</mo><mn>0.7</mn><mo>,</mo><mn>0.5</mn><mo stretchy="true" form="postfix">]</mo></mrow><mo>,</mo><mspace width="2.0em"></mspace><mi>w</mi><mo>=</mo><mrow><mo stretchy="true" form="prefix">[</mo><mn>0.8</mn><mo>,</mo><mo>−</mo><mn>0.6</mn><mo>,</mo><mn>0.4</mn><mo>,</mo><mo>−</mo><mn>0.9</mn><mo stretchy="true" form="postfix">]</mo></mrow><mo>,</mo><mspace width="2.0em"></mspace><mi>b</mi><mo>=</mo><mn>0.2</mn><mi>.</mi></mrow><annotation encoding="application/x-tex">x=[0.9,0.3,0.7,0.5],\qquad w=[0.8,-0.6,0.4,-0.9],\qquad b=0.2.</annotation></semantics></math></p>
<p>The products are
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mo stretchy="true" form="prefix">[</mo><mn>0.72</mn><mo>,</mo><mo>−</mo><mn>0.18</mn><mo>,</mo><mn>0.28</mn><mo>,</mo><mo>−</mo><mn>0.45</mn><mo stretchy="true" form="postfix">]</mo></mrow><annotation encoding="application/x-tex">[0.72,-0.18,0.28,-0.45]</annotation></semantics></math>,
their sum is 0.37, the pre-activation is 0.57 and the ideal output is
0.638763175149. x here is already a nonnegative normalized input.
Earlier signed optical-link experiments instead mapped a signed input
through
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>u</mi><mo>=</mo><mrow><mo stretchy="true" form="prefix">(</mo><mi>x</mi><mo>+</mo><mn>1</mn><mo stretchy="true" form="postfix">)</mo></mrow><mi>/</mi><mn>2</mn></mrow><annotation encoding="application/x-tex">u=(x+1)/2</annotation></semantics></math>;
do not apply that mapping a second time to the B22 input.</p>
<h2 id="inverse-mzm-encoding-and-the-dac">Inverse MZM encoding and the
DAC</h2>
<p>Let
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>V</mi><mi>π</mi></msub><annotation encoding="application/x-tex">V_\pi</annotation></semantics></math>
be the half-wave voltage and
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>ϕ</mi><mi>b</mi></msub><annotation encoding="application/x-tex">\phi_b</annotation></semantics></math>
the differential bias phase. With insertion loss
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>L</mi><annotation encoding="application/x-tex">L</annotation></semantics></math>
in dB, the implemented MZM power transfer is</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>T</mi><mrow><mo stretchy="true" form="prefix">(</mo><mi>V</mi><mo stretchy="true" form="postfix">)</mo></mrow><mo>=</mo><msup><mn>10</mn><mrow><mo>−</mo><mi>L</mi><mi>/</mi><mn>10</mn></mrow></msup><msup><mo>cos</mo><mn>2</mn></msup><mrow><mo stretchy="true" form="prefix">(</mo><mfrac><mrow><mi>π</mi><mi>V</mi></mrow><mrow><mn>2</mn><msub><mi>V</mi><mi>π</mi></msub></mrow></mfrac><mo>+</mo><mfrac><msub><mi>ϕ</mi><mi>b</mi></msub><mn>2</mn></mfrac><mo stretchy="true" form="postfix">)</mo></mrow><mi>.</mi></mrow><annotation encoding="application/x-tex">T(V)=10^{-L/10}\cos^2\left(\frac{\pi V}{2V_\pi}+\frac{\phi_b}{2}\right).</annotation></semantics></math></p>
<p>The factor
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>ϕ</mi><mi>b</mi></msub><mi>/</mi><mn>2</mn></mrow><annotation encoding="application/x-tex">\phi_b/2</annotation></semantics></math>
is essential. The inverse encoder chooses one branch of the <em>lossless
normalized</em> transfer:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msubsup><mi>V</mi><mi>i</mi><mo>*</mo></msubsup><mo>=</mo><mfrac><mrow><mn>2</mn><msub><mi>V</mi><mi>π</mi></msub></mrow><mi>π</mi></mfrac><mrow><mo stretchy="true" form="prefix">[</mo><mo>arccos</mo><mrow><mo stretchy="true" form="prefix">(</mo><msqrt><msub><mi>x</mi><mi>i</mi></msub></msqrt><mo stretchy="true" form="postfix">)</mo></mrow><mo>−</mo><mfrac><msub><mi>ϕ</mi><mi>b</mi></msub><mn>2</mn></mfrac><mo stretchy="true" form="postfix">]</mo></mrow><mi>.</mi></mrow><annotation encoding="application/x-tex">V_i^*=\frac{2V_\pi}{\pi}\left[\arccos(\sqrt{x_i})-\frac{\phi_b}{2}\right].</annotation></semantics></math></p>
<p>For
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>V</mi><mi>π</mi></msub><mo>=</mo><mn>1</mn></mrow><annotation encoding="application/x-tex">V_\pi=1</annotation></semantics></math>
V and
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>ϕ</mi><mi>b</mi></msub><mo>=</mo><mi>π</mi><mi>/</mi><mn>2</mn></mrow><annotation encoding="application/x-tex">\phi_b=\pi/2</annotation></semantics></math>,
x from 0 to 1 maps into +0.5 to −0.5 V. Matching the encoder and MZM
parameters is a calibration assumption. Insertion loss remains after
this inversion; the encoder does not automatically compensate it.</p>
<p>For an endpoint-inclusive converter with b bits,</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>Δ</mi><mo>=</mo><mfrac><mrow><msub><mi>V</mi><mo>max</mo></msub><mo>−</mo><msub><mi>V</mi><mo>min</mo></msub></mrow><mrow><msup><mn>2</mn><mi>b</mi></msup><mo>−</mo><mn>1</mn></mrow></mfrac><mo>,</mo><mspace width="1.0em"></mspace><mi>c</mi><mo>=</mo><mo>rint</mo><mrow><mo stretchy="true" form="prefix">(</mo><mfrac><mrow><msup><mi>V</mi><mo>*</mo></msup><mo>−</mo><msub><mi>V</mi><mo>min</mo></msub></mrow><mi>Δ</mi></mfrac><mo stretchy="true" form="postfix">)</mo></mrow><mo>,</mo><mspace width="1.0em"></mspace><mover><mi>V</mi><mo accent="true">̂</mo></mover><mo>=</mo><msub><mi>V</mi><mo>min</mo></msub><mo>+</mo><mi>c</mi><mi>Δ</mi><mi>.</mi></mrow><annotation encoding="application/x-tex">\Delta=\frac{V_{\max}-V_{\min}}{2^b-1},\quad c=\operatorname{rint}\left(\frac{V^*-V_{\min}}{\Delta}\right),\quad \widehat V=V_{\min}+c\Delta.</annotation></semantics></math></p>
<p><code>rint</code> rounds to nearest, with ties to even. The reference
DAC uses 12 bits and −0.5 to +0.5 V, giving a step of approximately
0.2442 mV. Commands outside the range are rejected unless explicit
clipping is enabled. The reconstructed voltage enters the nonlinear
transfer, producing
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>P</mi><mi>i</mi></msub><mo>=</mo><msub><mi>P</mi><mn>0</mn></msub><mi>T</mi><mrow><mo stretchy="true" form="prefix">(</mo><msub><mover><mi>V</mi><mo accent="true">̂</mo></mover><mi>i</mi></msub><mo stretchy="true" form="postfix">)</mo></mrow></mrow><annotation encoding="application/x-tex">P_i=P_0T(\widehat V_i)</annotation></semantics></math>.</p>
<h2 id="signed-optical-weighting">Signed optical weighting</h2>
<p>The ideal signed weight encoder makes two nonnegative power
transmissions:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msubsup><mi>t</mi><mi>i</mi><mo>+</mo></msubsup><mo>=</mo><mfrac><mrow><mn>1</mn><mo>+</mo><msub><mi>w</mi><mi>i</mi></msub></mrow><mn>2</mn></mfrac><mo>,</mo><mspace width="2.0em"></mspace><msubsup><mi>t</mi><mi>i</mi><mo>−</mo></msubsup><mo>=</mo><mfrac><mrow><mn>1</mn><mo>−</mo><msub><mi>w</mi><mi>i</mi></msub></mrow><mn>2</mn></mfrac><mi>.</mi></mrow><annotation encoding="application/x-tex">t_i^+=\frac{1+w_i}{2},\qquad t_i^-=\frac{1-w_i}{2}.</annotation></semantics></math></p>
<p>An equal optical splitter sends half the MZM power to each branch.
After attenuation and detection with responsivity
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>ℛ</mi><annotation encoding="application/x-tex">\mathcal R</annotation></semantics></math>,</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msubsup><mi>I</mi><mi>i</mi><mo>+</mo></msubsup><mo>=</mo><mfrac><mrow><mi>ℛ</mi><msub><mi>P</mi><mi>i</mi></msub></mrow><mn>2</mn></mfrac><msubsup><mi>t</mi><mi>i</mi><mo>+</mo></msubsup><mo>,</mo><mspace width="1.0em"></mspace><msubsup><mi>I</mi><mi>i</mi><mo>−</mo></msubsup><mo>=</mo><mfrac><mrow><mi>ℛ</mi><msub><mi>P</mi><mi>i</mi></msub></mrow><mn>2</mn></mfrac><msubsup><mi>t</mi><mi>i</mi><mo>−</mo></msubsup><mo>,</mo><mspace width="1.0em"></mspace><msubsup><mi>I</mi><mi>i</mi><mi>Δ</mi></msubsup><mo>=</mo><msubsup><mi>I</mi><mi>i</mi><mo>+</mo></msubsup><mo>−</mo><msubsup><mi>I</mi><mi>i</mi><mo>−</mo></msubsup><mo>=</mo><mfrac><mrow><mi>ℛ</mi><msub><mi>P</mi><mi>i</mi></msub><msub><mi>w</mi><mi>i</mi></msub></mrow><mn>2</mn></mfrac><mi>.</mi></mrow><annotation encoding="application/x-tex">I_i^+=\frac{\mathcal R P_i}{2}t_i^+,\quad I_i^-=\frac{\mathcal R P_i}{2}t_i^-,\quad I_i^\Delta=I_i^+-I_i^-=\frac{\mathcal R P_iw_i}{2}.</annotation></semantics></math></p>
<p>The optical powers never need to become negative. The signed result
is the difference between two nonnegative detector currents. Equal
deterministic dark currents cancel under ideal subtraction, but
independent detector shot fluctuations do not cancel sample by
sample.</p>
<p>If the upper split fraction is r instead of 1/2, the mean becomes
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>ℛ</mi><msub><mi>P</mi><mi>i</mi></msub><mrow><mo stretchy="true" form="prefix">[</mo><mi>r</mi><mrow><mo stretchy="true" form="prefix">(</mo><mn>1</mn><mo>+</mo><msub><mi>w</mi><mi>i</mi></msub><mo stretchy="true" form="postfix">)</mo></mrow><mi>/</mi><mn>2</mn><mo>−</mo><mrow><mo stretchy="true" form="prefix">(</mo><mn>1</mn><mo>−</mo><mi>r</mi><mo stretchy="true" form="postfix">)</mo></mrow><mrow><mo stretchy="true" form="prefix">(</mo><mn>1</mn><mo>−</mo><msub><mi>w</mi><mi>i</mi></msub><mo stretchy="true" form="postfix">)</mo></mrow><mi>/</mi><mn>2</mn><mo stretchy="true" form="postfix">]</mo></mrow><mo>=</mo><mi>ℛ</mi><msub><mi>P</mi><mi>i</mi></msub><mrow><mo stretchy="true" form="prefix">[</mo><mrow><mo stretchy="true" form="prefix">(</mo><mn>2</mn><mi>r</mi><mo>−</mo><mn>1</mn><mo stretchy="true" form="postfix">)</mo></mrow><mo>+</mo><msub><mi>w</mi><mi>i</mi></msub><mo stretchy="true" form="postfix">]</mo></mrow><mi>/</mi><mn>2</mn></mrow><annotation encoding="application/x-tex">\mathcal R P_i[r(1+w_i)/2-(1-r)(1-w_i)/2]=\mathcal R P_i[(2r-1)+w_i]/2</annotation></semantics></math>.
Thus splitter imbalance introduces an input-dependent offset in this
ideal weighting construction. Do not change r and continue quoting the
equal-split formula.</p>
<h2 id="charge-accumulation-gain-and-bias">Charge accumulation, gain and
bias</h2>
<p>For constant current over an interval
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>τ</mi><annotation encoding="application/x-tex">\tau</annotation></semantics></math>,
the capacitor increment is
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>I</mi><mi>τ</mi><mi>/</mi><mi>C</mi></mrow><annotation encoding="application/x-tex">I\tau/C</annotation></semantics></math>.
In the no-leakage reference,</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>V</mi><mi>C</mi></msub><mo>=</mo><mfrac><mi>τ</mi><mi>C</mi></mfrac><munder><mo>∑</mo><mi>i</mi></munder><msubsup><mi>I</mi><mi>i</mi><mi>Δ</mi></msubsup><mi>.</mi></mrow><annotation encoding="application/x-tex">V_C=\frac{\tau}{C}\sum_i I_i^\Delta.</annotation></semantics></math></p>
<p>With
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>P</mi><mn>0</mn></msub><mo>=</mo><mn>1</mn></mrow><annotation encoding="application/x-tex">P_0=1</annotation></semantics></math>
mW,
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>ℛ</mi><mo>=</mo><mn>1</mn></mrow><annotation encoding="application/x-tex">\mathcal R=1</annotation></semantics></math>
A/W,
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>τ</mi><mo>=</mo><mn>1</mn></mrow><annotation encoding="application/x-tex">\tau=1</annotation></semantics></math>
ns and
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mo>=</mo><mn>1</mn></mrow><annotation encoding="application/x-tex">C=1</annotation></semantics></math>
pF, the ideal scaling is</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>V</mi><mi>C</mi></msub><mo>=</mo><mrow><mo stretchy="true" form="prefix">(</mo><mn>0.5</mn><mspace width="0.167em"></mspace><mi mathvariant="normal">V</mi><mo stretchy="true" form="postfix">)</mo></mrow><munder><mo>∑</mo><mi>i</mi></munder><msub><mi>x</mi><mi>i</mi></msub><msub><mi>w</mi><mi>i</mi></msub><mi>.</mi></mrow><annotation encoding="application/x-tex">V_C=(0.5\,\mathrm V)\sum_i x_iw_i.</annotation></semantics></math></p>
<p>The amplifier applies gain 2 and offset 0.2 V. Dividing by the chosen
1 V normalization gives the dimensionless sigmoid argument. This scaling
connects the physical-model units to the mathematical neuron; it is not
an assertion that volts are dimensionless.</p>
<p>The standalone B22 experiment adds four parallel currents and
integrates for 1 ns. The Designer instead sends four sequential symbols,
each held for 1 ns, and integrates for 4 ns. The final charge agrees
when leakage is off and scaling matches. Their latency and architecture
are different. With leakage, earlier sequential contributions decay
more, so the final-value equivalence need not survive.</p>
<h2 id="activation-and-adc-readout">Activation and ADC readout</h2>
<p>The activation receives the gain/bias voltage. In the reference it
applies a sigmoid on the normalized 1 V scale, represented again as a
voltage between 0 and 1 V. The final ADC quantizes that voltage:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>c</mi><mi>A</mi></msub><mo>=</mo><mo>rint</mo><mrow><mo stretchy="true" form="prefix">[</mo><mrow><mo stretchy="true" form="prefix">(</mo><msup><mn>2</mn><mn>12</mn></msup><mo>−</mo><mn>1</mn><mo stretchy="true" form="postfix">)</mo></mrow><msub><mi>y</mi><mi>a</mi></msub><mo stretchy="true" form="postfix">]</mo></mrow><mo>,</mo><mspace width="2.0em"></mspace><mover><mi>y</mi><mo accent="true">̂</mo></mover><mo>=</mo><mfrac><msub><mi>c</mi><mi>A</mi></msub><mn>4095</mn></mfrac><mi>.</mi></mrow><annotation encoding="application/x-tex">c_A=\operatorname{rint}[(2^{12}-1)y_a],\qquad \widehat y=\frac{c_A}{4095}.</annotation></semantics></math></p>
<p>Current B22 ordering is <strong>analog activation then ADC</strong>.
The legacy PEMAN fixture’s ADC/digital-activation ordering differs.
Neither ordering should be silently substituted for the other.</p>
<table>
<thead>
<tr class="header">
<th style="text-align: left;">Stage</th>
<th style="text-align: right;">Reference result</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">Ideal dot product</td>
<td style="text-align: right;">0.37</td>
</tr>
<tr class="even">
<td style="text-align: left;">Ideal pre-activation</td>
<td style="text-align: right;">0.57</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Ideal sigmoid</td>
<td style="text-align: right;">0.638763175149</td>
</tr>
<tr class="even">
<td style="text-align: left;">Model capacitor voltage</td>
<td style="text-align: right;">0.185083940444 V</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Model gain and bias voltage</td>
<td style="text-align: right;">0.570167880888 V</td>
</tr>
<tr class="even">
<td style="text-align: left;">Model analog sigmoid on 1 V scale</td>
<td style="text-align: right;">0.638801911885 V</td>
</tr>
<tr class="odd">
<td style="text-align: left;">ADC code</td>
<td style="text-align: right;">2616</td>
</tr>
<tr class="even">
<td style="text-align: left;">Reconstructed normalized output</td>
<td style="text-align: right;">0.638827838828</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Absolute output difference from ideal</td>
<td
style="text-align: right;"><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>6.46637</mn><mo>×</mo><msup><mn>10</mn><mrow><mo>−</mo><mn>5</mn></mrow></msup></mrow><annotation encoding="application/x-tex">6.46637\times10^{-5}</annotation></semantics></math></td>
</tr>
</tbody>
</table>
<p>The small discrepancy is expected from finite converter precision in
this deterministic baseline. It does not mean every other input or
physical device will have the same error.</p>
<h1 id="noise-nonlinearity-and-memory">Noise, nonlinearity and
memory</h1>
<h2 id="the-noise-switch-has-a-specific-meaning">The noise switch has a
specific meaning</h2>
<p>A stochastic contribution requires both the global Noise switch and
its block-specific switch. Noise off leaves deterministic transfer
functions active: MZM nonlinearity, insertion loss, DAC/ADC
quantization, dark current, TIA filtering, leakage, clipping and
activation do not disappear.</p>
<p>Random streams combine a run seed, block seed and CRC32 of the
instance identifier, modulo
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msup><mn>2</mn><mn>32</mn></msup><annotation encoding="application/x-tex">2^{32}</annotation></semantics></math>.
Repeating the graph and settings reproduces a stream; renaming a block
changes it. The compact MAC uses internal detector names consistent with
the expanded reference. A seed is a reproducibility control, not an
experimental replicate count by itself.</p>
<h2 id="laser-intensity-and-linewidth">Laser intensity and
linewidth</h2>
<p>For one-sided RIN density
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>S</mi><mrow><mi mathvariant="normal">R</mi><mi mathvariant="normal">I</mi><mi mathvariant="normal">N</mi></mrow></msub><mo>=</mo><msup><mn>10</mn><mrow><msub><mrow><mi mathvariant="normal">R</mi><mi mathvariant="normal">I</mi><mi mathvariant="normal">N</mi></mrow><mrow><mi>d</mi><mi>B</mi><mi>/</mi><mi>H</mi><mi>z</mi></mrow></msub><mi>/</mi><mn>10</mn></mrow></msup></mrow><annotation encoding="application/x-tex">S_{\mathrm{RIN}}=10^{\mathrm{RIN}_{dB/Hz}/10}</annotation></semantics></math>
and sample rate
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>f</mi><mi>s</mi></msub><annotation encoding="application/x-tex">f_s</annotation></semantics></math>,
the linearized power perturbation uses</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>σ</mi><mi>P</mi></msub><mo>=</mo><msub><mi>P</mi><mn>0</mn></msub><msqrt><mrow><msub><mi>S</mi><mrow><mi mathvariant="normal">R</mi><mi mathvariant="normal">I</mi><mi mathvariant="normal">N</mi></mrow></msub><msub><mi>f</mi><mi>s</mi></msub><mi>/</mi><mn>2</mn></mrow></msqrt><mi>.</mi></mrow><annotation encoding="application/x-tex">\sigma_P=P_0\sqrt{S_{\mathrm{RIN}} f_s/2}.</annotation></semantics></math></p>
<p>It is a Gaussian white-sample approximation. Large fluctuations can
make sampled power negative; the model rejects such realizations instead
of taking an invalid square root. It is not a general low-photon-count
laser statistics model.</p>
<p>The phase diffusion increment obeys</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>Δ</mi><msub><mi>ϕ</mi><mi>k</mi></msub><mo>∼</mo><mi>𝒩</mi><mrow><mo stretchy="true" form="prefix">(</mo><mn>0</mn><mo>,</mo><mn>2</mn><mi>π</mi><mi>Δ</mi><mi>ν</mi><mi>/</mi><msub><mi>f</mi><mi>s</mi></msub><mo stretchy="true" form="postfix">)</mo></mrow><mo>,</mo><mspace width="2.0em"></mspace><msub><mi>ϕ</mi><mi>k</mi></msub><mo>=</mo><msub><mi>ϕ</mi><mn>0</mn></msub><mo>+</mo><munder><mo>∑</mo><mrow><mi>j</mi><mo>≤</mo><mi>k</mi></mrow></munder><mi>Δ</mi><msub><mi>ϕ</mi><mi>j</mi></msub><mi>.</mi></mrow><annotation encoding="application/x-tex">\Delta\phi_k\sim\mathcal N(0,2\pi\Delta\nu/f_s),\qquad \phi_k=\phi_0+\sum_{j\leq k}\Delta\phi_j.</annotation></semantics></math></p>
<p>Here
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>Δ</mi><mi>ν</mi></mrow><annotation encoding="application/x-tex">\Delta\nu</annotation></semantics></math>
is linewidth in Hz. The first generated noisy phase sample includes the
first increment. At zero linewidth the envelope phase is fixed.
Separately toggling RIN and linewidth allows you to observe intensity
and phase effects without conflating them.</p>
<h2 id="photodetection-and-receiver-noise">Photodetection and receiver
noise</h2>
<p>The current mean is
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>I</mi><mrow><mi mathvariant="normal">m</mi><mi mathvariant="normal">e</mi><mi mathvariant="normal">a</mi><mi mathvariant="normal">n</mi></mrow></msub><mo>=</mo><mi>ℛ</mi><msup><mrow><mo stretchy="true" form="prefix">|</mo><mi>E</mi><mo stretchy="true" form="postfix">|</mo></mrow><mn>2</mn></msup><mo>+</mo><msub><mi>I</mi><mi>d</mi></msub></mrow><annotation encoding="application/x-tex">I_{\mathrm{mean}}=\mathcal R|E|^2+I_d</annotation></semantics></math>
when dark current is enabled. The white Gaussian shot approximation
uses</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msubsup><mi>σ</mi><mi>I</mi><mn>2</mn></msubsup><mo>=</mo><mn>2</mn><mi>q</mi><msub><mi>I</mi><mrow><mi mathvariant="normal">m</mi><mi mathvariant="normal">e</mi><mi mathvariant="normal">a</mi><mi mathvariant="normal">n</mi></mrow></msub><mfrac><msub><mi>f</mi><mi>s</mi></msub><mn>2</mn></mfrac><mi>.</mi></mrow><annotation encoding="application/x-tex">\sigma_I^2=2qI_{\mathrm{mean}}\frac{f_s}{2}.</annotation></semantics></math></p>
<p><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>q</mi><annotation encoding="application/x-tex">q</annotation></semantics></math>
is electron charge. This implementation applies Gaussian fluctuations
around the mean; instantaneous samples can be negative even though mean
photocurrent is nonnegative. Use the model within the regime where the
approximation is meaningful. It is not a discrete photon-arrival
simulation.</p>
<p>The current-model detector does <strong>not</strong> silently add the
old legacy load-thermal term. The TIA accepts an explicit input-referred
current-noise density
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>i</mi><mi>n</mi></msub><annotation encoding="application/x-tex">i_n</annotation></semantics></math>
in
A/<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msqrt><mrow><mi mathvariant="normal">H</mi><mi mathvariant="normal">z</mi></mrow></msqrt><annotation encoding="application/x-tex">\sqrt{\mathrm{Hz}}</annotation></semantics></math>
and adds white noise of standard deviation
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>i</mi><mi>n</mi></msub><msqrt><mrow><msub><mi>f</mi><mi>s</mi></msub><mi>/</mi><mn>2</mn></mrow></msqrt></mrow><annotation encoding="application/x-tex">i_n\sqrt{f_s/2}</annotation></semantics></math>
before gain/filtering. This parameter may represent a measured receiver
noise budget; document its source and avoid double counting thermal
noise.</p>
<h2 id="tia-bandwidth">TIA bandwidth</h2>
<p>For resistance
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>R</mi><mi>f</mi></msub><annotation encoding="application/x-tex">R_f</annotation></semantics></math>
and bandwidth B, define
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>τ</mi><mi>f</mi></msub><mo>=</mo><mn>1</mn><mi>/</mi><mrow><mo stretchy="true" form="prefix">(</mo><mn>2</mn><mi>π</mi><mi>B</mi><mo stretchy="true" form="postfix">)</mo></mrow></mrow><annotation encoding="application/x-tex">\tau_f=1/(2\pi B)</annotation></semantics></math>,
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>Δ</mi><mi>t</mi><mo>=</mo><mn>1</mn><mi>/</mi><msub><mi>f</mi><mi>s</mi></msub></mrow><annotation encoding="application/x-tex">\Delta t=1/f_s</annotation></semantics></math>
and
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>α</mi><mo>=</mo><mi>Δ</mi><mi>t</mi><mi>/</mi><mrow><mo stretchy="true" form="prefix">(</mo><msub><mi>τ</mi><mi>f</mi></msub><mo>+</mo><mi>Δ</mi><mi>t</mi><mo stretchy="true" form="postfix">)</mo></mrow></mrow><annotation encoding="application/x-tex">\alpha=\Delta t/(\tau_f+\Delta t)</annotation></semantics></math>.
The backward-Euler update is</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>v</mi><mi>k</mi></msub><mo>=</mo><mi>α</mi><msub><mi>R</mi><mi>f</mi></msub><msub><mi>i</mi><mi>k</mi></msub><mo>+</mo><mrow><mo stretchy="true" form="prefix">(</mo><mn>1</mn><mo>−</mo><mi>α</mi><mo stretchy="true" form="postfix">)</mo></mrow><msub><mi>v</mi><mrow><mi>k</mi><mo>−</mo><mn>1</mn></mrow></msub><mi>.</mi></mrow><annotation encoding="application/x-tex">v_k=\alpha R_f i_k+(1-\alpha)v_{k-1}.</annotation></semantics></math></p>
<p>The first output is initialized to the first current sample times
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>R</mi><mi>f</mi></msub><annotation encoding="application/x-tex">R_f</annotation></semantics></math>.
It is not a zero-state startup transient. The discrete response depends
on
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>f</mi><mi>s</mi></msub><annotation encoding="application/x-tex">f_s</annotation></semantics></math>,
so a nominal analog bandwidth does not guarantee an exact digital −3 dB
frequency. This TIA has no saturation or slew-rate model; use the
separate amplifier rails only where that abstraction is appropriate.</p>
<h2 id="capacitor-leakage-and-sample-timing">Capacitor leakage and
sample timing</h2>
<p>Without leakage,
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>V</mi><mrow><mi>k</mi><mo>+</mo><mn>1</mn></mrow></msub><mo>=</mo><msub><mi>V</mi><mi>k</mi></msub><mo>+</mo><msub><mi>I</mi><mi>k</mi></msub><mi>Δ</mi><mi>t</mi><mi>/</mi><mi>C</mi></mrow><annotation encoding="application/x-tex">V_{k+1}=V_k+I_k\Delta t/C</annotation></semantics></math>.
With finite leakage resistance
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>R</mi><mi>L</mi></msub><annotation encoding="application/x-tex">R_L</annotation></semantics></math>
and constant current during each interval, the adapter uses the exact
interval update</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>V</mi><mrow><mi>k</mi><mo>+</mo><mn>1</mn></mrow></msub><mo>=</mo><msub><mi>V</mi><mi>k</mi></msub><msup><mi>e</mi><mrow><mo>−</mo><mi>Δ</mi><mi>t</mi><mi>/</mi><mrow><mo stretchy="true" form="prefix">(</mo><msub><mi>R</mi><mi>L</mi></msub><mi>C</mi><mo stretchy="true" form="postfix">)</mo></mrow></mrow></msup><mo>+</mo><msub><mi>I</mi><mi>k</mi></msub><msub><mi>R</mi><mi>L</mi></msub><mrow><mo stretchy="true" form="prefix">(</mo><mn>1</mn><mo>−</mo><msup><mi>e</mi><mrow><mo>−</mo><mi>Δ</mi><mi>t</mi><mi>/</mi><mrow><mo stretchy="true" form="prefix">(</mo><msub><mi>R</mi><mi>L</mi></msub><mi>C</mi><mo stretchy="true" form="postfix">)</mo></mrow></mrow></msup><mo stretchy="true" form="postfix">)</mo></mrow><mi>.</mi></mrow><annotation encoding="application/x-tex">V_{k+1}=V_ke^{-\Delta t/(R_LC)}+I_kR_L\left(1-e^{-\Delta t/(R_LC)}\right).</annotation></semantics></math></p>
<p>The stored output at array index k is the state
<strong>after</strong> integrating interval k, including one step at
index zero. The scope’s common time labels use
k/<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>f</mi><mi>s</mi></msub><annotation encoding="application/x-tex">f_s</annotation></semantics></math>;
account for this interval-end convention when interpreting capacitor
startup. Each run resets the state to <code>initial_V</code>. No reset
switch, kT/C noise or inter-run retained charge is modeled.</p>
<h2 id="amplifier-rails-and-activation">Amplifier rails and
activation</h2>
<p>The amplifier computes gain × input + offset and applies whichever
lower/upper rails are enabled. This is deterministic clipping. The
activation computes a shifted/scaled argument and applies sigmoid, tanh,
ReLU or linear transfer. Sigmoid arguments are clipped to ±60 for
numerical stability. These are behavioural functions, not
transistor-level activation circuits. A negative tanh or unbounded ReLU
output can exceed the default ADC’s 0–1 V range; change the intended
readout range or explicitly enable clipping.</p>
<h1 id="ann-inference-and-the-meaning-of-validation">ANN inference and
the meaning of validation</h1>
<h2 id="fixed-network-and-separate-reference-paths">Fixed network and
separate reference paths</h2>
<p>The current network has four inputs, three hidden neurons and two
output neurons:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>h</mi><mo>=</mo><mi>σ</mi><mrow><mo stretchy="true" form="prefix">(</mo><msub><mi>W</mi><mn>1</mn></msub><mi>x</mi><mo>+</mo><msub><mi>b</mi><mn>1</mn></msub><mo stretchy="true" form="postfix">)</mo></mrow><mo>,</mo><mspace width="2.0em"></mspace><mi>y</mi><mo>=</mo><mi>σ</mi><mrow><mo stretchy="true" form="prefix">(</mo><msub><mi>W</mi><mn>2</mn></msub><mi>h</mi><mo>+</mo><msub><mi>b</mi><mn>2</mn></msub><mo stretchy="true" form="postfix">)</mo></mrow><mo>,</mo></mrow><annotation encoding="application/x-tex">h=\sigma(W_1x+b_1),\qquad y=\sigma(W_2h+b_2),</annotation></semantics></math></p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>W</mi><mn>1</mn></msub><mo>=</mo><mrow><mo stretchy="true" form="prefix">[</mo><mtable><mtr><mtd columnalign="center" style="text-align: center"><mn>.8</mn></mtd><mtd columnalign="center" style="text-align: center"><mo>−</mo><mn>.6</mn></mtd><mtd columnalign="center" style="text-align: center"><mn>.4</mn></mtd><mtd columnalign="center" style="text-align: center"><mo>−</mo><mn>.9</mn></mtd></mtr><mtr><mtd columnalign="center" style="text-align: center"><mo>−</mo><mn>.3</mn></mtd><mtd columnalign="center" style="text-align: center"><mn>.7</mn></mtd><mtd columnalign="center" style="text-align: center"><mn>.5</mn></mtd><mtd columnalign="center" style="text-align: center"><mn>.2</mn></mtd></mtr><mtr><mtd columnalign="center" style="text-align: center"><mn>.6</mn></mtd><mtd columnalign="center" style="text-align: center"><mn>.1</mn></mtd><mtd columnalign="center" style="text-align: center"><mo>−</mo><mn>.8</mn></mtd><mtd columnalign="center" style="text-align: center"><mn>.7</mn></mtd></mtr></mtable><mo stretchy="true" form="postfix">]</mo></mrow><mo>,</mo><mspace width="1.0em"></mspace><msub><mi>b</mi><mn>1</mn></msub><mo>=</mo><mrow><mo stretchy="true" form="prefix">[</mo><mtable><mtr><mtd columnalign="center" style="text-align: center"><mn>.2</mn></mtd></mtr><mtr><mtd columnalign="center" style="text-align: center"><mo>−</mo><mn>.1</mn></mtd></mtr><mtr><mtd columnalign="center" style="text-align: center"><mn>.05</mn></mtd></mtr></mtable><mo stretchy="true" form="postfix">]</mo></mrow><mo>,</mo></mrow><annotation encoding="application/x-tex">W_1=\begin{bmatrix}.8&amp;-.6&amp;.4&amp;-.9\\-.3&amp;.7&amp;.5&amp;.2\\.6&amp;.1&amp;-.8&amp;.7\end{bmatrix},\quad b_1=\begin{bmatrix}.2\\-.1\\.05\end{bmatrix},</annotation></semantics></math></p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>W</mi><mn>2</mn></msub><mo>=</mo><mrow><mo stretchy="true" form="prefix">[</mo><mtable><mtr><mtd columnalign="center" style="text-align: center"><mn>.7</mn></mtd><mtd columnalign="center" style="text-align: center"><mo>−</mo><mn>.5</mn></mtd><mtd columnalign="center" style="text-align: center"><mn>.6</mn></mtd></mtr><mtr><mtd columnalign="center" style="text-align: center"><mo>−</mo><mn>.4</mn></mtd><mtd columnalign="center" style="text-align: center"><mn>.9</mn></mtd><mtd columnalign="center" style="text-align: center"><mo>−</mo><mn>.7</mn></mtd></mtr></mtable><mo stretchy="true" form="postfix">]</mo></mrow><mo>,</mo><mspace width="1.0em"></mspace><msub><mi>b</mi><mn>2</mn></msub><mo>=</mo><mrow><mo stretchy="true" form="prefix">[</mo><mtable><mtr><mtd columnalign="center" style="text-align: center"><mn>.1</mn></mtd></mtr><mtr><mtd columnalign="center" style="text-align: center"><mo>−</mo><mn>.05</mn></mtd></mtr></mtable><mo stretchy="true" form="postfix">]</mo></mrow><mi>.</mi></mrow><annotation encoding="application/x-tex">W_2=\begin{bmatrix}.7&amp;-.5&amp;.6\\-.4&amp;.9&amp;-.7\end{bmatrix},\quad b_2=\begin{bmatrix}.1\\-.05\end{bmatrix}.</annotation></semantics></math></p>
<p>Every model neuron includes the converter-aware optical/electronic
chain. Quantized model hidden outputs feed the model output layer. Ideal
hidden outputs independently feed the analytical output layer. Reusing
ideal hidden values in the model path would hide part of the accumulated
error.</p>
<p>The coefficients are fixed; no training occurred in this validation.
The inputs are synthetic numerical test vectors rather than a labelled
classification dataset.</p>
<h2 id="the-100-input-protocol">The 100-input protocol</h2>
<p>The experiment uses NumPy <code>default_rng(12345)</code> to generate
100 four-dimensional vectors uniformly from [0.05,0.95]. The first
vector is replaced with the B22 reference input. The stored CSV has 100
rows and two output-error columns, giving 200 comparisons. For errors
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>e</mi><mrow><mi>n</mi><mi>j</mi></mrow></msub><mo>=</mo><msub><mover><mi>y</mi><mo accent="true">̂</mo></mover><mrow><mi>n</mi><mi>j</mi></mrow></msub><mo>−</mo><msub><mi>y</mi><mrow><mi>n</mi><mi>j</mi></mrow></msub></mrow><annotation encoding="application/x-tex">e_{nj}=\widehat y_{nj}-y_{nj}</annotation></semantics></math>,</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mrow><mi mathvariant="normal">R</mi><mi mathvariant="normal">M</mi><mi mathvariant="normal">S</mi></mrow><mo>=</mo><msqrt><mrow><mfrac><mn>1</mn><mn>200</mn></mfrac><munderover><mo>∑</mo><mrow><mi>n</mi><mo>=</mo><mn>1</mn></mrow><mn>100</mn></munderover><munderover><mo>∑</mo><mrow><mi>j</mi><mo>=</mo><mn>1</mn></mrow><mn>2</mn></munderover><msubsup><mi>e</mi><mrow><mi>n</mi><mi>j</mi></mrow><mn>2</mn></msubsup></mrow></msqrt><mo>,</mo><mspace width="2.0em"></mspace><msub><mi>e</mi><mo>max</mo></msub><mo>=</mo><munder><mo>max</mo><mrow><mi>n</mi><mo>,</mo><mi>j</mi></mrow></munder><mrow><mo stretchy="true" form="prefix">|</mo><msub><mi>e</mi><mrow><mi>n</mi><mi>j</mi></mrow></msub><mo stretchy="true" form="postfix">|</mo></mrow><mi>.</mi></mrow><annotation encoding="application/x-tex">\mathrm{RMS}=\sqrt{\frac{1}{200}\sum_{n=1}^{100}\sum_{j=1}^{2}e_{nj}^2},\qquad e_{\max}=\max_{n,j}|e_{nj}|.</annotation></semantics></math></p>
<p>Recomputation from the supplied CSV gives RMS
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>7.864411795585</mn><mo>×</mo><msup><mn>10</mn><mrow><mo>−</mo><mn>5</mn></mrow></msup></mrow><annotation encoding="application/x-tex">7.864411795585\times10^{-5}</annotation></semantics></math>,
maximum
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>1.782838135357</mn><mo>×</mo><msup><mn>10</mn><mrow><mo>−</mo><mn>4</mn></mrow></msup></mrow><annotation encoding="application/x-tex">1.782838135357\times10^{-4}</annotation></semantics></math>
and mean signed error
<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>1.518043206350</mn><mo>×</mo><msup><mn>10</mn><mrow><mo>−</mo><mn>6</mn></mrow></msup></mrow><annotation encoding="application/x-tex">1.518043206350\times10^{-6}</annotation></semantics></math>.
The larger output’s index agrees with the analytical reference for all
100 vectors.</p>
<p><strong>0/100 ordering mismatches is not 100% classification
accuracy.</strong> There are no labels to classify. It shows agreement
of the two-output ordering for this fixed network and input sample. The
two sigmoid outputs are not a softmax probability distribution and need
not sum to one.</p>
<h2 id="separate-optical-link-noise-evidence">Separate optical-link
noise evidence</h2>
<p>The archived <code>full_chain_monte_carlo.csv</code> contains 200
runs per case, 800 rows total. Mean <em>per-run recovery RMS</em> values
are approximately:</p>
<table>
<thead>
<tr class="header">
<th style="text-align: left;">Link case</th>
<th style="text-align: right;">Mean recovery RMS</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">Laser RIN</td>
<td style="text-align: right;">0.00562061</td>
</tr>
<tr class="even">
<td style="text-align: left;">PD dark + shot</td>
<td style="text-align: right;">0.00483002</td>
</tr>
<tr class="odd">
<td style="text-align: left;">TIA noise</td>
<td style="text-align: right;">0.00366789</td>
</tr>
<tr class="even">
<td style="text-align: left;">Full link</td>
<td style="text-align: right;">0.00636798</td>
</tr>
</tbody>
</table>
<p>These values were recomputed from the stored CSV in this review. They
were not generated by a new hardware measurement or by injecting noise
into the 4–3–2 ANN. They describe a different link, normalization and
converter setup. An average of trial RMS values is not automatically the
same statistic as a pooled RMS over all samples. Do not add these RMS
values to the deterministic ANN RMS or call the result noisy ANN
accuracy.</p>
<h2 id="what-the-tests-establish">What the tests establish</h2>
<p>The original 14 fixtures exercise golden outputs and graph errors in
Python and C++17. Current Python integration tests cover adapters,
compact/expanded correspondence, controls and request errors. UI tests
check interaction and transport. These are useful engineering evidence
at different layers; passing them does not prove every physical
assumption.</p>
<p>The strongest present claim is: <strong>the implemented fixed
small-network model reproduces an independently computed analytical
reference with the reported finite-precision deviations on the stated
sample set.</strong> It supports further controlled modelling work.
Generalization to deeper trained networks, physical devices, tasks and
serving performance requires additional evidence.</p>
<h1 id="four-demonstrations-for-a-professor">Four demonstrations for a
professor</h1>
<h2 id="demonstration-1-explain-every-number">Demonstration 1: explain
every number</h2>
<p>Run the reference neuron with noise off. Show x and w and their
ranges. Read MAC drive to distinguish normalized commands from volts.
Explain the factor 1/2 from the optical split, the capacitor scaling,
gain 2 and bias 0.2. Show analog activation and ADC code separately.
Compare the final output with the worked table.</p>
<p>Expected explanation: the small difference comes from the modeled
finite converters; the ideal target is a separate calculation. Save the
run JSON before changing anything.</p>
<h2
id="demonstration-2-show-a-controlled-precision-change">Demonstration 2:
show a controlled precision change</h2>
<p>Reduce only DAC bits to 3, run, then restore 12. Keep input, weights,
duration, ADC, noise and seed unchanged. Compare the result and drive
trace. Do not call a single input an entire precision benchmark. If
making a plot for a paper, repeat a documented sweep and preserve all
settings and errors.</p>
<h2 id="demonstration-3-distinguish-phase-and-intensity">Demonstration
3: distinguish phase and intensity</h2>
<p>Load the noisy receiver. Turn laser RIN off, leave linewidth on and
inspect <code>laser.out</code> power and phase. Disable detector shot
and TIA noise if you want to isolate phase-only behaviour in the
receiver. Power remains constant while phase varies. Turn linewidth off
to remove phase diffusion, then enable RIN to see intensity
fluctuations. Explain why no direct-detection phase-to-intensity
conversion appears.</p>
<p>Restore the example before quoting its defaults. A changed seed
should change the realization; the original seed should reproduce
it.</p>
<h2 id="demonstration-4-connect-a-neuron-to-an-ann">Demonstration 4:
connect a neuron to an ANN</h2>
<p>In Studio’s ANN workspace, run the reference vector, inspect
ideal/model hidden and output values, then choose <strong>Validate 100
inputs</strong>. Read RMS, maximum error and mismatch count with their
definitions. Export the CSV. Explain the fixed weights, absence of
training and distinction between numerical agreement and task
accuracy.</p>
<p>A useful 10-minute sequence is: question and scope (1 minute),
component chain and equations (3), live neuron/phase demo (2), ANN
evidence (2), contribution and next experiment (2). Keep screenshots and
exported runs as a fallback if the browser runtime cannot load during
the evaluation.</p>
<h1 id="saving-replay-and-common-problems">Saving, replay and common
problems</h1>
<h2 id="save-the-experiment-not-just-a-picture">Save the experiment, not
just a picture</h2>
<p><strong>Save Designer project</strong> stores graph, positions, model
revision and run settings in <code>.prabha.json</code>. <strong>Export
engine netlist</strong> preserves the original plain netlist format;
settings are supplied separately. <strong>Export reproducible
run</strong> includes request, result, metadata, warnings, sampled
probes and full-simulation final values. A graph run can be replayed by
supplying its recorded <code>request</code> to the shared dispatcher.
Large plots alone do not preserve enough context.</p>
<p><strong>Plot ZIP</strong> depends on its optional JSZip CDN. JSON
export remains useful if that dependency is unavailable. Record the Git
commit, Python/NumPy versions, operating environment, model revision,
graph, parameter values, seeds and any comparison tolerance with an
experiment.</p>
<h2 id="troubleshooting-table">Troubleshooting table</h2>
<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Observation</th>
<th style="text-align: left;">Interpretation and next check</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">Both x and w used to show x</td>
<td style="text-align: left;">Display renderer reused a generic source
symbol; apply this patch</td>
</tr>
<tr class="even">
<td style="text-align: left;">Phase control disabled on ADC</td>
<td style="text-align: left;">Correct: choose an optical probe to
inspect phase</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Phase wanders; power is constant</td>
<td style="text-align: left;">Expected for phase-only noise and direct
detection</td>
</tr>
<tr class="even">
<td style="text-align: left;">ADC range error</td>
<td style="text-align: left;">Inspect upstream range; change intended
range or explicitly enable clipping</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Digital source error</td>
<td style="text-align: left;">Codes must be nonnegative integers within
the receiving DAC’s bit range</td>
</tr>
<tr class="even">
<td style="text-align: left;">Source/laser size or fs mismatch</td>
<td style="text-align: left;">Match rate × samples/symbol to laser fs
and check duration</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Run has unused-output warnings</td>
<td style="text-align: left;">Probe outputs may legitimately be unused;
read errors separately</td>
</tr>
<tr class="even">
<td style="text-align: left;">Results disappear after editing</td>
<td style="text-align: left;">Correct: stale results are
invalidated</td>
</tr>
<tr class="odd">
<td style="text-align: left;">A saved old graph differs from B22</td>
<td style="text-align: left;">Check legacy/current profile and
activation/converter ordering</td>
</tr>
<tr class="even">
<td style="text-align: left;">Negative laser power error</td>
<td style="text-align: left;">Gaussian RIN regime is invalid for that
realization; inspect density, fs and model suitability</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Docs/frontend show old content</td>
<td style="text-align: left;">Rebuild Python/web assets before Vite;
deploy the new commit and refresh</td>
</tr>
<tr class="even">
<td style="text-align: left;">No favicon / test-client warning</td>
<td style="text-align: left;">Cosmetic or dependency warning;
distinguish from failed tests</td>
</tr>
</tbody>
</table>
<p>The graph is feed-forward; a feedback loop is rejected. Do not
connect a capacitor output back into the graph and expect a general
circuit differential-equation solver. The present sample/state models
operate within a directed acyclic block schedule.</p>
<h1 id="research-contribution-novelty-and-next-evidence">Research
contribution, novelty and next evidence</h1>
<h2 id="defensible-contribution-now">Defensible contribution now</h2>
<p>Prabha’s implemented contribution is a specification-first,
inspectable workflow linking mixed optical/electrical models to a
numerical neuron and ANN reference, with saved experiments and a shared
Python execution path. The current Designer integration makes the
established component models accessible through explicit blocks. This is
substantive software engineering and reproducibility work.</p>
<p>That does not establish priority for optical neural computation,
photonic circuit simulation, component libraries, balanced detection,
converter-aware models or graphical composition. Simphony, Photontorch
and SAX provide important related simulation capabilities.
Lightening-Transformer and LightCode establish prior photonic
transformer and hybrid compilation work. The accompanying research paper
compares these scopes without claiming a performance win over them.</p>
<p>A targeted public literature review was performed on 30 September
2026. It is not an exhaustive priority or patent search. No published
head-to-head simulator benchmark, external user study or calibrated
hardware validation was found in the supplied Prabha evidence. Absence
of those results should not be replaced by an unsupported “first”
claim.</p>
<h2 id="a-useful-claim-table">A useful claim table</h2>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Claim</th>
<th style="text-align: left;">Present assessment</th>
<th style="text-align: left;">Evidence still needed</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">Reproducible small-network simulation</td>
<td style="text-align: left;">Supported within stated scope</td>
<td style="text-align: left;">Broader boundary/seed/size coverage</td>
</tr>
<tr class="even">
<td style="text-align: left;">Common current component logic across UI
transports</td>
<td style="text-align: left;">Implemented and tested in the
prototype</td>
<td style="text-align: left;">Continued cross-environment
regression</td>
</tr>
<tr class="odd">
<td style="text-align: left;">General C++/Python equivalence</td>
<td style="text-align: left;">Not established</td>
<td style="text-align: left;">Port and test all current kernels and
ANN</td>
</tr>
<tr class="even">
<td style="text-align: left;">New photonic device or activation
physics</td>
<td style="text-align: left;">Not established</td>
<td style="text-align: left;">A distinct model, calibration and
comparison</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Faster or more accurate simulator than
prior tools</td>
<td style="text-align: left;">Not established</td>
<td style="text-align: left;">Matched model/workload/tolerance
benchmarks</td>
</tr>
<tr class="even">
<td style="text-align: left;">Token-friendly LLM accelerator
advantage</td>
<td style="text-align: left;">Research hypothesis</td>
<td style="text-align: left;">Transformer mapping, traces, full costs,
quality and baselines</td>
</tr>
</tbody>
</table>
<p>For a software-introduction publication, organize the manuscript
around the research need, design, implementation, illustrative use,
reproducibility, validation and limitations. A software paper can be
valuable without inventing new optics. JOSS is a short software-article
venue with explicit software maturity and research-use requirements;
check its current author guidance and eligibility before adapting the
longer manuscript. The supplied full paper is a journal-neutral working
draft, not a claim of submission readiness or acceptance.</p>
<h2 id="priority-after-this-pause">Priority after this pause</h2>
<p>First reproduce the manual’s examples and explain every conversion.
Then freeze a reviewed release with a commit/tag and archived evidence.
Add calibrated models or a carefully scoped CNN primitive only after
this baseline is understood. A token-level accelerator study is a
separate research project: define a transformer workload, model
conversions/memory/residency/calibration, compare an optimized
electronic baseline, and report conditions where optical placement loses
as well as where it helps.</p>
<h1 id="open-source-distribution-and-possible-services">Open-source
distribution and possible services</h1>
<p>The repository includes an MIT licence. Retain its notices in
distributed source and verify provenance/licensing of additional assets
before adding them. The public research prototype can use its configured
GitHub Pages address initially. Its community links are the forum <a
href="https://prabhacommunity5701.flarum.cloud/"
class="uri">https://prabhacommunity5701.flarum.cloud/</a> and Discord <a
href="https://discord.gg/RUdRMHBFp"
class="uri">https://discord.gg/RUdRMHBFp</a>.</p>
<p>Use the forum for reproducible questions, model discussions and
showcase write-ups; use Discord for quick conversation, with durable
conclusions moved into documentation or issues. A helpful bug report
contains a minimal saved graph, settings, expected/actual result and
version. Label evidence as simulation, archived experiment or hardware
measurement.</p>
<p>The desktop wrapper is scaffolded; native Windows, macOS and Linux
installer builds and installation checks are still release gates. A
working Python sidecar alone is insufficient to advertise all three
desktop applications as verified releases. A custom domain is optional;
it does not improve scientific validation or require a change of compute
architecture.</p>
<p>Possible services after the prototype is stable are guided setup for
a lab/course, teaching workshops, model integration with documented
tests, reproducibility audits and maintenance/support arrangements.
These are proposed offerings, not existing customers or capabilities
already delivered. Begin with one clearly bounded pilot and publish its
acceptance criteria. A calibrated device-model service needs measured
data and expertise; an accelerator-performance service needs system
benchmarks. Avoid promising hardware speedups or reliability guarantees
from the current ANN regression.</p>
<h1 id="questions-to-rehearse">Questions to rehearse</h1>
<p><strong>What exactly did you build?</strong> A specification-driven
behavioural simulator workflow, original cross-engine conformance tests,
Python component/neuronal experiments, a fixed ANN regression and an
accessible interface exposing current models and reproducible runs.</p>
<p><strong>Where is the optical computation?</strong> Intensity
encoding, optical power splitting and ideal signed weight transmissions
form the products. Balanced photodetection converts the branch
difference to a signed current. Integration, gain/bias, activation and
conversion complete the electronic path.</p>
<p><strong>Why inverse encoding?</strong> The MZM’s cosine-squared
transfer is nonlinear. Inverting a chosen ideal branch makes requested
normalized intensity approximately linear in x before quantization and
loss. It does not remove every physical nonideality.</p>
<p><strong>Why are there two detectors?</strong> Each optical power is
nonnegative. Their difference represents a signed product without
assigning negative optical intensity.</p>
<p><strong>What makes the neuron nonlinear?</strong> MZM transfer is
nonlinear physically in its drive; inverse encoding compensates its
intended encoding. The separate activation supplies the neural
nonlinearity. Converter steps and clipping are other nonlinear effects
with different purposes.</p>
<p><strong>Can phase noise change the output?</strong> It can in a
coherent/interferometric system, but this current direct-detection chain
does not implement that coupling. Its phase display must not be mistaken
for proof of coherent computation.</p>
<p><strong>Does 43 passing tests prove the model?</strong> It supports
the tested software behaviours. Physical validity needs appropriate
assumptions and comparisons with measured or trusted reference data.</p>
<p><strong>Is zero winner mismatch an accuracy result?</strong> It is
agreement of the two-output ordering with a fixed mathematical reference
across 100 synthetic vectors, not a labelled task score.</p>
<p><strong>Why call the result validated?</strong> Because the defined
implementation was compared with explicit references under a documented
protocol. Always state that boundary rather than implying universal
validation.</p>
<p><strong>Is Prabha novel?</strong> The demonstrated contribution is
the concrete integrated software workflow and its reproducible
validation. Broad optics/simulator concepts have prior art. A strong
scientific novelty claim requires a sharper comparison and additional
evidence.</p>
<p><strong>Did the internship already implement the later ANN?</strong>
Keep the chronology explicit: the internship presentation covers device
studies and simulator foundations; later component integration and ANN
validation belong to subsequent BTP progress.</p>
<p><strong>What would make the next paper stronger?</strong> A released
version with independent reproduction, a clear related-work comparison,
calibrated model evidence, more systematic coverage and a demonstration
of a research question enabled by the software.</p>
<h1 id="references-and-source-record">References and source record</h1>
<p>The project source, supplied BTP master report, internship foundation
report, microring study, architecture decisions and archived CSVs are
the primary sources for Prabha-specific claims in this manual. The
revised manuscripts include fuller bibliographies.</p>
<ul>
<li>Ploeg, Gunther and Camacho. <em>Simphony: An open-source photonic
integrated circuit simulation framework</em>. <a
href="https://arxiv.org/abs/2009.05146"
class="uri">https://arxiv.org/abs/2009.05146</a>.</li>
<li>Laporte, Dambre and Bienstman. <em>Highly parallel simulation and
optimization of photonic circuits in time and frequency domain based on
the deep-learning framework PyTorch</em>. Scientific Reports 9, 5918
(2019). <a href="https://doi.org/10.1038/s41598-019-42408-2"
class="uri">https://doi.org/10.1038/s41598-019-42408-2</a>.</li>
<li>SAX project documentation. <a
href="https://gdsfactory.github.io/sax/"
class="uri">https://gdsfactory.github.io/sax/</a>.</li>
<li>Zhu et al. <em>Lightening-Transformer</em>. <a
href="https://arxiv.org/abs/2305.19533"
class="uri">https://arxiv.org/abs/2305.19533</a>.</li>
<li>Tomich, Zhong and Englund. <em>LightCode: Compiling LLM Inference
for Photonic-Electronic Systems</em>. <a
href="https://arxiv.org/abs/2509.16443"
class="uri">https://arxiv.org/abs/2509.16443</a>.</li>
<li>JOSS author guidance. <a
href="https://joss.readthedocs.io/en/latest/submitting.html"
class="uri">https://joss.readthedocs.io/en/latest/submitting.html</a>
(checked 30 September 2026).</li>
</ul>
<p>This revision used AI assistance for source inspection, drafting,
literature retrieval, code clarification and document preparation. The
project author should verify the text, figures, authorship,
acknowledgements and venue-specific disclosure before submission. No
paper has been submitted by this review.</p>
<h1 id="current-block-catalogue">Current block catalogue</h1>
<p>The following interfaces/defaults are extracted from the reviewed
block definitions. Values are defaults for a newly added block, not a
guarantee that every example uses them. The earlier mathematics chapters
explain the model equations and approximations. Ports labelled voltage
can carry normalized controls where explicitly stated. All current
blocks operate on sampled time-domain signals.</p>
<h2 id="nonlinear-activation">Nonlinear activation</h2>
<p><code>model_activation</code> · <code>ComponentActivation</code></p>
<p>Uses Activation.activate. Sigmoid, tanh, ReLU and linear; sigmoid
argument clipped to ±60 for numerical stability. Behavioral output is
represented on a normalized 1 V scale; this is not a transistor-level
device model. B22 places activation BEFORE ADC.</p>
<p>Inputs: <code>in</code> (voltage). Outputs: <code>out</code>
(voltage).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>kind</code></td>
<td style="text-align: left;">sigmoid</td>
<td style="text-align: left;">Behavioral transfer function. Options:
sigmoid, tanh, relu, linear.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>gain</code></td>
<td style="text-align: left;">1.0</td>
<td style="text-align: left;">Pre-activation scaling. Allowed: -1e+06 to
1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>threshold_V</code></td>
<td style="text-align: left;">0.0 V</td>
<td style="text-align: left;">Shift: z=gain × (Vin−threshold). Allowed:
-1e+06 to 1e+06.</td>
</tr>
</tbody>
</table>
<h2 id="adc">ADC</h2>
<p><code>model_adc</code> · <code>ComponentADC</code></p>
<p>Uses ADC.convert/code_to_voltage. code is the actual integer code;
voltage is the reconstructed quantized value. Range errors are visible
unless clipping is explicitly enabled. No jitter, INL or DNL model.</p>
<p>Inputs: <code>in</code> (voltage). Outputs: <code>code</code>
(digital), <code>voltage</code> (voltage).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>bits</code></td>
<td style="text-align: left;">12</td>
<td style="text-align: left;">Integer resolution; nearest code, NumPy
ties-to-even. Allowed: 1 to 16.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>v_min</code></td>
<td style="text-align: left;">0.0 V</td>
<td style="text-align: left;">Lower conversion endpoint. Allowed: -1e+06
to 1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>v_max</code></td>
<td style="text-align: left;">1.0 V</td>
<td style="text-align: left;">Upper conversion endpoint. Allowed: -1e+06
to 1e+06.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>clip</code></td>
<td style="text-align: left;">false</td>
<td style="text-align: left;">False rejects out-of-range commands; true
explicitly clips to converter rails.</td>
</tr>
</tbody>
</table>
<h2 id="voltage-amplifier">Voltage amplifier</h2>
<p><code>model_amplifier</code> · <code>ComponentAmplifier</code></p>
<p>Uses Amplifier.amplify: gain × Vin + offset, followed by enabled rail
limits. No bandwidth, slew-rate or amplifier noise beyond the separately
modeled TIA.</p>
<p>Inputs: <code>in</code> (voltage). Outputs: <code>out</code>
(voltage).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>gain</code></td>
<td style="text-align: left;">2.0</td>
<td style="text-align: left;">Voltage gain. Allowed: -1e+06 to
1e+06.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>offset_V</code></td>
<td style="text-align: left;">0.2 V</td>
<td style="text-align: left;">Additive bias after gain. Allowed: -1e+06
to 1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>lower_rail_enabled</code></td>
<td style="text-align: left;">false</td>
<td style="text-align: left;">Enable lower-rail saturation.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>v_min</code></td>
<td style="text-align: left;">-1.0 V</td>
<td style="text-align: left;">Lower output rail; must be below upper
rail if both enabled. Allowed: -1e+06 to 1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>upper_rail_enabled</code></td>
<td style="text-align: left;">false</td>
<td style="text-align: left;">Enable upper-rail saturation.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>v_max</code></td>
<td style="text-align: left;">1.0 V</td>
<td style="text-align: left;">Upper output rail. Allowed: -1e+06 to
1e+06.</td>
</tr>
</tbody>
</table>
<h2 id="balanced-current-subtraction">Balanced current subtraction</h2>
<p><code>model_balance</code> · <code>ComponentBalance</code></p>
<p>Iout=Iupper−Ilower. Each photodetector has its own noise stream. No
extra subtractor noise or hidden gain.</p>
<p>Inputs: <code>upper</code> (current), <code>lower</code> (current).
Outputs: <code>out</code> (current).</p>
<p>No editable parameters.</p>
<h2 id="capacitor-integrator">Capacitor integrator</h2>
<p><code>model_capacitor</code> · <code>ComponentCapacitor</code></p>
<p>Uses Capacitor.integrate_current with dt=1/fs. Output sample k is
voltage AFTER interval k; first sample includes one integration step.
Without leakage: V+=I dt/C. With leakage: Vnew=Vold
exp(−dt/RC)+IR(1−exp(−dt/RC)). No kT/C reset noise.</p>
<p>Inputs: <code>in</code> (current). Outputs: <code>out</code>
(voltage).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>capacitance_pF</code></td>
<td style="text-align: left;">1.0 pF</td>
<td style="text-align: left;">Charge storage capacitance. Allowed: 1e-12
to 1e+12.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>initial_V</code></td>
<td style="text-align: left;">0.0 V</td>
<td style="text-align: left;">Initial voltage; resets at start of every
run. Allowed: -1e+06 to 1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>leakage_enabled</code></td>
<td style="text-align: left;">false</td>
<td style="text-align: left;">Use finite RC leakage; deterministic even
with noise off.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>leakage_ohm</code></td>
<td style="text-align: left;">1000000.0 ohm</td>
<td style="text-align: left;">Leakage resistance; exact constant-current
RC solution per sample. Allowed: 1e-09 to 1e+20.</td>
</tr>
</tbody>
</table>
<h2 id="digital-code-source">Digital code source</h2>
<p><code>model_code_source</code> · <code>ComponentSource</code></p>
<p>Time-domain sequence of nonnegative integer codes. Connect to a
code-to-voltage DAC with sufficient resolution. No source noise is
invented.</p>
<p>Inputs: none. Outputs: <code>out</code> (digital).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>values</code></td>
<td style="text-align: left;">0,1024,2048,4095</td>
<td style="text-align: left;">Comma-separated samples held for sps
steps; final value is held until run end.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>rate</code></td>
<td style="text-align: left;">1.0 GHz</td>
<td style="text-align: left;">Symbol rate. fs = rate × 10^9 × sps. Set
all connected sources to the same fs. Allowed: 1e-12 to 1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>sps</code></td>
<td style="text-align: left;">16</td>
<td style="text-align: left;">Integer samples per symbol. Allowed: 1 to
256.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>kind</code></td>
<td style="text-align: left;">digital</td>
<td style="text-align: left;">Fixed port type for this source
definition. Options: digital.</td>
</tr>
</tbody>
</table>
<h2 id="current-source">Current source</h2>
<p><code>model_current_source</code> · <code>ComponentSource</code></p>
<p>Time-domain current sequence in amperes. Connect to a capacitor or
TIA. No source noise is invented.</p>
<p>Inputs: none. Outputs: <code>out</code> (current).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>values</code></td>
<td style="text-align: left;">0.9,0.3,0.7,0.5</td>
<td style="text-align: left;">Comma-separated samples held for sps
steps; final value is held until run end.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>rate</code></td>
<td style="text-align: left;">1.0 GHz</td>
<td style="text-align: left;">Symbol rate. fs = rate × 10^9 × sps. Set
all connected sources to the same fs. Allowed: 1e-12 to 1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>sps</code></td>
<td style="text-align: left;">16</td>
<td style="text-align: left;">Integer samples per symbol. Allowed: 1 to
256.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>kind</code></td>
<td style="text-align: left;">current</td>
<td style="text-align: left;">Fixed port type for this source
definition. Options: current.</td>
</tr>
</tbody>
</table>
<h2 id="dac-codes-to-voltage">DAC: codes to voltage</h2>
<p><code>model_dac</code> · <code>ComponentDAC</code></p>
<p>Uses DAC.code_to_voltage. Input must contain integer codes in
[0,2^bits−1]; output is volts. Use the command quantizer when starting
from a requested analog voltage.</p>
<p>Inputs: <code>code</code> (digital). Outputs: <code>out</code>
(voltage).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>bits</code></td>
<td style="text-align: left;">12</td>
<td style="text-align: left;">Integer converter resolution. Allowed: 1
to 16.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>v_min</code></td>
<td style="text-align: left;">-0.5 V</td>
<td style="text-align: left;">Converter lower endpoint. Must be less
than v_max. Allowed: -1e+06 to 1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>v_max</code></td>
<td style="text-align: left;">0.5 V</td>
<td style="text-align: left;">Converter upper endpoint. Allowed: -1e+06
to 1e+06.</td>
</tr>
</tbody>
</table>
<h2 id="dac-command-quantizer">DAC command quantizer</h2>
<p><code>model_dac_quantizer</code> ·
<code>ComponentDACQuantizer</code></p>
<p>Uses DAC.quantize from converter experiments: requested analog
command → integer code and quantized voltage.
LSB=(v_max−v_min)/(2^bits−1). No jitter, DNL or INL model.</p>
<p>Inputs: <code>in</code> (voltage). Outputs: <code>out</code>
(voltage), <code>code</code> (digital).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>bits</code></td>
<td style="text-align: left;">12</td>
<td style="text-align: left;">Integer resolution; rounds to nearest code
with NumPy ties-to-even. Allowed: 1 to 16.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>v_min</code></td>
<td style="text-align: left;">-0.5 V</td>
<td style="text-align: left;">Converter lower endpoint. Must be less
than v_max. Allowed: -1e+06 to 1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>v_max</code></td>
<td style="text-align: left;">0.5 V</td>
<td style="text-align: left;">Converter upper endpoint. Allowed: -1e+06
to 1e+06.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>clip</code></td>
<td style="text-align: left;">false</td>
<td style="text-align: left;">False rejects out-of-range commands; true
explicitly clips to converter rails.</td>
</tr>
</tbody>
</table>
<h2 id="inverse-mzm-encoder">Inverse MZM encoder</h2>
<p><code>model_encoder</code> · <code>ComponentEncoder</code></p>
<p>Calibration helper: x in [0,1] → V=(2Vpi/π)[acos(sqrt(x))−bias/2]. It
inverts ideal normalized transmission before insertion loss. Match its
parameters to the MZM.</p>
<p>Inputs: <code>x</code> (voltage). Outputs: <code>out</code>
(voltage).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>v_pi</code></td>
<td style="text-align: left;">1.0 V</td>
<td style="text-align: left;">MZM half-wave voltage. Allowed: 1e-09 to
1000.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>bias_rad</code></td>
<td style="text-align: left;">1.5707963268 rad</td>
<td style="text-align: left;">Differential bias phase; transfer uses
bias_rad / 2. Allowed: -100 to 100.</td>
</tr>
</tbody>
</table>
<h2 id="cw-laser">CW laser</h2>
<p><code>model_laser</code> · <code>ComponentLaser</code></p>
<p>Uses experiments’ CWLaser complex envelope. RIN and phase noise have
separate switches. Optical probes include power and unwrapped phase; no
phase-to-intensity conversion is assumed.</p>
<p>Inputs: none. Outputs: <code>out</code> (optical).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>power_mW</code></td>
<td style="text-align: left;">1.0 mW</td>
<td style="text-align: left;">Mean optical power. Allowed: 0 to
10000.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>wavelength_nm</code></td>
<td style="text-align: left;">1550.0 nm</td>
<td style="text-align: left;">Carrier wavelength; optical metadata, not
sampled carrier oscillation. Allowed: 1 to 1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>fs</code></td>
<td style="text-align: left;">16000000000.0 Hz</td>
<td style="text-align: left;">Sample rate; match rate × 10^9 × sps of
electrical sources. Allowed: 1e-06 to 1e+15.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>phase_rad</code></td>
<td style="text-align: left;">0.0 rad</td>
<td style="text-align: left;">Initial envelope phase. Allowed: -1e+06 to
1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>rin_enabled</code></td>
<td style="text-align: left;">true</td>
<td style="text-align: left;">Enables laser intensity fluctuations only
with global noise on.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>rin_db_hz</code></td>
<td style="text-align: left;">-150.0 dB/Hz</td>
<td style="text-align: left;">One-sided RIN density. Linearized Gaussian
power model; invalid negative-power realizations are rejected. Allowed:
-300 to -60.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>linewidth_enabled</code></td>
<td style="text-align: left;">true</td>
<td style="text-align: left;">Enables phase diffusion only with global
noise on.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>linewidth_hz</code></td>
<td style="text-align: left;">1000000.0 Hz</td>
<td style="text-align: left;">Lorentzian linewidth: phase-increment
variance 2π linewidth/fs. Direct power detection is phase insensitive.
Allowed: 0 to 1e+12.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>seed</code></td>
<td style="text-align: left;">0</td>
<td style="text-align: left;">Block seed offset. Combined with run seed
and instance ID; integer 0..2^32-1. Allowed: 0 to 4.29497e+09.</td>
</tr>
</tbody>
</table>
<h2 id="photonic-mac-component-models">Photonic MAC (component
models)</h2>
<p><code>model_mac</code> · <code>ComponentMAC</code></p>
<p>Compact encoder → DAC → nonlinear MZM → split → ideal signed weight
transmissions → independent photodetectors → current subtraction.
External laser preserves explicit power/noise wiring. x∈[0,1], w∈[−1,1]
use dimensionless values on voltage ports. Outputs are time samples, not
an automatic vector sum; integrate over the intended symbol duration.
Expand using the component-chain example to inspect every stage.</p>
<p>Inputs: <code>light</code> (optical), <code>x</code> (voltage),
<code>w</code> (voltage). Outputs: <code>out</code> (current),
<code>drive</code> (voltage).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>v_pi</code></td>
<td style="text-align: left;">1.0 V</td>
<td style="text-align: left;">MZM half-wave voltage. Allowed: 1e-09 to
1000.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>bias_rad</code></td>
<td style="text-align: left;">1.5707963268 rad</td>
<td style="text-align: left;">Differential bias phase; transfer uses
bias_rad / 2. Allowed: -100 to 100.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>loss_dB</code></td>
<td style="text-align: left;">0.0 dB</td>
<td style="text-align: left;">Deterministic insertion loss; remains
active with noise off. Allowed: 0 to 200.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>dac_bits</code></td>
<td style="text-align: left;">12</td>
<td style="text-align: left;">Input DAC integer resolution. Allowed: 1
to 16.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>v_min</code></td>
<td style="text-align: left;">-0.5 V</td>
<td style="text-align: left;">Converter lower endpoint. Must be less
than v_max. Allowed: -1e+06 to 1e+06.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>v_max</code></td>
<td style="text-align: left;">0.5 V</td>
<td style="text-align: left;">Converter upper endpoint. Allowed: -1e+06
to 1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>clip</code></td>
<td style="text-align: left;">false</td>
<td style="text-align: left;">False rejects out-of-range commands; true
explicitly clips to converter rails.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>ratio</code></td>
<td style="text-align: left;">0.5</td>
<td style="text-align: left;">Fraction of incident power in upper arm.
Allowed: 0 to 1.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>responsivity</code></td>
<td style="text-align: left;">1.0 A/W</td>
<td style="text-align: left;">Photocurrent per watt of incident optical
power. Allowed: 0 to 100.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>dark_enabled</code></td>
<td style="text-align: left;">true</td>
<td style="text-align: left;">Adds deterministic dark current even when
global noise is off.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>dark_current_A</code></td>
<td style="text-align: left;">0.0 A</td>
<td style="text-align: left;">Mean dark current, included in shot-noise
variance when enabled. Allowed: 0 to 1.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>shot_enabled</code></td>
<td style="text-align: left;">true</td>
<td style="text-align: left;">Global noise AND this switch enable white
Gaussian shot noise, variance 2 q Imean fs/2.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>seed</code></td>
<td style="text-align: left;">0</td>
<td style="text-align: left;">Block seed offset. Combined with run seed
and instance ID; integer 0..2^32-1. Allowed: 0 to 4.29497e+09.</td>
</tr>
</tbody>
</table>
<h2 id="machzehnder-modulator">Mach–Zehnder modulator</h2>
<p><code>model_mzm</code> · <code>ComponentMZM</code></p>
<p>Nonlinear power transfer T=cos²(πV/(2Vpi)+bias/2) × 10^(−loss/10).
Uses MachZehnderModulator.transfer. Envelope phase is passed through;
modulator chirp and coherent field sign are not modeled.</p>
<p>Inputs: <code>light</code> (optical), <code>drive</code> (voltage).
Outputs: <code>out</code> (optical).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>v_pi</code></td>
<td style="text-align: left;">1.0 V</td>
<td style="text-align: left;">MZM half-wave voltage. Allowed: 1e-09 to
1000.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>bias_rad</code></td>
<td style="text-align: left;">1.5707963268 rad</td>
<td style="text-align: left;">Differential bias phase; transfer uses
bias_rad / 2. Allowed: -100 to 100.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>loss_dB</code></td>
<td style="text-align: left;">0.0 dB</td>
<td style="text-align: left;">Deterministic insertion loss; remains
active with noise off. Allowed: 0 to 200.</td>
</tr>
</tbody>
</table>
<h2 id="photodetector">Photodetector</h2>
<p><code>model_pd</code> · <code>ComponentPD</code></p>
<p>Uses Photodetector.detect_white_shot: I=R|E|²+Idark, white-shot
variance=2q Imean fs/2. Single optical channel. Receiver filtering/noise
is handled explicitly by TIA; no automatic load-thermal term is
added.</p>
<p>Inputs: <code>in</code> (optical). Outputs: <code>out</code>
(current).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>responsivity</code></td>
<td style="text-align: left;">1.0 A/W</td>
<td style="text-align: left;">Photocurrent per watt of incident optical
power. Allowed: 0 to 100.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>dark_enabled</code></td>
<td style="text-align: left;">true</td>
<td style="text-align: left;">Adds deterministic dark current even when
global noise is off.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>dark_current_A</code></td>
<td style="text-align: left;">0.0 A</td>
<td style="text-align: left;">Mean dark current, included in shot-noise
variance when enabled. Allowed: 0 to 1.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>shot_enabled</code></td>
<td style="text-align: left;">true</td>
<td style="text-align: left;">Global noise AND this switch enable white
Gaussian shot noise, variance 2 q Imean fs/2.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>seed</code></td>
<td style="text-align: left;">0</td>
<td style="text-align: left;">Block seed offset. Combined with run seed
and instance ID; integer 0..2^32-1. Allowed: 0 to 4.29497e+09.</td>
</tr>
</tbody>
</table>
<h2 id="voltage-normalized-source">Voltage / normalized source</h2>
<p><code>model_source</code> · <code>ComponentSource</code></p>
<p>Time-domain voltage sequence. Normalized x and signed w may use the
voltage transport; these control values are dimensionless by convention.
No source noise is invented.</p>
<p>Inputs: none. Outputs: <code>out</code> (voltage).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>values</code></td>
<td style="text-align: left;">0.9,0.3,0.7,0.5</td>
<td style="text-align: left;">Comma-separated samples held for sps
steps; final value is held until run end.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>rate</code></td>
<td style="text-align: left;">1.0 GHz</td>
<td style="text-align: left;">Symbol rate. fs = rate × 10^9 × sps. Set
all connected sources to the same fs. Allowed: 1e-12 to 1e+06.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>sps</code></td>
<td style="text-align: left;">16</td>
<td style="text-align: left;">Integer samples per symbol. Allowed: 1 to
256.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>kind</code></td>
<td style="text-align: left;">voltage</td>
<td style="text-align: left;">Fixed port type for this source
definition. Options: voltage.</td>
</tr>
</tbody>
</table>
<h2 id="optical-splitter">Optical splitter</h2>
<p><code>model_splitter</code> · <code>ComponentSplitter</code></p>
<p>Power-conserving split before explicit insertion loss. Envelopes
scale by square roots of branch power ratios. No additional fabrication
or coupling model.</p>
<p>Inputs: <code>in</code> (optical). Outputs: <code>upper</code>
(optical), <code>lower</code> (optical).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>ratio</code></td>
<td style="text-align: left;">0.5</td>
<td style="text-align: left;">Fraction of incident power in upper arm.
Allowed: 0 to 1.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>loss_dB</code></td>
<td style="text-align: left;">0.0 dB</td>
<td style="text-align: left;">Deterministic insertion loss; remains
active with noise off. Allowed: 0 to 200.</td>
</tr>
</tbody>
</table>
<h2 id="transimpedance-amplifier">Transimpedance amplifier</h2>
<p><code>model_tia</code> · <code>ComponentTIA</code></p>
<p>Uses TIA.amplify. Noise is added before gain and finite-bandwidth
filtering. Density can represent the measured receiver noise budget; no
implicit second thermal-noise source. No TIA saturation model.</p>
<p>Inputs: <code>in</code> (current). Outputs: <code>out</code>
(voltage).</p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Parameter</th>
<th style="text-align: left;">Default / unit</th>
<th style="text-align: left;">Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;"><code>resistance_ohm</code></td>
<td style="text-align: left;">1000.0 ohm</td>
<td style="text-align: left;">Transimpedance gain. Allowed: 1e-09 to
1e+12.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>bandwidth_enabled</code></td>
<td style="text-align: left;">true</td>
<td style="text-align: left;">Apply the established first-order
backward-Euler low-pass.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>bandwidth_Hz</code></td>
<td style="text-align: left;">1000000000.0 Hz</td>
<td style="text-align: left;">Nominal analog −3 dB bandwidth; discrete
response depends on fs. First output equals first input × gain. Allowed:
1e-09 to 1e+15.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>noise_enabled</code></td>
<td style="text-align: left;">true</td>
<td style="text-align: left;">Global noise AND this switch enable
input-referred white current noise.</td>
</tr>
<tr class="odd">
<td style="text-align: left;"><code>noise_A_sqrtHz</code></td>
<td style="text-align: left;">1e-12 A/√Hz</td>
<td style="text-align: left;">User-specified total input current noise
density; variance before filtering is density² fs/2. Allowed: 0 to
1.</td>
</tr>
<tr class="even">
<td style="text-align: left;"><code>seed</code></td>
<td style="text-align: left;">0</td>
<td style="text-align: left;">Block seed offset. Combined with run seed
and instance ID; integer 0..2^32-1. Allowed: 0 to 4.29497e+09.</td>
</tr>
</tbody>
</table>
<h2 id="power-transmission-control">Power transmission control</h2>
<p><code>model_transmission</code> ·
<code>ComponentTransmission</code></p>
<p>Ideal weight attenuation: Eout=Ein sqrt(t), 0≤t≤1. Control uses a
voltage-kind port as a dimensionless transmission command. This is not a
voltage-driven nonlinear MZM.</p>
<p>Inputs: <code>light</code> (optical), <code>transmission</code>
(voltage). Outputs: <code>out</code> (optical).</p>
<p>No editable parameters.</p>
<h2 id="signed-weight-encoder">Signed weight encoder</h2>
<p><code>model_weights</code> · <code>ComponentWeights</code></p>
<p>Dimensionless signed w in [−1,1] becomes t+=(1+w)/2 and t−=(1−w)/2.
Ideal weight settings; no weight DAC or drift model has been
validated.</p>
<p>Inputs: <code>in</code> (voltage). Outputs: <code>upper</code>
(voltage), <code>lower</code> (voltage).</p>
<p>No editable parameters.</p>
