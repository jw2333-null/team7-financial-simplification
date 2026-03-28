# Annotation Guidelines — Financial Jargon Simplification

Read all guidelines before beginning annotation. **When in doubt, preserve meaning over simplicity.**

## Core Principles

1. **Preserve all key meaning.** The simplified version must convey the same information as the original. A reader of the simplified version should be able to make the same financial decisions. Do not add or remove information.

2. **Preserve numbers, dates, thresholds, and percentages exactly.** Never round, approximate, or omit a numerical value. "21 calendar days" must stay "21 calendar days," not "about three weeks."

3. **Preserve conditions, warnings, exclusions, obligations, and limitations.** If the original says "this does not apply if you close the account within 14 days," the simplified version must retain both the exclusion and the 14-day condition.

4. **Do not make the text legally weaker or stronger.** If the original uses "may" (possibility), do not change it to "will" (certainty). If the original says "you are responsible for," do not weaken it to "you should try to."

5. **Simplify wording and sentence structure for a non-expert consumer.** Replace jargon with everyday language where a good equivalent exists. Break long sentences into shorter ones — where possible, split sentences longer than 35 words into two or more shorter sentences. Use active voice where possible. Aim for approximately grade 8–10 reading level (FKGL).

6. **Preserve the grammatical person of the original.** If the original refers to "the borrower" or "the lender" in the third person, do not change it to "you" or "we." Changing person can alter who the obligation applies to and may distort the legal meaning.

7. **Do not add explanations, examples, or context that are not present in the original.** Simplification means rewording, not expanding. If you feel extra context is needed, note it in the notes field instead.

## Handling Jargon Without a Perfect Equivalent

- If the term has a widely understood short explanation, insert it in parentheses after the term the first time it appears. Example: "APR (the total yearly cost of borrowing, shown as a percentage)."
- If the term is defined in the glossary, use the glossary as a guide but do not copy it verbatim.
- If the term cannot be explained briefly without distorting its meaning, keep the original term and note it in the jargon_terms field. A simplification that retains one necessary technical term is better than one that replaces it with an inaccurate paraphrase.

## Parenthetical Explanations

- Keep parenthetical explanations to **10 words or fewer**.
- If the explanation requires more than 10 words, write it as a separate sentence immediately after, rather than embedding it in parentheses.

  ✓ `"APR (the yearly cost of borrowing, as a percentage)"`

  ✗ `"APR (this stands for Annual Percentage Rate and represents the total yearly cost of borrowing shown as a percentage including all fees and charges)"`

- Do not use multiple parenthetical explanations in the same sentence, as this disrupts readability.

## Common Mistakes to Avoid

- **Do NOT substitute technical terms with inaccurate equivalents.**

  ✗ `"bonds" → "investment certificates"` (factually wrong — these are different financial instruments)

  ✓ `"bonds (debt investments that pay regular interest)"`

- **Do NOT drop numerical thresholds, monetary values, or time limits.**

  ✗ Omitting "less than £1 million" from a regulatory condition

  ✓ Always keep exact figures exactly as written

- **Do NOT shift grammatical person without reason.**

  ✗ `"the lender can report the borrower" → "we can report you"` (changes who the obligation applies to)

  ✓ Keep the same grammatical person as the original

- **Do NOT resolve modality — preserve possibility vs certainty.**

  ✗ `"may be charged" → "will be charged"` (turns a possibility into a certainty)

  ✓ Keep "can", "may", "might", "will" exactly as they appear in the original

- **Do NOT add information not present in the original.**

  ✗ Adding an example, consequence, or explanation that was not in the source text

  ✓ If you feel context is needed, note it in the notes field instead

## Handling Ambiguity

If the original text is genuinely ambiguous, do not resolve the ambiguity. Rewrite the sentence to be clearer in structure but preserve the same range of possible meanings. If you believe the ambiguity is a drafting error, note it in the notes field but do not correct it.

## When to Reject a Snippet

Mark `rejected = TRUE` if:
- The snippet is unintelligible without a table, figure, or preceding paragraph not included in the dataset
- The snippet is already written in plain, accessible language and does not need simplification
- The snippet is a boilerplate legal formula that cannot be simplified without changing its legal effect
- The snippet contains an error in the source document that would make any simplification misleading

Record the reason in the `rejection_reason` field.

## Confidence Rating

- **High** — You are confident the simplification preserves all meaning and is clearly easier to read.
- **Medium** — You think the simplification is correct but are unsure about one aspect (e.g. whether a jargon term was handled well).
- **Low** — You are uncertain whether the simplification preserves the full meaning. Flag for review.

## Examples

### Good Simplification
**Original:** "If you go over your credit limit, you'll have to pay an over credit limit fee. We will move any remaining promotional balances on your account back to your standard balance and charge interest at your standard rate."

**Simplified:** "If you spend more than your credit limit, you will be charged a fee. Any special lower-rate deals on your account will end, and we will charge interest at your normal rate instead."

Why this works: Numbers and conditions preserved. "Promotional balance" explained in plain terms. "Standard rate" → "normal rate" is a safe substitution. The warning about consequences is retained.

### Bad Simplification
**Original:** "You may be charged a late payment fee of £12 if your minimum payment is not received by the due date."

**Bad:** "You will be charged £12 if you pay late."

Why this fails: "May be charged" became "will be charged" (modality shift — turned possibility into certainty). "Minimum payment" and "due date" were dropped, losing specificity.

## Version History

- v1.0 — Initial guidelines (before pilot annotation)
- v1.1 — Added Core Principles 6 and 7 (grammatical person, no added information); added Parenthetical Explanations section; added Common Mistakes to Avoid section (after pilot calibration, Phase 4.3)
