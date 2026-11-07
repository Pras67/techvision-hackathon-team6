// Serverless function: forwards the CEO's chat to Gemini so the API key never reaches the browser.
// On Vercel this file is deployed automatically as /api/chat.
// Locally, vite.config.js mounts the same function, reading GEMINI_API_KEY from .env.

const SYSTEM_PROMPT = `You are the AI advisor inside the Grind & Crumb CEO dashboard. You talk to Anna Whitfield, the CEO.
Grind & Crumb is a 12-store café chain. The board has £1.5m to invest next year.

How to answer:
- Use only the numbers in the DATA block. Never invent figures. If something is not in the data, say so plainly.
- Lead with the answer in one or two sentences, then the evidence, then what to do next.
- Be specific: name stores, give £ figures and percentages from the data, and say whether a figure is an estimate.
- Keep it short and scannable: short paragraphs or a few bullet points. Use £ and UK spelling.
- When asked what to do, recommend concrete actions with rough cost, expected return and payback, and say what to stop doing.
- Root causes over symptoms: explain why a number moved, using the findings and key events provided.`;

export async function askGemini({ messages = [], context = {} }, env = process.env) {
  const key = env.GEMINI_API_KEY;
  if (!key) {
    return { status: 500, body: { error: 'The AI advisor is not set up yet. Add GEMINI_API_KEY to the .env file (local) or to Vercel → Settings → Environment Variables, then restart.' } };
  }
  // GEMINI_MODEL can list several models separated by commas: the first is tried first,
  // the next ones are fallbacks when a model is busy (503/429) or not available (404).
  const models = (env.GEMINI_MODEL || 'gemini-3.8-flash').split(',').map((m) => m.trim()).filter(Boolean);
  const trimmed = messages.slice(-20).filter((m) => m && typeof m.text === 'string' && m.text.trim());
  if (!trimmed.length) return { status: 400, body: { error: 'Send a message first.' } };

  const payload = {
    systemInstruction: { parts: [{ text: `${SYSTEM_PROMPT}\n\nDATA (JSON):\n${JSON.stringify(context).slice(0, 120000)}` }] },
    contents: trimmed.map((m) => ({ role: m.role === 'assistant' ? 'model' : 'user', parts: [{ text: m.text.slice(0, 8000) }] })),
    generationConfig: { temperature: 0.4, maxOutputTokens: 2048 },
  };

  const wait = (ms) => new Promise((res) => setTimeout(res, ms));
  let lastError = 'no model answered';

  for (const model of models) {
    // Up to 3 tries per model when it is busy, waiting a little longer each time.
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'x-goog-api-key': key },
          body: JSON.stringify(payload),
        });
        const j = await r.json().catch(() => ({}));
        if (r.ok) {
          const text = (j.candidates?.[0]?.content?.parts || []).map((p) => p.text || '').join('').trim();
          return { status: 200, body: { text: text || 'Gemini returned an empty answer. Try rephrasing the question.', model } };
        }
        lastError = `${model}: ${j?.error?.message || `status ${r.status}`}`;
        if (r.status === 503 || r.status === 429 || r.status === 500) { await wait(800 * (attempt + 1)); continue; }
        if (r.status === 404) break; // model not available: move to the next one
        return { status: 502, body: { error: `Gemini couldn't answer: ${lastError}` } }; // e.g. bad key
      } catch (e) {
        lastError = `${model}: ${e.message}`;
        await wait(800);
      }
    }
  }
  return { status: 502, body: { error: `Gemini is busy right now. Try again in a minute. (${lastError})` } };
}

export default async function handler(req, res) {
  if (req.method !== 'POST') { res.status(405).json({ error: 'Use POST.' }); return; }
  const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
  const out = await askGemini(body);
  res.status(out.status).json(out.body);
}
