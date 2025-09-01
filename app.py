from flask import Flask, render_template, request, jsonify
from rag import answer_query
from ingest import build_index

app = Flask(__name__)


@app.route("/ingest_local", methods=["POST"])
def ingest_local():
    try:
        embeddings, metas = build_index()
        return {"status": "ok", "chunks": len(embeddings)}
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    q = data.get("question", "").strip()
    if not q:
        return jsonify({"error": "empty question"}), 400
    try:
        resp = answer_query(q, top_k=4)
        return jsonify(resp)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
