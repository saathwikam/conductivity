from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.routers.predict import router as predict_router


app = FastAPI(
    title="Ionic SL API",
    version="0.1.0",
    description="Dual-phase ionic conductivity prediction service for solid and liquid lithium battery electrolytes.",
)


@app.get("/")
def root():
    return {"status": "Ionic SL API is running", "docs": "/docs"}

@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <html>
        <head>
            <title>Ionic SL Predictor</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 760px; margin: 50px auto; padding: 0 20px; line-height: 1.5;">
            <h2>⚡ Ionic Conductivity Predictor</h2>

            <form onsubmit="event.preventDefault(); sendData();" style="text-align: center;">
                <select id="phase" style="padding:10px; width:320px; margin-bottom: 12px;">
                    <option value="liquid">Liquid electrolyte</option>
                    <option value="solid">Solid electrolyte</option>
                </select>
                <br>
                <input id="formula" placeholder="Enter formula (e.g. LiPF6 in EC/EMC)" style="padding:10px; width:300px;">
                <br><br>
                <button type="submit" style="padding:10px 20px;">Predict</button>
            </form>

            <h3 id="result" style="text-align: center;"></h3>
            <pre id="details" style="background:#f7f7f7; padding:16px; border-radius:8px; white-space:pre-wrap; word-break:break-word;"></pre>

            <script>
                async function sendData() {
                    const phase = document.getElementById("phase").value;
                    const formula = document.getElementById("formula").value.trim();
                    const resultEl = document.getElementById("result");
                    const detailsEl = document.getElementById("details");

                    if (!formula) {
                        resultEl.innerText = "Please enter a formula or formulation.";
                        detailsEl.innerText = "";
                        return;
                    }

                    resultEl.innerText = "Running prediction...";
                    detailsEl.innerText = "";

                    const response = await fetch("/predict", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ phase: phase, formula: formula })
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        resultEl.innerText = "Prediction failed";
                        detailsEl.innerText = typeof data.detail === "string"
                            ? data.detail
                            : JSON.stringify(data.detail, null, 2);
                        return;
                    }

                    resultEl.innerText = "Predicted conductivity (" + data.phase + "): " + data.prediction;
                    detailsEl.innerText = JSON.stringify({
                        graph_stats: data.graph_stats,
                        matched_record: data.matched_record,
                        narrative: data.narrative
                    }, null, 2);
                }
            </script>
        </body>
    </html>
    """
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(predict_router)
