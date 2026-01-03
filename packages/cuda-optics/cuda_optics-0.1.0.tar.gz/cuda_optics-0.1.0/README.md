# Welcome to cuda_optics!
![Language](https://img.shields.io/badge/language-Python%20%7C%20C%2B%2B%20%7C%20CUDA-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

**cuda_optics** is a high-performance ray-tracing simulation framework designed to bridge the gap between Python's approachability and raw hardware acceleration. It functions as a scriptable, 2D optical CAD library , optimized for simulating optical benches, lens barrels, and telescope/microscope designs.

The system features a hybrid architecture flexible enough for any hardware environment. It serves as a **physics sandbox**, offering students, educators, hobbyists, and researchers a large selection of built-in functionalities while maintaining maximum control over ray generation and element geometry.

## Why use this framework?
1. **Cross-Platform Core:** Native support for both Linux and Windows systems with automatic compiler detection.

2. **Hardware Acceleration:** Optimized for NVIDIA GPUs (Compute Capability 6.1+), supporting architectures from GTX 10-series (sm_61) to RTX 40-series (sm_89) and Hopper (sm_90).

3. **Hybrid Fallback:** Includes a highly optimized C++ CPU engine that activates automatically if no GPU is detected, ensuring code runs everywhere. Users can also force CPU-only execution if desired.

4. **Zero-Restriction Geometry:** Unlike standard matrix-optics tools, this framework poses no restrictions on element orientation or position. Rays and elements can be placed anywhere in 2D space without hard-coded optical axes.

5. **Rich Component Library:** Built-in support for 10+ optical elements including parabolic mirrors, thick lenses (meniscus/biconvex), prisms, and diffraction gratings.

6. **Visualization:** Integrated Matplotlib plotting tools provide instant visual feedback for debugging optical paths.

7. **Python abstraction:** A user-friendly Python interface utilizes intuitive commands, making complex simulations easy to write and understand.

8. **Open & Free:** Released under the MIT License, making it free for both educational and industrial use.

## Motivation behind the framework and design
While working on a project regarding spectroscopes, I required a software/library to simulate various configurations and validate my calculations. Even after spending a lot of time searching for such resources, I couldn't find one which could solve my very specific problem. This prompted me to write a python code for my immediate requirements and while doing that, I realised how I can code an actual generalised physics engine for optical system simulation. I then researched about various optical simulators available and found that 
existing resources were either too simplistic for niche problems or were expensive proprietary software inaccessible to students.

I focused on both educational and industrial value of this project. The plotting functionalities help in learning and build confidence through instant visualisation and easy to interpret feedback. The C++ and CUDA backends allow for high throughput ray tracing suitable for rigorous analysis. The OOP based architecture allows more optical elements and functionalities to be added as and when required.

Why 2D? Designed effectively as a virtual optical bench, the framework currently focuses on 2D arrangements to prioritize clarity and speed. This allows for precise Meridional Plane Analysis which is ideal for symmetric systems like telescopes or planar experiments. However, the core physics logic is built on dimension-agnostic vector algebra (Linear Algebra), meaning the simulation code is ready for N-dimensional expansion with minimal architectural changes.