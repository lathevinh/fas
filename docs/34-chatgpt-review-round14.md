# Review Round 14 — Chốt research direction, methodology và novelty trước coding

Ngày review: 2026-09-18. Repository: `lathevinh/fas`.

Commit được review: [`2a13dc483b92a0ccc555fc3a8ef823faccf0483f`](https://github.com/lathevinh/fas/commit/2a13dc483b92a0ccc555fc3a8ef823faccf0483f), đặc biệt `docs/00`–`docs/06` và `docs/33-review-response-round13.md`.

## 1. Sửa lại phạm vi review

Chủ dự án muốn **chốt nghiên cứu có cơ sở để nhắm một bài Q3**, rồi mới lập kế hoạch code và experiment. Tôi đồng ý rằng Rounds 11–13 đã đi quá sớm sang engineering readiness. Các lỗi validator vẫn có giá trị cho giai đoạn sau, nhưng không phải điều kiện để chấp thuận một research proposal.

Vòng này không chạy thêm validator probes, không yêu cầu implementation artifacts và không lập coding schedule. Các tiêu chí bằng chứng dưới đây xác định claim nào có thể được kiểm chứng; chúng không phải yêu cầu phải có kết quả ngay bây giờ.

**Verdict:** hướng nghiên cứu đáng theo đuổi và không thấy một fatal novelty overlap trong các nguồn trực tiếp đã đối chiếu. Bộ lõi đủ hợp lý cho một empirical-method paper. Tuy nhiên chưa nên freeze nguyên văn bản hiện tại: cần chốt ba quyết định phương pháp ở mục 4–6. Tôi đưa luôn phương án cụ thể, không yêu cầu thêm kiến trúc hay một vòng code để quyết định.

## 2. Trả lời trực tiếp năm câu hỏi trong response

| Câu hỏi | Kết luận của reviewer |
|---|---|
| Khả thi trên RTX 4080 16 GB? | Có cơ sở để xem là khả thi với frozen backbones chạy tuần tự và small heads; chưa có phép đo để bảo đảm runtime. Dataset access và chia subject là điều kiện thực tế cần xác minh sau khi chốt đề tài. |
| Novelty có đủ đáng nhắm Q3? | Plausible với đóng góp về **failure-risk transfer trong selective PAD và attribution có đối chứng**. Không đủ nếu chỉ là DINO + CLIP + averaging hoặc logistic confidence head. |
| Bỏ labeled MICO pilot đã đóng objection lớn chưa? | Đã giải quyết đường ảnh hưởng từ global labeled pilot tới outer target. Nhưng “nested” phải bao gồm candidate selection bên trong risk-OOF nếu muốn gọi records hoàn toàn out-of-fold. |
| Năm điều kiện bằng chứng đã đủ chưa? | Cần sửa cấu trúc: fusion rescue, error ranking và selective utility là các claim liên quan nhưng không tạo thành chuỗi tất yếu. Cross-fitting phải có đối chứng riêng; routing không phải điều kiện bắt buộc của core paper. |
| Đã chấp thuận để lập kế hoạch triển khai chưa? | **Chấp thuận về nguyên tắc bộ lõi sửa đổi ở mục 9.** Chỉ còn đồng bộ các quyết định phương pháp bằng tài liệu; chưa bật giai đoạn code/experiment planning trong review này. |

Q3 là mục tiêu venue, không phải một ngưỡng novelty thống nhất. Không thể kết luận “đủ Q3” chỉ bằng cấu hình hoặc hứa hẹn kết quả; cũng không nên suy ngược rằng ít algorithmic novelty tự động loại bài khỏi venue tốt hơn. Cần đối chiếu scope, chất lượng bằng chứng và journal/category cụ thể khi chọn nơi nộp. Review này không xác minh quartile của bất kỳ journal nào.

## 3. Novelty: phần còn bảo vệ được sau đối chiếu literature

Đã kiểm tra trực tiếp các nguồn dưới đây ngày 2026-09-18. Đây là focused overlap audit, không phải systematic review hay bằng chứng rằng không tồn tại bất kỳ công trình trùng nào.

| Công trình | Overlap xác minh được | Khoảng phân biệt cần giữ |
|---|---|---|
| [FLIP, ICCV 2023](https://arxiv.org/abs/2309.16649) | Language-guided cross-domain FAS, visual/text alignment và contrastive learning. | Không nhận generic prompts hoặc dùng CLIP là novelty. Trọng tâm của đề tài này là failure prediction sau classifier đã cố định. |
| [CA-FAS](https://arxiv.org/html/2411.01263v2) | Confidence bằng Gaussian/Mahalanobis, joint triplet mining và từ chối mẫu thiếu tin cậy. | Selective/reliable FAS đã có trước. Cần chứng minh giá trị của heterogeneous source-OOF error information, không chỉ thêm reject option. |
| [RPSR-FAS, published 08-09-2026](https://link.springer.com/article/10.1007/s44443-026-01145-z) | Semantic token reorganization; reliability branch điều chỉnh sample contribution trong classification training. | Vai trò reliability khác inference-time error-risk/abstention của đề tài. Paper dùng CelebA-Spoof source; không so trực tiếp số với strict MICO như cùng protocol. |
| [VFM benchmark, CVPRW 2026](https://arxiv.org/html/2604.19196v2) | DINOv2-Reg là baseline mạnh; recipe được báo cáo fine-tune encoder cùng augmentation/patch loss. | Frozen DINO + small head của đề tài không phải reproduction của toàn recipe đó. Không gọi thắng frozen control là thắng published VFM baseline. |
| [ConfidNet, NeurIPS 2019](https://arxiv.org/abs/1910.04851) | Học confidence để dự đoán lỗi đã là hướng nghiên cứu có trước. | Logistic error head không tự tạo novelty. Bài cần trả lời một câu hỏi PAD dưới shift bằng kiểm định và đối chứng rõ. |

Với RPSR-FAS, overlap không thể chỉ suy từ từ “reliability” trong tên bài. Phân biệt **training-time reweighting** và **post-classifier failure-risk transfer** là hợp lý; vẫn phải tránh claim rộng kiểu “first reliability-aware VLM for FAS”.

Tôi chưa truy cập được primary full text của DOI ESCL `10.1109/TIFS.2024.3356234` qua công cụ trong vòng này. Các paper khác trong reading list cũng chưa được audit lại đầy đủ. Vì vậy không xác nhận một claim “first” trên toàn literature; không lấy giới hạn truy cập đó làm lý do dừng chốt một đề tài có claim hẹp.

### Câu đóng góp đề nghị khóa

> We study whether source-domain cross-fitted error supervision makes heterogeneous frozen foundation predictors useful for selective single-image face PAD under unseen domains, beyond single-branch confidence and a matched same-family ensemble.

Ba phần đóng góp dự kiến:

1. Một phương pháp đơn giản, source-only, học failure risk cho một PAD decision rule cố định từ pseudo-domain shifts.
2. Phân tích có đối chứng để tách lợi ích của thêm predictor, heterogeneous pairing và cách tạo risk-training records.
3. Đánh giá security–usability trade-off với target-blind operating rules và transaction accounting rõ ràng.

Đây là **đóng góp dự kiến cần bằng chứng**, không phải ba kết quả đã có. Không tuyên bố tạo ra calibration, cross-validation, disagreement hoặc ensemble learning mới.

## 4. Quyết định phương pháp số 1: đơn giản hóa selection, hoặc nest toàn learning procedure

Bằng chứng repo: [method — source-only risk calibration](https://github.com/lathevinh/fas/blob/2a13dc483b92a0ccc555fc3a8ef823faccf0483f/docs/03-method.md#L102), [experiment plan — Stage 1/2](https://github.com/lathevinh/fas/blob/2a13dc483b92a0ccc555fc3a8ef823faccf0483f/docs/05-experiment-plan.md#L74).

Bỏ global labeled pilot là quyết định tốt. Nhưng hai lớp exclusion khác nhau:

- Outer target T không được ảnh hưởng final training/selection: bản mới đã cam kết đúng.
- Một pseudo-domain U dùng sinh risk-training errors không được ảnh hưởng **cả selector** tạo predictor cho U: vẫn cần diễn đạt tường minh.

Ví dụ nguồn là A/B/C. Chọn VLM j* bằng macro validation trên A/B/C, rồi dùng chính j* để tạo OOF prediction cho A từ model fit B/C, thì label A đã ảnh hưởng j*. Không có outer-target leakage, nhưng risk records không hoàn toàn out-of-fold đối với selection. “Nested” mà chỉ nằm ngoài final target chưa đủ.

Nếu giữ adaptive candidates, định nghĩa learning algorithm L(S) gồm candidate selection, checkpoint selection, calibration và thresholding chỉ trên S. Risk records cho U phải đến từ **L(S\U)**; final target dùng L(S). Khi S có ba domains, bước chọn candidate bên trong L(S\U) chỉ còn hai domains, có thể phải đánh giá train-one/validate-one. Điều này hợp lệ về nguyên tắc nhưng tăng variance và số small-head fits; nó không tự làm experiment đáng tin hơn chỉ vì nhiều tầng.

**Phương án đề nghị khóa cho bài tối thiểu:** dùng một frozen OpenCLIP ViT-B/16 candidate và generic core prompt bank chọn a priori, chung cho mọi target; candidate/preprocessing search chuyển thành secondary robustness study. Candidate ViT-B/16 đã có sẵn trong dossier, không cần đưa thêm model family. Chọn vì giới hạn phạm vi/compute, không vì kết quả target. DINO head selection và branch calibration vẫn hoàn toàn source-only trong từng OOF fold.

Phương án này không tạo novelty mới; nó loại một nuisance factor và giúp trả lời RQ chính rõ hơn. Nếu chủ dự án muốn giữ nested candidate selection làm primary, phải chốt định nghĩa L(S) ở trên và cho homogeneous control selection budget tương đương. Không cần code để quyết định giữa hai cách.

Toàn bộ global analysis choices phải được cố định trước khi xem bất kỳ outer-target result nào. Không chạy target thứ nhất, sửa method rồi vẫn gọi cả bốn targets confirmatory. Một dataset được dùng làm source trong fold khác là bình thường của MICO; điều cần giữ là fold-specific target exclusion và không dùng kết quả outer folds để sửa global procedure.

## 5. Quyết định phương pháp số 2: bỏ kill hierarchy đang đồng nhất fusion và selection

Bằng chứng: [Stage 1 kill hierarchy](https://github.com/lathevinh/fas/blob/2a13dc483b92a0ccc555fc3a8ef823faccf0483f/docs/05-experiment-plan.md#L120), [charter success criteria](https://github.com/lathevinh/fas/blob/2a13dc483b92a0ccc555fc3a8ef823faccf0483f/docs/00-project-charter.md#L43).

Repo đang bắt realized fusion rescue pass trước, nếu không thì stop dual-foundation direction. Điều đó quá mạnh đối với một bài có chủ đề failure prediction.

Hai classifier có thể cùng giữ nguyên nhãn nhưng confidence của nhánh thứ hai vẫn giúp nhận ra khi nào nhánh chính/fusion sắp sai. Khi đó averaging không cứu thêm nhiều lỗi, nhưng selective ranking vẫn có ích. Ngược lại, fusion sửa được lỗi không đảm bảo risk model xếp hạng các lỗi còn lại tốt. Đây là hai giả thuyết cần kiểm tra riêng.

**Cấu trúc claim đề nghị khóa:**

- **Core:** heterogeneous risk model cải thiện transferable error ranking và selective security–usability so với baselines phù hợp.
- **Classifier benefit:** fusion rescue/net error reduction là một kết quả bổ sung; cần pass nếu tuyên bố fusion cải thiện PAD classification, không là điều kiện logic bắt buộc để nghiên cứu selective risk.
- **Heterogeneity attribution:** cần hơn same-family control tại endpoint được claim; thắng FARR không tự chứng minh thắng risk transfer.
- **Explicit-disagreement attribution:** chỉ giữ nếu biến đổi |pD−pV| giúp so với probability-only nonlinear baselines; không pass thì bỏ chữ disagreement, không xóa core finding.
- **Routing:** chỉ cần nếu paper giữ claim compute saving; không pass thì bỏ routing claim.

Nếu cả failure ranking lẫn selective utility không hơn baselines thì model-centric risk contribution không còn được hỗ trợ. Nếu heterogeneous pairing không hơn same-family pairing thì hạn chế/reframe cross-foundation advantage; không diễn đạt điều này như bằng chứng mọi heterogeneous ensemble đều vô ích.

### Rescue phải có chiều gây hại

FARR là metric có điều kiện trên DINO false accepts. Nó chưa trừ các attack từng được DINO chặn nhưng fusion lại cho qua, và chưa xét bona-fide harm. Với cùng attack set và các threshold đã source-select:

\[
APCER(D)-APCER(F)
=\frac{N_{\text{D false accept, F blocks}}-N_{\text{D blocks, F false accept}}}{N_{\text{attack}}}.
\]

Giữ FARR để mô tả, nhưng thêm net change và BPCER/BFNR khi kết luận security-useful. Không chọn lại target threshold để tạo matched-security result rồi gọi đó là deployed policy; các target-matched curves chỉ là diagnostics.

### Disagreement không thêm thông tin mới khi đã biết hai xác suất

Vì d=|pD−pV| là hàm xác định của pD,pV, gain so với linear logistic chỉ chứng minh feature transform/inductive bias có ích trong family đó. Nó không chứng minh một nguồn thông tin độc lập mới. Capacity-matched nonlinear control đã có trong dossier là đúng hướng; cần giữ nó ở evidence bắt buộc cho disagreement claim, không chỉ một optional ablation.

## 6. Quyết định phương pháp số 3: khóa paper core, bỏ điều kiện deployment khỏi novelty tối thiểu

[Response Round 13](https://github.com/lathevinh/fas/blob/2a13dc483b92a0ccc555fc3a8ef823faccf0483f/docs/33-review-response-round13.md) và Stage 3 đã gọi routing là optional. Nhưng charter vẫn yêu cầu conditional compute benefit, và novelty kill conditions vẫn có routing failure. Đây là mâu thuẫn scope, không phải thiếu code.

**Đề nghị khóa:**

| Core paper | Secondary hoặc paper sau |
|---|---|
| Frozen DINO + frozen VLM; fixed fusion; source-domain OOF risk | Conditional routing và latency ceiling |
| Four-fold MICO, target-blind protocol | Distillation, LoRA, generative MLLM |
| Failure ranking + selective utility, same-family control | Cue ontology, localization, faithfulness maps |
| Separate SiW-M attack-shift validation nếu giữ attack-shift claim | External mask transfer và prompt-family concept endpoints |

Vẫn báo inference cost của core method; không phải mọi bài dùng hai models đều phải có conditional routing mới xuất bản được. Nếu SiW-M không khả dụng, phải bỏ attack-shift claim trước evaluation và giữ domain-shift paper; không âm thầm thay dataset sau kết quả xấu. Một second shift axis tăng sức thuyết phục nhưng không phải định nghĩa của novelty.

Tiêu đề làm việc an toàn hơn:

> **Source-Only Failure-Risk Estimation for Selective Face Presentation Attack Detection with Heterogeneous Foundation Models**

“Estimation” không hứa risk probability được calibrated trên unseen target. Branch calibration được phép giữ đúng tên kỹ thuật; reliability diagrams/Brier/NLL sau này quyết định có thêm target-calibration claim không.

## 7. Minimum evidence để claim đứng được — không phải danh sách chạy experiment lúc này

### Hai nguyên nhân của gain phải được phân biệt

Novelty đề xuất gồm heterogeneous pairing và source-domain cross-fitting. Vì vậy cần một phép phân biệt hai yếu tố, thay vì chỉ “proposed > entropy”:

- giữ classifier/error labels cố định khi so domain-OOF với sample-OOF risk training;
- giữ recipe và data budget tương ứng khi so heterogeneous system với same-family system;
- giữ fixed-g_ref risk table riêng với end-to-end system table, như dossier đã đề xuất.

Không so AUPR của hai hệ thống có error prevalence khác nhau rồi gán toàn bộ khác biệt cho risk estimator. Riêng delta-CF trên errors của DINO+VLM fusion cũng không phải bằng chứng nhân quả về loại pretraining: nhánh VLM góp phần định nghĩa chính error target đó. Nên gọi nó là incremental predictive value conditional on g_ref. Same-family end-to-end comparison và joint-error analysis hỗ trợ claim thực nghiệm hẹp; không cần thêm một causal theory để bài tồn tại.

### Baselines tối thiểu theo chức năng

1. DINO-only, VLM-only, calibrated average, và DINO-Reg + plain-DINO pair với cùng anchor/splits.
2. Margin-to-decision-boundary, fused MSP/entropy, quality-only, single/dual probability risk; nonlinear probability-only risk nếu giữ disagreement claim. Single-branch comparator phải có confidence/margin hoặc nonlinear capacity hợp lý; chỉ logistic tuyến tính trên p có thể không biểu diễn được risk tăng gần decision boundary.
3. Sample-OOF và domain-OOF với cùng final base predictions, để kiểm tra chính rationale pseudo-domain shift.
4. Một comparator reliability-FAS thích hợp, ưu tiên CA-FAS nếu tái lập được protocol. Simple Mahalanobis trên DINO là control có ích nhưng không được gọi là CA-FAS reproduction.

FLIP và published DINO benchmark cho context về classifier strength. Các published numbers chỉ dùng như literature context khi data/frames/training budget khác; không cần buộc core attribution chạy mọi architecture trong reading list. VLM visual-head control giữ lại nếu muốn diễn giải riêng vai trò text semantics; không tuyên bố semantic causality chỉ từ thắng một same-family pair.

### Endpoints và điều kiện claim

Giữ prediction-error AUPR làm primary ranking endpoint; dùng paired within-target deltas và macro qua bốn fixed target domains. AURC/selective curves và attack/bona coverage hỗ trợ utility; với K=1 phải có FA_end2end và BFNR_end2end vì abstain là terminal non-accept. Không lấy covered accuracy cao làm bằng chứng người dùng được phục vụ tốt hơn khi abstain tăng mạnh.

Để tránh “positive rất nhỏ cũng pass”, đề nghị **quy tắc inference được khóa trước mọi target**: positive lower confidence bound cho primary paired macro gain, kèm consistency 3/4 domains và harm tolerance đã công bố; các tiêu chí này không thay cho nhau. Subject resampling phải ghép qua seeds; đây là uncertainty trên fixed evaluated datasets, không phải chứng minh tổng quát cho mọi domain mới.

Không cần đoán effect size/N_min khi chưa biết source event counts. Nhưng phải khóa **cách chọn** các giá trị đó bằng source-only information, và không chỉnh rule sau khi thấy target. Source power/count planning không có nghĩa được tùy chỉnh meaningful-effect threshold để proposed chắc pass. Nếu chưa đủ events thì inconclusive, không biến nó thành fail hoặc chuyển target operating point tùy ý.

Các hạng mục trên là evidence standard của proposal. Không đòi hỏi có bảng số liệu để chấp nhận hypothesis đáng nghiên cứu.

## 8. Feasibility: hợp lý, nhưng “cache once” cần hiểu đúng

Frozen encoders + sequential inference + small head/risk fitting là một scope hợp lý cho một GPU 16 GB. Đây là đánh giá thiết kế, không phải kết quả benchmark. Chưa đủ thông tin để cam kết training duration hoặc latency ceiling.

Method hiện có learned attention pooling. Nếu pooling trainable theo fold, chỉ cache một pooled vector từ pooling đã fit trên toàn dữ liệu có thể làm sai lineage. Cần cache frozen patch tokens trước pooling, hoặc dùng fixed pooling. Frozen backbone không làm phần pooling trainable tự trở thành frozen.

Ví dụ tính dung lượng, không phải số mẫu thực tế: 518/14=37, tức 1,369 patch tokens; ở dimension 768 và FP16, riêng tokens tốn khoảng 2.10 MB/image. 100,000 images tương đương khoảng 210 GB chưa tính metadata, views và model khác. Crop/augmentation khác nhau cũng không dùng chung một cached tensor bất biến. Vì vậy bottleneck có thể là storage/I/O, không chỉ GPU memory.

Không xem đây là conceptual blocker. Nếu muốn minimum paper gọn hơn, fixed CLS + mean-pooled patches là một lựa chọn hợp lý và attention pooling là secondary. Nếu giữ attention pooling, thừa nhận patch-cache budget; không cần đổi scientific contribution. Không yêu cầu làm storage benchmark ngay để chốt methodology.

## 9. Bộ phương pháp tối thiểu reviewer đề nghị chốt

1. **Task:** single-image RGB physical PAD, target-domain-unseen; failure prediction và abstention, không gọi là generic unknownness detection.
2. **Models:** frozen DINOv2-Reg + small PAD head; một frozen OpenCLIP ViT-B/16 chính, generic fixed prompts. Không jointly optimize agreement. Fixed pooling ưu tiên nếu cần giảm scope.
3. **Classifier:** mỗi branch có monotone source calibration; calibrated average và source-selected decision threshold là fixed g_ref.
4. **Risk:** logistic model từ source-domain OOF errors của g_ref; probabilities, quality, absolute difference là feature set; same labels cho risk baselines. Margin variant báo riêng. Không hứa target probability calibration.
5. **Protocol:** không labeled MICO pilot; bốn outer folds, mọi fitting/selection fold-local; core model/prompt/analysis rule khóa trước target results. Attack-OOF là track riêng nếu claim attack shift.
6. **Attribution:** same-family pairing, sample-vs-domain OOF và appropriate uncertainty/learned-risk controls. Disagreement là hypothesis phụ, không novelty mặc định.
7. **Success:** core failure-ranking gain phải đi kèm selective utility và không che class-specific harm. Fusion rescue là claim riêng; routing không quyết định sự tồn tại của core paper.
8. **Boundary:** không thêm generative MLLM, LoRA, ontology, evidence maps hoặc deployment optimization vào yêu cầu tối thiểu.

Đây là một proposal đủ cụ thể để chốt về khoa học. Không cần phát minh thêm module để “trông novel”. Điều chưa thể chốt trước dữ liệu là hypothesis có đúng hay không, không phải research question có hợp lý hay không.

## 10. Freeze decision và bước tiếp theo

**RESEARCH DIRECTION ACCEPTED. REVISED CORE METHODOLOGY ACCEPTED IN PRINCIPLE.**

Tôi chưa ký chấp thuận vô điều kiện cho nguyên văn commit `2a13dc4`, vì ba quyết định ở mục 4–6 còn cần được chủ dự án tiếp thu vào normative docs. Chúng đã có phương án giải quyết trong review này; không cần implementation hoặc empirical result để đóng.

Trước khi chuyển sang code/experiment planning, chỉ cần một bản methodology nhất quán trả lời:

- Primary dùng fixed VLM như đề nghị, hay nested toàn L(S)?
- Core claim là failure-risk/selective utility; fusion rescue và routing đã tách thành claim riêng chưa?
- Scope/title/kill criteria đã thống nhất, và attribution baselines/endpoint semantics đã đi cùng claim chưa?

Sau khi đồng bộ đúng các quyết định đó, không có lý do từ review này để tiếp tục trì hoãn bằng một vòng validator audit. Việc lập coding plan và detailed experiment plan chỉ bắt đầu khi chủ dự án xác nhận bản methodology chốt.

## Phạm vi công việc vòng này

Đã pull và review tài liệu tại SHA nêu đầu file; đối chiếu trực tiếp năm primary sources có link ở mục 3. Không sửa model/config/code, không chạy experiments, không đưa kết quả giả định thành kết quả quan sát. Commit của vòng này chỉ thêm file phản biện Markdown theo workflow đã được chủ repo cho phép.
