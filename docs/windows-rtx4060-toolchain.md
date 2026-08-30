# Windows RTX 4060 toolchain record

记录日期：2026-08-30。此文档记录实际机器状态，不把“已安装”混同为“已熟练”。

## Hardware and compiler

| Item | Verified value |
| --- | --- |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU, 8188 MiB |
| Compute capability | 8.9 (Ada, build target `sm_89`) |
| Driver | 591.74 |
| CUDA Toolkit | 12.4 Update 1, `nvcc` 12.4.131 |
| Host compiler | MSVC 19.38.33145 (v143 14.38) |
| CMake | 4.4.3 |
| Windows | 10.0.26200.9168 |

CUDA 12.4 is deliberately aligned with the repositories' CI image. Its
[Windows installation guide](https://docs.nvidia.com/cuda/archive/12.4.1/cuda-installation-guide-microsoft-windows/index.html)
supports the MSVC 193x compiler family, so builds explicitly select MSVC 14.38
instead of the installed 14.44 toolset.

## Physical D-drive locations

| Purpose | Physical location |
| --- | --- |
| VS2022 C++ Build Tools | `D:\DevTools\Microsoft\VS2022-BuildTools` |
| Visual Studio shared payload | `D:\DevTools\Microsoft\VS-Shared` |
| CMake | `D:\DevTools\Kitware\CMake-4.4.3` |
| CUDA Toolkit | `D:\DevTools\NVIDIA\CUDA\v12.4` |
| Nsight Systems, CUDA-bundled | `D:\DevTools\NVIDIA\Nsight-Systems-2023.4.4` |
| Nsight Systems, current | `D:\DevTools\NVIDIA\Nsight-Systems-2026.4.1` |
| Nsight Compute, driver-matched archive | `D:\DevTools\NVIDIA\Nsight-Compute-2025.4.1-driver-matched-archive` |
| Nsight Compute, current | `D:\DevTools\NVIDIA\Nsight-Compute-2026.2.1` |
| Downloaded installers/cache | `D:\DevTools\Installers` |
| Out-of-tree builds | `D:\DevTools\Builds` |
| Raw profiler reports | `D:\DevTools\Profiles` |

The standard CUDA entry at
`C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA` is a directory junction
to `D:\DevTools\NVIDIA\CUDA`; the CUDA-bundled Nsight Systems directory under
`C:\Program Files\NVIDIA Corporation` is also a compatibility junction to its
D-drive location. Nsight Compute 2026.2.1 is the active MSI installation. The
2025.4.1 directory is a runnable archive retained before the current release's
major upgrade replaced its registration. The pre-existing shared Windows SDK remains under
`C:\Program Files (x86)\Windows Kits\10`; it was reused rather than reinstalled.
Windows Installer and the Visual Studio Installer may retain small system
registration/cache data on C even though movable application payloads are on D.

## Reproducible Windows build

The workspace contains Chinese characters. CUDA compiler identification failed
when `nvcc` received that path, so `D:\CUDA-Training` is a directory junction to
the original workspace. Repository build scripts automate the same workaround
with links under `D:\DevTools\Builds\_source_links`.

```powershell
.\cuda-kernel-lab\scripts\build_windows.ps1
.\cuda-stream-pipeline\scripts\build_windows.ps1

cmake -S D:\CUDA-Training\gpu-perf-playbook `
  -B D:\DevTools\Builds\gpu-perf-playbook-rtx4060 `
  -G 'Visual Studio 17 2022' -A x64 -T version=14.38 `
  -DBUILD_CUDA_BACKEND=ON -DCMAKE_CUDA_ARCHITECTURES=89
cmake --build D:\DevTools\Builds\gpu-perf-playbook-rtx4060 --config Release
```

Windows CUDA targets use the shared CUDA runtime to match MSVC's `/MD` runtime
and avoid `LNK4098` static/dynamic CRT conflicts.

## Profiler validation status

- Nsight Systems 2026.4.1 successfully generated a CUDA timeline and SQLite
  export for the four-stream benchmark. On Windows, the scripts use
  `cuda,nvtx`, `--sample=none` and `--cpuctxsw=none`; WDDM/CPU traces require an
  elevated session. Start the tool from an ASCII-only working directory.
- Nsight Compute 2024.1.1 (tested before the later MSI upgrade), archived
  2025.4.1 and active 2026.2.1 all exit with Windows status
  `0xC0000409` while initializing `--list-sets`; the same happens elevated, before
  any project kernel is launched. No Compute metric is claimed from this host.
  The driver-matched 2025.4.1 release officially recommends driver 591.59 or
  newer, and this host has 591.74, so the remaining issue is recorded as a
  system-level compatibility defect pending isolation.
- Compute Sanitizer's WDDM debugger interface is enabled. Both repositories'
  final Release test binaries passed memcheck with `0 errors` and racecheck
  with `0 errors, 0 warnings`. The Toolkit's
  `compute-sanitizer\EnableDebuggerInterface.bat` must be run once as
  administrator on a fresh Windows installation.

The official profiler pages used here are
[Nsight Systems](https://developer.nvidia.com/nsight-systems/get-started),
[current Nsight Compute](https://developer.nvidia.com/tools-overview/nsight-compute/get-started)
and the driver-matched
[Nsight Compute 2025.4](https://developer.nvidia.com/tools-overview/nsight-compute/get-started-2025_4).
