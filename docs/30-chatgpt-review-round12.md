# Review Round 12 — Executable readiness của PAD

Ngày review: 2026-09-18 (Asia/Saigon)  
Repository: `lathevinh/fas`, branch `main`  
Commit được kiểm tra: [`6256a01df2e1990d98801086e112b98c2831302d`](https://github.com/lathevinh/fas/commit/6256a01df2e1990d98801086e112b98c2831302d) — `feat: freeze executable PAD preregistration`  
Đối chiếu: Round 11 và `docs/29-review-response-round11.md`.

## Kết luận

**Repo đã vượt khỏi prose-only, nhưng mới có scaffold kiểm tra preregistration và primitive calibration. Chưa hoàn tất Stage 0, chưa có executable Stage 1.**

Round 11 được tiếp thu thực chất: có bảy config, hai bảng manifest mẫu, validator, calibration monotone và bảy tests chạy được. Không nên tiếp tục nhận xét rằng repo chỉ có tài liệu. Tuy nhiên, câu “configuration-frozen” hiện mạnh hơn bằng chứng: nhiều quyết định chưa được cụ thể hóa và validator có thể cấp readiness cho dữ liệu vô nghĩa.

Khuyến nghị: tiếp tục xây dựng Stage 0 và smoke test Stage 1 bằng dữ liệu synthetic/source được phép; **chưa dùng `PREREGISTRATION READY` hiện tại làm điều kiện đủ để mở pilot hoặc chạy confirmatory**. Không cần thêm kiến trúc.

## 1. Kiểm kê artifact thực tế

| Hạng mục | Bằng chứng tại commit | Đánh giá |
|---|---|---|
| Core/aux prompts, candidates, seeds, preprocessing, evaluation, pilot | 7 file trong `configs/` | Có lựa chọn cụ thể, nhưng schema/lineage chưa đầy đủ |
| Readiness CLI | `scripts/validate_preregistration.py`, `src/fas/preregistration.py` | Chạy được, chưa chứng minh tính hợp lệ của protocol |
| Calibration | `src/fas/calibration.py` | Có transform với slope dương và hàm loss; chưa có fitting |
| Tests | `tests/test_calibration.py`, `tests/test_preregistration.py` | 7/7 pass |
| Dataset/split summaries | `manifests/*.csv` | Cả năm dataset đều `not_audited`, counts/hash trống |
| Role manifests và split audit | Không có file role-level trong tracked tree | Chưa có bằng chứng subject/video separation |
| Stage-0 results | `results/stage0/README.md` | Chỉ hướng dẫn, chưa có generated audit report |
| Stage-1 pipeline | Không có extractor, trainer, calibration fitter, inference/evaluator CLI | Chưa executable |
| Stage-1 evidence | Không có prediction cache, fitted anchor identity, rescue table, latency output | Chưa có kết quả |
| Environment | Không có dependency manifest/lock trong tracked tree | Các primitive hiện chạy bằng standard library; môi trường model chưa tái lập được |

Đây là inventory của commit đã tải, không phải khẳng định tác giả không có dữ liệu hoặc kết quả riêng ngoài repo.

## 2. Kết quả kiểm tra trực tiếp

Chạy từ repository root:

```text
python -m unittest discover -s tests -v
  7 tests: PASS

python scripts/validate_preregistration.py --allow-incomplete-counts
  exit 0: CONFIG FROZEN; COUNTS PENDING

python scripts/validate_preregistration.py
  exit 1: NOT READY
  attestation pending; effect/validity thresholds pending;
  five datasets unaudited; counts and hashes missing
```

Strict failure trên bản gốc là **hành vi đúng và được dự kiến**, không phải regression. Nhưng negative probes trên bản sao tạm phát hiện:

```text
strict_with_null_effects_fake_counts_no_role_files: []
permissive_with_empty_critical_configs: []
loss_accepts_probabilities_outside_unit_interval: 9.999778782803785e-13
```

`[]` nghĩa là validator không trả lỗi. Script tái hiện nằm cạnh review: `probe_readiness.py`; chạy từ thư mục cha của clone bằng `python review_outputs/probe_readiness.py`. Probe chỉ thay đổi bản sao trong temporary directory, không sửa source repository.

## 3. Findings ưu tiên

### F1 — P1: Readiness gate kiểm tra nhãn trạng thái, chưa kiểm tra bằng chứng

Bằng chứng: [preregistration.py, L68–108](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/src/fas/preregistration.py#L68).

Strict mode chỉ yêu cầu effect/validity `status == frozen`; không xác nhận giá trị effect có tồn tại, hữu hạn, đúng miền hoặc khác zero. CSV chỉ được kiểm tra nonempty và `audit_status == complete`; không kiểm tra schema đầy đủ, integer counts, dataset coverage, duplicate rows, arithmetic, role disjointness hay hash thực tế.

**Tái hiện:** đổi attestation thành `attested_not_inspected`, hai status thành `frozen`, điền `NOT_A_COUNT_OR_HASH` vào các ô metadata/count/hash. Giữ nguyên effect `null`, không tạo role manifests. `validate(..., require_counts=True)` vẫn trả `[]`. CLI dùng trực tiếp kết quả này để in `PREREGISTRATION READY`.

Permissive mode còn chấp nhận `{}` cho preprocessing, evaluation và auxiliary prompts. Vì vậy output `CONFIG FROZEN` cũng không chứng minh config schema đầy đủ. Hàm hash chỉ tính digest của nội dung hiện tại, không so với một freeze record đã lưu; băm file sau khi sửa không chứng minh file không đổi.

**Yêu cầu trước pilot:** typed schema và negative tests; required columns/datasets; counts nguyên không âm với điều kiện nonempty cho từng role bắt buộc; applicability riêng MICO/SiW-M; aggregate reconciliation từ role manifests; kiểm tra overlap và hash file thực; numerical effects/validity criteria; freeze record gồm commit/config hashes và attestation. Role manifests có thể giữ local/private, còn báo cáo không nhạy cảm được commit. Không cần công khai dữ liệu hạn chế.

### F2 — P1: Core prompt chứa attack-family text mà downstream-unseen tuyên bố loại bỏ

Bằng chứng: [prompts_core_v1.yaml, L16](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/configs/prompts_core_v1.yaml#L16) và [protocol, L38–60](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/docs/04-data-and-protocols.md#L38).

Core spoof prompt mới là `a printed, displayed, or masked face presentation`. Với hold-out ở cấp family print/replay/mask, loại matching prompts khỏi auxiliary bank **không loại tên family khỏi core binary score**. Đây là mâu thuẫn giữa artifact mới và định nghĩa downstream-unseen có exclusion text. Nếu chỉ hold-out subtype và cho phép generic family wording, phải ghi rõ trường hợp đó; không thể suy rộng thành family-unseen có text exclusion.

Sửa trước inspection: dùng core thực sự generic và freeze phiên bản mới, hoặc đổi tên/claim thành downstream-image-unseen có semantic family exposure. Không sửa core khác nhau sau khi thấy kết quả từng fold.

Ngoài ra, auxiliary scores không tham gia binary probability/risk primary. Nếu hai setting chỉ khác auxiliary text thì primary PAD predictions phải giống nhau. Cần nêu rõ endpoint nào thực sự khác, thay vì trình bày hai bảng binary PAD như hai hệ thống khác biệt.

### F3 — P1: Stage-1 selection chưa đủ xác định để tái lập

Bằng chứng: [pilot_selection_v1.yaml](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/configs/pilot_selection_v1.yaml), [vlm_candidates_v1.yaml](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/configs/vlm_candidates_v1.yaml), [experiment plan, L324](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/docs/05-experiment-plan.md#L324).

Seed và tên model không xác định duy nhất fitted DINO anchor. Config chỉ ghi “one fixed source-trained selection checkpoint per MICO fold”; chưa có recipe đầy đủ, head/attention-pooling specification, checkpoint selection rule hoặc hash fitted checkpoint/cache. Có thể freeze recipe trước source training rồi freeze checkpoint trước pilot; không cần giả định checkpoint đã tồn tại ngay bây giờ.

Candidate IDs rõ hơn vòng trước nhưng `immutable_ids: true` không pin bytes: chưa có library revision/version, pretrained-weight digest và detector-weight identity. Source operating threshold mới được mô tả là “recompute independently”; chưa chốt primary alpha, pooled/worst-source rule, tie handling hoặc infeasible fallback trong config. Latency ceiling chưa nói rõ đo riêng VLM hay toàn dual pipeline, decode/crop có nằm trong preprocessing không, và xử lý khi không candidate nào đạt.

DINO resolution config là 518, trong khi ví dụ training còn 448. Một tài liệu gọi ví dụ là indicative không đủ gây lỗi ngay, nhưng cần quy tắc config là nguồn chuẩn để người triển khai không dùng hai recipe khác nhau.

**Artifact tối thiểu:** executable source-only recipe, environment lock, model/checkpoint hashes, anchor prediction hash, threshold-selection specification, latency scope và deterministic candidate selector. Đây là điều kiện có thể kiểm thử trước khi chạy dữ liệu thật.

### F4 — P1: Global pilot selection cần audit đường đi dữ liệu qua các MICO folds

Bằng chứng: [RQ2](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/docs/02-research-questions.md#L35) và [source/target roles](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/docs/04-data-and-protocols.md#L208).

MSU là pilot, còn OULU/CASIA/Replay là confirmatory targets. Để đánh giá candidate trên MSU theo MICO, selection anchor/calibrators dùng OULU/CASIA/Replay làm source. Candidate được chọn sau đó dùng toàn cục. Khi OULU trở thành target, OULU đã có thể ảnh hưởng candidate qua đường source fit của pilot.

Đây **không tự động là test-set leakage** nếu chỉ dùng official source train/dev và giữ test subjects tách biệt. Tuy nhiên nó không tương thích với cách đọc tuyệt đối “confirmatory-target data never ... select any model”, và không đủ để gọi mọi confirmatory domain hoàn toàn untouched. Repo chưa có manifests để phân biệt hai trường hợp.

Chốt estimand và scope của firewall: (a) test-partition-unseen với global development có dùng train/dev của các domain, phải mô tả minh bạch; hoặc (b) strict outer-domain-unseen, trong đó toàn bộ candidate/effect selection lineage cho target T loại T, kể cả đường qua pilot. Không kết luận có leakage thực tế khi chưa có run; đây là lỗ hổng protocol cần đóng trước khi code cố định nó.

### F5 — P2: Readiness đang trộn pre-pilot và pre-confirmatory gates

Bằng chứng: [evaluation config](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/configs/evaluation_v1.yaml), [Stage-0 exit](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/docs/05-experiment-plan.md#L24), [freeze timeline](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/docs/04-data-and-protocols.md#L216).

Strict gate trước pilot đòi cả effect thresholds và OOF-to-final validity threshold, trong khi các ngưỡng này cần source pseudo-shift/risk experiments và docs khác cho phép khóa continuation thresholds sau pilot, trước confirmatory. Có thể tính cho mọi candidate trước pilot, nhưng repo chưa quy định như vậy. Hiện chưa rõ source-only experiments nào được phép chạy khi readiness fail và model nào sinh ra ngưỡng.

Nên tách trạng thái: schema-valid → data-audited → pre-pilot-ready → selected-config-frozen → confirmatory-ready. Mỗi trạng thái có dependencies riêng. Pending empirical thresholds không được ngăn source-only work cần thiết để ước lượng chính chúng.

Config cũng chưa có trường số cho `N_min`, `gamma`, diagnostic APCER, branch competency, primary security alpha hoặc beta routing; validity mới có status mà chưa có threshold value/metric/direction. Không nên chỉ thêm status để đóng review.

### F6 — P2: Finite-sample security rule chưa có định nghĩa inference sau threshold selection

Bằng chứng: [protocol, L237–243](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/docs/04-data-and-protocols.md#L237).

Repo chọn threshold trên validation và yêu cầu từng source có `UCB_95%(APCER_d) <= alpha`. Một pointwise binomial interval ở threshold cố định không tự động thành guarantee cho threshold được chọn thích nghi từ nhiều threshold. Tương tự, các bound 95% riêng từng domain không tự động tạo joint 95% guarantee cho tất cả domains.

Trước khi dùng từ statistically constrained/certified, freeze cơ chế inference: tập certification tách riêng, hoặc selection-aware/order-statistic/simultaneous rule phù hợp và đã được kiểm thử. Xác định rõ coverage là per-domain hay joint. Nếu chưa triển khai, gọi nominal empirical constraint là chính xác hơn.

Video cũng không mặc nhiên độc lập khi cùng subject/instrument. Config chọn subject bootstrap nhưng summary mới chỉ đếm subjects/videos tổng. Stage 0 cần báo cluster structure và xác định đơn vị independent event; không dùng số video như bằng chứng độc lập chỉ vì mỗi video có một frame.

### F7 — P2: Có calibration transform, chưa có calibration procedure đúng hai mục tiêu loss

Bằng chứng: [calibration.py](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/src/fas/calibration.py) và [method calibration loss](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/docs/03-method.md#L20).

`MonotoneAffineCalibrator` nhận theta/intercept có sẵn và transform; không fit. Hàm loss duy nhất giữ natural prevalence trong domain, phù hợp risk fitting. Branch calibration trong method lại cần class-balanced loss trong mỗi domain rồi equal-domain average. Chưa có implementation branch loss đó. Đây là thiếu implementation, **chưa phải bằng chứng pipeline đã fit sai**, vì pipeline chưa tồn tại.

Thêm hai hàm/entry points có tên rõ, tests trên class imbalance, fitter với convergence/failure policy và checkpoint serialization. Freeze numeric regularization/solver cho risk thay vì chỉ nói “fixed”.

Lỗi nhỏ đã tái hiện: loss chấp nhận probability -5 và 5 rồi clip thành gần hoàn hảo nếu labels là 0 và 1. Nên reject giá trị ngoài [0,1] trước numerical clipping để bắt lỗi truyền logits vào API probabilities. Positive slope đảm bảo monotonicity toán học; finite precision có thể saturation thành bằng nhau, nên không hứa strict ordering trên mọi finite logit.

### F8 — P2: Claim hierarchy chưa thành quy tắc thống kê có thể thực thi

Bằng chứng: [Stage-1 gates](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/docs/05-experiment-plan.md#L102) và [confirmatory aggregation](https://github.com/lathevinh/fas/blob/6256a01df2e1990d98801086e112b98c2831302d/docs/05-experiment-plan.md#L265).

Ordered claims là tiến bộ. Nhưng rule macro positive + 2/3 domains + 2/3 seeds vẫn chưa xác định minimum-effect/CI test cuối cùng. Chưa có bootstrap repetitions, CI construction, xử lý zero DINO false accepts hoặc one-class risk labels, và cách kết hợp seed variance với sample uncertainty. Cùng subject predictions qua ba seed cần được ghép khi resampling nếu tính một CI cho seed-averaged paired delta; không coi ba seed là ba bộ người độc lập.

Preregister “inconclusive/underpowered” riêng với “fail” khi `N_FA < N_min`; không tự chuyển sang threshold khác sau khi nhìn target. Với delta-CF trừ max hai single-branch AUPR, phải tính lại max trong mỗi paired resample hoặc dùng một comparator đã khóa; không chọn comparator thuận lợi sau target.

## 4. Những sửa đổi Round 11 được công nhận

- Wording domain shift và attack shift đã tách, không cần thêm joint-shift track.
- Pilot identity, candidate list, core strings, exact seeds, device/latency parameters đã cụ thể hơn rõ rệt.
- Repo thừa nhận data chưa audited và results chưa có; không bịa counts từ paper.
- Science features vẫn loại margin; operational margin có attribution riêng.
- Same cached DINO anchor policy, detector-success risk population và end-to-end transaction population được ghi rõ.
- Monotone slope implementation và natural-prevalence equal-domain loss primitive chạy qua tests hiện có.

Các điểm này nên giữ, không mở lại architecture discussion.

## 5. Deliverables cho vòng kế tiếp

Theo thứ tự phụ thuộc:

1. Đóng F1/F2/F4: validator phải reject negative probes; thống nhất prompt semantics và outer-fold selection lineage.
2. Stage-0 metadata parser + deterministic role generator + leakage checker; xuất counts theo role/class/family/cluster, official split identity và hash reconciliation. Không cần commit ảnh/video.
3. Metrics tests với synthetic fixtures: label polarity, APCER/BPCER denominators, detector failure, abstention, empty classes, zero rescue denominator, paired anchor IDs. CLI tạo báo cáo JSON/CSV có version/hash.
4. Stage-1 smoke run: frozen feature extraction → head fit → branch calibration fit → source threshold selection → prediction cache → paired rescue/evaluation. Synthetic/source smoke phải được ghi nhãn, không trình bày thành kết quả khoa học.
5. Freeze source recipes, anchor/model bytes, candidate selection/latency rules, effect derivation và analysis code ở đúng stage; chỉ mở pilot khi gate tương ứng có bằng chứng thật.

Vòng tới nên review generated audit report và prediction lineage. Một response Markdown nhận lỗi nhưng không có những artifact này sẽ chưa thay đổi verdict.

## 6. Phạm vi và giới hạn kiểm tra

Đã clone GitHub, đọc config/source/tests và các method/protocol/experiment documents tại SHA nêu trên; chạy bảy tests, hai chế độ validator và ba negative probes. Working tree của clone sạch sau review. Không sửa hoặc push repository.

Không có restricted dataset, GPU experiment hoặc fitted model trong tracked tree; vì vậy chưa kiểm chứng official split feasibility, model loading, latency, accuracy hay hiệu quả PAD. Không thực hiện literature refresh trong vòng này: các findings tập trung vào artifact và tính nhất quán nội bộ, không đưa ra kết luận mới về novelty so với literature.
