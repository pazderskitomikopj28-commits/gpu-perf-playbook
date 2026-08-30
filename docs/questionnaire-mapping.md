# Questionnaire evidence map

| Item | Evidence to collect |
| --- | --- |
| Kernel/Grid/Block/Thread | A kernel with annotated launch geometry and boundary handling |
| SIMT/Warp/Divergence | A before/after case with branch-efficiency or stall evidence |
| Shared Memory | Tiled transpose, bank-conflict explanation, barrier placement |
| Tensor Core/WMMA/WGMMA | A tested matrix path, API and shape restrictions explicitly recorded |
| Coalescing | Input layout, alignment assumption and measured bandwidth |
| Stream/concurrency | Systems timeline showing copies and kernels overlap |
| Nsight Systems/Compute | Raw report, exported CSV and interpretation notes |
| 国产 GPU | SDK version, device output and a real porting log; otherwise mark as learning |
| Git/VSCode/AI Coding | Commit history, reproducible build, tests and AI-assisted review notes |
| GitHub/blog proof | Public repository, benchmark command, report and dated technical article |

Every row should point to a file or command. “熟悉” without an artifact is a
weak answer to a selection questionnaire.
