# Interactive Entropy and Information Gain

**Information Entropy** measures how unpredictable/mixed a dataset is:

- **Low entropy** (close to 0): Dataset is pure (all one class)
- **High entropy** (close to log₂(# of classes)): Dataset is well-mixed

**Information Gain** measures how much we reduce entropy with a split:

- **Higher gain** = Better split (we removed more uncertainty)
- **Lower gain** = Worse split (didn't help much)

Decision Trees choose splits that **maximize Information Gain** to build effective classifiers!

## Try These Experiments

1. Set all points to one color
2. Split with all points on one side - notice information gain = 0 
3. Create a perfect split where each side has only one color - maximum gain!

<iframe
  src="https://marimo.app/l/onhftz?show-code=false&embed=true"
  width="100%"
  height="800px"
  frameborder="0"
  style="min-height: 800px; height: 100vh;"
></iframe>

## Results

1. Notice that you can't split pure data to gain anything - there's no uncertainty left to remove!

- entropy before = 0
- entropy after = 0
- information gain = 0

2. Useless Split. If the split doesn't actually separate the classes, you've gained nothing. The entropy stays exactly the same because all points remain mixed together on one side. This teaches you that Decision Trees must be strategic about WHERE they split

- entropy before = 1.0
- entropy after = 1.0 (unchanged!)
- information gain = 0

3. This is the goal! You went from maximum confusion (mixed colors) to zero confusion (pure branches)

- entropy before = 1.0 (maximum confusion for 2 classes)
- entropy after = 0 (both branches pure!)
- information gain = 1.0 (maximum possible!)
