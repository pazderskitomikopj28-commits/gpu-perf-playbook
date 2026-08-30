#!/usr/bin/env python3
"""Small, dependency-free arithmetic-intensity/Roofline calculator."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flops", type=float, required=True, help="FLOPs per invocation")
    parser.add_argument("--bytes", type=float, required=True, help="bytes moved per invocation")
    parser.add_argument("--peak-flops", type=float, required=True, help="device peak FLOP/s")
    parser.add_argument("--peak-bandwidth", type=float, required=True, help="device peak byte/s")
    args = parser.parse_args()
    if min(args.flops, args.bytes, args.peak_flops, args.peak_bandwidth) <= 0:
        parser.error("all numeric arguments must be positive")

    intensity = args.flops / args.bytes
    ridge = args.peak_flops / args.peak_bandwidth
    attainable = min(args.peak_flops, intensity * args.peak_bandwidth)
    bound = "compute" if args.peak_flops <= intensity * args.peak_bandwidth else "memory"
    print(f"arithmetic_intensity_FLOP_per_byte={intensity:.6g}")
    print(f"ridge_point_FLOP_per_byte={ridge:.6g}")
    print(f"roofline_upper_bound_FLOP_per_s={attainable:.6g}")
    print(f"likely_bound={bound}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
