from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/add", methods=["GET"])
def add():
    a = float(request.args.get("a"))
    b = float(request.args.get("b"))
    return jsonify({"operation": "addition", "a": a, "b": b, "result": a + b})

@app.route("/subtract", methods=["GET"])
def subtract():
    a = float(request.args.get("a"))
    b = float(request.args.get("b"))
    return jsonify({"operation": "subtraction", "a": a, "b": b, "result": a - b})

@app.route("/multiply", methods=["GET"])
def multiply():
    a = float(request.args.get("a"))
    b = float(request.args.get("b"))
    return jsonify({"operation": "multiplication", "a": a, "b": b, "result": a * b})

@app.route("/divide", methods=["GET"])
def divide():
    try:
        a = float(request.args.get("a"))
        b = float(request.args.get("b"))
        if b == 0:
            return jsonify({"error": "Division by zero not allowed"}), 400
        return jsonify({"operation": "division", "a": a, "b": b, "result": a / b})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)



#http://127.0.0.1:5000/add?a=10&b=5
#http://127.0.0.1:5000/divide?a=10&b=0

