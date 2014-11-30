from justaworkoutdb import db

if __name__ == "__main__":
    print("Creating Database...")
    db.create_all()
    print("Success!")