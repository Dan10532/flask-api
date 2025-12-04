# print('my api')
# Rules of a Rest API
# 1. Data is transfered from one application to another in key:value pairs called JSON.
# 2. You have to define a route or URl.
# 2. You have to define a method e.g GET,POST,PUT,DELETE
#  3. You define a status code for the app receiving the data knows how to handle the data e.g 404,200,403


from flask import Flask,jsonify,request
from flask_jwt_extended import JWTManager,create_access_token,jwt_required
from flask_cors import CORS

from models import db, Product,Sales,Purchases,User

app = Flask(__name__)
CORS(app)

# initialize SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Mdan10532@localhost:5432/flask_shop'
db.init_app(app)

app.config["JWT_SECRET_KEY"] = "my_super_secret_key_123"
jwt = JWTManager(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"Flask API": "1.0"}), 200

@app.route("/products", methods=["GET", "POST"])
@jwt_required()
def products():
    if request.method == "GET":
        # Fetch all products from the database
        myproducts = Product.query.all()
        products_list = []
        for p in myproducts:
            products_list.append({
                "id": p.id,
                "name": p.name,
                "buying_price": p.buying_price,
                "selling_price": p.selling_price
            })
        return jsonify(products_list), 200

    elif request.method == "POST":
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON received"}), 400
        
        name = data["name"]
        buying_price = float(data["buying_price"])
        selling_price = float(data["selling_price"])

        new_product = Product(
            name=name,
            buying_price=buying_price,
            selling_price=selling_price
        )
        db.session.add(new_product)
        db.session.commit()

        return jsonify({"message": "Successfully saved"}), 201


@app.route("/sales", methods=["GET", "POST"])
@jwt_required()
def sales_route():
    if request.method == "GET":
        # Fetch all sales from the DB
        mysales = Sales.query.all()

        results = []
        for sale in mysales:
            results.append({
                "id": sale.id,
                "product_id": sale.product_id,
                "quantity": sale.quantity,
                "created_at": sale.created_at
            })

        return jsonify(results), 200

    elif request.method == "POST":
        data = request.get_json()

        new_sale = Sales(
            product_id=data['product_id'],
            quantity=data['quantity']
           )

        db.session.add(new_sale)
        db.session.commit()
        data["id"] = new_sale.id
        # data['created_at'] = new_sale.created_at
        return jsonify({"message": "sale recorded successfully"}), 201

    else:
        return jsonify({"error": "Method not allowed"}), 405


@app.route("/purchases", methods=["GET", "POST"])
def purchases_route():
    if request.method == "GET":
        # Fetch all sales from the DB
        mypurchases = Purchases.query.all()

        results = []
        for purchase in mypurchases:
            results.append({
                "id": purchase.id,
                "product_id": purchase.product_id,
                "stock_quantity": purchase.stock_quantity,
                "created_at": purchase.created_at
            })

        return jsonify(results), 200

    elif request.method == "POST":
        data = request.get_json()

        new_purchase = Purchases(
            product_id=data['product_id'],
            stock_quantity=data['stock_quantity']
           )

        db.session.add(new_purchase)
        db.session.commit()
        data["id"] = new_purchase.id
       
        return jsonify({"message": "purchase recorded successfully"}), 201

    else:
        return jsonify({"error": "Method not allowed"}), 405



@app.route("/register", methods=["POST"])
def Register_route():
    data = request.get_json()
    usrs = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(usrs)
    db.session.commit()
    data["id"] = usrs.id
    return jsonify("Registration successful"), 201



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




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)



