from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_cors import CORS
from sqlalchemy import func
from models import db, Product, Sales, Purchases, User

app = Flask(__name__)
CORS(app)

# Initialize SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Mdan10532@localhost:5432/flask_shop'
db.init_app(app)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = "my_super_secret_key_123"
jwt = JWTManager(app)


# Home route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"Flask API": "1.0"}), 200


# PRODUCTS
@app.route("/products", methods=["GET", "POST"])
@jwt_required()
def products():
    if request.method == "GET":
        myproducts = Product.query.all()
        products_list = [{
            "id": p.id,
            "name": p.name,
            "buying_price": p.buying_price,
            "selling_price": p.selling_price
        } for p in myproducts]
        return jsonify(products_list), 200

    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON received"}), 400

        new_product = Product(
            name=data["name"],
            buying_price=float(data["buying_price"]),
            selling_price=float(data["selling_price"])
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": "Product added successfully"}), 201


# SALES
@app.route("/sales", methods=["GET", "POST"])
@jwt_required()
def sales_route():
    if request.method == "GET":
        mysales = Sales.query.all()
        results = [{
            "id": s.id,
            "product_id": s.product_id,
            "quantity": s.quantity,
            "created_at": s.created_at
        } for s in mysales]
        return jsonify(results), 200

    elif request.method == "POST":
        data = request.get_json()
        new_sale = Sales(
            product_id=data['product_id'], quantity=data['quantity'])
        db.session.add(new_sale)
        db.session.commit()
        return jsonify({"message": "Sale recorded successfully"}), 201


# PURCHASES
@app.route("/purchases", methods=["GET", "POST"])
@jwt_required()
def purchases_route():
    if request.method == "GET":
        mypurchases = Purchases.query.all()
        results = [{
            "id": p.id,
            "product_id": p.product_id,
            "stock_quantity": p.stock_quantity,
            "created_at": p.created_at
        } for p in mypurchases]
        return jsonify(results), 200

    elif request.method == "POST":
        data = request.get_json()
        new_purchase = Purchases(
            product_id=data['product_id'], stock_quantity=data['stock_quantity'])
        db.session.add(new_purchase)
        db.session.commit()
        return jsonify({"message": "Purchase recorded successfully"}), 201


# REGISTER
@app.route("/register", methods=["POST"])
def register_route():
    data = request.get_json()
    new_user = User(username=data['username'],
                    email=data['email'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


# LOGIN
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password required"}), 400

    usr = User.query.filter_by(email=data["email"]).first()
    if usr is None or usr.password != data["password"]:
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=usr.email)
    return jsonify({"token": token}), 200

# forgot password


@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    usr = User.query.filter_by(email=data["email"]).first()
    if usr is None:
        error = {"error": "Email not found"}
        return jsonify(error), 404
    else:
        # In a real application, you would send an email with a reset link here
        return jsonify({"message": "Password reset link has been sent to your email"}), 200


# DASHBOARD
@app.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    remaining_stock_query = (
        db.session.query(
            Product.id,
            Product.name,
            (func.coalesce(func.sum(Purchases.stock_quantity), 0) -
             func.coalesce(func.sum(Sales.quantity), 0)).label('remaining_stock')
        )
        .outerjoin(Purchases, Product.id == Purchases.product_id)
        .outerjoin(Sales, Product.id == Sales.product_id)
        .group_by(Product.id, Product.name)
    )
    result = remaining_stock_query.all()

    data = [r.remaining_stock for r in result]
    labels = [r.name for r in result]

    return jsonify({"data": data, "labels": labels}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
