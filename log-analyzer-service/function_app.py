import azure.functions as func
import json
import joblib
import os

# Initialize the Azure Functions V2 app framework
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Cache the loaded model bundle on startup to keep inference lightning fast
MODEL_PATH = os.path.join(os.path.dirname(__file__), "log_analyzer.pkl")
model_bundle = joblib.load(MODEL_PATH)

@app.route(route="AnalyzeLog", methods=["POST"])
def analyze_log(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        log_message = req_body.get('log')
        
        if not log_message:
            return func.HttpResponse(
                json.dumps({"error": "Missing required 'log' key in request payload."}),
                status_code=400,
                mimetype="application/json"
            )
        
        # 1. Vectorize the incoming text using the trained vocabulary
        vec_data = model_bundle['vectorizer'].transform([log_message])
        
        # 2. Get inference scores from both models simultaneously
        predicted_severity = model_bundle['severity_model'].predict(vec_data)
        predicted_relevance = model_bundle['relevance_model'].predict(vec_data)
        
        # 3. Respond with clean payload back to the agentic workflow loop
        return func.HttpResponse(
            json.dumps({
                "severity": str(predicted_severity[0]),
                "relevance_percentage": round(float(predicted_relevance[0]) * 100, 2)
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": f"Internal scoring pipeline exception: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )