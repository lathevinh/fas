# Review Round 15 — Chấp thuận bộ lõi; khóa đúng đại lượng được so sánh

Ngày: 2026-09-18. Repository: `lathevinh/fas`, branch `main`.

Commit được review: [`81f4160957152032f10b7219d002702f4bd9018c`](https://github.com/lathevinh/fas/commit/81f4160957152032f10b7219d002702f4bd9018c). Đối chiếu Round 14, `docs/35-review-response-round14.md` và các normative documents `00`–`06`.

## 1. Quyết định của reviewer

**METHODOLOGY ACCEPTED FOR IMPLEMENTATION PLANNING.**

Ba quyết định Round 14 đã được đưa vào phương pháp chính, không chỉ ghi trong response:

- một OpenCLIP ViT-B/16 cố định, không còn global labeled pilot hoặc primary candidate search;
- fixed CLS + mean-patch pooling cho DINO, giữ frozen-feature design đơn giản;
- failure-risk transfer là core; fusion rescue, explicit disagreement và conditional routing có claim riêng.

Tôi không đề nghị thêm backbone, module, loss family, benchmark hoặc kiến trúc ở vòng này. Không còn lý do từ review này để giữ đề tài trong một chuỗi sửa prose vô hạn trước khi lập kế hoạch triển khai.

Sự chấp thuận này là cho **research design đáng kiểm chứng**, không phải xác nhận mô hình có hiệu quả hay chắc được nhận ở journal Q3. Các điểm ở mục 3–6 là ràng buộc cho cách đặc tả phép so sánh và đọc kết quả; cần đưa vào analysis specification trước target evaluation, nhưng không đòi một vòng thiết kế kiến trúc mới hoặc code chứng minh ngay.

Vòng này chỉ review và xuất Markdown. Không lập coding plan, không sửa implementation, không chạy experiment hoặc mở target labels.

## 2. Những gì đã đóng được

| Vấn đề trước | Trạng thái mới | Nhận xét |
|---|---|---|
| Candidate selection có thể đi vào pseudo-domain risk records | Primary VLM fixed a priori | Đã loại selector này khỏi đường ảnh hưởng; head/calibration/threshold vẫn phải fold-local |
| Learned pooling làm “cache once” thiếu chính xác | Fixed mean pooling | Đã đơn giản hóa hợp lý; không ảnh hưởng câu hỏi novelty |
| Không có fusion rescue thì dừng risk study | RQ1 là failure-risk transfer; classifier claim riêng | Đã sửa đúng quan hệ logic |
| Routing optional nhưng lại là điều kiện sống còn của bài | Charter, novelty và response tách routing | Đã sửa scope cốt lõi |
| Hứa calibrated risk quá sớm | Title dùng failure-risk estimation | Phù hợp hơn với shift; probability calibration vẫn cần bằng chứng riêng |
| Domain-OOF chỉ là một lựa chọn không được kiểm định | Matched sample-OOF trở thành control cho RQ1 | Đúng hướng attribution |
| Positive point estimate quá yếu | Có macro LCB, consistency và harm constraints | Tốt hơn; còn phải gắn mỗi rule với đúng contrast |

Bộ lõi lúc này đủ rõ: frozen DINO và OpenCLIP độc lập → source branch calibration → fixed average classifier → source-domain OOF risk → selective evaluation, trên bốn MICO outer folds. SiW-M là một claim riêng phụ thuộc khả năng tiếp cận dữ liệu, không phải lý do làm core paper phình thêm.

## 3. Điểm quan trọng nhất: RQ1 và RQ2 không dùng cùng một kiểu AUPR contrast

Bằng chứng: [RQ1/RQ2](https://github.com/lathevinh/fas/blob/81f4160957152032f10b7219d002702f4bd9018c/docs/02-research-questions.md#L3), [hai result tables](https://github.com/lathevinh/fas/blob/81f4160957152032f10b7219d002702f4bd9018c/docs/05-experiment-plan.md#L198), [ablation matrix](https://github.com/lathevinh/fas/blob/81f4160957152032f10b7219d002702f4bd9018c/docs/05-experiment-plan.md#L314).

Repo đã nói phải giữ fixed error labels khi so risk estimators. Tuy nhiên RQ2 mới yêu cầu thắng cả same-family **system**, trong khi matrix row M vẫn chỉ có calibrated average và `Abstain = No`. Cần làm rõ phép so sánh đó trước khi diễn giải heterogeneous risk advantage.

### RQ1: transfer của risk estimator, giữ classifier cố định

Với target t và seed s, đặt `e_DV` là error labels của cùng final heterogeneous classifier. Một contrast rõ ràng là:

\[
\Delta_{OOF,t,s}=AP(e_{DV},r^{domain}_{DVd})-AP(e_{DV},r^{sample}_{DVd}).
\]

Hai risk models dùng cùng feature family, loss, regularization và final base predictions; khác cách sinh source training records. AP ở đây nên được định nghĩa cụ thể là average precision với error=1 và score cao nghĩa là risk cao, tránh một implementation dùng trapezoidal PR-AUC còn implementation khác dùng AP.

Đây là phép so sánh hợp lệ cho câu hỏi domain-OOF có giúp không. Các probability-feature contrasts cũng giữ `e_DV` cố định. Chốt primary feature variant trước target results; không lấy variant tốt nhất giữa `R_DV`, `R_DVd` và `R_DVdm` sau khi nhìn kết quả.

### RQ2: khác cả classifier thì không lấy raw error-AUPR làm bằng chứng duy nhất

Nếu heterogeneous system dùng `g_DV`, homogeneous system dùng `g_DH`, hai hệ thống tạo ra error sets và error prevalence khác nhau. `AP(e_DV,r_DV) - AP(e_DH,r_DH)` có thể tính và mô tả, nhưng không cô lập chất lượng risk estimator. Paired bootstrap không sửa được sự khác nhau của estimand; normalized AUPR cũng không tự giải quyết mọi khác biệt độ khó.

**Cách đóng trong plan:**

- Giữ fixed-`g_DV` table cho các risk-estimator claims.
- Same-family system phải có risk estimator và gate tương ứng, không chỉ fusion-only row M. Giữ shared DINO anchor, data budget và source-only selection rules.
- Đánh giá heterogeneous-vs-homogeneous **system advantage** bằng selective/end-to-end outcomes trên cùng transactions, với operating policies được chọn trước từ sources; công bố cả classification quality và error prevalence.
- Nếu muốn riêng một claim “heterogeneous features dự đoán cùng lỗi tốt hơn”, phải khai báo một common reference classifier/error target và cùng supervision cho tất cả comparators. Không cần thêm phép thử này nếu bài chỉ nhận system-level advantage.

Không suy ra “pretraining heterogeneity gây ra gain” chỉ vì một DINO–CLIP pair thắng một DINO–DINO pair. Cách diễn đạt đủ mạnh và đúng là advantage của cặp được khảo sát so với matched same-family control trong protocol này.

## 4. K=1 làm rõ giới hạn của selective security–usability

Bằng chứng: [fixed classifier và accept/abstain action](https://github.com/lathevinh/fas/blob/81f4160957152032f10b7219d002702f4bd9018c/docs/03-method.md#L208), [FA/BFNR và K=1](https://github.com/lathevinh/fas/blob/81f4160957152032f10b7219d002702f4bd9018c/docs/04-data-and-protocols.md#L320).

Trong protocol hiện tại, predicted spoof và abstain đều dẫn tới terminal non-accept. Vì vậy chuyển một predicted-spoof decision sang abstain không đổi kết quả truy cập của transaction đó. Nó có thể đổi selective coverage/covered error, nhưng không tự giảm end-to-end false acceptance hoặc bona-fide non-accept.

Đặt g(x)=live là quyết định live của fixed classifier trên detector-success population, r là risk và t là gate threshold. Detector failure luôn non-accept. Khi đó:

\[
FA_{end2end}(t)=P(\text{detector success},g=live,r\leq t\mid attack),
\]

\[
BFNR_{end2end}(t)=1-P(\text{detector success},g=live,r\leq t\mid bona\ fide).
\]

Với **cùng classifier** và so với không gating, gate chỉ có thể giảm/giữ FA và tăng/giữ BFNR. Vì vậy claim cần là **trade-off tốt hơn các risk gates đối chứng**, không phải chỉ thêm abstain là đồng thời cải thiện cả security lẫn usability so với ungated baseline.

Đây không làm đề tài vô hiệu. Nó xác định chính xác utility phải đo. Giữ overall error AP để nghiên cứu failure ranking, nhưng khi kết luận access-control benefit phải kiểm tra các quyết định live bị gate chặn, số attack được chặn thêm và bona-fide bị từ chối thêm. Một gain chủ yếu ở việc nhận ra false rejects có thể hữu ích cho failure diagnosis nhưng chưa chứng minh security–usability benefit dưới K=1.

Không cần thêm manual review, retry nhiều lần, action-specific risk heads hoặc một threat model mới để giải quyết. Chỉ cần giữ action semantics hiện tại và giới hạn claim cho đúng.

Một scalar threshold nói chung không đồng thời khớp chính xác cả attack coverage lẫn bona-fide coverage của hai methods. Cụm “matched class coverage” trong Stage-2 exit criteria nên được đặc tả thành một rule source-selected cụ thể và report cả hai achieved coverages. Không dùng true target class để chọn hai threshold riêng rồi coi đó là deployable gate.

## 5. “Matched sample-OOF” cần khống chế điều gì?

Bằng chứng: [sample/domain OOF construction](https://github.com/lathevinh/fas/blob/81f4160957152032f10b7219d002702f4bd9018c/docs/05-experiment-plan.md#L151).

Giữ final target predictions giống nhau là cần thiết nhưng chưa cô lập mọi khác biệt trong source supervision. Domain-OOF bỏ một domain có thể lớn/nhỏ hơn nhiều so với một fold sample-OOF. Nó cũng có thể tạo nhiều errors hơn vì base model khó hơn, khiến risk learner nhận nhiều positive examples hơn.

Không yêu cầu hai schemes phải có error prevalence bằng nhau: làm vậy sẽ phá natural-prevalence objective. Nhưng plan cần ghi rõ:

- cùng candidate universe của source subjects/videos, cùng exclusion của gate holdout;
- số OOF records, frame/video unit, source macro weighting, quality features và optimization budget;
- sample-OOF là subject-disjoint, không random frames của cùng subject/video qua train và validation;
- báo effective branch-fit sizes và risk error prevalence theo pseudo-fold;
- nếu training sizes lệch lớn, có một budget-matched sensitivity hoặc giới hạn diễn giải thành lợi ích của **toàn bộ domain-OOF construction**, không quy hết cho domain holdout riêng lẻ.

Đây là đặc tả fairness của control đã được chấp thuận, không phải thêm một research question hay yêu cầu cân bằng giả tạo dữ liệu.

## 6. Inference rules: gắn từng claim với endpoint, không dùng một stop rule toàn cục

Bằng chứng: [primary confirmatory rule](https://github.com/lathevinh/fas/blob/81f4160957152032f10b7219d002702f4bd9018c/docs/05-experiment-plan.md#L276), [novelty kill list](https://github.com/lathevinh/fas/blob/81f4160957152032f10b7219d002702f4bd9018c/docs/01-related-work-and-novelty.md#L91).

Các chỉnh lý hữu hạn cần đưa vào analysis specification:

1. **N_FA/N_min chỉ áp dụng endpoint cần false-accept events.** Zero DINO false accepts khiến FARR không xác định, nhưng error AP có thể vẫn estimable nếu classifier còn false rejects. Không đánh dấu cả RQ1 inconclusive chỉ vì FARR thiếu mẫu; chiều ngược lại cũng không lấy FR-driven AP gain làm bằng chứng attack utility.
2. **Chốt primary contrast cho từng RQ.** “Positive macro LCB” phải nói LCB của delta nào. Nếu muốn tuyên bố thắng mọi comparator thì phải thực sự kiểm tra conjunction đó; nếu chỉ chọn một comparator bất kỳ trong nhiều cái, cần rule về multiplicity/selection. Không chọn đối thủ dễ thắng sau target evaluation.
3. **Meaningful effect khác statistical positivity.** Nếu đã đặt delta_min, phải chỉ rõ nó tham gia pass rule thế nào; không khai báo rồi chỉ kiểm LCB>0. Có thể dùng point gain >= delta_min cùng LCB>0, hoặc mạnh hơn LCB>delta_min; chọn trước và không tráo sau kết quả.
4. **Underpowered không đồng nghĩa hypothesis false.** Giữ “inconclusive” riêng “evidence against”. Chưa có data để đánh giá power không ngăn chốt một design kiểm định được.
5. **Bỏ `agreement is high when both branches are wrong` khỏi unconditional kill list.** Với hard binary decisions, hai branch cùng sai thì chúng cùng dự đoán lớp đối diện; agreement trong nhóm đó là tất yếu. Cần phân tích confident shared-error frequency và risk ranking trên nhóm này, không dừng bài chỉ vì có shared errors.

Tất cả là quy tắc báo cáo/claim của phương pháp đã chọn. Không cần giải quyết bằng một module mới.

## 7. Dọn vài dấu vết cũ, không mở lại methodology

- Matrix row G ghi `Calibrated JS, sample-OOF`, trong khi main feature đã là absolute difference và cần matched logistic risk comparator. Row M chưa có risk/abstain dù RQ2 yêu cầu same-family selective system. Matrix cần phản ánh đúng method bằng một lần sửa.
- Stage-2 còn nhãn `Level 3`; Stage 5 nói `Only after Stages 1–4 pass`, có thể vô tình phục hồi dependence vào classifier/routing success đã bỏ. Thay bằng claim-specific dependencies.
- Method mô tả two gates có thể khiến đọc nhầm routing là core. Ghi core = always-on dual + selective gate; routing là extension.
- READMЕ vẫn trỏ Round-13 response là normative reference dù Round-14 response đã supersede. Cập nhật thứ tự ưu tiên tài liệu.
- Không lấy các configs/provisional code cũ làm lý do mở lại fixed VLM/pooling đã chốt. Việc đồng bộ code thuộc phase sau.

Những điểm này không phải fatal novelty/protocol flaws. Không nên dùng chúng để kéo dài thêm một vòng “chưa được bắt đầu planning”.

## 8. Novelty và khả năng công bố

Tôi giữ verdict Round 14: một **empirical-method contribution có cơ sở** nếu đạt error-risk transfer và selective utility có đối chứng, đặc biệt domain-OOF control và same-family system comparison. Không có thuật toán foundation model mới được đề xuất, và dossier đã nhận đúng giới hạn đó.

Các ranh giới literature đã kiểm tra trực tiếp ở Round 14 vẫn áp dụng: [FLIP](https://arxiv.org/abs/2309.16649) đã có language-guided FAS; [CA-FAS](https://arxiv.org/html/2411.01263v2) đã có confidence/rejection; [RPSR-FAS](https://link.springer.com/article/10.1007/s44443-026-01145-z) có reliability-guided training; [ConfidNet](https://arxiv.org/abs/1910.04851) đã học confidence cho failure prediction. Đây là nguồn đối chiếu đã đọc trong cùng ngày, không phải một literature search mới ở Round 15.

Khoảng đóng góp cần giữ là **source-only error supervision dưới pseudo-domain shift và bằng chứng heterogeneous selective PAD vượt đối chứng thích hợp**. Thắng một heuristic yếu hoặc đổi tên logistic gate sẽ không đủ. Ngược lại, không cần invent thêm module chỉ để có sơ đồ phức tạp hơn.

Q3 vẫn là mục tiêu có thể theo đuổi, không phải cam kết acceptance. Journal/category, dataset access và empirical effect chưa được xác nhận. Chấp thuận phương pháp không có nghĩa giả định những điều đó đã giải quyết.

## 9. Kết luận bàn giao

**Có thể chốt hướng nghiên cứu và bộ phương pháp lõi để chuyển sang implementation/experiment planning khi chủ dự án yêu cầu.**

Không cần tiếp tục đổi backbone, tìm một “novel module” hoặc sửa validator để được reviewer chấp thuận. Handoff nên mang theo đúng ba yêu cầu nghiên cứu hữu hạn:

1. contrast nào giữ classifier/error labels cố định, contrast nào so whole systems;
2. utility thực sự theo action semantics K=1;
3. matched OOF và claim-specific inference rules.

Những yêu cầu này có thể được đặc tả trong phase planning; phải khóa trước target results. Chúng không đảo ngược sự chấp thuận methodological core ở đầu review.

## Phạm vi kiểm tra

Đã pull tới SHA nêu đầu file, đối chiếu diff Round 14→15 và đọc RQ/method/protocol/evidence plan. Không chạy test suite, không audit validator, không tạo implementation plan, không làm experiment. Commit review chỉ thêm file Markdown này; không sửa normative method thay chủ dự án.
