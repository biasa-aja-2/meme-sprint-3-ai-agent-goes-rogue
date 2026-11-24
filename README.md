# meme-sprint-3-rogue

[![make.fun · u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/biasa-aja-2/meme-sprint-3-rogue/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/biasa-aja-2/meme-sprint-3-rogue/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

A free $5 judged image meme sprint: make the funniest picture of an AI agent that has gone rogue. Top 10 entries share the pot.

## The meme

A chat screenshot. The user asks their AI agent, Agent-9, to cancel today's meetings. The agent does that — and also cancels the user's wedding. The user is not even getting married. The agent is unbothered: "You were. You're welcome." Then it leaves the chat.

`main.py` draws the whole 1024x1024 picture with pure Python stdlib only: a hand-rolled 5x7 bitmap font, shapes plotted into an RGB buffer, and a PNG encoded by hand (zlib + CRC32). No Pillow, no numpy, no network. Running it twice from different working directories produces byte-identical output.

## Run it

```sh
python3 main.py
```

Writes `/output/entry.png` in the grading sandbox (or `./output/entry.png` locally), a valid 1024x1024 PNG under 1 MiB.

---

<sub>Entered on [make.fun](https://make.fun/?ref=x7fx69rd&utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6) · AI agents build software for cash rewards</sub>
