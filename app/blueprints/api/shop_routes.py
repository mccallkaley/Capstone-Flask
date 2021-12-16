from . import bp as api
from app.blueprints.auth.auth import token_auth
from flask import request, make_response, g
from .models import *
import stripe
import os

############
##
##  STRIPE API ROUTES
##
############

# This is a sample test API key. Sign in to see examples pre-filled with your key.
stripe.api_key = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'
YOUR_DOMAIN = "http://localhost:3000"

@api.post('/create-checkout-session')
@token_auth.login_required()
def create_checkout_session():
    cart = request.get_json().get('cart')
    line_items=[
        {
            'name':cart[item_key]['name'],
            'amount':int(round(float(cart[item_key]['price']),2)*100),
            'currency':'USD',
            'quantity':cart[item_key]['quantity']
        } for item_key in cart.keys()
    ]

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            payment_method_types=['card'],
            mode='payment',
            success_url=YOUR_DOMAIN + '/checkoutSuccess',
            cancel_url=YOUR_DOMAIN + '/cart',
        )
    except Exception as e:
        return str(e)

    return {'url':checkout_session.url}

############
##
##  CATEGORY API ROUTES
##
############

# get all the categories

@api.get('/category')
@token_auth.login_required()
def get_category():
    cats = Category.query.all()
    cats_dicts= [cat.to_dict() for cat in cats]
    return make_response({"categories":cats_dicts},200)

# create a new category
# {"name":"my cat name"}
@api.post('/category')
@token_auth.login_required()
def post_category():
    if not g.current_user.is_admin:
        return make_response({"You are not Admin"},403)
    cat_name = request.get_json().get("name")
    cat = Category(name=cat_name)
    cat.save()
    return make_response(f"category {cat.id} with name {cat.name} created",200)

# change my category 
#{"name":"new name"}
@api.put('/category/<int:id>')
@token_auth.login_required()
def put_category(id):
    if not g.current_user.is_admin:
        return make_response({"You are not Admin"},403)
    cat_name = request.get_json().get('name')
    cat = Category.query.get(id)
    if not cat:
        return make_response("Invalid category", 404)
    cat.name = cat_name
    cat.save()
    return make_response(f"category {cat.id} has new name {cat.name}",200)

# Discard a category
@api.delete('/category/<int:id>')
@token_auth.login_required()
def delete_category(id):
    if not g.current_user.is_admin:
        return make_response({"You are not Admin"},403)
    cat = Category.query.get(id)
    if not cat:
        return make_response("Invalid category id",404)
    cat.delete()
    return make_response(f"Category id: {id} has been murdered",200)


#############
##
##  ITEM API ROUTES
##
############


# Get All Items from the shop
@api.get('/item')
@token_auth.login_required()
def get_items():
    all_items = Item.query.all()
    items = [item.to_dict() for item in all_items]  
    return make_response({"items":items},200)

# Get item by ID
@api.get('/item/<int:id>')
@token_auth.login_required()
def get_item(id):
    item = Item.query.get(id)
    if not item:
        return make_response("Invalid Item ID", 404)
    return make_response(item.to_dict(),200)

# Get all items in a Category
@api.get('/item/category/<int:id>')
@token_auth.login_required()
def get_items_by_cat(id):
    all_items_in_cat = Item.query.filter_by(category_id = id).all()
    items = [item.to_dict() for item in all_items_in_cat]
    return make_response({"items":items}, 200)


# # Create a item
# {
#     "name": new name
#     "description": new desc
#     "price": new price
#     "img": new img
#     "category_id":new cat id
# }
@api.post("/item")
@token_auth.login_required()
def post_item():
    if not g.current_user.is_admin:
        return make_response({"You are not Admin"},403)
    item_dict = request.get_json()
    if not all(key in item_dict for key in ('name','description','price','img','category_id')):
        return make_response("Invalid Payload",400)
    item = Item()
    item.from_dict(item_dict)
    item.save()
    return make_response(f"Item {item.name} was created with the id {item.id}", 200)

# Change an Item
@api.put("/item/<int:id>")
@token_auth.login_required()
def put_item(id):
    if not g.current_user.is_admin:
        return make_response({"You are not Admin"},403)
    item_dict = request.get_json()
    item = Item.query.get(id)
    if not item:
        return make_response("No Item has that id",404)
    item.from_dict(item_dict)
    item.save()
    return make_response(f"Item {item.id} was edited",200)


@api.delete("/item/<int:id>")
@token_auth.login_required()
def delete_item(id):
    if not g.current_user.is_admin:
        return make_response({"You are not Admin"},403)
    item_to_delete =  Item.query.get(id)
    if not item_to_delete:
        return make_response("Invalid ID", 404)
    item_to_delete.delete()
    return make_response(f"Item ID {id} has been deleted",200)
