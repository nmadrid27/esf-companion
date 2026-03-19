# Getting Started with the ESF Community Toolkit

This guide walks you through setup step by step. No technical experience required.

---

## Step 1: Download the Toolkit

1. Go to the [ESF Community Toolkit on GitHub](https://github.com/nmadrid27/esf-community-toolkit)
2. Click the green **Code** button
3. Click **Download ZIP**
4. Unzip the downloaded file and open the folder

You now have everything you need. The key folder is `templates/` — it contains five files you will use in your projects.

---

## Step 2: Understand the Templates

Each template matches one ESF practice. Here is what they do:

| Template | What it does | When to use it |
|----------|-------------|----------------|
| `position-statement.md` | Captures your direction before AI gets involved | Before every AI session |
| `record-of-resistance.md` | Documents when you reject or revise AI output | During AI-assisted work |
| `ai-use-log.md` | Tracks what AI contributed and what you changed | During and after AI-assisted work |
| `five-questions-checklist.md` | A checkpoint to make sure the work is genuinely yours | Before finalizing any deliverable |
| `disclosure-statement.md` | An honest statement of what AI contributed | Attached to finished work |

You do not need to use all five right away. Start with the **Position Statement** — it is the foundation of the process.

---

## Step 3: Start Your First Project

1. Create a new folder for your project (you can name it anything)
2. Copy `templates/position-statement.md` into your project folder
3. Open it in any text editor (Google Docs, Word, Notes, or any plain text editor)
4. Fill it in **before** you open any AI tool

The Position Statement asks three things:
- **Your stance** — What is your argument, concept, or direction?
- **What matters most** — What must the final result accomplish?
- **Non-negotiables** — What will you not compromise on?

This is the anchor for everything that follows. Once you have written it, you are ready to bring in AI.

---

## Step 4: Use with Your AI Tool

### Option A: ChatGPT, Gemini, Claude.ai, or any other AI tool

1. Open the file `prompts/esf-companion.md` from the toolkit
2. Copy the entire contents
3. Paste it at the start of a new conversation with your AI tool (as a system prompt, custom instruction, or first message)
4. The AI will now follow the ESF process — it will ask for your Position Statement before helping with project work

### Option B: Claude Cowork (no terminal needed)

If you use the Claude desktop app, [Cowork](https://claude.com/product/cowork) can work directly with the ESF templates on your computer.

1. Open Claude Desktop and start a Cowork session
2. Point Claude to your toolkit folder — it can read your local files directly, including the companion prompt and all templates
3. Claude reads the ESF companion prompt on its own and guides you through the full workflow

No copying or pasting required. Claude will check for your Position Statement, help you explore and build, prompt you to log AI contributions, and remind you to record moments of resistance — all by reading and writing files in your toolkit folder. Available on Pro, Max, Team, and Enterprise plans.

### Option C: Claude Code (for developers)

If you use Claude Code, the toolkit includes configuration files in the `.claude/` folder that work automatically. Just run `claude` in the toolkit directory and it will check for your Position Statement before assisting.

---

## Step 5: Work Through the Process

Once your Position Statement is written and your AI tool is set up:

1. **Explore** — Let the AI challenge your position, surface alternatives, and ask questions. It should not originate direction — that is your job.
2. **Build** — Work with AI on your deliverable. Use the AI Use Log to track what AI contributed. Each time you reject or revise AI output, create a Record of Resistance.
3. **Validate** — Run the Five Questions checklist. Fix anything that does not pass.
4. **Disclose** — Write a disclosure statement and attach it to your finished work.

---

## Where to Go Next

- **[Essentials](essentials.md)** — The three core practices explained in under two minutes
- **[What Is ESF?](what-is-esf.md)** — The full framework explanation and research behind it
- **[WORKFLOW.md](../WORKFLOW.md)** — A visual diagram of the complete process

---

## FAQ

**Do I need to know how to code?**
No. The toolkit is a set of document templates. You can use them in any text editor.

**Do I need to install anything?**
No. Download the ZIP, open the templates, and start writing. There is an optional installer script for people who prefer automated setup, but it is not required.

**Which AI tool should I use?**
Any of them. The toolkit works with ChatGPT, Claude, Gemini, Copilot, or any AI tool that accepts text input. The companion prompt in `prompts/esf-companion.md` works with all of them.

**What if I only want to try one practice?**
Start with the Position Statement. It is the most important practice and takes five minutes. Add the others as you get comfortable.
