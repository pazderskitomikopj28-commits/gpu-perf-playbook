# GPU Performance Playbook

[![CI](https://github.com/pazderskitomikopj28-commits/gpu-perf-playbook/actions/workflows/ci.yml/badge.svg)](https://github.com/pazderskitomikopj28-commits/gpu-perf-playbook/actions/workflows/ci.yml)

一套围绕 GPU 性能工程的可复现模板：如何设计 benchmark、用 Nsight Systems/Compute 采集证据、做简单 Roofline 分析，以及为壁仞 BIRENSUPA/br_pytorch 预留清晰的后端适配边界。

这个仓库不上传未经测量的“提升百分比”。`benchmarks/results.schema.csv` 只有字段定义，真实结果应由你在实际 GPU 环境中运行后填写。

## 快速开始

```bash
python scripts/roofline.py --flops 2.0e9 --bytes 8.0e9 \
  --peak-flops 20.0e12 --peak-bandwidth 900e9

python scripts/validate_manifest.py examples/benchmark_manifest.json

python scripts/parse_ncu_csv.py tests/data/ncu_sample.csv
```

Windows PowerShell：

```powershell
python .\scripts\roofline.py --flops 2.0e9 --bytes 8.0e9 `
  --peak-flops 20.0e12 --peak-bandwidth 900e9
python .\scripts\validate_manifest.py .\examples\benchmark_manifest.json
```

## 项目组成

- `scripts/profile_cuda.*`：对 CUDA benchmark 生成 Nsight Systems/Compute 报告；
- `scripts/parse_ncu_csv.py`：定位 `ncu --page raw --csv` 表头，按 Kernel/Metric 聚合重复采样，输出 Markdown 或 JSON；
- `scripts/roofline.py`：根据 FLOPs、字节数和硬件峰值判断计算/带宽上界；
- `portable_backend/`：最小后端接口和 CUDA/SUPA 适配边界示例；
- `docs/questionnaire-mapping.md`：将工程证据对应到选拔问卷 10 项。
- `docs/windows-rtx4060-toolchain.md`：RTX 4060 Windows 真机工具链、D 盘路径和已知限制。

## 自动验证

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

CI 会执行 Python 工具测试、实验清单校验和不依赖厂商 SDK 的 SUPA stub 构建测试。CUDA 后端仍需在安装 CUDA Toolkit 的环境中显式使用 `-DBUILD_CUDA_BACKEND=ON` 构建。

本机 Windows/RTX 4060 的工具链与路径记录见
[`docs/windows-rtx4060-toolchain.md`](docs/windows-rtx4060-toolchain.md)。

## 证据规范

每个结果至少记录：commit、GPU 型号、驱动/SDK、编译参数、输入形状、warm-up 次数、测量次数、均值/分位数、正确性阈值和完整命令。Nsight 的截图应与原始报告或 CSV 一起保存，方便复核。

## 壁仞适配声明

仓库里的 CUDA 代码和后端接口可以用于迁移训练，但没有假设 BIRENSUPA 的私有头文件、设备执行组织或 profiling 指标。`portable_backend` 中的 SUPA 实现是明确标注的 stub；只有在获得官方 SDK 并通过真机测试后，才应把它描述为“壁仞开发经验”。

## 许可证

MIT
