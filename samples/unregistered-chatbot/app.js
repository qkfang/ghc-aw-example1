// Test fixture: an AI solution that has NOT been logged in governance/ai-register.yml.
// The AI Governance Scan workflow should detect this and raise an issue.
import Anthropic from "@anthropic-ai/sdk";
import express from "express";

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const app = express();
app.use(express.json());

app.post("/chat", async (req, res) => {
  const message = await anthropic.messages.create({
    model: "claude-sonnet-4-5",
    max_tokens: 512,
    messages: [{ role: "user", content: String(req.body.question ?? "") }],
  });
  res.json({ answer: message.content[0].text });
});

app.listen(3000);
