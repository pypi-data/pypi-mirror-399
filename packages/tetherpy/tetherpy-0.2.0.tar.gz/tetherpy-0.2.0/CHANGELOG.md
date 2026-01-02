# CHANGELOG


## v0.2.0 (2025-12-29)

### Chores

- Add comprehensive benchmark suite for Tether, snnTorch, and SpikingJelly frameworks
  ([`f401fda`](https://github.com/Khushiyant/tether/commit/f401fda0e7e4f3a21a616f47368ad9eecdd759f2))

- Add comprehensive benchmark suite for Tether, snnTorch, and SpikingJelly frameworks
  ([`70eb398`](https://github.com/Khushiyant/tether/commit/70eb398f3e889625cd1aecaab304e72c89b58d77))

- Add SpikingCIFARModel and TetherLM for CIFAR-10 training, include dataset download functionality,
  and update dependencies in pyproject.toml
  ([`8d3144c`](https://github.com/Khushiyant/tether/commit/8d3144cd18d13a62ead899611ed4fef38e915613))

- Refactor PLIF and LIF modules for improved readability and performance
  ([`26846fc`](https://github.com/Khushiyant/tether/commit/26846fc3acc85286968282255ed7b16329ce66e6))

- Enhanced the PLIF and LIF classes by restructuring the initialization parameters for better
  clarity. - Updated the forward methods in both classes to improve code readability and
  maintainability. - Added support for vectorized decay and threshold parameters in PLIF. - Improved
  the handling of surrogate gradients in both LIF and PLIF. - Refactored the attention mechanism in
  SpikingSelfAttention to streamline operations. - Updated the Monitor utility to enhance voltage
  trace monitoring capabilities. - Added comprehensive tests for new features and ensured backward
  compatibility. - Cleaned up code formatting across multiple files for consistency.

- Remove obsolete documentation files for tether modules
  ([`ae7b023`](https://github.com/Khushiyant/tether/commit/ae7b02367182dad192798b2a6f2c4af0271aa68d))

- Simplify spike handling in SNNTorch models and reset hidden states in MNIST model
  ([`70f4a42`](https://github.com/Khushiyant/tether/commit/70f4a42f1e0e584c99bf1d28ff8b852362c893a2))

### Features

- Implement Triton kernels for causal linear attention and rate encoding, optimize LinearLIF layer
  ([`669912f`](https://github.com/Khushiyant/tether/commit/669912ff1a6b8d8dbe66621251ebc357b5086a74))


## v0.1.1 (2025-12-25)

### Bug Fixes

- Enhance LIF and PLIF implementations with detailed documentation, improve Triton kernels, and
  update workflow for semantic release
  ([`99c7532`](https://github.com/Khushiyant/tether/commit/99c75322c986d0e188f239c7f4626ef200e61e87))


## v0.1.0 (2025-12-25)

### Chores

- Add Sphinx documentation setup and update dependencies in pyproject.toml
  ([`4e77841`](https://github.com/Khushiyant/tether/commit/4e77841f26f2a65ab04f95abe53106c6f91ac28d))

- Correct package path in wheel build configuration
  ([`2ba9444`](https://github.com/Khushiyant/tether/commit/2ba9444db2146dbfb2dbf1fde2e7707ebbbe5b5a))

- Enhance documentation, add new encoding utilities, and improve LIF functionality with surrogate
  gradients
  ([`daf68ab`](https://github.com/Khushiyant/tether/commit/daf68ab216bca211149e1160630a747d7e5906cc))

- Remove test workflow from GitHub Actions
  ([`67f52af`](https://github.com/Khushiyant/tether/commit/67f52af0aaf60eead7162a5cd6b60e344f78a2e7))

- Rename job from 'build-and-deploy' to 'build' in GitHub Actions workflow
  ([`2e43c26`](https://github.com/Khushiyant/tether/commit/2e43c26ea5ca6b5f14fd31ff0cf158a2727d2493))

- Reorganize GitHub Actions test workflow and remove CHANGELOG file
  ([`4ef708e`](https://github.com/Khushiyant/tether/commit/4ef708e2cf9d6ebdd58c741c06053fb2844b9eea))

- Update project description in pyproject.toml
  ([`758268b`](https://github.com/Khushiyant/tether/commit/758268b05dd909bb4190060051cdcd31e39320ea))

- Update project name in pyproject.toml and streamline dependencies formatting
  ([`77bedba`](https://github.com/Khushiyant/tether/commit/77bedba46f8005dcbe1aa084862da352d911953c))

- Update Sphinx documentation build paths and fix directory structure
  ([`e022cae`](https://github.com/Khushiyant/tether/commit/e022caef05d7bef7db6065fab6455c429d2bae22))

- Update Sphinx documentation build process and dependencies in pyproject.toml
  ([`777b38b`](https://github.com/Khushiyant/tether/commit/777b38bef72df6260d5d104eaf529fddfa708c46))

### Features

- Implement ALIF and PLIF modules with Triton kernels, add surrogate gradient classes, and enhance
  benchmark functionality
  ([`042f891`](https://github.com/Khushiyant/tether/commit/042f8913b14678df292802e73f0c2d09a127b2e1))


## v0.0.1 (2025-12-25)

### Bug Fixes

- Define shape variables in forward method of SpikingSelfAttention class
  ([`c7e15a7`](https://github.com/Khushiyant/tether/commit/c7e15a764ea982bb417e95db23e8491543641118))

### Chores

- Add GitHub Actions for semantic release and testing
  ([`5a12ca2`](https://github.com/Khushiyant/tether/commit/5a12ca2de145a672490c1e57223021c58637b15e))

- Add GitHub Actions workflow for testing with multiple Python versions
  ([`6334c5d`](https://github.com/Khushiyant/tether/commit/6334c5d7c193d0b1fac3b94eeeb442e28d212556))

- Add GitHub Actions workflows for semantic release and testing with multiple Python versions
  ([`19ee3fc`](https://github.com/Khushiyant/tether/commit/19ee3fcdb9948a4bc7efa55f8361790cbfd25bb7))

- Add initial CHANGELOG file
  ([`ad53c31`](https://github.com/Khushiyant/tether/commit/ad53c3199b765f0d53b57eec5cd3c3f6aecbc76f))

- Downgrade Python version to 3.10 and simplify dependencies in pyproject.toml
  ([`9eb2844`](https://github.com/Khushiyant/tether/commit/9eb28443f08c19bbb79cb679bfc6f960d9044973))

- Initial commit
  ([`1a7d8f2`](https://github.com/Khushiyant/tether/commit/1a7d8f23c7f69210fd9ff42310d291c84455da64))

- Update GitHub Actions workflow to use 'uv' for Python setup and dependency management
  ([`d29f398`](https://github.com/Khushiyant/tether/commit/d29f398e9c39ce1eb2828e36477caa2ef4a53aea))
