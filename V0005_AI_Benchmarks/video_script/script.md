# I Took OpenAI's Original Coding Benchmark that everyone forgot about


## Episode 1 – The Benchmark That Started AI Coding

**Duration:** ~5 minutes

---

# Chapter 1 — Cold Open (0:00 – 0:35)

## Visuals

Quick montage of model logos (OpenAI, Anthropic, DeepSeek, Gemini), code editor with passing/failing tests, and your tracking spreadsheet.

## Script

Back in 2021, OpenAI released a benchmark called HumanEval. For a long time, it was the standard metric for testing how well AI could write code. Every model provider bragged about their HumanEval score.

Today? Almost nobody talks about it anymore.

So, I decided to run an experiment. I'm putting myself up against this classic benchmark to answer three things:

>
> **Can I beat this benchmark myself?**
>
> **Where do human developers actually trip up on simple coding problems?**
>
**And why did the AI industry move past HumanEval so fast?**

**Cut to Title**

# HumanEval vs Me

---

# Chapter 2 — The Results (Without Spoiling Everything) (0:35 – 0:55)

Show a quick dashboard.

```
After 30 Problems

✅ Pass@1 : 67%

⏱ Average Time : 7.4 min

❌ Biggest Failure :
Edge Cases

🤯 Biggest Surprise :
Sometimes my solution was cleaner than
the canonical solution.
```

## Script

I won't spoil the whole run, but my initial results were a bit of an eye-opener.

I was failing problems I thought were trivial, completely overthinking basic logic, and in one weird instance with regular expressions, I accidentally wrote cleaner code than the benchmark's official reference solution.

Before we get into my mistakes, let's look at what HumanEval actually tests.

# Chapter 3 — What is HumanEval? (0:55 – 1:45)

## Animation

Visual diagram showing function prompt >> docstring >> execution against hidden unit tests.

## Script

OpenAI created HumanEval in 2021 for their Codex paper. It's a suite of 164 handwritten Python programming problems.
Each problem gives you a standard setup: a function signature, a docstring explaining what to do, and a couple of basic example inputs.

The catch? You pass or fail based on hidden test cases you can't see while writing the code.

The primary metric used here is Pass@1. In simple terms: did your code pass every single test on your very first try, without any debugging runs?

---

# Chapter 4 — Why HumanEval Became Famous (1:45 – 2:20)

## Timeline Animation

```
2021 (Codex)>> 2022 (GPT-3.5)?? 2023 (GPT-4) >> 2024–Present (Claude 3.5 / DeepSeek / Gemini)
```

## Script

Between 2021 and 2023, HumanEval was the gold standard. It was lightweight, fully reproducible, and easy to run.

If you built a new LLM, showing off a high HumanEval score was the quickest way to convince developers your model could actually code.
---

# Chapter 5 — The Twist (2:20 – 3:00)

## Visual
Continuation from previous chapter.

## Script

So why did everyone move on? Two main reasons: saturation and realism.

First, modern models essentially maxed it out. When every flagship model scores above 90%, the benchmark loses its ability to differentiate between good models and great ones. Plus, because the 164 problems are public, data contamination became a real issue.

Second, HumanEval only tests standalone Python functions. Real software engineering isn't writing 10-line helper functions in isolation—it's navigating large codebases, fixing GitHub issues, and working across multiple files.

That's why the industry moved on to benchmarks like **LiveCodeBench** for untainted, competitive programming problems, and **SWE-bench** for real-world software development.

---

# Chapter 6 — My Experiment (3:00 – 3:40)

Show your spreadsheet.

## Script

Even if HumanEval is obsolete for frontier AI, it's actually a great warm-up for human devs.

Instead of just grading myself on a pass/fail basis, I set up a tracker to measure:

Solve time per problem

Strict Pass@1 rate (no test runs before submission)

Category of error when I failed

Code length and style compared to the canonical reference solutions

I wanted to see how I compare to an LLM on basic, isolated coding tasks.
---

# Chapter 7 — What Stood Out (3:40 – 4:35)

Simple bar chart showing failure modes (Edge Cases at the top, followed by Misreading Prompts, Logic Errors, and Syntax Errors).

## Example Visual

```
Failure Causes

Edge Cases
██████████

Logic
██████

Syntax
███

Algorithm
██
```

## Script (NOTE : Needs to be updated based on my actual performance)

The biggest takeaway so far? My failures almost never came from hard algorithms. They came from missing subtle edge cases—like handling empty lists, negative numbers, or custom string formatting.

An LLM doesn't get tired or skip reading docstring details, but humans do.

On the flip side, human intuition still wins on code cleanliness sometimes. Canonical benchmark solutions often lean heavily on dense list comprehensions. In a few cases, taking a step back gave me a much simpler, more readable implementation than the benchmark's own reference code.

---

# Chapter 8 — Conclusion (4:35 – 5:00)

## Script

> HumanEval may no longer be the benchmark that decides which AI model is best.
>
> But it's still an incredible benchmark for improving your own programming skills.
>
As a part of this journey, I solved all **164 HumanEval problems.**
>
Next, we will be moving straight to LiveCodeBench and SWE-bench to see **Can humans still keep up?**


---

# Suggested Thumbnail

### Left Side

🤖 GPT-5

Claude

Gemini

DeepSeek

### Right Side

👨‍💻 You

Timer running

Spreadsheet

HumanEval logo

Large Text

```
Can I Beat AI?
```

or

```
Human vs GPT
```

---

# End Screen

```
HumanEval Progress

█████░░░░░░░░░░░░░░░

Solved : 27 / 164

Pass@1 : 71%

Average Time : 6m 42s

Current Goal

➡ Finish all 164 problems
➡ Move to LiveCodeBench
➡ Finally tackle SWE-bench
```

---

# Overall Narrative

This video isn't really about solving coding problems.

It's about telling the story of a benchmark that launched the AI coding revolution, why it mattered, why it quietly faded into the background, and what happens when a human decides to compete against it anyway.

That story gives viewers history, competition, learning, and an ongoing series to follow.