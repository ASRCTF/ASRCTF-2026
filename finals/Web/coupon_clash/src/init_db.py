from app import app


if __name__ == "__main__":
    with app.app_context():
        app.init_db()
    print("Coupon Clash database initialized.")
