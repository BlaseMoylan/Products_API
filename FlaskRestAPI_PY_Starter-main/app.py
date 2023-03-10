from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ
from marshmallow import post_load, fields, ValidationError
load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models
class Movie(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(255),nullable=False)
    description=db.Column(db.String(255))
    price=db.Column(db.Float,nullable=False)
    inventory_quantity=db.Column(db.Integer,nullable=False)
    image=db.Column(db.String(255))

    def __repr__(self):
        return f'{self.name}{self.description}{self.price}{self.inventory_quantity}'

# Schemas
class MovieSchema(ma.Schema):
    id=fields.Integer(primary_key=True)
    name=fields.String(required=True)
    description=fields.String()
    price=fields.Float(required=True)
    inventory_quantity=fields.Integer(required=True)
    image=fields.String()
    class Meta:
        fields=('id','name','description','price','inventory_quantity','image')
    
    @post_load
    def create_movie(self,data,**kwargs):
        return Movie(**data)
movie_schema=MovieSchema()
movies_schema=MovieSchema(many=True)
# Resources

class MovieListResource(Resource):
    def get(self):
        all_movies=Movie.query.all()
        return movies_schema.dump(all_movies), 200

    def post(self):
        try:
            form_data=request.get_json()
            new_movie=movie_schema.load(form_data)
            db.session.add(new_movie)
            db.session.commit()
            return movie_schema.dump(new_movie), 201
        except ValidationError as err:
            return err.messages, 400
    
class MovieResource(Resource):
    def get(self,pk):
        movie_from_db=Movie.query.get_or_404(pk)
        return movie_schema.dump(movie_from_db), 200
    
    def delete(self, pk):
        movie_from_db=Movie.query.get_or_404(pk)
        db.session.delete(movie_from_db)
        return '', 204
    
    def put(self, pk):
        movie_from_db =Movie.query.get_or_404(pk)

        if 'name' in request.json:
            movie_from_db.name =request.json['name']
        if 'description' in request.json:
            movie_from_db.description =request.json['description']
        if 'price' in request.json:
            movie_from_db.price =request.json['price']
        if 'inventory_quantity' in request.json:
            movie_from_db.inventory_quantity =request.json['inventory_quantity']
        if 'image' in request.json:
            movie_from_db.image =request.json['image']

        db.session.commit()
        return movie_schema.dump(movie_from_db), 200

# Routes
api.add_resource(MovieListResource, '/api/products/')
api.add_resource(MovieResource, '/api/products/<int:pk>')