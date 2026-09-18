# Review Round 13 — Data firewall, anchor evidence và vòng đời freeze

Ngày: 2026-09-18. Repository: `lathevinh/fas`, branch `main`.

Commit được review: [`79c1f30df954947d10152da7ae0777ac55a9b70c`](https://github.com/lathevinh/fas/commit/79c1f30df954947d10152da7ae0777ac55a9b70c), `fix: harden PAD readiness gates`.

Đối chiếu với `6256a01` và `docs/31-review-response-round12.md`. Review này đánh giá code/protocol tại SHA trên; không tuyên bố đã chạy dữ liệu PAD thật.

## Verdict

**Round 12 đã được tiếp thu bằng code thật. Nhưng readiness vẫn chưa đồng nghĩa với protocol-safe: các probe mới tái hiện việc nhận test data làm source, chấp nhận calibration partition chỉ có attack và cấp pre-pilot readiness khi không có fitted anchor.**

Repo hiện là **schema-valid Stage-0 scaffold**, đúng như README đã sửa. Chưa có generated Stage-0 audit từ dữ liệu thật; chưa có Stage-1 pipeline hoặc prediction artifacts. Không nên quay lại nhận xét prose-only, cũng chưa thể gọi implementation-ready cho pilot.

Ưu tiên tiếp theo là nối validator với evidence có ý nghĩa và triển khai một pipeline synthetic chạy xuyên suốt. Không cần thêm kiến trúc, loss family hoặc endpoint mới.

## 1. Những sửa đổi được công nhận

| Round 12 | Trạng thái tại commit mới |
|---|---|
| Fake counts, null effects, empty configs được validator cũ cho qua | Các probe cũ đã có kiểm tra và tests tốt hơn; còn lỗ hổng mới bên dưới |
| Core prompt chứa print/display/mask | Đã bỏ family-specific string khỏi core |
| Hai unseen settings không đổi binary probability | Đã công khai rằng chỉ auxiliary concept endpoints khác nhau |
| Global pilot selection ảnh hưởng future target domains | Đã chọn và diễn đạt test-partition-unseen, không còn hứa strict outer-domain-unseen trong RQ/charter |
| Pre-pilot gate phụ thuộc empirical effects tương lai | Đã tách schema/data/pre-pilot/confirmatory, nhưng snapshot lifecycle chưa hoàn chỉnh |
| Branch calibration và risk dùng loss khác nhau | Đã thêm class-balanced branch loss, giữ natural-prevalence risk loss |
| Loss âm thầm clip probability ngoài [0,1] | Đã reject, có test |
| Confidence bound sau adaptive threshold selection | Đã đổi primary thành nominal empirical constraint |
| Bootstrap/zero-event semantics chưa rõ | Đã có paired subject resampling, 2,000 repetitions và inconclusive rules |

Đã chạy `python -m unittest discover -s tests -v`: **17/17 tests pass**. `--stage schema` trả `SCHEMA READY`; `--stage data` fail vì counts và private evidence thiếu, đúng với trạng thái repo. Data-stage failure hiện tại là expected blocker, không phải regression.

## 2. P1 — Official evaluation firewall chỉ tồn tại trong prose

Bằng chứng: [preregistration.py, L227–242](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/src/fas/preregistration.py#L227), [metadata reader, L326–346](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/src/fas/preregistration.py#L326), [manifest contract](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/manifests/README.md).

Metadata có `official_split`, nhưng validator không dùng trường này khi xác nhận role admissibility. Metadata→roles join chỉ so `(subject_id, video_id)` và binary label. Hash đúng chứng minh file không đổi so với summary, không chứng minh mẫu được phép tham gia training/calibration.

**Probe đã chạy:** lấy reconciled synthetic fixture của repo; đổi mọi OULU metadata row từ `official_split=train` thành `test`; giữ các role train/calibration/gate/routing, cập nhật đúng metadata hash. `validate_stage(root, 'data')` trả `[]`.

Đây không phải khẳng định real run đã leak — real run chưa tồn tại. Nhưng gate không thực thi chính firewall mà RQ2 mới chọn. Một parser gán nhầm official split vẫn có thể được chứng nhận data-ready. Response thừa nhận chưa có official parser là đúng; điều đó có nghĩa finding này vẫn mở, không thể đóng chỉ bằng arithmetic reconciliation.

**Sửa tối thiểu:** dataset-specific protocol map và version/hash cho official protocol; whitelist split nào được cấp từng source role; explicit evaluation-ID/subject exclusion; kiểm tra subject/video giao nhau giữa evaluation partition và mọi development role. Những mẫu không dùng phải có exclusion reason hoặc audited unused inventory. Hash phải đi cùng semantic checks. Thêm test chuyển `train → test` như probe trên, không chỉ subject overlap giữa source roles.

Với SiW-M, còn cần fold-specific admissibility theo held-out attack family; một permanent role file không tự chứng minh known-attack-only lineage. Khi chưa có per-fold generator/checker, không nên coi data-ready chung là đủ cho unseen-attack execution.

## 3. P1 — Pre-pilot vẫn có thể pass khi không có fitted anchor hoặc exact environment

Bằng chứng: [model-pin validation, L114–132](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/src/fas/preregistration.py#L114), [freeze validation, L101–111](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/src/fas/preregistration.py#L101).

`anchor_registry.json` chỉ được kiểm tra `.exists()`. Không parse JSON, không xác nhận entries, seed, fitting-source IDs, checkpoint/cache hash hoặc file tương ứng. Registry cũng không nằm trong `artifact_hashes()`. Vì vậy thay toàn bộ registry sau freeze không làm config/summary digest thay đổi.

Package pins chỉ cần truthy values: `packages={"torch":"latest"}` vẫn qua check. Candidate library revision `main` được chấp nhận như một exact pin. Lockfile được kiểm tra digest, nhưng nội dung arbitrary text vẫn pass. `created_from_commit` chỉ cần dài 40 ký tự, không cần là Git commit.

**Probe đã chạy trên một bản sao synthetic riêng:**

```text
packages = {"torch": "latest"}
lockfile content = "not an environment lock"  # hash khớp file
candidate.library_revision = "main"
candidate.weight_sha256 = "a" repeated 64 times
detector_weight_sha256 = "b" repeated 64 times
anchor_registry.json = "NOT JSON; NO FITTED ANCHOR"
created_from_commit = "z" repeated 40 times
artifact_sha256 = hashes của config/summary hiện tại
pilot attestation = attested_not_inspected

validate_stage(root, "pre-pilot") -> []
```

Data fixture trong probe có đầy đủ evidence nội bộ hợp lệ để cô lập lỗi này; không dùng fake CSV counts kiểu vòng trước.

**Sửa tối thiểu:** typed anchor registry chứa dataset/fold/seed, recipe hash, fitting/calibration/selection manifest references, backbone/checkpoint/prediction hashes; xác minh các artifact local hoặc content-addressed storage. Freeze phải bind registry và analysis code. Environment lock phải resolve exact versions/revisions và có verification report từ môi trường chạy. Không cần commit weights vào Git; cần kiểm chứng bytes được dùng khớp digest đã khai báo.

Đối với confirmatory, cần thêm **selected-candidate record**: candidate ID thuộc finite set, source thresholds, measured latency, pilot-selection result và tie-break outcome. Hiện `confirmatory` chỉ thêm numerical gate checks; chưa yêu cầu bằng chứng pilot đã chọn candidate nào. Đây là thiếu điều kiện readiness, không phải yêu cầu mở thêm candidate search.

## 4. P1 — Một mutable freeze record không biểu diễn được hai mốc freeze

Bằng chứng: [stage inheritance, L76–88](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/src/fas/preregistration.py#L76), [artifact hashes, L91–109](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/src/fas/preregistration.py#L91), [freeze writer, L18–33](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/scripts/write_freeze_record.py#L18).

Tách readiness stages là đúng hướng. Nhưng tất cả config, bao gồm `evaluation_v1.yaml`, vẫn bị bind vào một `results/stage0/freeze_record.json`. Sau pilot, cập nhật source-derived effects từ pending sang giá trị frozen — một bước được protocol cho phép — làm pre-pilot snapshot mismatch. Confirmatory lại kế thừa kiểm tra snapshot này.

**Probe:** sau một pre-pilot pass, chỉ cập nhật effect status/value trong evaluation config. Kết quả thành `freeze record hashes do not match current artifacts`. Đây là invalidation đúng nếu file supposed immutable, nhưng lifecycle hiện không phân biệt phần pre-pilot immutable với phần được hoàn thiện sau pilot.

Writer có thể ghi đè cùng path và chỉ yêu cầu data-ready. Do đó workaround hiện là rewrite record; validator không kiểm tra lịch sử để chứng minh core prompts/candidate set đã giữ nguyên qua thời điểm pilot inspection. Git có thể giữ lịch sử nếu người vận hành commit đúng, nhưng gate không yêu cầu hay xác minh chuỗi đó.

README Stage 0 còn hướng dẫn write/commit freeze rồi obtain attestation; nếu attestation được ghi vào config sau đó thì cũng invalidates snapshot.

**Sửa:** hai snapshot bất biến có scope rõ:

1. Pre-pilot record bind prompts, candidate set, recipe, environment, source manifests, anchor registry và attestation event.
2. Pre-confirmatory record bind selected candidate, numerical gates, analysis code và **hash của pre-pilot record**. Check immutable subset chưa đổi; chỉ cho phép các trường hậu-pilot được khai báo trước.

Writer không silently overwrite event cũ. Ghi actual commit lineage và kiểm tra file bytes phù hợp snapshot; dirty-tree handling phải rõ. Không cần chữ ký mật mã để bắt đầu, nhưng cần audit trail có thể kiểm tra.

Portability phụ: `str(path.relative_to(root))` tạo `configs\\...` trên Windows và `configs/...` trên Linux. Config environment chọn Linux còn review đang chạy Windows. Dùng `as_posix()` cho manifest keys và thống nhất byte/line-ending policy để cùng artifact không mismatch do nền tảng.

## 5. P2 — Role evidence có counts nhưng chưa chứng minh partition khả dụng

Bằng chứng: [split validation, L285–309](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/src/fas/preregistration.py#L285), [reconciliation, L366–389](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/src/fas/preregistration.py#L366).

Summary yêu cầu subjects và attack videos dương cho required roles, không có bona-fide count theo role. Branch loss mới đúng đắn reject one-class domain, nhưng data validator lại cho partition đó qua.

**Probe A:** trong OULU synthetic fixture, chuyển bona-fide subject của `branch_calibration` sang `train`, cập nhật subject counts và role hash. Branch calibration chỉ còn attack; `data` vẫn trả `[]`. Đây là mismatch cụ thể giữa data-ready và precondition của branch-calibration loss.

**Probe B:** chuyển bona-fide train row của OULU sang `g_attack`; giữ `g_attack_subjects` và `g_attack_attack_videos` trống như một role không áp dụng cho MICO. Cập nhật train count/hash. `data` vẫn trả `[]`. Lý do: role validity kiểm membership trong union của mọi roles, còn reconciliation bỏ qua summary ô trống/zero. Actual row trong role không áp dụng không bị reject.

**Sửa:** validate actual allowed roles theo dataset/track, kể cả summary trống; so mọi aggregate với evidence, bao gồm zero/not-applicable. Thêm bona/attack counts theo role và class-presence constraints nơi thuật toán cần hai lớp. Minimum event counts cho inference có thể chờ source-derived gates, nhưng class feasibility cho branch fitter phải kiểm tra được ngay Stage 0.

## 6. P2 — Source-validation dùng để chọn checkpoint chưa có role cụ thể

Bằng chứng: [source recipe, L4–23](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/configs/source_recipe_v1.yaml#L4), [protocol lineage, L190–206](https://github.com/lathevinh/fas/blob/79c1f30df954947d10152da7ae0777ac55a9b70c/docs/04-data-and-protocols.md#L190).

Recipe mới chọn checkpoint bằng lowest source-validation domain-macro ACER. Role contract chỉ có train, branch_calibration, g_domain/g_attack, routing_validation. Hai gate holdouts và routing partition đã có nhiệm vụ riêng; source-training subvalidation được nhắc trong prose nhưng chưa có assignment/key cụ thể. Chưa chốt ACER checkpoint score dùng raw threshold nào hay fitted calibration nào, và phép fit đó dùng partition nào.

Điểm này chưa phải leakage đã xảy ra. Nó là chỗ implementer dễ tái dùng branch-calibration hoặc routing validation cho early stopping rồi tưởng vẫn đúng role contract.

Không nhất thiết thêm một permanent partition làm thiếu dữ liệu. Có thể chọn deterministic inner validation bên trong allowed train remainder, hoặc fixed-epoch rule nếu đó là quyết định khoa học phù hợp. Nhưng phải serialize inner split, threshold semantics và per-fold exclusions; pipeline không nên tự quyết lúc chạy.

Tương tự, hai `primary_alpha` và hai latency ceilings hiện trùng nhau nhưng chưa có consistency check. Nên dùng một nguồn chuẩn hoặc fail khi mâu thuẫn. Numeric effects/validity threshold cần domain bounds theo metric; chỉ kiểm tra positive cho AUPR threshold vẫn cho giá trị >1.

## 7. Stage 0/1: điều gì vẫn chưa có

Tracked tree vẫn không có official metadata parser, deterministic role generator, frame/crop extractor, APCER/BPCER evaluator, calibration fitter/serialization, DINO head trainer, candidate selector hoặc prediction-cache generator. `results/stage0/` chỉ có README; summary counts còn `not_audited`; model pins và effects còn pending.

Response đã thừa nhận những thiếu sót này, nên không xem chúng là claim sai. Nhưng **thiếu restricted datasets chỉ ngăn empirical audit/run; không ngăn synthetic implementation**. Các module metric, role/fold generator và fitter có thể được triển khai và kiểm thử mà không cần ảnh sinh trắc học thật.

Milestone tiếp theo nên là một lệnh chạy trên synthetic fixture, tạo manifest → source fit/calibration → threshold → prediction table → rescue metrics, có lineage hashes xuyên suốt. Test phải bắt:

- evaluation row lọt vào source role;
- một role thiếu bona-fide hoặc có role không áp dụng;
- malformed/empty anchor registry và wrong checkpoint/cache digest;
- một seed dùng anchor khác giữa heterogeneous và homogeneous pair;
- detector failure/abstention không làm mất end-to-end denominator;
- legitimate post-pilot update pass nhưng core/candidate mutation bị reject;
- zero-FA/one-class risk evaluation trả inconclusive, không NaN được âm thầm aggregate.

Synthetic smoke chỉ chứng minh đường thực thi và accounting, không phải scientific PAD result. Sau đó mới đưa official source metadata vào cùng pipeline.

## 8. Tái hiện các probe

Các probe chạy độc lập trên temporary copies tạo bởi `PreregistrationTest._copy()` và `_write_synthetic_evidence()` từ test suite của repo. Mỗi thay đổi evidence đều cập nhật đúng summary/hash để không bị lỗi hash che semantic bug. Không sửa private data hoặc tracked source trong clone.

Observed output:

```text
all_OULU_roles_from_test_partition: []
branch_calibration_attack_only: []
undeclared_inapplicable_g_attack_row: []
prepilot_invalid_registry_floating_pins_noncommit: []
postpilot_effect_update: ['freeze record hashes do not match current artifacts']
```

`[]` nghĩa là không có validation errors. Đoạn ngắn dưới đây tái hiện firewall finding trực tiếp tại repository root, dùng fixture hiện có và không cần datasets:

```python
import csv
import sys
from pathlib import Path

repo = Path.cwd()
sys.path[:0] = [str(repo / 'src'), str(repo / 'tests')]
from fas.preregistration import validate_stage
from test_preregistration import PreregistrationTest

fixture = PreregistrationTest()
with fixture._copy() as root:
    fixture._write_synthetic_evidence(root)
    metadata = root / 'manifests/private/oulu_npu_metadata.csv'
    with metadata.open(newline='', encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row['official_split'] = 'test'
    fixture._write_csv(metadata, tuple(rows[0]), rows)
    fixture._update_hash(
        root / 'manifests/dataset_summary.csv',
        'OULU-NPU', 'manifest_sha256', metadata,
    )
    print(validate_stage(root, 'data'))  # observed: []
```

## 9. Scope

Đã pull fast-forward tới SHA ghi đầu bài, đọc diff/config/source/tests và protocol liên quan, chạy 17 tests cùng schema/data checks và năm probe outputs ở trên. Không chạy GPU, không tải restricted datasets, không đo latency/accuracy, không refresh literature. Findings là implementation/protocol review, không phải kết luận về hiệu quả mô hình.

Review này được chuẩn bị để commit trực tiếp thành `docs/32-chatgpt-review-round13.md` theo yêu cầu của chủ repo. Không đề nghị thay đổi implementation trong commit review.
