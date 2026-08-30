# CUDA → BIRENSUPA migration notes

This document is intentionally a checklist, not a claim of device-specific
knowledge. Public information confirms that Biren provides the BIRENSUPA
software platform and br_pytorch ecosystem, but the exact SDK headers,
instruction set, execution grouping and profiling counters depend on the
assigned environment and version.

## Porting order

1. Capture a CPU reference and shape/stride contract.
2. Port the simplest correct kernel through the officially supported compiler.
3. Validate numerical tolerances and boundary cases.
4. Re-measure memory access and synchronization behavior on the actual device.
5. Replace NVIDIA-only WMMA/WGMMA calls with the platform's documented matrix
   API, if available; do not perform a textual rename.
6. Rebuild the performance model using the device's documented peak numbers and
   profiler counters.

## Questions to ask during training

- What is the hardware execution group corresponding to a CUDA warp?
- Which barriers are block-, subgroup- or device-scoped?
- What are the shared/local memory bank and alignment rules?
- Which asynchronous copy and event APIs are supported?
- How are device kernels compiled, cached and profiled?
- Which PyTorch/`br_pytorch` ABI and tensor layouts are guaranteed?

The answers belong in a dated lab note with SDK version and command output.
That note, not a generic compatibility claim, is the evidence to put in a
portfolio.
