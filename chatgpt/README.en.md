# Using the skill in ChatGPT

**English** | [Français](README.md)

Two routes. The first is the simplest if skills are enabled in your workspace; the second works with a custom GPT.

## Route 1: ChatGPT skill (beta)

ChatGPT skills follow the open Agent Skills format, the same one as this repository. They are off by default during the beta: the workspace owner must enable them in the workspace settings.

1. Build the archive: `python3 scripts/build_zips.py` (produces `dist/pcg-france-skill.zip`).
2. In ChatGPT, import the skill from the skills management interface, providing the `skills/pcg-france/` folder (or the archive). If direct import is not offered on your plan, ask ChatGPT "Build me a skill", paste the content of `skills/pcg-france/SKILL.md`, and attach the files from the `references/` and `scripts/` folders.
3. Mention the skill with @ in a conversation, or let ChatGPT pick it based on its description.

Capabilities and eligible plans change over time: check the current OpenAI documentation for import details.

## Route 2: custom GPT

1. Build the pack: `python3 scripts/build_zips.py` (produces `dist/pcg-france-gpt-pack.zip`) and unzip it.
2. In ChatGPT: Explore GPTs, then Create.
3. In the Configure tab:
   - Name: "Assistant PCG France".
   - Instructions: paste the content of `instructions.md` (written in French, under 8,000 characters).
   - Knowledge files: upload the four `plan-comptable-YYYY.csv` files (2023 to 2026), `cloture.md` and `pcg.py`.
   - Capabilities: enable the Code Interpreter, needed to run `pcg.py` and to generate XLSX files.
4. Save, then test with:
   - "Which account for an insurance premium?"
   - "Validate these codes: 411 44571 9999"
   - uploading `examples/balance-exemple.csv` with "Check this trial balance and give me the result"
   - uploading `examples/fec-exemple.txt` with "Check this FEC".

If uploading the `.py` file is refused, rename `pcg.py` to `pcg.txt`, upload it, and add to the instructions: "copy pcg.txt to pcg.py before running it".

Warning: a real FEC contains company data. Check the privacy policy of your ChatGPT plan before uploading one.
