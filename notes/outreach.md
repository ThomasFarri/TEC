# Outreach drafts (DRAFTS ONLY, nothing has been sent or posted)

Thomas decides whether, when and how to send. Check every number against the technical note and results files before using anything here. Edit into your own voice.

## 1. LinkedIn post draft

Key figure: figures/fig4_sensitivity.png (top left panel) or figures/fig2_loss_vs_wall_mass.png.

---

Moving liquid oxygen and methane between spacecraft starts with a warm tank. How much propellant does it cost to cool it down?

I built a Python model to find out, for my own learning, and checked it against NASA test data.

What I found for a 1 m3 aluminium receiver with a 40 kg wall, starting at 290 K:
- Chilling the receiver costs about 0.4 % of the oxygen load and 1.4 % of the methane load in the model.
- Cooling a half-inch line by 3 m costs a few kilograms, because real chilldown is only 4 to 9 % efficient (vapour film insulates the wall).
- 5 to 10 K of subcooling in the supply liquid decides whether chilling the receiver is needed at all.

How far to trust it: against 32 NASA hydrogen no-vent fills the mean error in final pressure is 7 %, worst case 26 %. It is a best-case model, and I have no oxygen or methane test data to check it on. If you have, I would like to hear.

Code and notes: [link, only if Thomas makes the repo public]

#cryogenics #spaceflight #propellanttransfer

---

Notes for Thomas:
- Do not publish before you can explain every number without notes.
- The repository is private. Do not make it public without deciding to.
- Do not tag the company or any person unless you decide to.

## 2. Outreach message to Cédric Dupont

Short version for a LinkedIn message (under 100 words):

---

Dear Mr Dupont,

I am a final-year aerospace engineering student at Bristol. I built a small Python model of LOX and LCH4 transfer losses (line and receiver chilldown, no-vent fill), validated against NASA hydrogen tests. In the model, 5 to 10 K of inlet subcooling decides whether receiver chilldown is needed at all. I would value 15 minutes of your view on where it is wrong. Short note attached.

Thomas Farrugia

---

Email version:

Subject: Question on LOX/LCH4 transfer chilldown losses, short note attached

Dear Mr Dupont,

I am Thomas Farrugia, finishing an MEng in Aerospace Engineering at the University of Bristol. I have been following the work on in-orbit cryogenic transfer at TEC Luxembourg and ESA InSPoC-2.

To learn the problem I built an open model of chilldown loss for LOX and LCH4 transfer. It checks an equilibrium receiver model against 32 NASA LH2 no-vent fills (7 % mean error in final pressure, 26 % worst) and line chilldown against 28 NASA LN2 flight tests, then applies it to oxygen and methane. For a 1 m3 aluminium receiver it gives about 0.4 % and 1.4 % of the load lost to chilldown, and shows that 5 to 10 K of inlet subcooling decides whether chilldown is needed. The note lists where the model is weak. It has no LOX or LCH4 test data behind it.

I would be grateful for 15 minutes, or just a pointer on which of my assumptions are least realistic for your concept. The note is attached, six questions are on its last page.

Thank you for your time.

Thomas Farrugia
[contact details]

---

Notes for Thomas:
- Check Cédric's exact title and the correct channel before sending.
- Do not claim any link to TEC's design. The model is generic.
- Read section 5 of the note (limitations) again before sending. Never say the model is validated for oxygen or methane.
- Attach the PDF, which has not yet been generated. The note is in notes/technical_note.md.
