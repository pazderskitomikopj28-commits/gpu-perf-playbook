# GPU Performance Playbook

[![CI](https://github.com/pazderskitomikopj28-commits/gpu-perf-playbook/actions/workflows/ci.yml/badge.svg)](https://github.com/pazderskitomikopj28-commits/gpu-perf-playbook/actions/workflows/ci.yml)

一套围绕 GPU 性能工程的工具与参考实现：设计可复现 benchmark、用 Nsight Systems/Compute 分析运行行为、做简单 Roofline 分析，并探索 CUDA 与其他 GPU 后端之间的适配边界。

这个仓库不上传未经测量的“提升百分比”。`benchmarks/results.schema.csv` 只有字段定义，真实结果应由你在实际 GPU 环境中运行后填写。

## 快速开始

```bash
python scripts/roofline.py --flops 2.0e9 --bytes 8.0e9 \
  --peak-flops 20.0e12 --peak-bandwidth 900e9

python scripts/validate_manifest.py examples/benchmark_manifest.json

python scripts/parse_ncu_csv.py tests/data/ncu_sample.csv
python scripts/benchmark_stats.py summarize tests/data/benchmark_samples.csv
python scripts/capture_environment.py --repository .
```

Windows PowerShell：

```powershell
python .\scripts\roofline.py --flops 2.0e9 --bytes 8.0e9 `
  --peak-flops 20.0e12 --peak-bandwidth 900e9
python .\scripts\validate_manifest.py .\examples\benchmark_manifest.json
python .\scripts\benchmark_stats.py summarize .\tests\data\benchmark_samples.csv
python .\scripts\capture_environment.py --repository .
```

## 项目组成

- `scripts/profile_cuda.*`：对 CUDA benchmark 生成 Nsight Systems/Compute 报告；
- `scripts/parse_ncu_csv.py`：定位 `ncu --page raw --csv` 表头，按 Kernel/Metric 聚合重复采样，输出 Markdown 或 JSON；
- `scripts/roofline.py`：根据 FLOPs、字节数和硬件峰值判断计算/带宽上界；
- `scripts/capture_environment.py`：采集 Git revision、GPU/驱动、CUDA、Nsight、
  编译器和 Host 环境，敏感的 remote URL 用户信息会被移除；
- `scripts/benchmark_stats.py`：校验逐次原始样本，汇总 Mean/P50/P95/MAD，并按
  性能方向、样本数和阈值执行回归检查；
- `portable_backend/`：最小后端接口和 CUDA/SUPA 适配边界示例；
- `docs/nsight.md`：从系统时间线到 Kernel 指标的分析流程；
- `docs/supa-porting.md`：CUDA 到其他设备后端的迁移问题清单；
- `templates/benchmark-report.md`：可复用的实验记录模板；
- `docs/windows-rtx4060-toolchain.md`：RTX 4060 Windows 真机工具链、D 盘路径和已知限制。
- `benchmarks/rtx4060-laptop-2026-08-30.csv`：带 commit、环境和命令的真机结果。
- `benchmarks/environment-rtx4060-2026-08-30.json`：由采集工具从干净提交生成的
  RTX 4060、D 盘 CUDA/Nsight/MSVC 工具链快照；
- `benchmarks/rtx4060-raw-samples-2026-08-30.csv`：Graph、memory pool 和 RMSNorm
  实验的逐进程原始样本，可直接交给统计工具复算；
- `docs/statistics-and-regression.md`：原始样本格式、分位数口径和回归门限的解释。

## 自动验证

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

CI 会执行 Python 工具测试、实验清单校验和不依赖厂商 SDK 的 SUPA stub 构建测试。CUDA 后端仍需在安装 CUDA Toolkit 的环境中显式使用 `-DBUILD_CUDA_BACKEND=ON` 构建。

性能回归命令在超过阈值时返回退出码 1，但阈值只是工程门禁，不等同于统计显著性。
基线和候选必须来自同一 GPU、功耗模式、工具链与输入；先查看 P95 和 MAD 是否表明
环境噪声过大，再解释小幅变化。

本机 Windows/RTX 4060 的工具链与路径记录见
[`docs/windows-rtx4060-toolchain.md`](docs/windows-rtx4060-toolchain.md)。
跨仓库结果解释见 [`docs/rtx4060-results.md`](docs/rtx4060-results.md)。

## 实验记录规范

每次测量至少记录：commit、环境快照、GPU 型号、驱动/SDK、编译参数、输入形状、
warm-up 次数、逐次原始样本、均值/分位数/MAD、正确性阈值和完整命令。Nsight
截图应与原始报告或 CSV 一起保存，方便复现和比较。

## 壁仞适配声明

仓库里的 CUDA 代码和后端接口可以用于迁移训练，但没有假设 BIRENSUPA 的私有头文件、设备执行组织或 profiling 指标。`portable_backend` 中的 SUPA 实现是明确标注的 stub；只有在获得官方 SDK 并通过真机测试后，才应把它描述为“壁仞开发经验”。

## 许可证

MIT
