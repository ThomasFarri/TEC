# Lesson 6: Writing a technical note an expert will trust

A model nobody reads, or reads and does not trust, is worth nothing. This lesson is about the document that carries your work to Cédric. It is a different skill from the modelling, and the main rule is that an expert reader is checking one thing: do you know where your result stops being true?

## 1. Who reads it and what they do

Cédric Dupont runs cryogenic refuelling. He knows boiling, venting and no-vent fill better than you do. He will not read a long note. He will read the first paragraph, look at the figures, jump to limitations, and then decide whether you are worth a call. So the structure is built for skimming:

1. A problem statement that says what is asked and why it matters, in two paragraphs.
2. Method, short, with the assumptions named as assumptions.
3. Validation before results. An expert asks "how do you know?" before "what did you get?".
4. Results with numbers.
5. Limitations, in their own section, specific and numbered.
6. Questions for the reader. This turns a report into a conversation.

## 2. The validation-first order

Lesson 2 and 3 showed the model has a mean error of 7 % on hydrogen fills, a worst case of 26 %, and that line chilldown real efficiency is 3 to 69 % of the thermodynamic limit. If the results section comes first, "LOX loses 0.44 %" reads as a prediction. If validation comes first, the reader already knows the error bar, and reads 0.44 % as "of order half a percent, with a margin". Order shapes how numbers are heard.

## 3. Quote numbers with their error and their domain

A bare number invites attack. Compare:

- "LCH4 chilldown loses 1.4 %."
- "For a 1 m3 aluminium receiver at baseline, the equilibrium model gives 1.4 % for LCH4. It has been validated on LH2 to 7 % mean error in final pressure, so treat it as a best case."

The second is longer and safer. Three things go with every headline number: the case (inputs), the model status (validated against what), and the direction of the bias (best case, so real losses are higher).

## 4. Writing limitations without apologising

A limitations section is not a confession. It is a map of where the model is not yet known to work. Each item should say what is missing, why it matters and which way the error goes. Example from the note: "The transient model is wrong by a factor 3 to 6 at low flow; do not use below about 300 kg/(m2 s)." That sentence protects you. A reader who finds the failure themselves will distrust everything; a reader you told will trust the rest.

Compare with a weak version: "The model has some limitations at low flow." No number, no direction, no action.

## 5. Questions for the reader

Ask only questions whose answers would change the model. In the note, the pressure limit and wall mass, inlet subcooling and start temperature are asked about because the sensitivity study (lesson 5) shows they decide the result. This is also a quiet demonstration that you understand which inputs matter. Do not ask things you could look up.

## 6. Worked example from this project

The note has about 1800 words and four figures. Take the headline claim in the conclusion: "chilldown loss is about 0.4 % (LOX) and 1.4 % (LCH4) of the load, and the line chilldown a few kilograms". Trace its support:

- 0.44 % is 4.4 kg of 1017 kg, from results/fig2_loss_vs_wall_mass.csv.
- 1.4 % is 5.2 kg of 376 kg, same file.
- A few kilograms: 2.4 to 3.4 kg LOX from results/transient_application.csv, an extrapolation of an LN2 calibration, and the note says so.
- Error bar: 7 % mean, 26 % worst, from results/validation_nvf_summary.csv.

Every sentence in a good note can be traced to a file in this way. If you cannot trace it, delete it or mark it as an assumption.

## 7. Plain prose

Short sentences. Define a symbol when it first appears. No decoration. Avoid words like "novel", "significant", "robust" unless you can give a number. An engineer reads "robust" as "I did not check".

## Self-test questions

1. Why does the note put validation before results?
2. Name the three things that should accompany every headline number.
3. Rewrite "the model has limitations at low flow" as a useful limitation statement.
4. Why should the questions for TEC be linked to the sensitivity study?
5. A reader asks where "2.4 kg for a 3 m LOX line" comes from. What do you show them, and what do you admit?

## Answers

1. The reader needs the error bar before they hear the numbers, so the numbers are read with the right amount of trust.
2. The case (inputs), the model status (what it was validated against) and the direction of the bias.
3. "The transient model is 3 to 6 times too slow below about 40 kg/(m2 s) and should not be used below about 300 kg/(m2 s) until checked against clean low-flow data."
4. Because the sensitivity study identifies which inputs drive the result, so the answers to those questions would change the model most. It also shows you know where the leverage is.
5. The transient model output (results/transient_application.csv), the calibration on one LN2 flight test (F2, C_fb = 2.41), and that extrapolating to LOX is untested and the lower flow range lies outside the calibrated regime.

## Further reading

Booth, Colomb and Williams, The Craft of Research, on structuring arguments for a reader. Any NASA technical memorandum in VALIDATION.md is a good example of the genre, particularly how Chato states test uncertainties up front.
