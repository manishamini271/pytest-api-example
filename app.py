import uuid
from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace

app = Flask(__name__)
api = Api(app, version='1.0', title='Petstore API',
          description='A simple Petstore API')

PET_STATUS = ['available', 'sold', 'pending']
PET_TYPE = ['cat', 'dog', 'fish']

pet_model = api.model('Pet', {
    'id': fields.Integer(description='The pet ID'),
    'name': fields.String(required=True, description='The pet name'),
    'type': fields.String(required=True, description='The pet type', enum=PET_TYPE),
    'status': fields.String(description='The pet status', enum=PET_STATUS)
})

order_model = api.model('Order', {
    'id': fields.String(readonly=True),
    'pet_id': fields.Integer(required=True),
    'status': fields.String(enum=PET_STATUS)
})

order_update_model = api.model('OrderUpdate', {
    'status': fields.String(required=True, enum=PET_STATUS)
})

pet_ns = Namespace('pets', description='Pets operations')
store_ns = Namespace('store', description='Store operations')

api.add_namespace(pet_ns)
api.add_namespace(store_ns)

pets = [
    {'id': 0, 'name': 'snowball', 'type': 'cat', 'status': 'available'},
    {'id': 1, 'name': 'ranger', 'type': 'dog', 'status': 'pending'},
    {'id': 2, 'name': 'flippy', 'type': 'fish', 'status': 'available'}
]

orders = {}

# ---------------- PETS ---------------- #

@pet_ns.route('/')
class PetList(Resource):

    @pet_ns.marshal_list_with(pet_model)
    def get(self):
        return pets

    @pet_ns.expect(pet_model)
    @pet_ns.marshal_with(pet_model, code=201)
    def post(self):
        pet = api.payload

        if any(p['id'] == pet['id'] for p in pets):
            api.abort(409, f"Pet with ID {pet['id']} already exists")

        pets.append(pet)
        return pet, 201


@pet_ns.route('/<int:pet_id>')
class Pet(Resource):

    @pet_ns.marshal_with(pet_model)
    def get(self, pet_id):
        pet = next((p for p in pets if p['id'] == pet_id), None)
        if not pet:
            api.abort(404, f"Pet with ID {pet_id} not found")
        return pet


@pet_ns.route('/findByStatus')
class PetFindByStatus(Resource):

    @pet_ns.marshal_list_with(pet_model)
    def get(self):
        status = request.args.get('status')

        if not status:
            api.abort(400, "Status query parameter is required")

        if status not in PET_STATUS:
            api.abort(400, f"Invalid pet status {status}")

        return [p for p in pets if p['status'] == status]


# ---------------- STORE ---------------- #

@store_ns.route('/order')
class OrderResource(Resource):

    @store_ns.expect(order_model)
    @store_ns.marshal_with(order_model, code=201)
    def post(self):
        order_data = api.payload
        pet_id = order_data.get('pet_id')

        pet = next((p for p in pets if p['id'] == pet_id), None)
        if not pet:
            api.abort(404, f"No pet found with ID {pet_id}")

        if pet['status'] != 'available':
            api.abort(400, f"Pet with ID {pet_id} is not available")

        pet['status'] = 'pending'

        order_id = str(uuid.uuid4())
        order_data['id'] = order_id
        order_data['status'] = 'pending'

        orders[order_id] = order_data
        return order_data, 201


@store_ns.route('/order/<string:order_id>')
class OrderUpdateResource(Resource):

    def patch(self, order_id):

        if order_id not in orders:
            api.abort(404, "Order not found")

        update_data = request.json

        if not update_data or 'status' not in update_data:
            api.abort(400, "Status is required")

        new_status = update_data['status']

        if new_status not in PET_STATUS:
            api.abort(400, f"Invalid status '{new_status}'")

        order = orders[order_id]
        pet_id = order['pet_id']
        pet = next((p for p in pets if p['id'] == pet_id), None)

        if not pet:
            api.abort(404, f"No pet found with ID {pet_id}")

        order['status'] = new_status
        pet['status'] = new_status

        return {"message": "Order and pet status updated successfully"}


if __name__ == '__main__':
    app.run(debug=True)
