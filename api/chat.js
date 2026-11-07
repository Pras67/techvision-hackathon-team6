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

  const BASE = 'https://generativelanguage.googleapis.com/v1beta';
  const headers = { 'Content-Type': 'application/json', 'x-goog-api-key': key };
  const wait = (ms) => new Promise((res) => setTimeout(res, ms));
  const started = Date.now();
  const outOfTime = () => Date.now() - started > 45000; // give up after ~45s in total
  let lastError = 'no model answered';

  // One call to one model, cut off after 25 seconds so the chat never hangs.
  async function call(model) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 25000);
    try {
      const r = await fetch(`${BASE}/models/${encodeURIComponent(model)}:generateContent`, { method: 'POST', headers, body: JSON.stringify(payload), signal: ctrl.signal });
      const j = await r.json().catch(() => ({}));
      return { status: r.status, ok: r.ok, j };
    } catch (e) {
      return { status: 0, ok: false, j: { error: { message: e.name === 'AbortError' ? 'took longer than 25s' : e.message } } };
    } finally { clearTimeout(timer); }
  }

  // Ask Google which "flash" models this key can use, as automatic backups.
  async function discoverBackups(skip) {
    try {
      const r = await fetch(`${BASE}/models?pageSize=200`, { headers });
      const j = await r.json();
      return (j.models || [])
        .filter((m) => (m.supportedGenerationMethods || []).includes('generateContent'))
        .map((m) => m.name.replace(/^models\//, ''))
        .filter((n) => /flash/i.test(n) && !/(image|tts|audio|live|embedding|preview-\d{2}-\d{2})/i.test(n) && !skip.includes(n))
        .sort((a, b) => b.localeCompare(a, undefined, { numeric: true })) // newest version numbers first
        .slice(0, 4);
    } catch { return []; }
  }

  async function tryModels(list, triesEach) {
    for (const model of list) {
      for (let attempt = 0; attempt < triesEach; attempt++) {
        if (outOfTime()) return null;
        const { status, ok, j } = await call(model);
        if (ok) {
          const text = (j.candidates?.[0]?.content?.parts || []).map((p) => p.text || '').join('').trim();
          console.log(`[advisor] answered by ${model} in ${((Date.now() - started) / 1000).toFixed(1)}s`);
          return { status: 200, body: { text: text || 'Gemini returned an empty answer. Try rephrasing the question.', model } };
        }
        lastError = `${model}: ${j?.error?.message || `status ${status}`}`;
        console.log(`[advisor] ${lastError}`);
        if (status === 400 || status === 401 || status === 403) return { status: 502, body: { error: `Gemini couldn't answer: ${lastError}` } }; // bad key or request
        if (status === 404) break; // model not available to this key: next model
        await wait(600 * (attempt + 1)); // busy or timed out: short pause, try again
      }
    }
    return null;
  }

  const first = await tryModels(models, 2);
  if (first) return first;
  const backups = await discoverBackups(models);
  if (backups.length) console.log(`[advisor] trying backups: ${backups.join(', ')}`);
  const second = await tryModels(backups, 1);
  if (second) return second;
  return { status: 502, body: { error: `Gemini is busy right now. Try again in a minute. (${lastError})` } };
}

export default async function handler(req, res) {
  if (req.method !== 'POST') { res.status(405).json({ error: 'Use POST.' }); return; }
  const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
  const out = await askGemini(body);
  res.status(out.status).json(out.body);
}
