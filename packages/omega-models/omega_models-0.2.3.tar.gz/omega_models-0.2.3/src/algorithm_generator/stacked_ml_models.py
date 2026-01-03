import os
import math
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


# -----------------------
# Config
# -----------------------
@dataclass
class CFG:
    # Teachers (DeepSeek distills that are feasible on 1-2 GPUs)
    teacher_model_ids: List[str] = None

    # Student to distill into (can be one of the teachers, or another model)
    student_model_id: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

    # Ensemble variation beyond size: different "modes"
    # (system prompts + temperature differences)
    system_prompts: List[str] = None
    temperatures: List[float] = None

    # Data
    train_jsonl: str = "train.jsonl"
    max_seq_len: int = 2048

    # Compute
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    dtype: torch.dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16

    # Training
    batch_size: int = 2
    num_workers: int = 0

    # Stacker
    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    stacker_hidden: int = 256
    stacker_lr: float = 2e-4
    stacker_epochs: int = 2

    # Distill
    distill_lr: float = 1e-5
    distill_epochs: int = 1
    kl_temperature: float = 1.0          # temp for KL between student and teacher-mixture
    alpha_kl: float = 1.0               # weight on KL loss
    alpha_ce: float = 0.0               # optional: add CE to ground truth

    # Outputs
    out_dir: str = "out_stack_distill"


def make_cfg() -> CFG:
    cfg = CFG()
    cfg.teacher_model_ids = [
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    ]
    cfg.system_prompts = [
        "You are a helpful assistant. Answer clearly and correctly.",
        "You are a careful reasoning assistant. Think step-by-step internally, but only output the final answer.",
    ]
    cfg.temperatures = [0.2, 0.7]
    return cfg


# -----------------------
# Helpers: tokenization
# -----------------------
def build_chat_text(system_prompt: str, user_prompt: str, assistant_response: str) -> str:
    # Generic instruction formatting (works broadly even if model has its own chat template)
    # If your DeepSeek variant requires a specific template, swap this out.
    return (
        f"<|system|>\n{system_prompt}\n"
        f"<|user|>\n{user_prompt}\n"
        f"<|assistant|>\n{assistant_response}"
    )

def tokenize_pair(tok, prompt_text: str, full_text: str, max_len: int):
    # full_text includes prompt + response
    full = tok(full_text, truncation=True, max_length=max_len, return_tensors="pt")
    prompt = tok(prompt_text, truncation=True, max_length=max_len, return_tensors="pt")
    return full, prompt


# -----------------------
# Dataset
# -----------------------
class PromptResponseDataset(torch.utils.data.Dataset):
    def __init__(self, jsonl_path: str):
        self.rows = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    self.rows.append(json.loads(line))

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        return self.rows[i]["prompt"], self.rows[i]["response"]


# -----------------------
# Teacher forward (logits)
# -----------------------
@torch.no_grad()
def teacher_logits_for_example(
    model,
    tok,
    prompt: str,
    response: str,
    system_prompt: str,
    max_len: int,
    device: str,
    dtype: torch.dtype,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Returns:
      logits: [T, V] logits for each token position of full sequence (shifted later)
      labels_mask: [T] mask for which positions belong to response tokens (1=response, 0=prompt)
    """
    # Build text for (prompt only) and (prompt+response)
    prompt_text = build_chat_text(system_prompt, prompt, "")
    full_text   = build_chat_text(system_prompt, prompt, response)

    full_enc, prompt_enc = tokenize_pair(tok, prompt_text, full_text, max_len)

    input_ids = full_enc["input_ids"].to(device)
    attn_mask = full_enc["attention_mask"].to(device)

    out = model(input_ids=input_ids, attention_mask=attn_mask)
    logits = out.logits.squeeze(0).to(torch.float32)  # [T, V] in fp32 for stability

    # Mark response region: tokens after prompt length
    prompt_len = prompt_enc["input_ids"].shape[1]
    T = input_ids.shape[1]
    mask = torch.zeros(T, dtype=torch.float32, device=logits.device)
    mask[prompt_len:T] = 1.0

    return logits, mask


# -----------------------
# Stacker: gating network
# -----------------------
class GatingNet(nn.Module):
    def __init__(self, embed_dim: int, n_teachers: int, hidden: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embed_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_teachers),
        )

    def forward(self, prompt_emb: torch.Tensor) -> torch.Tensor:
        # returns teacher weights (simplex)
        return F.softmax(self.net(prompt_emb), dim=-1)


def mixture_from_teachers(
    teacher_logits: List[torch.Tensor],   # each [T, V]
    weights: torch.Tensor,                # [n_teachers]
    temperature: float = 1.0,
) -> torch.Tensor:
    """
    Build mixture distribution over vocab at each position:
      p_mix = sum_i w_i * softmax(logits_i / temp)
    Returns probs [T, V]
    """
    probs = []
    for lg in teacher_logits:
        probs.append(F.softmax(lg / temperature, dim=-1))
    # Weighted sum
    mix = torch.zeros_like(probs[0])
    for w, p in zip(weights, probs):
        mix += w * p
    # Normalize just in case (should already sum to 1)
    mix = mix / (mix.sum(dim=-1, keepdim=True) + 1e-12)
    return mix


def kl_to_mixture(student_logits: torch.Tensor, teacher_mix_probs: torch.Tensor, temperature: float) -> torch.Tensor:
    """
    KL( teacher || student ) over vocab, averaged over positions.
    student_logits: [T, V]
    teacher_mix_probs: [T, V]
    """
    # student log probs with temperature
    logp_s = F.log_softmax(student_logits / temperature, dim=-1)
    # teacher probs
    p_t = teacher_mix_probs
    # KL(p_t || p_s) = sum p_t * (log p_t - log p_s)
    kl = (p_t * (torch.log(p_t + 1e-12) - logp_s)).sum(dim=-1)
    return kl.mean()


# -----------------------
# Main: train stacker then distill student
# -----------------------
def main():
    cfg = make_cfg()
    os.makedirs(cfg.out_dir, exist_ok=True)

    # Prompt embedder for stacking (variation source not related to model size)
    embedder = SentenceTransformer(cfg.embed_model, device=cfg.device)

    # Load dataset
    ds = PromptResponseDataset(cfg.train_jsonl)
    loader = DataLoader(ds, batch_size=1, shuffle=True, num_workers=cfg.num_workers)

    # Load tokenizers and teachers
    teacher_toks = []
    teachers = []
    for mid in cfg.teacher_model_ids:
        tok = AutoTokenizer.from_pretrained(mid, use_fast=True)
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            mid,
            torch_dtype=cfg.dtype,
            device_map="auto" if cfg.device == "cuda" else None,
        )
        model.eval()
        teacher_toks.append(tok)
        teachers.append(model)

    # Stacker gating net
    # Use embedding dim from SentenceTransformer
    test_emb = embedder.encode(["test"], convert_to_tensor=True)
    embed_dim = test_emb.shape[-1]
    gating = GatingNet(embed_dim, n_teachers=len(teachers), hidden=cfg.stacker_hidden).to(cfg.device)
    opt_g = torch.optim.AdamW(gating.parameters(), lr=cfg.stacker_lr)

    # -----------------------
    # (A) Train the stacker (gating net)
    # Objective: maximize teacher-mixture likelihood on reference response tokens
    # -----------------------
    print("\n[A] Training stacker (gating net)...")
    gating.train()

    for epoch in range(cfg.stacker_epochs):
        pbar = tqdm(loader, desc=f"Stacker epoch {epoch+1}/{cfg.stacker_epochs}")
        for prompt, response in pbar:
            prompt = prompt[0]
            response = response[0]

            # Embed prompt (the stacker sees prompt features)
            emb = embedder.encode([prompt], convert_to_tensor=True).to(cfg.device)  # [1, D]
            weights = gating(emb).squeeze(0)  # [n_teachers]

            # Collect teacher logits with variation beyond size:
            # We'll randomly choose a (system_prompt, temperature) mode each step,
            # and compute teacher logits under that formatting.
            # (You can expand to multiple modes and average them if you want.)
            sys = cfg.system_prompts[torch.randint(0, len(cfg.system_prompts), (1,)).item()]

            # IMPORTANT: use the tokenizer that corresponds to each teacher
            teacher_logits = []
            teacher_masks = []
            for model, tok in zip(teachers, teacher_toks):
                lg, mask = teacher_logits_for_example(
                    model=model, tok=tok, prompt=prompt, response=response,
                    system_prompt=sys, max_len=cfg.max_seq_len,
                    device=cfg.device, dtype=cfg.dtype
                )
                teacher_logits.append(lg)
                teacher_masks.append(mask)

            # Make sure sequence lengths match: truncate to min T
            T = min(l.shape[0] for l in teacher_logits)
            teacher_logits = [l[:T] for l in teacher_logits]
            teacher_masks = [m[:T] for m in teacher_masks]

            # Mixture probs (token dist)
            mix_probs = mixture_from_teachers(teacher_logits, weights, temperature=1.0)  # [T, V]

            # Compute NLL of reference tokens under mixture
            # We need the reference token IDs (use first teacher tokenizer as "reference tokenizer")
            # Best practice: use a single shared tokenizer; if they differ, pick one and keep consistent.
            ref_tok = teacher_toks[0]
            full_text = build_chat_text(sys, prompt, response)
            enc = ref_tok(full_text, truncation=True, max_length=cfg.max_seq_len, return_tensors="pt")
            input_ids = enc["input_ids"].to(cfg.device).squeeze(0)  # [T_ref]
            T_ref = min(T, input_ids.shape[0])
            input_ids = input_ids[:T_ref]

            # Response mask from teacher 0 (aligned-ish)
            mask = teacher_masks[0][:T_ref]  # [T_ref]

            # shift for next-token prediction
            # logits[t] predicts token[t+1]
            probs_next = mix_probs[:T_ref-1]  # [T_ref-1, V]
            target_next = input_ids[1:T_ref]  # [T_ref-1]
            mask_next = mask[1:T_ref]         # [T_ref-1]

            # NLL
            p_true = probs_next.gather(dim=-1, index=target_next.unsqueeze(-1)).squeeze(-1)  # [T_ref-1]
            nll = -(torch.log(p_true + 1e-12) * mask_next).sum() / (mask_next.sum() + 1e-12)

            opt_g.zero_grad(set_to_none=True)
            nll.backward()
            opt_g.step()

            pbar.set_postfix({"nll": float(nll.detach().cpu())})

    torch.save(gating.state_dict(), os.path.join(cfg.out_dir, "gating.pt"))
    print(f"Saved gating net → {cfg.out_dir}/gating.pt")

    # -----------------------
    # (B) Distill into student
    # Student matches stacked mixture distribution (KL)
    # -----------------------
    print("\n[B] Distilling student...")
    student_tok = AutoTokenizer.from_pretrained(cfg.student_model_id, use_fast=True)
    if student_tok.pad_token is None:
        student_tok.pad_token = student_tok.eos_token

    student = AutoModelForCausalLM.from_pretrained(
        cfg.student_model_id,
        torch_dtype=cfg.dtype,
        device_map="auto" if cfg.device == "cuda" else None,
    )
    student.train()
    opt_s = torch.optim.AdamW(student.parameters(), lr=cfg.distill_lr)

    gating.eval()

    for epoch in range(cfg.distill_epochs):
        pbar = tqdm(loader, desc=f"Distill epoch {epoch+1}/{cfg.distill_epochs}")
        for prompt, response in pbar:
            prompt = prompt[0]
            response = response[0]

            # Choose a mode (this is extra ensemble variance, not model size)
            sys = cfg.system_prompts[torch.randint(0, len(cfg.system_prompts), (1,)).item()]
            # You can also randomize temperature for teacher mixture
            temp = cfg.temperatures[torch.randint(0, len(cfg.temperatures), (1,)).item()]

            # Prompt embedding → teacher weights
            emb = embedder.encode([prompt], convert_to_tensor=True).to(cfg.device)
            weights = gating(emb).squeeze(0)  # [n_teachers]

            # Teacher logits
            teacher_logits = []
            teacher_masks = []
            for model, tok in zip(teachers, teacher_toks):
                lg, mask = teacher_logits_for_example(
                    model=model, tok=tok, prompt=prompt, response=response,
                    system_prompt=sys, max_len=cfg.max_seq_len,
                    device=cfg.device, dtype=cfg.dtype
                )
                teacher_logits.append(lg)
                teacher_masks.append(mask)

            T = min(l.shape[0] for l in teacher_logits)
            teacher_logits = [l[:T] for l in teacher_logits]
            teacher_masks = [m[:T] for m in teacher_masks]
            mask = teacher_masks[0]  # [T]

            teacher_mix = mixture_from_teachers(teacher_logits, weights, temperature=temp)  # [T, V]

            # Student forward on same text
            full_text = build_chat_text(sys, prompt, response)
            enc = student_tok(full_text, truncation=True, max_length=cfg.max_seq_len, return_tensors="pt")
            input_ids = enc["input_ids"].to(cfg.device)
            attn_mask = enc["attention_mask"].to(cfg.device)

            out = student(input_ids=input_ids, attention_mask=attn_mask)
            student_logits = out.logits.squeeze(0).to(torch.float32)  # [T_s, V_s]

            # Align lengths & vocab note:
            # This assumes same vocab size. If student/teachers have different tokenizers/vocabs,
            # you need a vocab mapping or distill on sampled outputs instead of logits.
            Ts = min(T, student_logits.shape[0], teacher_mix.shape[0])
            student_logits = student_logits[:Ts]
            teacher_mix = teacher_mix[:Ts]
            mask = mask[:Ts]

            # Shift for next-token distillation
            student_logits_next = student_logits[:-1]
            teacher_mix_next = teacher_mix[:-1]
            mask_next = mask[1:Ts]  # align with targets

            # KL distill loss (only on response region)
            kl = kl_to_mixture(student_logits_next, teacher_mix_next, temperature=cfg.kl_temperature)
            # Apply response mask (simple reweight)
            # (We approximate by scaling KL by fraction of response tokens.)
            frac = (mask_next.mean().clamp_min(1e-3)).detach()
            loss_kl = kl / frac

            loss = cfg.alpha_kl * loss_kl

            # Optional: add CE to ground-truth tokens
            if cfg.alpha_ce > 0:
                targets = input_ids.squeeze(0)[1:Ts]  # [Ts-1]
                ce = F.cross_entropy(student_logits_next, targets, reduction="none")  # [Ts-1]
                ce = (ce * mask_next[:-1]).sum() / (mask_next[:-1].sum() + 1e-12)
                loss = loss + cfg.alpha_ce * ce

            opt_s.zero_grad(set_to_none=True)
            loss.backward()
            opt_s.step()

            pbar.set_postfix({"loss": float(loss.detach().cpu()), "kl": float(loss_kl.detach().cpu())})

    # Save student
    student_out = os.path.join(cfg.out_dir, "student_distilled")
    os.makedirs(student_out, exist_ok=True)
    student.save_pretrained(student_out, safe_serialization=True)
    student_tok.save_pretrained(student_out)
    print(f"\nSaved distilled student → {student_out}")


if __name__ == "__main__":
    main()
