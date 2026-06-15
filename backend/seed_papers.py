"""种子脚本：批量添加论文、作者、标签、关系、笔记和概念，用于知识图谱测试。"""
import sys
sys.path.insert(0, '.')

from database import SessionLocal, engine
from models import (
    Paper, Author, Venue, Tag, Note, Concept,
    NoteConcept, PaperRelation, User,
    paper_authors, paper_tags,
)

db = SessionLocal()

# ── 先取一个用户 ID（用于笔记） ──
user = db.query(User).first()
user_id = user.user_id if user else 1
print(f"Using user_id={user_id}")

# ── 清旧数据（可选） ──
# 注意：不清除已有数据，只要不冲突就行

# ============================================================
# 1. 创建会议/期刊
# ============================================================
venues_data = [
    ("CVPR", "conference"),
    ("ICCV", "conference"),
    ("NeurIPS", "conference"),
    ("ICML", "conference"),
    ("ICLR", "conference"),
    ("ACL", "conference"),
    ("EMNLP", "conference"),
    ("AAAI", "conference"),
    ("TPAMI", "journal"),
    ("JMLR", "journal"),
    ("Nature", "journal"),
    ("Science", "journal"),
]
venue_map = {}
for vname, vtype in venues_data:
    v = db.query(Venue).filter(Venue.venue_name == vname).first()
    if not v:
        v = Venue(venue_name=vname, venue_type=vtype)
        db.add(v)
        db.flush()
    venue_map[vname] = v
print(f"Venues: {len(venue_map)}")

# ============================================================
# 2. 创建作者
# ============================================================
authors_data = [
    # CV / Image Generation
    ("Jonathan Ho", "UC Berkeley"),
    ("Prafulla Dhariwal", "OpenAI"),
    ("Alex Nichol", "OpenAI"),
    ("Robin Rombach", "Stability AI"),
    ("Andreas Blattmann", "Stability AI"),
    ("Patrick Esser", "Runway ML"),
    # NLP / LLM
    ("Ashish Vaswani", "Google Brain"),
    ("Noam Shazeer", "Google Brain"),
    ("Jacob Devlin", "Google AI"),
    ("Ming-Wei Chang", "Google AI"),
    ("Tom Brown", "OpenAI"),
    ("Jason Wei", "OpenAI"),
    ("Hugo Touvron", "Meta AI"),
    # ML Theory / Other
    ("Ian Goodfellow", "Stanford"),
    ("Yoshua Bengio", "MILA"),
    ("Yann LeCun", "Meta AI / NYU"),
    ("Geoffrey Hinton", "University of Toronto"),
    ("Kaiming He", "MIT"),
    ("Zhuang Liu", "Meta AI"),
    ("Tim Salimans", "OpenAI"),
]
author_map = {}
for aname, affil in authors_data:
    a = db.query(Author).filter(Author.author_name == aname).first()
    if not a:
        a = Author(author_name=aname, affiliation=affil)
        db.add(a)
        db.flush()
    author_map[aname] = a
print(f"Authors: {len(author_map)}")

# ============================================================
# 3. 创建标签
# ============================================================
tags_data = [
    ("Diffusion Models", "#e74c3c"),
    ("Image Generation", "#e67e22"),
    ("Flow Matching", "#f1c40f"),
    ("Classifier-free Guidance", "#2ecc71"),
    ("Transformer", "#3498db"),
    ("Attention Mechanism", "#9b59b6"),
    ("Language Model", "#1abc9c"),
    ("Text-to-Image", "#e91e63"),
    ("Self-Supervised Learning", "#00bcd4"),
    ("GAN", "#ff5722"),
    ("Representation Learning", "#795548"),
    ("Optimization", "#607d8b"),
    ("Neural ODE", "#8bc34a"),
    ("Score-based Model", "#ff9800"),
    ("Chain-of-Thought", "#2196f3"),
    ("RLHF", "#4caf50"),
]
tag_map = {}
for tname, color in tags_data:
    t = db.query(Tag).filter(Tag.tag_name == tname).first()
    if not t:
        t = Tag(tag_name=tname, color=color)
        db.add(t)
        db.flush()
    tag_map[tname] = t
print(f"Tags: {len(tag_map)}")

# ============================================================
# 4. 创建论文
# ============================================================
_papers = [
    # ── Diffusion Models ──
    {
        "title": "Denoising Diffusion Probabilistic Models",
        "abstract": "We present high quality image synthesis results using diffusion probabilistic models, a class of latent variable models inspired by considerations from nonequilibrium thermodynamics.",
        "year": 2020,
        "venue": "NeurIPS",
        "authors": ["Jonathan Ho", "Prafulla Dhariwal", "Alex Nichol"],
        "tags": ["Diffusion Models", "Image Generation", "Score-based Model"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    {
        "title": "Diffusion Models Beat GANs on Image Synthesis",
        "abstract": "We show that diffusion models can achieve image sample quality superior to the current state-of-the-art generative models.",
        "year": 2021,
        "venue": "NeurIPS",
        "authors": ["Prafulla Dhariwal", "Alex Nichol"],
        "tags": ["Diffusion Models", "Image Generation", "Classifier-free Guidance"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    {
        "title": "High-Resolution Image Synthesis with Latent Diffusion Models",
        "abstract": "By decomposing the image formation process into a sequential application of denoising autoencoders, diffusion models achieve state-of-the-art synthesis results on image data and beyond.",
        "year": 2022,
        "venue": "CVPR",
        "authors": ["Robin Rombach", "Andreas Blattmann", "Patrick Esser"],
        "tags": ["Diffusion Models", "Image Generation", "Text-to-Image"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    {
        "title": "Flow Matching for Generative Modeling",
        "abstract": "We introduce Flow Matching, a simple and general framework for training continuous normalizing flows. Flow Matching enables simulation-free training of CNFs at scale.",
        "year": 2023,
        "venue": "ICLR",
        "authors": ["Robin Rombach", "Andreas Blattmann"],
        "tags": ["Flow Matching", "Image Generation", "Neural ODE"],
        "paper_type": "article",
        "reading_status": "reading",
    },
    {
        "title": "Scalable Diffusion Models with Transformers",
        "abstract": "We explore a new class of diffusion models based on the transformer architecture. We call them Diffusion Transformers (DiTs).",
        "year": 2023,
        "venue": "ICCV",
        "authors": ["Kaiming He", "Zhuang Liu"],
        "tags": ["Diffusion Models", "Transformer", "Image Generation"],
        "paper_type": "article",
        "reading_status": "unread",
    },
    # ── Transformers & NLP ──
    {
        "title": "Attention Is All You Need",
        "abstract": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        "year": 2017,
        "venue": "NeurIPS",
        "authors": ["Ashish Vaswani", "Noam Shazeer"],
        "tags": ["Transformer", "Attention Mechanism", "Language Model"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers.",
        "year": 2019,
        "venue": "NAACL",
        "authors": ["Jacob Devlin", "Ming-Wei Chang"],
        "tags": ["Transformer", "Language Model", "Self-Supervised Learning"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    {
        "title": "Language Models are Few-Shot Learners",
        "abstract": "We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches.",
        "year": 2020,
        "venue": "NeurIPS",
        "authors": ["Tom Brown"],
        "tags": ["Language Model", "Transformer", "Self-Supervised Learning"],
        "paper_type": "article",
        "reading_status": "reading",
    },
    {
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "abstract": "We explore how generating a chain of thought—a series of intermediate reasoning steps—significantly improves the ability of large language models to perform complex reasoning.",
        "year": 2022,
        "venue": "NeurIPS",
        "authors": ["Jason Wei"],
        "tags": ["Chain-of-Thought", "Language Model", "Transformer"],
        "paper_type": "article",
        "reading_status": "done",
    },
    {
        "title": "LLaMA: Open and Efficient Foundation Language Models",
        "abstract": "We introduce LLaMA, a collection of foundation language models ranging from 7B to 65B parameters. We train our models on trillions of tokens.",
        "year": 2023,
        "venue": "AAAI",
        "authors": ["Hugo Touvron"],
        "tags": ["Language Model", "Transformer", "Self-Supervised Learning"],
        "paper_type": "article",
        "reading_status": "unread",
    },
    # ── ML Theory & Foundations ──
    {
        "title": "Generative Adversarial Networks",
        "abstract": "We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G and a discriminative model D.",
        "year": 2014,
        "venue": "NeurIPS",
        "authors": ["Ian Goodfellow", "Yoshua Bengio"],
        "tags": ["GAN", "Image Generation", "Representation Learning"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    {
        "title": "Deep Residual Learning for Image Recognition",
        "abstract": "We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously.",
        "year": 2016,
        "venue": "CVPR",
        "authors": ["Kaiming He"],
        "tags": ["Representation Learning", "Optimization"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    {
        "title": "Training language models to follow instructions with human feedback",
        "abstract": "We present InstructGPT, a method for fine-tuning language models to follow instructions by using reinforcement learning from human feedback (RLHF).",
        "year": 2022,
        "venue": "NeurIPS",
        "authors": ["Tom Brown", "Jason Wei"],
        "tags": ["RLHF", "Language Model", "Chain-of-Thought"],
        "paper_type": "article",
        "reading_status": "reading",
    },
    {
        "title": "Neural Ordinary Differential Equations",
        "abstract": "We introduce a new family of deep neural network models. Instead of specifying a discrete sequence of hidden layers, we parameterize the derivative of the hidden state using a neural network.",
        "year": 2018,
        "venue": "NeurIPS",
        "authors": ["Tim Salimans"],
        "tags": ["Neural ODE", "Optimization", "Representation Learning"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    {
        "title": "Score-Based Generative Modeling through Stochastic Differential Equations",
        "abstract": "We present a stochastic differential equation (SDE) framework for score-based generative modeling. We can generate high-fidelity samples from complex distributions.",
        "year": 2021,
        "venue": "ICLR",
        "authors": ["Jonathan Ho", "Tim Salimans"],
        "tags": ["Score-based Model", "Neural ODE", "Diffusion Models"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    # ── Vision + More ──
    {
        "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
        "abstract": "We apply a standard Transformer directly to images, with the fewest possible modifications. To do so, we split an image into patches and provide the sequence of linear embeddings of these patches as input.",
        "year": 2021,
        "venue": "ICLR",
        "authors": ["Ashish Vaswani", "Kaiming He"],
        "tags": ["Transformer", "Representation Learning", "Attention Mechanism"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    {
        "title": "Improving Diffusion Models with Classifier-Free Guidance",
        "abstract": "We introduce classifier-free guidance, a technique for improving the sample quality of conditional diffusion models without requiring a separately trained classifier.",
        "year": 2022,
        "venue": "CVPR",
        "authors": ["Jonathan Ho", "Tim Salimans"],
        "tags": ["Classifier-free Guidance", "Diffusion Models", "Image Generation"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    {
        "title": "Consistency Models",
        "abstract": "We propose consistency models, a new family of generative models that achieve high sample quality without adversarial training. They map any point on the diffusion ODE trajectory back to its origin.",
        "year": 2023,
        "venue": "ICML",
        "authors": ["Jonathan Ho", "Tim Salimans"],
        "tags": ["Diffusion Models", "Score-based Model", "Neural ODE"],
        "paper_type": "article",
        "reading_status": "reading",
    },
    {
        "title": "Deep Unsupervised Learning using Nonequilibrium Thermodynamics",
        "abstract": "A central problem in machine learning involves modeling complex datasets using highly flexible families of probability distributions. We connect diffusion models to nonequilibrium thermodynamics.",
        "year": 2015,
        "venue": "ICML",
        "authors": ["Geoffrey Hinton"],
        "tags": ["Diffusion Models", "Self-Supervised Learning", "Score-based Model"],
        "paper_type": "article",
        "reading_status": "finished",
    },
    {
        "title": "Representation Learning with Contrastive Predictive Coding",
        "abstract": "We propose a universal unsupervised learning approach to extract useful representations from high-dimensional data, which we call Contrastive Predictive Coding.",
        "year": 2018,
        "venue": "AAAI",
        "authors": ["Yoshua Bengio", "Geoffrey Hinton"],
        "tags": ["Representation Learning", "Self-Supervised Learning"],
        "paper_type": "article",
        "reading_status": "finished",
    },
]

paper_objs = []
for pdata in _papers:
    # 查找或创建 venue
    vname = pdata.get("venue")
    venue_obj = db.query(Venue).filter(Venue.venue_name == vname).first() if vname else None

    paper = Paper(
        title=pdata["title"],
        abstract=pdata["abstract"],
        year=pdata["year"],
        venue=vname,
        venue_ref=venue_obj,
        paper_type=pdata.get("paper_type", "article"),
        reading_status=pdata.get("reading_status", "unread"),
    )
    # 关联作者
    for aname in pdata["authors"]:
        a = author_map[aname]
        paper.authors.append(a)
    # 关联标签
    for tname in pdata["tags"]:
        t = tag_map[tname]
        paper.tags.append(t)

    db.add(paper)
    db.flush()
    paper_objs.append(paper)

print(f"Papers created: {len(paper_objs)}")

# ============================================================
# 5. 创建论文关系（cites, same_topic, method_related, improves, compares_with）
# ============================================================
# 用标题前缀查找
def find(title_prefix):
    return db.query(Paper).filter(Paper.title.like(f"{title_prefix}%")).first()

relations = [
    # DDPM 系列互相引用
    ("Deep Unsupervised Learning", "Denoising Diffusion Probabilistic Models", "cites", 0.95),
    ("Denoising Diffusion Probabilistic Models", "Diffusion Models Beat GANs", "cites", 0.9),
    ("Denoising Diffusion Probabilistic Models", "High-Resolution Image Synthesis", "cites", 0.85),
    ("Denoising Diffusion Probabilistic Models", "Flow Matching for Generative", "cites", 0.7),
    # Score-based 系列
    ("Denoising Diffusion Probabilistic Models", "Score-Based Generative Modeling", "same_topic", 0.92),
    ("Score-Based Generative Modeling", "Consistency Models", "improves", 0.88),
    ("Score-Based Generative Modeling", "Flow Matching for Generative", "method_related", 0.82),
    ("Denoising Diffusion Probabilistic Models", "Consistency Models", "cites", 0.75),
    # Diffusion 内部关系
    ("Diffusion Models Beat GANs", "Improving Diffusion Models", "improves", 0.93),
    ("High-Resolution Image Synthesis", "Scalable Diffusion Models", "method_related", 0.78),
    ("Diffusion Models Beat GANs", "High-Resolution Image Synthesis", "compares_with", 0.72),
    # GAN vs Diffusion
    ("Generative Adversarial Networks", "Diffusion Models Beat GANs", "compares_with", 0.91),
    ("Generative Adversarial Networks", "Denoising Diffusion Probabilistic Models", "compares_with", 0.85),
    # Transformer 系列
    ("Attention Is All You Need", "BERT: Pre-training of Deep", "cites", 0.95),
    ("Attention Is All You Need", "Language Models are Few-Shot", "cites", 0.9),
    ("Attention Is All You Need", "An Image is Worth 16x16", "cites", 0.88),
    ("Attention Is All You Need", "Scalable Diffusion Models", "cites", 0.72),
    # LLM 之间关系
    ("BERT: Pre-training of Deep", "Language Models are Few-Shot", "same_topic", 0.82),
    ("Language Models are Few-Shot", "Chain-of-Thought Prompting", "cites", 0.87),
    ("Language Models are Few-Shot", "Training language models to follow", "improves", 0.89),
    ("Chain-of-Thought Prompting", "Training language models to follow", "method_related", 0.84),
    ("Language Models are Few-Shot", "LLaMA: Open and Efficient", "same_topic", 0.91),
    # 跨领域
    ("Deep Residual Learning for Image", "An Image is Worth 16x16", "compares_with", 0.65),
    ("Deep Residual Learning for Image", "Scalable Diffusion Models", "method_related", 0.60),
    # Neural ODE 与 Diffusion
    ("Neural Ordinary Differential Equations", "Score-Based Generative Modeling", "method_related", 0.94),
    ("Neural Ordinary Differential Equations", "Flow Matching for Generative", "method_related", 0.93),
    ("Neural Ordinary Differential Equations", "Consistency Models", "cites", 0.78),
    # 表征学习
    ("Representation Learning with Contrastive", "BERT: Pre-training of Deep", "same_topic", 0.76),
    ("Representation Learning with Contrastive", "Deep Residual Learning for Image", "method_related", 0.68),
    ("Representation Learning with Contrastive", "Language Models are Few-Shot", "method_related", 0.55),
]

created_relations = 0
for src_prefix, tgt_prefix, rtype, weight in relations:
    src = find(src_prefix)
    tgt = find(tgt_prefix)
    if not src or not tgt:
        print(f"  SKIP relation: '{src_prefix}' -> '{tgt_prefix}' (missing paper)")
        continue
    # 避免重复
    existing = db.query(PaperRelation).filter(
        PaperRelation.source_paper_id == src.paper_id,
        PaperRelation.target_paper_id == tgt.paper_id,
        PaperRelation.relation_type == rtype,
    ).first()
    if existing:
        continue
    rel = PaperRelation(
        source_paper_id=src.paper_id,
        target_paper_id=tgt.paper_id,
        relation_type=rtype,
        weight=weight,
        description=f"{src.title[:30]}... {rtype} {tgt.title[:30]}...",
        generated_by="user",
        confidence=weight,
        is_confirmed=True,
    )
    db.add(rel)
    created_relations += 1
print(f"Paper relations: {created_relations}")

# ============================================================
# 6. 创建概念
# ============================================================
concepts_data = [
    ("Denoising Process", "The progressive removal of noise from data in diffusion models — typically via a learned reverse process parameterized by a neural network."),
    ("Attention Score", "A compatibility function between a query and a key, producing a weight that determines how much focus each token receives during context aggregation."),
    ("Latent Space", "A compressed, lower-dimensional representation learned by a model to capture the essential structure of the input data."),
    ("Score Function", "The gradient of the log probability density with respect to the data — a key quantity in score-based generative models."),
    ("Flow Field", "A time-dependent vector field that transports a simple base distribution to a complex data distribution in continuous normalizing flows."),
    ("Classifier-Free Guidance", "A technique that mixes conditional and unconditional score estimates during sampling to improve sample quality without a separate classifier."),
    ("Chain of Thought", "A reasoning paradigm where intermediate logical steps are generated before the final answer, improving complex problem-solving in LLMs."),
    ("Representation Learning", "Learning useful feature representations from data, often without explicit supervision, so downstream tasks can be solved more effectively."),
    ("Adversarial Training", "A two-player game where a generator and discriminator compete, driving the generator to produce increasingly realistic samples."),
    ("Residual Connection", "A skip connection that adds input directly to the output of a layer, enabling stable training of very deep networks by mitigating vanishing gradients."),
    ("Continuous Normalizing Flow", "A generative model that defines a transformation via a neural ODE, continuously evolving a base distribution into the data distribution."),
    ("Self-Supervised Pretraining", "A training paradigm where models learn from unlabeled data by solving pretext tasks (e.g., masked token prediction), then fine-tune on downstream tasks."),
    ("RLHF", "Reinforcement Learning from Human Feedback — a fine-tuning process where a reward model trained on human preferences guides the policy via RL."),
    ("Stochastic Differential Equation", "A differential equation that incorporates a random noise term; in generative modeling, SDEs unify score-based and diffusion approaches."),
]

concept_map = {}
for cname, cdesc in concepts_data:
    c = db.query(Concept).filter(Concept.concept_name == cname).first()
    if not c:
        c = Concept(concept_name=cname, description=cdesc)
        db.add(c)
        db.flush()
    concept_map[cname] = c
print(f"Concepts: {len(concept_map)}")

# ============================================================
# 7. 创建笔记 + 笔记-概念关联
# ============================================================
notes_data = [
    {
        "title": "DDPM 核心公式推导",
        "content": "DDPM 的前向过程：$q(x_t|x_{t-1}) = \\mathcal{N}(x_t; \\sqrt{1-\\beta_t}x_{t-1}, \\beta_t I)$。反向过程：$p_\\theta(x_{t-1}|x_t) = \\mathcal{N}(x_{t-1}; \\mu_\\theta(x_t, t), \\sigma_t^2 I)$。训练目标是优化变分下界（ELBO），简化后等价于预测噪声 $\\epsilon_\\theta$。",
        "note_type": "formula",
        "paper": "Denoising Diffusion Probabilistic",
        "concepts": ["Denoising Process", "Score Function"],
    },
    {
        "title": "Flow Matching 与 Diffusion 的对比",
        "content": "Flow Matching 直接回归向量场 $v_t(x)$，而 diffusion 预测噪声 $\\epsilon$。两者等价于不同的参数化方式。Flow Matching 的优势在于可以使用任意概率路径，而不仅仅是扩散路径。",
        "note_type": "comparison",
        "paper": "Flow Matching for Generative",
        "concepts": ["Flow Field", "Denoising Process", "Continuous Normalizing Flow"],
    },
    {
        "title": "Transformer 注意力公式",
        "content": "Scaled Dot-Product Attention: $\\text{Attention}(Q,K,V) = \\text{softmax}(\\frac{QK^T}{\\sqrt{d_k}})V$。多头注意力将 $Q,K,V$ 投影到 $h$ 个不同子空间并行计算，然后拼接输出。",
        "note_type": "formula",
        "paper": "Attention Is All You Need",
        "concepts": ["Attention Score", "Residual Connection"],
    },
    {
        "title": "Classifier-Free Guidance 推导",
        "content": "CFG 的核心思想：$\\tilde{\\epsilon}_\\theta(x_t, c) = \\epsilon_\\theta(x_t, \\emptyset) + w \\cdot (\\epsilon_\\theta(x_t, c) - \\epsilon_\\theta(x_t, \\emptyset))$。当 $w>1$ 时增强条件信号。这避免了单独训练分类器。",
        "note_type": "formula",
        "paper": "Improving Diffusion Models",
        "concepts": ["Classifier-Free Guidance", "Denoising Process"],
    },
    {
        "title": "Score-Based SDE 框架总结",
        "content": "SDE 框架统一了 score matching 和 diffusion。正向 SDE: $dx = f(x,t)dt + g(t)dw$。反向 SDE: $dx = [f(x,t) - g(t)^2\\nabla_x \\log p_t(x)]dt + g(t)d\\bar{w}$。",
        "note_type": "summary",
        "paper": "Score-Based Generative Modeling",
        "concepts": ["Score Function", "Stochastic Differential Equation", "Denoising Process"],
    },
    {
        "title": "Chain-of-Thought 实验分析",
        "content": "CoT 在 GSM8K 数学推理任务上大幅超越标准 prompting。算术推理、常识推理、符号推理三个任务类别均有显著提升。效果随模型规模增加而增强——仅对 ~100B+ 参数模型明显有效。",
        "note_type": "analysis",
        "paper": "Chain-of-Thought Prompting",
        "concepts": ["Chain of Thought", "Self-Supervised Pretraining"],
    },
    {
        "title": "RLHF 三阶段训练流程",
        "content": "阶段 1: SFT — 收集人类示范数据微调。阶段 2: RM — 训练奖励模型来预测人类偏好排名。阶段 3: PPO — 使用奖励模型作为奖励函数，通过强化学习进一步微调策略。",
        "note_type": "summary",
        "paper": "Training language models to follow",
        "concepts": ["RLHF", "Self-Supervised Pretraining", "Chain of Thought"],
    },
    {
        "title": "Latent Diffusion 架构笔记",
        "content": "LDM 在 VAE 的潜在空间中执行扩散过程。编码器 $E$ 将图像压缩到潜在空间，扩散模型在该空间运行，解码器 $D$ 重建图像。通过交叉注意力层注入文本/语义条件。",
        "note_type": "architecture",
        "paper": "High-Resolution Image Synthesis",
        "concepts": ["Latent Space", "Denoising Process", "Attention Score"],
    },
    {
        "title": "ResNet 残差连接思考",
        "content": "残差连接 $y = F(x) + x$ 解决了深层网络退化问题。梯度可以直接通过恒等映射传播，无需经过非线性变换。这是后来 Transformer 中 residual connection 的灵感来源之一。",
        "note_type": "reflection",
        "paper": "Deep Residual Learning for Image",
        "concepts": ["Residual Connection", "Representation Learning"],
    },
    {
        "title": "Consistency Models 关键洞察",
        "content": "一致性模型强制 ODE 轨迹上所有点映射到同一终点：$f(x_t, t) = f(x_{t'}, t') = x_0$。这允许单步或少步生成，大幅加速采样。训练方式可以是 consistency distillation（从预训练 DM）或 consistency training（从头训练）。",
        "note_type": "analysis",
        "paper": "Consistency Models",
        "concepts": ["Score Function", "Denoising Process", "Continuous Normalizing Flow"],
    },
]

created_notes = 0
created_nc = 0
for ndata in notes_data:
    paper = find(ndata["paper"])
    if not paper:
        print(f"  SKIP note: '{ndata['title']}' (paper not found)")
        continue
    note = Note(
        paper_id=paper.paper_id,
        user_id=user_id,
        title=ndata["title"],
        content=ndata["content"],
        note_type=ndata.get("note_type", "summary"),
    )
    db.add(note)
    db.flush()
    created_notes += 1

    # 关联概念
    for cname in ndata["concepts"]:
        c = concept_map.get(cname)
        if c:
            nc = NoteConcept(
                note_id=note.note_id,
                concept_id=c.concept_id,
                confidence=0.9,
                source="manual",
            )
            db.add(nc)
            created_nc += 1

print(f"Notes: {created_notes}, Note-Concept links: {created_nc}")

# ============================================================
# 提交
# ============================================================
db.commit()
print("\n✅ All seed data committed successfully!")
print(f"Summary: {len(paper_objs)} papers, {len(author_map)} authors, {len(tag_map)} tags")
print(f"          {len(venue_map)} venues, {created_relations} relations, {created_notes} notes")
print(f"          {len(concept_map)} concepts, {created_nc} note-concept links")
db.close()
