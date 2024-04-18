import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from peewee import *
from werkzeug.utils import secure_filename
import requests  
#import webview

app = Flask(__name__,static_folder='./static', template_folder='./templates')

app.secret_key = 's293kksd23'



YELP_API_KEY = os.environ.get('_ZzBW07hTN1WypmbX3FOPGJjXxKHSN1J137Pzdgk-DYYwJX8poCTVQ6zR6kAbAHipmgZtE2H_LcYIPf9jWezuGdYiNgmueF4tBtsz8uegufFVKFDU-9KfeOwbbMGZnYx')
# Configure SQLite connection
database = SqliteDatabase('database.db')


# Define the User model
class User(Model):
    id = AutoField(primary_key=True)
    username = CharField(unique=True)
    password = CharField()

    @staticmethod
    def get_by_username(username):
        try:
            user = User.get(User.username == username)
            return user
        except DoesNotExist:
            return None

    class Meta:
        database = database
        table_name = 'user'


# Create the store table if it doesn't exist
class Store(Model):
    id = AutoField()
    store_name = CharField()
    location = CharField()
    description = TextField()
    owner = ForeignKeyField(User, backref='stores')

    class Meta:
        database = database
        table_name = 'store'


# Create the products table if it doesn't exist
class Product(Model):
    id = AutoField()
    name = CharField()
    quantity = IntegerField()
    price = DecimalField(max_digits=10, decimal_places=2)
    description = TextField()
    store = ForeignKeyField(Store, backref='products')

    class Meta:
        database = database
        table_name = 'products'


# Connect to the database
database.connect()
database.create_tables([User, Store, Product])

YELP_API_KEY = '_ZzBW07hTN1WypmbX3FOPGJjXxKHSN1J137Pzdgk-DYYwJX8poCTVQ6zR6kAbAHipmgZtE2H_LcYIPf9jWezuGdYiNgmueF4tBtsz8uegufFVKFDU-9KfeOwbbMGZnYx'

if not User.select().where(User.username == 'user1').exists():
    # Create 'user1' with a password (replace 'password1' with the desired password)
    User.create(username='user1', password='password1')
    
users = {
  'user1': {
      'username': 'user1',
      'password': 'password1'
  },
  'user2': {
      'username': 'user2',
      'password': 'password2'
  }
}

# Function to fetch business data from Yelp API and store it in the database
def fetch_and_store_businesses():
   if not session.get('stores_fetched'):
        default_user = User.get_by_username('user1')
   
    
        headers = {
            'Authorization': 'Bearer ' + YELP_API_KEY
        }
        url = 'https://api.yelp.com/v3/businesses/search'
        params = {
            'term': 'food,shopping',
            'categories': 'restaurants,shopping',
            'location': 'Canada',
            'limit': 1
        }
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            for business in data.get('businesses', []):
                # Check if store already exists
                existing_store = Store.get_or_none(store_name=business.get('name'))
                if existing_store:
                    print("Store already exists:", business.get('name'))
                    continue

                # Create store with owner "user1"
                store = Store.create(
                    store_name=business.get('name'),
                    location=''.join(business.get('location', {}).get('display_address', [])),
                    description=''.join([category['title'] for category in business.get('categories', [])]),
                    owner=default_user
                )
                print("Store created:", business.get('name'))
        session['stores_fetched'] = True       

            
            

# Route to fetch and store business data from Yelp API
@app.route('/fetch_businesses')
def fetch_businesses():
    fetch_and_store_businesses()
    return 'Businesses fetched and stored successfully.'







# Modify the index route

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate and create a new user
        if not username or not password:
            return 'Please provide a username and password.'

        try:
            # Create the user in the database
            user = User(username=username, password=password)
            user.save()
        except IntegrityError:
            return 'Username already exists.'

        # Redirect the user to the login page
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve user from the database or storage
        user = User.get_by_username(username)

        if user and user.password == password:
            # User is authenticated, store user_id in the session
            session['user_id'] = username
            return redirect(url_for('create_store'))

        return 'Invalid username or password'

    return render_template('login.html')
# Import the required Flask modules and classes
# Custom decorator to protect routes


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/')
def index():

    return render_template('index.html', store_created=False)




@app.route('/store/<store_name>/add_product', methods=['GET', 'POST'])
def render_add_product(store_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    store = Store.get(Store.store_name == store_name)

    # Fetch the products for the store
    products = Product.select().where(Product.store == store)

    return render_template('store_details.html', products=products, store=store)




@app.route('/store/<store_name>/add_products', methods=['GET', 'POST'])
def add_product(store_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Retrieve the store based on the store_name
    store = Store.get_or_none(Store.store_name == store_name)
    products = Product.select().where(Product.store == store)
    if not store:
        return "Store not found"

    # Get product data from the form
    name = request.form['name']
    quantity = request.form['quantity']
    price = request.form['price']
    description = request.form['description']

    # Perform any necessary operations with the product data
    # For example, you can insert the data into the database
    product = Product.create(
        name=name,
        quantity=quantity,
        price=price,
        description=description,
        store=store  # Associate the product with the store
    )
    product.save()

    # Redirect the user to the store details page
    return redirect(url_for('get_store', products=products, store_name=store_name))




# Route to retrieve the products
@app.route('/products', methods=['POST'])
def get_products():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Retrieve the products from the database
    products = Product.select().dicts()

    # Convert the products to a list
    products_list = list(products)

    # Return the products as a JSON response
    return jsonify({'products': products_list})


@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Delete the product from the database
    product = Product.get_or_none(Product.id == product_id)
    if product:
        product.delete_instance()
        flash('Product deleted successfully.', 'success')
    # Redirect to the product listing page
    return redirect(url_for('get_products'))


@app.route('/user-data', methods=['GET'])
def get_user_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Retrieve the user's data (products) from the database
    products = Product.select()

    # Convert the product objects to a list of dictionaries
    products_list = [
        {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description
        }
        for product in products
    ]

    # Return the user's data (products) as a JSON response
    return jsonify({'products': products_list})


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = 'C:/Users/noahs/PycharmProjects/pythonProject/'

@app.route('/store/<store_name>/products', methods=['GET', 'POST'])
def store(store_name):
    store = Store.get_or_none(Store.store_name == store_name)
    if not store:
        return "Store not found"
    products = Product.select().where(Product.store == store)

    return render_template('store_details.html',store=store, products=products,)

@app.route('/store/<store_name>', methods=['GET', 'POST'])
def get_store(store_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    username = session['user_id']
    user = User.get_by_username(username)

    store = Store.get_or_none(Store.store_name == store_name)

    if request.method == 'POST' and 'create_product' in request.form:
        # The button with name 'create_product' is clicked
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']
        description = request.form['description']
        

       

        # Perform any necessary operations with the product data
        # For example, you can insert the data into the database
        product = Product.create(
            name=name,
            quantity=quantity,
            price=price,
            description=description,
            store=store  # Associate the product with the store
        )
        product.save()

        # Redirect to the same page to prevent duplicate form submissions
        return redirect(url_for('get_store', store_name=store_name))

    products = Product.select().where(Product.store == store)
    if not store:
        return "Store not found"

    # Render a template with the store details
    return render_template('store_details.html', store=store, products=products, current_user=user)

@app.route('/store/delete/<int:store_id>', methods=['GET'])
def delete_store(store_id):
    # Retrieve the store based on the ID
    store = Store.get_or_none(Store.id == store_id)

    if store:
        # Delete the store from the database
        store.delete_instance()
        flash('Store deleted successfully.', 'success')
    else:
        flash('Store not found.', 'error')

    # Redirect back to the page displaying the stores
    return redirect(url_for('create_store'))

@app.route('/create_store', methods=['GET', 'POST'])
def create_store():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to the login page if user is not authenticated

    # User is authenticated, retrieve user data and render the dashboard
    username = session['user_id']
    user = User.get_by_username(username)

    if request.method == 'POST':
        # Get form data
        store_name = request.form['store_name']
        location = request.form['location']
        description = request.form['description']

        # Check if store name already exists
        existing_store = Store.get_or_none(Store.store_name == store_name)
        if existing_store:
            return "Store name already exists. Please choose a different name."

        # Create the store in the database with the correct owner
        try:
            with database.atomic():
                store = Store.create(store_name=store_name, location=location, description=description, owner=user)
        except IntegrityError as e:
            print(e)  # Print the specific error message
            return "Error creating store. Please try again."

        # Redirect the user to the store details page
        return redirect(url_for('get_store', store_name=store.store_name))

    # Fetch all stores from the database
    stores = Store.select().where(Store.owner == user)

    # Render the create store form
    return render_template('create_store.html', stores=stores, current_user=user, store_created=False)
  
   
  
@app.route('/stores')
def stores():
  
  
   default_user = User.get_by_username('user1')
   location = "Canada"
   headers = {
        'Authorization': 'Bearer ' + YELP_API_KEY  # Include your Yelp API key 
    }

    # Make a request to Yelp API to fetch data (e.g., restaurants in a specific location)
   url = 'https://api.yelp.com/v3/businesses/search'
   params = {
        'term': 'restaurant and stores',
        'location': 'Toronto'
    }
    
   response = requests.get(url, params=params, headers=headers)

   data = response.json()

    # Parse and store the retrieved data in your database
   for business in data.get('businesses', []):
        # Extract relevant information from the Yelp API response and store it in your database
        Store.create(
            store_name=business.get('name'),
            location= '' .join(business.get('location', {}).get('address1')),
            description= '' .join(business.get('categories', [])[0].get('title')),
            owner=default_user
        )
        
        
    # Fetch all stores from the database
   stores = Store.select()

    

        # Render the stores page
   return render_template('add_product.html', stores=stores)
    
#webview.create_window('Instock247', app, width=1700,height=1400)


if __name__ == '__main__':
    app.run(debug=True)
    #webview.start()
