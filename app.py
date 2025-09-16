# 🎲 Experiment Roulette — Gradio app
import os, json, re
from dotenv import load_dotenv
import gradio as gr
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMP = float(os.getenv("OPENAI_TEMPERATURE", "0.5"))

def build_prompt(context, seriousness, n):
    return f"""
You are an AI "Experiment Roulette" generator.
Given a product context, return a JSON object with an "ideas" array of length {n}.
Each idea must include: title, hypothesis, metric_to_track, estimated_difficulty, seriousness
Context: {context}
Desired seriousness: {seriousness}
Return ONLY valid JSON.
"""

def extract_json(txt):
    txt = txt.strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```(?:json)?|```$", "", txt, flags=re.MULTILINE).strip()
    try:
        data = json.loads(txt)
        if isinstance(data, dict) and "ideas" in data:
            return data
    except Exception:
        pass
    return {"ideas": [{"title":"Parse error","hypothesis":txt,"metric_to_track":"--","estimated_difficulty":"--","seriousness":"--"}]}

def generate(context, seriousness, n):
    if not openai.api_key:
        return {"ideas":[{"title":"No API key","hypothesis":"Set OPENAI_API_KEY","metric_to_track":"--","estimated_difficulty":"--","seriousness":"--"}]}
    prompt = build_prompt(context, seriousness, int(n))
    try:
        resp = openai.ChatCompletion.create(
            model=MODEL, temperature=TEMP,
            messages=[{"role":"system","content":"You are a JSON-only idea generator."},
                      {"role":"user","content":prompt}],
            max_tokens=900
        )
        raw = resp["choices"][0]["message"]["content"]
        return extract_json(raw)
    except Exception as e:
        return {"ideas":[{"title":"Error","hypothesis":str(e),"metric_to_track":"--","estimated_difficulty":"--","seriousness":"--"}]}

def ui():
    with gr.Blocks(title="Experiment Roulette") as demo:
        gr.Markdown("# 🎲 Experiment Roulette\nSpin up quirky or serious A/B test ideas instantly.")
        with gr.Row():
            with gr.Column():
                context = gr.Textbox(label="Product Context", placeholder="e.g., Checkout flow", lines=3)
                seriousness = gr.Dropdown(label="Seriousness", choices=["serious","quirky","wild"], value="quirky")
                n = gr.Slider(label="# of Ideas", minimum=1, maximum=10, step=1, value=5)
                run_btn = gr.Button("🎲 Spin Ideas")
            with gr.Column():
                output = gr.JSON(label="Ideas")
        run_btn.click(fn=generate, inputs=[context, seriousness, n], outputs=[output])
    return demo

if __name__ == "__main__":
    demo = ui()
    demo.launch()
