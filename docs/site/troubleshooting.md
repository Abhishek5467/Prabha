# Troubleshooting

## Python is still loading

The first static-site run downloads Pyodide, NumPy and JSON Schema from jsDelivr. The top bar reports progress. Keep the tab open and allow up to two minutes. If loading fails, check the connection, then run again; the failed worker is discarded.

If your institution blocks jsDelivr, use the [local Python API](quickstart.md) or a tested desktop package. No browser security setting needs to be disabled.

## Results disappeared after editing a setting

Results belong to the request that produced them. Run again after changing inputs, precision, coefficients or lab controls. Export JSON before reloading or navigating away to keep a run.

## The batch does not match the archived numbers

Select **Reset reference**, then **Validate 100 inputs**. Use 12-bit converters, default coefficients, 100 samples and seed 12345. Expected RMS is about 7.8644e-5, maximum error 1.7828e-4 and 0/100 ordering mismatches.

Custom precision or weights change the batch. The four input sliders affect single inference, not the random batch. Single-run errors need not equal batch errors. The graph designer is a separate numerical path; see [model scope](model-scope.md).

## Import rejected

Import a settings file or ANN run JSON exported by the new Studio. Result-only JSON from an older preview lacks the complete configuration. CSV, neuron runs, component runs and designer files are not ANN imports. Designer files open in the designer.

Check that the JSON is below 256 KB and contains finite numeric values, a 4–3–2 network, and integer converter resolutions from 3 to 16.

## Local API cannot be reached

Run the server from [quick start](quickstart.md) and keep its terminal open. Confirm that [API health](http://127.0.0.1:8000/api/health) responds. The Vite development proxy expects port 8000.

If the server is unavailable at startup, Studio can select Browser Python. Check the engine label to know where computation runs. Refresh after restoring the server to select the local API.

## GitHub Pages still shows the old version

Push your changed files, then open **Actions → Publish web preview → Run workflow** on the updated branch. Start a **new run**: re-running an old workflow keeps its original commit. **Validate prototype** checks code but does not deploy.

Confirm the new run succeeds, refresh without cache, and check the footer version. See [deployment](deployment.md).

## Docs, images or Python bundle return 404

Run `python scripts/build_web_assets.py` before `npm run build --prefix frontend/studio`. Deploy the complete `frontend/studio/dist` folder, including assets. Keep the relative Vite base so a project URL such as `/Prabha/` works.

## Export did not appear

Browser downloads follow your browser settings. On desktop, choose a destination in the Save dialog; cancelling does not write a file. Desktop exports are limited to 16 MB. Use the public website for larger downloads. Permission or disk errors appear in the Studio.

## Report a problem

Use the [Help forum](https://prabhacommunity5701.flarum.cloud/) for setup questions or [GitHub issues](https://github.com/Abhishek5467/Prabha/issues) for reproducible bugs. Include OS, browser/app version, engine label, steps, error text and exported run JSON where possible.
