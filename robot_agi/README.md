# Robot AGI – Advanced Python Package

This directory is a **standalone Python package** containing the advanced robotics / AGI system modules. It is completely independent of the PWA digital business card that lives in the repo root.

## Structure

```
robot_agi/
├── advanced/               # Core library packages
│   ├── meta_learning/      # MAML, Reptile, few-shot & zero-shot learning
│   ├── reasoning/          # Causal, commonsense, knowledge-graph & symbolic reasoning
│   ├── multimodal/         # Sensor/modality fusion, VLM, active perception
│   ├── hierarchical_planning/  # Mission, task, motion & neural planners
│   ├── manipulation/       # Dexterous, contact-rich, force-control & tool use
│   ├── social/             # Emotion recognition, theory of mind, social navigation
│   ├── swarm/              # Coordination, consensus, formation, collective intelligence
│   ├── diagnosis/          # Anomaly detection, self-diagnostics, predictive maintenance
│   ├── sim2real/           # Domain randomisation, gap bridging, transfer learning
│   ├── memory/             # Episodic, semantic, working memory & consolidation
│   ├── learning/           # Offline RL, MARL, inverse RL, curriculum, self-supervised
│   ├── optimization/       # Quantisation, pruning, compression, hardware acceleration
│   ├── safety/             # Adversarial defence, safe exploration, formal verification
│   ├── collaboration/      # Intent prediction, handover, shared autonomy, proactive assistance
│   └── explainability/     # XAI, interpretable models, attention visualisation, NL explanations
├── config/
│   └── advanced_features.yaml  # Feature flags and hyperparameter defaults
└── tests/
    └── test_advanced_features.py  # Full unittest suite (62 tests)
```

## Running tests

From inside this directory:

```bash
python3 -m unittest discover -s tests -v
```

Or from the repo root:

```bash
python3 -m unittest discover -s robot_agi/tests -v
```

## Configuration

`config/advanced_features.yaml` contains default settings for every subsystem (meta-learning algorithms, memory capacities, optimisation targets, etc.). Override values by loading the YAML and passing parameters to the relevant class constructors.
