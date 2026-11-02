# Lesson 7: Defending a model under questioning

A model survives questioning if you can answer three things about every assumption: what it is, why you made it, and which way it pushes the answer. This lesson teaches how to build that habit and applies it to this project.

## 1. The assumption ledger

Write every assumption in a table with three columns: statement, justification, bias direction. The ledger in notes/defend_this.md is the example. The point is that bias direction turns a weakness into a design margin. "Equilibrium is optimistic" is not an admission of failure. It tells the reader to add margin.

Why do this at all? Because in an interview or review, the dangerous question is the one you did not expect. If you have classified every assumption as optimistic, pessimistic or unknown, you can answer the unexpected question by locating it in the ledger.

## 2. Three types of challenge

**"Is it right?"** Answer with validation numbers and their range. Mean absolute error 7 % on 32 LH2 fills, worst 26 %. Never say "accurate".

**"Does it apply here?"** Answer with an argument and mark it as an argument. LOX and LCH4 have a wall to load energy ratio of about 3 % against 24 % for LH2, so the wall matters less. This is reasoning, not data.

**"What would change your mind?"** Answer with a test. A LOX line chilldown with measured mass and time at G above 300 kg/(m2 s) would check the transient model directly.

## 3. Worked example: a hard question, answered

Question: "Your result says no chilldown is needed at 10 K subcooling. Is that believable?"

Build the answer in steps.

1. Facts from the model: at 5 K subcooling LOX needs one CHV cycle and loses 0.44 %; at 10 K zero. Cooling capacity is 203.3 kJ/kg at 5 K and 212.0 kJ/kg at 10 K, a 4.3 % increase.
2. Why a small change flips the result: wall energy is about 2.9 % of load capacity, so the system is close to the pass/fail threshold.
3. Bias: equilibrium is a best case and real fills ran up to 26 % higher pressure. So the threshold is probably at a higher subcooling in reality.
4. Conclusion: "In the model, 10 K removes the need. I would read that as: subcooling is the strongest lever, and real tests are needed to place the threshold."

That answer has a fact, a mechanism, a bias and a conclusion. Use that four-part shape.

## 4. Saying "I do not know"

You will be asked something you did not test, such as what happens with a composite tank. The right answer is short: "I have not modelled that. The model would need the wall specific heat and mass; I would expect X because of Y. I would test it by Z." Guessing fluently is worse than not knowing, because experts can tell.

## 5. Know the numbers cold

Keep about ten numbers in your head (section C of the sheet). Not because anyone tests recall, but because being able to quote them shows the work is yours.

## Self-test questions

1. What three things must you know about every assumption?
2. What is the difference between validation and an argument of applicability?
3. Why does knowing the bias direction help in a review?
4. Give the four-part shape of a good answer.
5. You are asked about a composite receiver. What do you say?

## Answers

1. What it is, why you made it, and which way it pushes the answer.
2. Validation compares model output with measurements in the same regime. An applicability argument says why the model should still work somewhere else, with no measurements there.
3. It tells you whether to add or subtract margin, and lets you place an unexpected question in the ledger.
4. Fact from the model, mechanism, bias direction, conclusion.
5. That you have not modelled it, what inputs the model would need (wall specific heat and mass), what you expect and why (composites have low thermal mass and conductivity, so wall energy would be smaller but wall temperature gradients larger), and how you would check it.
