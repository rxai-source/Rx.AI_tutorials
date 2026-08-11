
---

# I Took OpenAI's Original Coding Benchmark That Everyone Forgot About

**Estimated Duration:** ~5–6 minutes

---

## Chapter 1 — Cold Open (0:00 – 0:35)

### Visuals

Fast-paced montage: Logos of OpenAI, Anthropic, DeepSeek, and Gemini flashing on screen, Twitter/X posts showing benchmark graphs, a code editor running tests, and your tracking spreadsheet.

### Script

This benchmark used to be the gold standard for AI coding ability. Now top labs don’t even bother reporting it. Here’s what killed it.

Back in 2021, OpenAI released HumanEval. Over the next few years, AI companies spent billions bragging about their HumanEval scores on Twitter... over a dataset that’s smaller than a single chapter of a college CS textbook.

Today? Nobody talks about it anymore.

So, I decided to run an experiment. Today, I’m taking the same benchmark myself to answer three questions:

> **Can a human developer actually beat this benchmark?**
> **Where do we trip up on supposedly simple coding tasks?**
> **And why did the entire AI industry abandon HumanEval so fast?**

**[Cut to Title Card: HumanEval vs Me]**

---

## Chapter 2 — The Dashboard & The Challenge (0:35 – 0:55)

### Visuals

On-screen dashboard with live statistics from your run.

```
After 30 Problems

✅ Pass@1 : 67%
⏱ Average Time : 7.4 min

❌ Biggest Failure : Edge Cases
🤯 Biggest Surprise : Cleaner than canonical code

```

### Script

I won't spoil the whole run yet, but looking at my initial dashboard... it was a massive reality check.

I was failing problems I thought were trivial, overthinking simple logic, and in one weird instance with regular expressions, I accidentally wrote cleaner code than the benchmark’s official reference solution.

Looking at these problems, I have to ask: **how many of these 164 questions do you think you could solve?**

Before we break down my mistakes, let's look at what this benchmark actually is.

---

## Chapter 3 — What is HumanEval? (0:55 – 1:45)

### Visuals

Diagram animation showing function prompt $\rightarrow$ docstring $\rightarrow$ execution against hidden unit tests.

### Script

OpenAI created HumanEval in 2021 for their landmark Codex paper.

Only 164 Python programming problems. That’s it.

Yet this tiny benchmark became one of the most influential AI evaluations ever created.

Each problem gives you a standard setup: a function signature, a docstring explaining what to do, and a couple of basic example inputs.

The catch? You pass or fail based on hidden unit tests you can't see while writing the code.

The primary metric here is **Pass@1**. In plain English: did your code pass every single hidden test on your very first try, without any debugging or re-runs?

---

## Chapter 4 — The Historical Record of AI (1:45 – 2:20)

### Visuals

Timeline on screen tracking model score jumps over time.

* 2021: OpenAI Codex
Pass@1 score around 28-33% — the spark for AI coding.


* 2022–2023: GPT-3.5 & GPT-4
Pass@1 jumps from ~48% to over 67%. HumanEval becomes the global metric.


* 2024–2026: Claude 3.5, DeepSeek, Gemini
Models break 90%+ accuracy, saturating the benchmark completely.


### Script

Every major LLM company has used it to prove they’re better.

This is my favorite observation about HumanEval: **the benchmark accidentally became a timeline of AI progress.**

For years, every major coding model announcement included one mandatory sentence: *"We achieved X% on HumanEval."*

Because every lab used the exact same 164 problems, HumanEval became a historical record of AI capability, charting the leap from basic code completion to near-perfect logic in under three years.

---

## Chapter 5 — What Killed HumanEval? (2:20 – 3:00)

### Visuals

Graph showing model scores flattening at 90-95%+ near the top of the chart, transitioning to logos for SWE-bench and LiveCodeBench.

### Script

So why did everyone move on?

It comes down to two things: **saturation** and **realism**.

A 2026 research audit found 29 out of 60 widely-used benchmarks show high or very-high saturation, with older benchmarks saturating more often than newer ones — HumanEval is basically a poster child for this pattern.

When every flagship model scores above 90%, the test loses its ability to separate good models from frontier ones. Add in public web availability — where data contamination became an open secret — and the numbers stopped meaning much.

On top of that, HumanEval only tests standalone Python functions. Real software engineering isn't writing 10-line helper functions; it's navigating massive codebases, fixing GitHub issues, and configuring build systems.

That’s why the industry moved on to **LiveCodeBench** for untainted competitive coding, and **SWE-bench** for real-world development tasks.

---

## Chapter 6 — My Experiment (3:00 – 3:40)

### Visuals

Screen recording scrolling through your detailed tracking spreadsheet showing columns for time, pass/fail, error category, and code length.

### Script

Even if HumanEval is obsolete for frontier AI models, it’s an incredible mirror for human developers.

To test myself under strict AI conditions, I tracked four things:

* Solve time per problem
* Strict Pass@1 rate (no test runs allowed before submitting)
* Category of error on every failure
* Code style compared to the canonical reference solutions

I wanted to see where a human brain fails compared to a neural network when forced to get code right on the very first try.

---

## Chapter 7 — Deep Dive: Where Humans Trip Up (3:40 – 4:35)

### Visuals

Simple failure mode breakdown chart alongside side-by-side code snippets comparing your code vs canonical solutions.

```
Failure Causes

Edge Cases  ██████████
Logic       ██████
Syntax      ███
Algorithm   ██

```

### Script

Looking across the first batch of 30 problems, my failures almost never came from complex algorithms. They came from missing subtle edge cases—like handling empty lists, negative inputs, or custom formatting string edge-cases.

An LLM doesn't get tired or skim past docstring details, but humans do.

On the flip side, human intuition wins on code simplicity. Canonical benchmark solutions often lean heavily on dense, unreadable list comprehensions. In several instances, writing code naturally gave me a far cleaner implementation than the benchmark's reference code.

When you look across all 30 problems, it raises the core question: **What is this problem really testing?**

It isn't testing deep algorithmic genius. **It's testing attention to detail under zero-iteration constraints.** It tests your ability to translate written specifications into error-proof edge-case handling on the very first attempt.

---

## Chapter 8 — Conclusion & Next Steps (4:35 – 5:00)

### Visuals

Full-screen graphic showing your current benchmark completion bar filling up to 164.

### Script

HumanEval may no longer be the benchmark that decides which multi-billion-dollar AI model is supreme. But as a workout for your own coding precision, it's unmatched.

I am completing all **164 HumanEval problems** to set my baseline score.

Once this is wrapped up, we’re moving straight to **LiveCodeBench** and **SWE-bench** to answer the ultimate question: **Can human developers still keep up with frontier AI in real-world environments?**

Hit subscribe to catch the next episode, and drop your guessed Pass@1 score in the comments below.

---

## End Screen Visuals

```
HumanEval Progress
█████░░░░░░░░░░░░░░░

Solved : 30 / 164
Pass@1 : 67%
Average Time : 7m 24s

Current Goal
➡ Finish all 164 HumanEval problems
➡ Challenge LiveCodeBench
➡ Final Boss: SWE-bench

```