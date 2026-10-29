# Paper324 - Complete primary tables

All rates and AUROC below are percentages. Alpha=5%; no seed is omitted.
Intervals are conditional paired-cluster percentile95 intervals, not security guarantees.
Oracle BFA uses evaluation labels and has no confidence interval in this package.

## Equal-seed descriptive summaries

| Target | System | AUROC | Policy FA | Policy BFA | Oracle BFA | FA-safe /3 | Policy utility /3 | Oracle utility /3 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| OULU-NPU | dino_reg | 87.77 | 36.13 | 91.94 | 46.67 | 0 | 0 | 0 |
| OULU-NPU | supervised_clip | 79.20 | 16.62 | 53.70 | 23.43 | 0 | 0 | 0 |
| OULU-NPU | fixed_equal_two_dino | 86.60 | 58.87 | 97.13 | 41.11 | 0 | 0 | 0 |
| OULU-NPU | matched_deeppixbis | 91.98 | 15.12 | 81.11 | 58.70 | 0 | 0 | 3 |
| CASIA-FASD | dino_reg | 99.94 | 0.00 | 39.26 | 98.89 | 3 | 0 | 3 |
| CASIA-FASD | supervised_clip | 98.20 | 0.00 | 46.67 | 85.56 | 3 | 0 | 3 |
| CASIA-FASD | fixed_equal_two_dino | 99.94 | 0.00 | 40.37 | 98.89 | 3 | 0 | 3 |
| CASIA-FASD | matched_deeppixbis | 86.61 | 1.48 | 42.59 | 54.81 | 3 | 0 | 2 |
| MSU-MFSD | dino_reg | 87.56 | 41.67 | 90.00 | 42.50 | 0 | 0 | 0 |
| MSU-MFSD | supervised_clip | 89.22 | 9.17 | 65.00 | 57.50 | 0 | 0 | 3 |
| MSU-MFSD | fixed_equal_two_dino | 92.67 | 22.78 | 92.50 | 68.33 | 0 | 0 | 3 |
| MSU-MFSD | matched_deeppixbis | 92.98 | 8.89 | 79.17 | 52.50 | 0 | 0 | 1 |
| SiW-Mv2 | dino_reg | 88.01 | 9.67 | 58.24 | 34.87 | 0 | 0 | 0 |
| SiW-Mv2 | supervised_clip | 85.02 | 3.59 | 31.42 | 38.19 | 3 | 0 | 0 |
| SiW-Mv2 | fixed_equal_two_dino | 87.38 | 16.02 | 74.33 | 45.72 | 0 | 0 | 0 |
| SiW-Mv2 | matched_deeppixbis | 76.00 | 49.82 | 87.36 | 23.75 | 0 | 0 | 0 |

## All 48 target/system/seed primary rows

Usable/original supports are attack,bona-fide respectively.
Acceptance counts use all-original denominators.

| Target | Seed | System | Usable / original | Accepted attack,BF | FA [95%] | BFA [95%] | AUROC [95%] | Oracle BFA |
|---|---:|---|---|---|---:|---:|---:|---:|
| OULU-NPU | 20260917 | dino_reg | 1440,360 / 1440,360 | 520,331 | 36.11 [26.25, 45.97] | 91.94 [86.11, 96.67] | 87.81 [84.77, 91.13] | 46.67 |
| OULU-NPU | 20260917 | supervised_clip | 1440,360 / 1440,360 | 241,193 | 16.74 [11.18, 23.06] | 53.61 [41.10, 66.67] | 79.19 [73.76, 83.90] | 23.33 |
| OULU-NPU | 20260917 | fixed_equal_two_dino | 1440,360 / 1440,360 | 853,351 | 59.24 [49.65, 68.96] | 97.50 [94.17, 99.72] | 86.50 [83.55, 89.86] | 40.83 |
| OULU-NPU | 20260917 | matched_deeppixbis | 1440,360 / 1440,360 | 210,297 | 14.58 [9.37, 20.83] | 82.50 [74.44, 90.00] | 92.30 [90.45, 94.43] | 61.94 |
| OULU-NPU | 20260923 | dino_reg | 1440,360 / 1440,360 | 519,331 | 36.04 [26.25, 45.97] | 91.94 [86.11, 96.67] | 87.75 [84.71, 91.08] | 46.67 |
| OULU-NPU | 20260923 | supervised_clip | 1440,360 / 1440,360 | 240,193 | 16.67 [11.11, 23.06] | 53.61 [41.10, 66.67] | 79.18 [73.75, 83.89] | 23.33 |
| OULU-NPU | 20260923 | fixed_equal_two_dino | 1440,360 / 1440,360 | 844,349 | 58.61 [48.75, 68.61] | 96.94 [93.61, 99.44] | 86.71 [83.69, 90.12] | 41.67 |
| OULU-NPU | 20260923 | matched_deeppixbis | 1440,360 / 1440,360 | 280,307 | 19.44 [15.76, 23.19] | 85.28 [78.61, 91.11] | 91.98 [90.41, 93.70] | 57.78 |
| OULU-NPU | 20261001 | dino_reg | 1440,360 / 1440,360 | 522,331 | 36.25 [26.60, 45.97] | 91.94 [86.11, 96.67] | 87.76 [84.73, 91.06] | 46.67 |
| OULU-NPU | 20261001 | supervised_clip | 1440,360 / 1440,360 | 237,194 | 16.46 [11.04, 22.64] | 53.89 [41.11, 66.94] | 79.23 [73.77, 83.96] | 23.61 |
| OULU-NPU | 20261001 | fixed_equal_two_dino | 1440,360 / 1440,360 | 846,349 | 58.75 [49.24, 68.54] | 96.94 [93.61, 99.44] | 86.58 [83.61, 89.98] | 40.83 |
| OULU-NPU | 20261001 | matched_deeppixbis | 1440,360 / 1440,360 | 163,272 | 11.32 [7.57, 15.76] | 75.56 [67.22, 83.33] | 91.66 [89.92, 93.77] | 56.39 |
| CASIA-FASD | 20260917 | dino_reg | 265,89 / 270,90 | 0,36 | 0.00 [0.00, 0.00] | 40.00 [27.78, 52.22] | 99.94 [99.78, 100.00] | 98.89 |
| CASIA-FASD | 20260917 | supervised_clip | 265,89 / 270,90 | 0,42 | 0.00 [0.00, 0.00] | 46.67 [38.89, 53.33] | 98.19 [97.02, 99.15] | 85.56 |
| CASIA-FASD | 20260917 | fixed_equal_two_dino | 265,89 / 270,90 | 0,34 | 0.00 [0.00, 0.00] | 37.78 [26.67, 47.78] | 99.93 [99.80, 100.00] | 98.89 |
| CASIA-FASD | 20260917 | matched_deeppixbis | 265,89 / 270,90 | 3,37 | 1.11 [0.00, 2.96] | 41.11 [36.67, 46.67] | 84.12 [78.67, 88.84] | 50.00 |
| CASIA-FASD | 20260923 | dino_reg | 265,89 / 270,90 | 0,36 | 0.00 [0.00, 0.00] | 40.00 [27.78, 52.22] | 99.94 [99.77, 100.00] | 98.89 |
| CASIA-FASD | 20260923 | supervised_clip | 265,89 / 270,90 | 0,42 | 0.00 [0.00, 0.00] | 46.67 [38.89, 53.33] | 98.19 [97.02, 99.15] | 85.56 |
| CASIA-FASD | 20260923 | fixed_equal_two_dino | 265,89 / 270,90 | 0,39 | 0.00 [0.00, 0.00] | 43.33 [32.22, 54.44] | 99.94 [99.81, 100.00] | 98.89 |
| CASIA-FASD | 20260923 | matched_deeppixbis | 265,89 / 270,90 | 4,37 | 1.48 [0.00, 3.33] | 41.11 [36.67, 46.67] | 86.47 [82.55, 90.03] | 48.89 |
| CASIA-FASD | 20261001 | dino_reg | 265,89 / 270,90 | 0,34 | 0.00 [0.00, 0.00] | 37.78 [25.56, 50.00] | 99.94 [99.80, 100.00] | 98.89 |
| CASIA-FASD | 20261001 | supervised_clip | 265,89 / 270,90 | 0,42 | 0.00 [0.00, 0.00] | 46.67 [38.89, 53.33] | 98.20 [97.00, 99.16] | 85.56 |
| CASIA-FASD | 20261001 | fixed_equal_two_dino | 265,89 / 270,90 | 0,36 | 0.00 [0.00, 0.00] | 40.00 [28.89, 51.11] | 99.94 [99.82, 100.00] | 98.89 |
| CASIA-FASD | 20261001 | matched_deeppixbis | 265,89 / 270,90 | 5,41 | 1.85 [0.37, 3.70] | 45.56 [38.89, 52.22] | 89.25 [85.74, 92.73] | 65.56 |
| MSU-MFSD | 20260917 | dino_reg | 116,40 / 120,40 | 49,36 | 40.83 [28.33, 52.50] | 90.00 [82.50, 97.50] | 87.69 [81.70, 93.49] | 42.50 |
| MSU-MFSD | 20260917 | supervised_clip | 116,40 / 120,40 | 11,26 | 9.17 [3.33, 15.00] | 65.00 [52.50, 77.50] | 89.25 [85.35, 93.23] | 57.50 |
| MSU-MFSD | 20260917 | fixed_equal_two_dino | 116,40 / 120,40 | 27,37 | 22.50 [11.67, 34.17] | 92.50 [85.00, 100.00] | 92.16 [86.29, 97.27] | 62.50 |
| MSU-MFSD | 20260917 | matched_deeppixbis | 116,40 / 120,40 | 14,34 | 11.67 [5.00, 19.17] | 85.00 [75.00, 95.00] | 91.68 [88.47, 95.00] | 37.50 |
| MSU-MFSD | 20260923 | dino_reg | 116,40 / 120,40 | 49,36 | 40.83 [28.33, 52.50] | 90.00 [82.50, 97.50] | 87.59 [81.53, 93.39] | 42.50 |
| MSU-MFSD | 20260923 | supervised_clip | 116,40 / 120,40 | 11,26 | 9.17 [3.33, 15.00] | 65.00 [52.50, 77.50] | 89.25 [85.35, 93.23] | 57.50 |
| MSU-MFSD | 20260923 | fixed_equal_two_dino | 116,40 / 120,40 | 28,37 | 23.33 [11.67, 35.83] | 92.50 [85.00, 100.00] | 93.15 [87.65, 97.99] | 75.00 |
| MSU-MFSD | 20260923 | matched_deeppixbis | 116,40 / 120,40 | 8,34 | 6.67 [2.50, 10.83] | 85.00 [75.00, 95.00] | 95.04 [92.75, 97.33] | 72.50 |
| MSU-MFSD | 20261001 | dino_reg | 116,40 / 120,40 | 52,36 | 43.33 [31.67, 54.17] | 90.00 [82.50, 97.50] | 87.39 [81.10, 93.31] | 42.50 |
| MSU-MFSD | 20261001 | supervised_clip | 116,40 / 120,40 | 11,26 | 9.17 [3.33, 15.00] | 65.00 [52.50, 77.50] | 89.18 [85.40, 93.10] | 57.50 |
| MSU-MFSD | 20261001 | fixed_equal_two_dino | 116,40 / 120,40 | 27,37 | 22.50 [11.65, 35.00] | 92.50 [85.00, 100.00] | 92.69 [87.26, 97.55] | 67.50 |
| MSU-MFSD | 20261001 | matched_deeppixbis | 116,40 / 120,40 | 10,27 | 8.33 [3.33, 15.00] | 67.50 [57.50, 77.50] | 92.22 [88.87, 95.83] | 47.50 |
| SiW-Mv2 | 20260917 | dino_reg | 359,260 / 362,261 | 35,153 | 9.67 [6.70, 12.95] | 58.62 [52.77, 64.29] | 87.94 [85.07, 90.53] | 34.48 |
| SiW-Mv2 | 20260917 | supervised_clip | 359,260 / 362,261 | 13,82 | 3.59 [1.76, 5.61] | 31.42 [25.76, 37.45] | 85.14 [82.08, 87.88] | 38.31 |
| SiW-Mv2 | 20260917 | fixed_equal_two_dino | 359,260 / 362,261 | 59,197 | 16.30 [12.67, 20.28] | 75.48 [70.57, 80.82] | 88.09 [85.27, 90.66] | 47.13 |
| SiW-Mv2 | 20260917 | matched_deeppixbis | 359,260 / 362,261 | 179,234 | 49.45 [44.54, 54.70] | 89.66 [85.94, 93.09] | 77.13 [73.42, 80.67] | 26.44 |
| SiW-Mv2 | 20260923 | dino_reg | 359,260 / 362,261 | 35,153 | 9.67 [6.70, 12.95] | 58.62 [52.77, 64.29] | 88.00 [85.15, 90.60] | 34.48 |
| SiW-Mv2 | 20260923 | supervised_clip | 359,260 / 362,261 | 13,82 | 3.59 [1.76, 5.61] | 31.42 [25.76, 37.45] | 85.12 [82.05, 87.86] | 38.31 |
| SiW-Mv2 | 20260923 | fixed_equal_two_dino | 359,260 / 362,261 | 56,194 | 15.47 [11.95, 19.30] | 74.33 [69.32, 79.52] | 87.70 [84.80, 90.31] | 46.74 |
| SiW-Mv2 | 20260923 | matched_deeppixbis | 359,260 / 362,261 | 211,243 | 58.29 [53.19, 63.34] | 93.10 [89.96, 96.05] | 75.31 [71.51, 78.92] | 21.84 |
| SiW-Mv2 | 20261001 | dino_reg | 359,260 / 362,261 | 35,150 | 9.67 [6.82, 12.90] | 57.47 [51.68, 63.05] | 88.08 [85.22, 90.68] | 35.63 |
| SiW-Mv2 | 20261001 | supervised_clip | 359,260 / 362,261 | 13,82 | 3.59 [1.76, 5.61] | 31.42 [25.76, 37.45] | 84.81 [81.68, 87.61] | 37.93 |
| SiW-Mv2 | 20261001 | fixed_equal_two_dino | 359,260 / 362,261 | 59,191 | 16.30 [12.76, 20.41] | 73.18 [68.20, 78.55] | 86.34 [83.30, 89.11] | 43.30 |
| SiW-Mv2 | 20261001 | matched_deeppixbis | 359,260 / 362,261 | 151,207 | 41.71 [37.03, 46.88] | 79.31 [74.26, 84.28] | 75.57 [71.68, 79.28] | 22.99 |

## All primary paired differences against DINO-Reg

Differences and intervals are percentage points. Policies may violate different
attack-FA constraints: BFA differences alone are not same-security gains.
Seeds share evaluation observations; these intervals are not multiple-testing-adjusted.

| Target | Seed | System minus DINO-Reg | Metric | Difference | Conditional 95% | Valid /2000 |
|---|---:|---|---|---:|---:|---:|
| OULU-NPU | 20260917 | supervised_clip | FA | -19.38 | [-29.24, -8.54] | 2000 |
| OULU-NPU | 20260917 | supervised_clip | BFA | -38.33 | [-50.00, -26.11] | 2000 |
| OULU-NPU | 20260917 | supervised_clip | AUROC_usable | -8.63 | [-12.65, -4.78] | 2000 |
| OULU-NPU | 20260917 | fixed_equal_two_dino | FA | 23.12 | [18.89, 27.99] | 2000 |
| OULU-NPU | 20260917 | fixed_equal_two_dino | BFA | 5.56 | [2.22, 9.44] | 2000 |
| OULU-NPU | 20260917 | fixed_equal_two_dino | AUROC_usable | -1.31 | [-3.17, -0.08] | 2000 |
| OULU-NPU | 20260917 | matched_deeppixbis | FA | -21.53 | [-32.57, -10.97] | 2000 |
| OULU-NPU | 20260917 | matched_deeppixbis | BFA | -9.44 | [-16.94, -1.94] | 2000 |
| OULU-NPU | 20260917 | matched_deeppixbis | AUROC_usable | 4.49 | [1.06, 7.68] | 2000 |
| OULU-NPU | 20260923 | supervised_clip | FA | -19.38 | [-29.24, -8.61] | 2000 |
| OULU-NPU | 20260923 | supervised_clip | BFA | -38.33 | [-50.00, -26.11] | 2000 |
| OULU-NPU | 20260923 | supervised_clip | AUROC_usable | -8.57 | [-12.61, -4.71] | 2000 |
| OULU-NPU | 20260923 | fixed_equal_two_dino | FA | 22.57 | [18.33, 27.64] | 2000 |
| OULU-NPU | 20260923 | fixed_equal_two_dino | BFA | 5.00 | [2.22, 8.33] | 2000 |
| OULU-NPU | 20260923 | fixed_equal_two_dino | AUROC_usable | -1.04 | [-2.77, 0.14] | 2000 |
| OULU-NPU | 20260923 | matched_deeppixbis | FA | -16.60 | [-27.09, -6.11] | 2000 |
| OULU-NPU | 20260923 | matched_deeppixbis | BFA | -6.67 | [-13.89, 0.56] | 2000 |
| OULU-NPU | 20260923 | matched_deeppixbis | AUROC_usable | 4.23 | [1.03, 6.96] | 2000 |
| OULU-NPU | 20261001 | supervised_clip | FA | -19.79 | [-29.51, -9.23] | 2000 |
| OULU-NPU | 20261001 | supervised_clip | BFA | -38.06 | [-49.44, -25.83] | 2000 |
| OULU-NPU | 20261001 | supervised_clip | AUROC_usable | -8.52 | [-12.57, -4.65] | 2000 |
| OULU-NPU | 20261001 | fixed_equal_two_dino | FA | 22.50 | [18.33, 27.43] | 2000 |
| OULU-NPU | 20261001 | fixed_equal_two_dino | BFA | 5.00 | [2.22, 8.33] | 2000 |
| OULU-NPU | 20261001 | fixed_equal_two_dino | AUROC_usable | -1.18 | [-2.97, 0.02] | 2000 |
| OULU-NPU | 20261001 | matched_deeppixbis | FA | -24.93 | [-35.07, -15.14] | 2000 |
| OULU-NPU | 20261001 | matched_deeppixbis | BFA | -16.39 | [-24.44, -8.60] | 2000 |
| OULU-NPU | 20261001 | matched_deeppixbis | AUROC_usable | 3.90 | [0.69, 6.80] | 2000 |
| CASIA-FASD | 20260917 | supervised_clip | FA | 0.00 | [0.00, 0.00] | 2000 |
| CASIA-FASD | 20260917 | supervised_clip | BFA | 6.67 | [-8.89, 21.11] | 2000 |
| CASIA-FASD | 20260917 | supervised_clip | AUROC_usable | -1.75 | [-2.92, -0.80] | 2000 |
| CASIA-FASD | 20260917 | fixed_equal_two_dino | FA | 0.00 | [0.00, 0.00] | 2000 |
| CASIA-FASD | 20260917 | fixed_equal_two_dino | BFA | -2.22 | [-13.33, 8.89] | 2000 |
| CASIA-FASD | 20260917 | fixed_equal_two_dino | AUROC_usable | -0.01 | [-0.09, 0.06] | 2000 |
| CASIA-FASD | 20260917 | matched_deeppixbis | FA | 1.11 | [0.00, 2.96] | 2000 |
| CASIA-FASD | 20260917 | matched_deeppixbis | BFA | 1.11 | [-11.11, 13.33] | 2000 |
| CASIA-FASD | 20260917 | matched_deeppixbis | AUROC_usable | -15.82 | [-21.27, -11.07] | 2000 |
| CASIA-FASD | 20260923 | supervised_clip | FA | 0.00 | [0.00, 0.00] | 2000 |
| CASIA-FASD | 20260923 | supervised_clip | BFA | 6.67 | [-8.89, 21.11] | 2000 |
| CASIA-FASD | 20260923 | supervised_clip | AUROC_usable | -1.74 | [-2.92, -0.80] | 2000 |
| CASIA-FASD | 20260923 | fixed_equal_two_dino | FA | 0.00 | [0.00, 0.00] | 2000 |
| CASIA-FASD | 20260923 | fixed_equal_two_dino | BFA | 3.33 | [-5.56, 13.33] | 2000 |
| CASIA-FASD | 20260923 | fixed_equal_two_dino | AUROC_usable | 0.00 | [-0.09, 0.11] | 2000 |
| CASIA-FASD | 20260923 | matched_deeppixbis | FA | 1.48 | [0.00, 3.33] | 2000 |
| CASIA-FASD | 20260923 | matched_deeppixbis | BFA | 1.11 | [-11.11, 13.33] | 2000 |
| CASIA-FASD | 20260923 | matched_deeppixbis | AUROC_usable | -13.47 | [-17.37, -9.90] | 2000 |
| CASIA-FASD | 20261001 | supervised_clip | FA | 0.00 | [0.00, 0.00] | 2000 |
| CASIA-FASD | 20261001 | supervised_clip | BFA | 8.89 | [-6.67, 23.33] | 2000 |
| CASIA-FASD | 20261001 | supervised_clip | AUROC_usable | -1.74 | [-2.93, -0.80] | 2000 |
| CASIA-FASD | 20261001 | fixed_equal_two_dino | FA | 0.00 | [0.00, 0.00] | 2000 |
| CASIA-FASD | 20261001 | fixed_equal_two_dino | BFA | 2.22 | [-6.67, 12.22] | 2000 |
| CASIA-FASD | 20261001 | fixed_equal_two_dino | AUROC_usable | -0.00 | [-0.08, 0.08] | 2000 |
| CASIA-FASD | 20261001 | matched_deeppixbis | FA | 1.85 | [0.37, 3.70] | 2000 |
| CASIA-FASD | 20261001 | matched_deeppixbis | BFA | 7.78 | [-4.44, 21.11] | 2000 |
| CASIA-FASD | 20261001 | matched_deeppixbis | AUROC_usable | -10.70 | [-14.24, -7.21] | 2000 |
| MSU-MFSD | 20260917 | supervised_clip | FA | -31.67 | [-45.83, -18.31] | 2000 |
| MSU-MFSD | 20260917 | supervised_clip | BFA | -25.00 | [-40.00, -10.00] | 2000 |
| MSU-MFSD | 20260917 | supervised_clip | AUROC_usable | 1.55 | [-5.27, 9.12] | 2000 |
| MSU-MFSD | 20260917 | fixed_equal_two_dino | FA | -18.33 | [-25.83, -11.67] | 2000 |
| MSU-MFSD | 20260917 | fixed_equal_two_dino | BFA | 2.50 | [-5.00, 10.00] | 2000 |
| MSU-MFSD | 20260917 | fixed_equal_two_dino | AUROC_usable | 4.46 | [-0.07, 9.21] | 2000 |
| MSU-MFSD | 20260917 | matched_deeppixbis | FA | -29.17 | [-40.83, -17.50] | 2000 |
| MSU-MFSD | 20260917 | matched_deeppixbis | BFA | -5.00 | [-15.00, 5.00] | 2000 |
| MSU-MFSD | 20260917 | matched_deeppixbis | AUROC_usable | 3.99 | [-2.61, 10.78] | 2000 |
| MSU-MFSD | 20260923 | supervised_clip | FA | -31.67 | [-45.83, -18.31] | 2000 |
| MSU-MFSD | 20260923 | supervised_clip | BFA | -25.00 | [-40.00, -10.00] | 2000 |
| MSU-MFSD | 20260923 | supervised_clip | AUROC_usable | 1.66 | [-5.15, 9.28] | 2000 |
| MSU-MFSD | 20260923 | fixed_equal_two_dino | FA | -17.50 | [-25.00, -10.00] | 2000 |
| MSU-MFSD | 20260923 | fixed_equal_two_dino | BFA | 2.50 | [0.00, 7.50] | 2000 |
| MSU-MFSD | 20260923 | fixed_equal_two_dino | AUROC_usable | 5.56 | [1.24, 10.23] | 2000 |
| MSU-MFSD | 20260923 | matched_deeppixbis | FA | -34.17 | [-46.67, -22.50] | 2000 |
| MSU-MFSD | 20260923 | matched_deeppixbis | BFA | -5.00 | [-15.00, 5.00] | 2000 |
| MSU-MFSD | 20260923 | matched_deeppixbis | AUROC_usable | 7.46 | [1.80, 13.67] | 2000 |
| MSU-MFSD | 20261001 | supervised_clip | FA | -34.17 | [-47.50, -21.67] | 2000 |
| MSU-MFSD | 20261001 | supervised_clip | BFA | -25.00 | [-40.00, -10.00] | 2000 |
| MSU-MFSD | 20261001 | supervised_clip | AUROC_usable | 1.79 | [-5.13, 9.53] | 2000 |
| MSU-MFSD | 20261001 | fixed_equal_two_dino | FA | -20.83 | [-28.33, -12.50] | 2000 |
| MSU-MFSD | 20261001 | fixed_equal_two_dino | BFA | 2.50 | [-5.00, 10.00] | 2000 |
| MSU-MFSD | 20261001 | fixed_equal_two_dino | AUROC_usable | 5.30 | [0.80, 10.15] | 2000 |
| MSU-MFSD | 20261001 | matched_deeppixbis | FA | -35.00 | [-45.83, -24.17] | 2000 |
| MSU-MFSD | 20261001 | matched_deeppixbis | BFA | -22.50 | [-35.00, -12.50] | 2000 |
| MSU-MFSD | 20261001 | matched_deeppixbis | AUROC_usable | 4.83 | [-2.28, 11.98] | 2000 |
| SiW-Mv2 | 20260917 | supervised_clip | FA | -6.08 | [-9.52, -2.61] | 2000 |
| SiW-Mv2 | 20260917 | supervised_clip | BFA | -27.20 | [-34.73, -19.50] | 2000 |
| SiW-Mv2 | 20260917 | supervised_clip | AUROC_usable | -2.80 | [-6.17, 0.30] | 2000 |
| SiW-Mv2 | 20260917 | fixed_equal_two_dino | FA | 6.63 | [4.06, 9.24] | 2000 |
| SiW-Mv2 | 20260917 | fixed_equal_two_dino | BFA | 16.86 | [11.85, 22.27] | 2000 |
| SiW-Mv2 | 20260917 | fixed_equal_two_dino | AUROC_usable | 0.15 | [-1.04, 1.32] | 2000 |
| SiW-Mv2 | 20260917 | matched_deeppixbis | FA | 39.78 | [34.61, 45.07] | 2000 |
| SiW-Mv2 | 20260917 | matched_deeppixbis | BFA | 31.03 | [25.19, 37.03] | 2000 |
| SiW-Mv2 | 20260917 | matched_deeppixbis | AUROC_usable | -10.82 | [-14.34, -7.15] | 2000 |
| SiW-Mv2 | 20260923 | supervised_clip | FA | -6.08 | [-9.52, -2.61] | 2000 |
| SiW-Mv2 | 20260923 | supervised_clip | BFA | -27.20 | [-34.73, -19.50] | 2000 |
| SiW-Mv2 | 20260923 | supervised_clip | AUROC_usable | -2.88 | [-6.25, 0.22] | 2000 |
| SiW-Mv2 | 20260923 | fixed_equal_two_dino | FA | 5.80 | [3.42, 8.29] | 2000 |
| SiW-Mv2 | 20260923 | fixed_equal_two_dino | BFA | 15.71 | [10.75, 20.93] | 2000 |
| SiW-Mv2 | 20260923 | fixed_equal_two_dino | AUROC_usable | -0.30 | [-1.51, 0.86] | 2000 |
| SiW-Mv2 | 20260923 | matched_deeppixbis | FA | 48.62 | [43.40, 54.06] | 2000 |
| SiW-Mv2 | 20260923 | matched_deeppixbis | BFA | 34.48 | [28.69, 40.45] | 2000 |
| SiW-Mv2 | 20260923 | matched_deeppixbis | AUROC_usable | -12.70 | [-16.38, -8.93] | 2000 |
| SiW-Mv2 | 20261001 | supervised_clip | FA | -6.08 | [-9.58, -2.62] | 2000 |
| SiW-Mv2 | 20261001 | supervised_clip | BFA | -26.05 | [-33.59, -18.43] | 2000 |
| SiW-Mv2 | 20261001 | supervised_clip | AUROC_usable | -3.28 | [-6.70, -0.15] | 2000 |
| SiW-Mv2 | 20261001 | fixed_equal_two_dino | FA | 6.63 | [4.17, 9.22] | 2000 |
| SiW-Mv2 | 20261001 | fixed_equal_two_dino | BFA | 15.71 | [10.59, 21.05] | 2000 |
| SiW-Mv2 | 20261001 | fixed_equal_two_dino | AUROC_usable | -1.74 | [-2.95, -0.55] | 2000 |
| SiW-Mv2 | 20261001 | matched_deeppixbis | FA | 32.04 | [27.12, 37.13] | 2000 |
| SiW-Mv2 | 20261001 | matched_deeppixbis | BFA | 21.84 | [14.73, 28.52] | 2000 |
| SiW-Mv2 | 20261001 | matched_deeppixbis | AUROC_usable | -12.51 | [-16.09, -8.85] | 2000 |

All 144 operating cases, including 1%/10% sensitivities:
[cases CSV](paper324-cases-v1.csv). All 756 conditional/paired interval records:
[intervals CSV](paper324-intervals-v1.csv).
Descriptive macro/worst-target results for every seed and alpha:
[closure JSON](paper324-comparison-v1.json).
