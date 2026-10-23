# Offline digits benchmark snapshot

`digits_8x8_split.npz` contains the 1,797 images and labels loaded by
scikit-learn's `load_digits`, plus the exact train/validation/test index arrays.
The source is the optical-recognition handwritten-digits subset maintained in
scikit-learn, not MNIST. Dataset documentation and original source attribution:
https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html

Pixels are integers 0 through 16. The script divides them by 16 with no learned
normalisation. The image-stratified split is 1,149 training, 288 validation and
360 test examples, with random seeds 20261015 and 20261016. These are local
experimental splits; they are not a writer-disjoint or official external test.

The frozen split and selected model make the reported inference reproducible
without downloading data or using scikit-learn at evaluation time. Arrays are
read using `allow_pickle=False`. Dataset/model hashes are in the result JSON.
