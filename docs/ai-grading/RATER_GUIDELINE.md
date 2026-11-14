# Rater Guideline — EduMentor AI short-answer grading (gold set)

> Version 1.0 · 14/11/2026 · owner: Tuấn (module 09) · raters: **Hòa, Tâm**
> Change log is at the bottom. Read this whole page once before you start (about 10 minutes).

## 1. Why we need you

We are building an AI that grades short answers about basic Python, item by item, using a rubric.
To show the teacher **how accurate** it is, we need a set of answers graded by people: the *gold set*.
The AI's grades are compared with yours. Your grades are the reference, so please grade
**carefully, independently and consistently**: it matters more than speed.

- You grade **alone**. Do not look at the other rater's sheet and do not discuss specific answers after the
  calibration round (section 6).
- You will **never see the AI's grade**. Do not try to guess it, and do not run the answers through any AI tool.
- Expected effort: about 120 answers ≈ 400 rubric items, roughly **3–4 hours**. You can split it into sessions.

## 2. Your sheet

You receive one CSV file (open it in Google Sheets or Excel). **One row = one rubric item of one answer.**

| Column | Meaning |
|---|---|
| `row_id`, `answer_id` | IDs. Do not edit. |
| `question_code`, `question` | The question the learner answered. |
| `answer` | The learner's full answer. It is repeated on every row of the same answer. |
| `item_no`, `item` | The rubric item you grade on this row. |
| `max_points` | Points of the item (for information only, you do not compute points). |
| **`label`** | **Fill in:** `full`, `partial` or `none` (lower case, exactly these words). |
| `note` | Optional: a short reason. **Please write one when you choose `partial` or when you are unsure.** |

Rows of the same answer are next to each other; the order of answers is shuffled.
Do not sort, delete or add rows. Leave the other columns as they are.

## 3. The three labels

Grade **each item on its own**: does the answer, *anywhere*, express the idea of this item?

| Label | Use it when | Points (computed later) |
|---|---|---|
| **full** | The idea of the item is stated **correctly** and **clearly linked to the right subject**. | all points of the item |
| **partial** | The idea is there but **incomplete or vague**: the subject is missing or unclear, only half of the idea is stated, or it is mostly right with a small mistake. | half |
| **none** | The idea is **missing or wrong**: not mentioned, factually wrong, contradicted elsewhere, only the question copied back, or only the subject named with no idea about it. | 0 |

When you hesitate between two labels, choose the **lower** one and write why in `note`.

## 4. General rules

1. **Meaning, not keywords.** Different words with the same meaning are correct ("exits the loop" =
   "stops the loop" = "jumps out of the loop"). Using the right keyword with a wrong meaning is **not** correct.
2. **Ignore spelling, grammar and style.** "brake stop the loop" for `break` is still `full` if the idea is clear.
   Answers in Vietnamese or mixed language are graded on meaning too (write `vi` in `note`).
3. **Code counts.** `a, b = b, a`, `if n % 2 == 0:` or `print(a + b)` can satisfy an item by themselves.
4. **Subject matters.** "It cannot be changed" is `full` only if it is clear that *it* is the tuple. If the
   reader cannot tell which thing is meant → `partial`.
5. **Swapped or reversed ideas → `none`.** "A list cannot be changed, a tuple can" gets `none` for both items.
6. **Contradiction → `none`.** If the answer says the idea and also its opposite, the item is `none`.
7. **Copying the question earns nothing.** Words that are only repeated from the question do not count.
8. **Any correct example is fine.** The examples in brackets in the rubric are suggestions, not the only answer.
9. **Extra wrong statements do not remove points from other items**, unless they contradict that item (rule 6).
10. **Bare keyword lists** ("mutable immutable [] ()") with no statement about anything → `none`, or `partial` if
    one idea is still unambiguous. A short but real sentence ("list mutable, tuple not") is fine.
11. **Do not grade the overall quality.** Only the rubric items. A messy answer can still get `full` on every item.

## 5. Worked examples

**Concept item** — ITER-TL-01, item 1: *"break exits / stops the loop completely"*

| Answer (extract) | Label | Why |
|---|---|---|
| "break ends the loop immediately." | full | Same idea, different words. |
| "It stops the loop." (and the answer talks about continue in the same sentence) | partial | Unclear whether *it* is break or continue. |
| "break skips to the next iteration." | none | That describes continue (rule 5). |
| "break is a keyword used in loops." | none | Only names the subject; no idea about it. |

**Contrast item with a subject** — PY-TL-02, item 2: *"A tuple cannot be changed after it is created"*

| Answer (extract) | Label | Why |
|---|---|---|
| "Tuples are immutable." | full | |
| "A list can be changed, but not the other one." | partial | Idea present, subject not clear. |
| "You cannot change it." with no subject anywhere | partial | |
| "A tuple can be changed with append()." | none | Wrong. |

**Value / code item** — COND-TL-06, item 1: *"Condition age < 12"*

| Answer (extract) | Label | Why |
|---|---|---|
| `if age < 12 or age >= 60:` | full | Code satisfies the item. |
| "people younger than 12" | full | Same condition in words. |
| `age <= 12` | partial | Almost right; boundary wrong (small mistake). |
| "children get a discount" | partial | Idea but no threshold. |

**Explanation item** — CS-TL-05, item 2: *"the division is done before the addition (it prints 7.0)"*

| Answer (extract) | Label | Why |
|---|---|---|
| "/ has higher priority than +, so only b is divided." | full | |
| "It prints 7.0 instead of 5." | partial | Gives the symptom, not the cause. |
| "Because of operator order." | partial | Cause named but not explained. |
| "Because a and b are integers." | none | Wrong cause. |

**Example item** — CS-TL-03, item 3: *"a sensible example (a missing colon; a wrong condition...)"*

| Answer (extract) | Label | Why |
|---|---|---|
| "e.g. writing `prnt('hi')`" | full | Any correct example is fine (rule 8). |
| "for example a mistake in the code" | none | Not an example, just a restatement. |

## 6. Calibration round (before the main grading)

1. Tuấn sends both of you the **same 20 answers** (`rater_<name>_calibration.csv`).
2. You grade them alone, then the three of you meet (≈ 30 minutes) and look only at the rows where your labels differ.
3. If a disagreement comes from an unclear rule, Tuấn updates this guideline (new version below).
   Calibration answers are **not** part of the gold set.
4. After that you grade the main sheet **independently**. No more discussion of specific answers.

Remaining disagreements in the main sheet are decided by Tuấn or the teacher; your original labels are kept, and
the agreement between you two is reported (Cohen's kappa).

## 7. Before you send the sheet back

- [ ] Every row has a `label` (`full` / `partial` / `none`).
- [ ] `note` is filled for `partial` and unsure rows.
- [ ] Rows were not sorted, deleted or added.
- [ ] Download as **CSV** and send the file back to Tuấn privately (not in the group chat). The answers are learners'
      data: do not share them.

## Change log

| Version | Date | Change |
|---|---|---|
| 1.0 | 14/11/2026 | First version. |
