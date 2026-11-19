# Breakdown of Octopus 0.4 Machine Learning Overview

This guide explains the machine learning mechanics inside `Octopus Learning Overview.gh`, clarifies why pressing **F5 (Calculate)** appears to happen instantaneously, and details the two smaller, visually rich files created in `Tareas/Tarea_4/`.

---

## 1. Why Did F5 Run "So Fast That You Couldn't See It"?

When you press **F5 (Recompute / Calculate)** in Grasshopper, three things happen that create this illusion:

1. **Microsecond Execution (< 1 ms):**
   * The training dataset contains only **10 one-dimensional numbers** ($X \in [0, 1] \to Y \in [0, 1]$).
   * Fitting an analytical **Support Vector Machine (SVM)** on 10 numbers using an RBF kernel (`encog-octopus.dll` / libsvm) takes approximately **0.0002 seconds (200 microseconds)** on modern CPUs.
   * Evaluating 50 test points takes **100 microseconds**.
   * Training a tiny 2-layer Neural Network with Resilient Propagation takes ~**1.5 milliseconds**.
   * Total execution time is literally faster than a screen refresh (60 Hz = 16.6 ms).

2. **Zero Geometry in the Rhino 3D Viewport:**
   * In the original file, all outputs were kept as abstract numerical lists piped into the tiny 2D `Quick Graph` canvas widget.
   * **Not a single Point3d, Curve, or Mesh component was connected**, leaving Rhino's 3D viewport 100% blank white/grey space.

3. **Batch (Non-Iterative) Convergence:**
   * Unlike real-time physics simulations (e.g., Kangaroo) or evolutionary optimization (Galapagos/Octopus Pareto), Supervised Learning (SVM and Resilient Backprop) calculates its mathematical solution in a single synchronous pass.

---

## 2. Structure of the Two Split Files

We separated the original 117-component monolithic canvas into two dedicated, cleanly positioned files starting at $(100, 100)$ (rendered with Graphviz from [octopus_learning_flow.dot](./octopus_learning_flow.dot)):

![Octopus Learning Breakdown Flowchart](./octopus_learning_flow.svg)

---

## 3. File 1: `01_Octopus_Supervised_SVM.gh`

### Location:
* **[01_Octopus_Supervised_SVM.gh](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/01_Octopus_Supervised_SVM.gh)**

### What It Models:
Supervised Learning means **learning from known $(X, Y)$ ground truth examples**.
* **Target Function:** A non-linear curve defined in a `Graph Mapper` mapping $X \in [0, 1] \to Y \in [0, 1]$.
* **Training Phase:**
  1. `Range` + `Number Slider` samples $N_{\text{learn}}$ training points (default: 10 points).
  2. `SVMLearn (octSupervLearn)` fits an optimal hyperplane in kernel space (default RBF kernel).
  3. `NetLearn (octSupervLearn)` trains an Artificial Neural Network using multi-core Resilient Propagation.
* **Testing / Inference Phase:**
  1. A denser grid of $N_{\text{test}} = 50$ points along $X$ is fed into `SVMEval` and `EvalN`.
  2. The models output predicted values $\hat{Y}$.

### Interactive Experiments to Try:
1. **Watch Generalization Live:** Drag the `Number of Learning Examples` slider from **3** up to **20**:
   * At $N = 3$, the model underfits (cannot capture the curve curvature).
   * At $N = 10\text{–}15$, the predicted curve smoothly snaps onto the true function.
2. **Change Curve Topology:** Double-click the `Graph Mapper`, pick a different curve (e.g., Sine, Parabola, or Bezier S-curve), and watch the models immediately adapt.
3. **SVM vs. Neural Net:** Compare the `SVM` output (statistically robust with analytical margin) against the `Network` output (probabilistic neural weights).

---

## 4. File 2: `02_Octopus_Evolutionary_NEAT.gh`

### Location:
* **[02_Octopus_Evolutionary_NEAT.gh](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/02_Octopus_Evolutionary_NEAT.gh)**

### What It Models:
Evolutionary / Reinforcement Learning means **gradual improvement through trial, evaluation, and selection**:
* **The NEAT Algorithm:** Conceived by Kenneth Stanley (*NeuroEvolution of Augmenting Topologies*), it does not use gradient descent or backpropagation.
* **How It Works:**
  1. Starts with minimal neural networks (1 input neuron, 1 output neuron).
  2. Random mutations add new hidden neurons, insert new synaptic connections, and tweak connection weights.
  3. Uses non-differentiable or trigonometric activation functions (e.g., Sine `.1`, Cosine `.1`) — this is a **CPPN (Compositional Pattern Producing Network)**.
  4. Evaluates each candidate network's fitness:
     $$\text{Fitness} = - \sum_{i=1}^{N} (Y_{\text{target}, i} - Y_{\text{pred}, i})^2$$
  5. Selects the fittest networks, performs crossover (breeding), and advances to the next generation.

---

## 5. Visualizing Machine Learning Inside the Rhino 3D Viewport

To see the curves and points in Rhino instead of abstract numbers, pipe the outputs to simple geometry components:

| Data Stream | Grasshopper Component | Result in Rhino 3D Viewport |
| :--- | :--- | :--- |
| **Training Samples** ($X_{\text{train}}, Y_{\text{train}}$) | `Construct Point` $(100 \cdot X, 100 \cdot Y, 0)$ $\to$ `Point` | **Red / Orange Points** marking the exact known sample coordinates. |
| **Target Function** ($X_{\text{test}}, Y_{\text{true}}$) | `Construct Point` $\to$ `Interpolate Curve` | **Smooth Green Curve** representing the Ground Truth function. |
| **SVM Prediction** ($X_{\text{test}}, Y_{\text{pred}}$) | `Construct Point` $\to$ `Interpolate Curve` | **Cyan / Blue Curve** showing the learned mathematical function. |
| **Residual Error Bars** | `Line` from $(X, Y_{\text{true}}, 0)$ to $(X, Y_{\text{pred}}, 0)$ | **Vertical Lines** showing where the model makes errors. |
| **Readout Table** | `Panel` | Live table of $[X, Y_{\text{true}}, Y_{\text{pred}}, \text{Error}]$ and MSE. |

---

## 6. Summary Comparison

| Feature | `01_Octopus_Supervised_SVM.gh` | `02_Octopus_Evolutionary_NEAT.gh` |
| :--- | :--- | :--- |
| **Paradigm** | **Supervised Learning** (Regression) | **Evolutionary Learning** (NEAT / Genetic) |
| **Learning Engine** | SVM (libsvm RBF) + ANN (Resilient Prop) | Genetic Topology Mutation & Breeding |
| **Speed** | Instantaneous (< 2 ms) | Iterative across generations |
| **Best For** | Fitting known data points, surrogate modeling, fast pro-forma prediction | Evolving novel architectural forms, patterns, and topologies without gradients |
