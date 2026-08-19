# C09 final source-family acceptance matrix

> Developmental query controls only; every row requires a fresh D05 systematic rerun after protocol approval/freeze.

| Family | Source | Query | Records | Complete | Sample R/U | Burden | Sentinel | Disposition | Manifest SHA-256 |
|---|---|---|---:|---|---:|---:|---|---|---|
| S1 | Semantic Scholar | `S2-S1I3` | 331 | Yes | 16/3 | 38.0% | Pass | `accepted_complete` | `5cf1e6a7714da67d7024088eea303b62f88ca3115a68fb48ae304ed35daf40c5` |
| S2 | OpenAlex | `OA-S2I2` | 257 | Yes | 38/6 | 88.0% | Pass | `accepted_bounded_integrative_union` | `28a990eded5100d5705ec37b020bcf67ca14631f1b6e97d0f29b82751012a372` |
| S3 | OpenAlex | `OA-S3R3` | 134 | Yes | 9/2 | 22.0% | Pass | `accepted_complete` | `a0a7d827b2e542babd61df035288fdabb73410a318bb7f66c149c42cda869b12` |
| S3 | Semantic Scholar | `S2-S3R3` | 15 | Yes | 14/0 | 93.3% | Pass | `accepted_complete` | `b34bf698cf0ede5fd66f350d4be2d18c832ff5f46523003979acd7fdc7b0fe53` |
| S4/S5R | OpenAlex | `OA-S4R6` | 564 | Yes | 15/5 | 40.0% | Pass | `accepted_complete` | `2fe4b053d6ba00b6198660e66ab3f1808b45c956dc0b1ea479d600ae5605b060` |
| S4/S5R | Semantic Scholar | `S2-S4R5` | 279 | Yes | 13/12 | 50.0% | Pass | `accepted_complete` | `348aa553f5082514ce85aae4e829cc8c494410dfe57fbe15271982b296bf2102` |
| S4/S5R | arXiv | `AX-S5R` | 187 | Yes | 16/12 | 56.0% | Pass | `accepted_complete_mapped` | `79bc0ff650a16d5acb27fb4331940080fcf5a9533dd48856e3d96a21b90d70a6` |
| S5T | OpenAlex | `OA-S5TR4` | 137 | Yes | 39/6 | 90.0% | Pass | `accepted_complete` | `e9c946ba5561c4a9fd9f8f4a2fead8359cbdde35ac8e9d5021f86af966caa482` |
| S5T | arXiv | `AX-S5T` | 394 | Yes | 23/1 | 48.0% | Pass | `accepted_complete_mapped` | `16de14545695bf78deb8a64e5cb2d4f50ac2171cf5402ae3e5795b7c1a6f3e84` |
| S5S | OpenAlex | `OA-S5SR7` | 19 | Yes | 8/2 | 52.6% | Pass | `accepted_complete` | `ec1e0922d5805a4af5553824e8bb6cd86343b31ced6f3052474dd3d575488b5b` |
| S5S | arXiv | `AX-S5S` | 1,333 | Yes | 6/7 | 13.0% | Pass | `accepted_complete_mapped` | `c7898ce9cfd57a3404a5b5b0009aa38017ccc8614120a87a2124110ccd18b58c` |
| S6 | OpenAlex | `OA-S6R8` | 231 | Yes | 20/6 | 52.0% | Pass | `accepted_complete` | `0b7916cfff56e233130d27ef3624bb2f4eddb5d4fca268c8cdccb7f78db9f96e` |
| S6 | arXiv | `AX-S6R` | 29 | Yes | 10/0 | 34.5% | Pass | `accepted_complete_mapped` | `5e2b8e9e0497ec41f8095c5cc54363948572f74808222705676644eed9761051` |
| S7 | OpenAlex | `OA-S7R4` | 49 | Yes | 18/11 | 59.2% | Pass | `accepted_complete` | `43e07612ac071c4ce9d3c5031a50f60ffd0019792edf70d4c27b6c2520e5547e` |
| S7 | Semantic Scholar | `S2-S7R4` | 19 | Yes | 12/3 | 78.9% | Pass | `accepted_complete` | `c70562a2801220e7ca085700042e6cfb53b678931f728b3e1968d5602102135e` |
| S7 | arXiv | `AX-S7R4` | 7 | Yes | 5/2 | 100.0% | Pass | `accepted_complete` | `5a07947420080a0d079e2edec46d06b5df303a196c17adee406c19088e1b8de1` |
| S8 | OpenAlex | `OA-S8R6` | 1,097 | Yes | 39/9 | 48.0% | Pass | `accepted_complete` | `c8755a60f3866d03df53cf5205fcfe82d39a31771cd54a4dfc5901bba4b58c5f` |
| S8 | Semantic Scholar | `S2-S8R6` | 794 | Yes | 18/3 | 42.0% | Pass | `accepted_complete` | `a23416421507f8532643acbdcc668aa5f4c1edf301d9494b5b49e514e11c1fc4` |

S2 is the sole bounded-union disposition: its complete 257-record discovery component is combined only for known-item control with the predeclared exact-title recovery documented in `gate2/output/development/c08_bounded_union_acceptance_20260816.json`. It is not a fresh OA-S2I3 export.

The matrix covers all 18 source-family pairs in the approved non-Cartesian allocation. Counts overlap across sources and families and are not deduplicated, screened, included, or PRISMA counts.
