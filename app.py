from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_jwt_extended import create_access_token, JWTManager, jwt_required

environ.setdefault('DB_URL','sqlite:///employee.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
app.config['JWT_SECRET_KEY'] = 'SECRET_KEY'

db = SQLAlchemy(app)
app.app_context().push()
jwt = JWTManager(app)

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    designation = db.Column(db.String(120), nullable=False)

    def json(self):
        return {'id': self.id,'name': self.name, 'designation': self.designation}

db.create_all()


@app.route('/employees', methods=['POST'])
@jwt_required()
def create_employee():
    """
    create new employee
    """
    try:
        data = request.get_json()
        new_employee = Employee(name=data['name'],designation=data['designation'])
        db.session.add(new_employee)
        db.session.commit()
        return make_response(jsonify({'message': 'employee record created'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'error creating employee {e}'}), 500)

@app.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """
    Get all employees details
    """
    try:
        employees = Employee.query.all()
        return make_response(jsonify([employee.json() for employee in employees]), 200)
    except:
        return make_response(jsonify({'message': 'error fetching employees'}), 500)

@app.route('/employees/<int:id>', methods=['GET'])
@jwt_required()
def get_employee(id):
    """
    Get employee details based on ID
    """
    try:
        employee = Employee.query.filter_by(id=id).first()
        if employee:
            return make_response(jsonify([employee.json()]), 200)
        return make_response(jsonify({'message': 'employee not found'}), 404)
    except:
        return make_response(jsonify({'message': 'error fetching employee'}), 500)

@app.route('/employees/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_employee(id):
    """
    Delete employee based on ID
    """
    try:
        employee = Employee.query.filter_by(id=id).first()
        if employee:
            db.session.delete(employee)
            db.session.commit()
            return make_response(jsonify({'message': 'employee deleted'}), 200)
        return make_response(jsonify({'message': 'employee not found'}), 404)
    except:
        return make_response(jsonify({'message': 'error deleting employee'}), 500)

@app.route('/employees/<int:id>', methods=['PUT'])
@jwt_required()
def update_employee(id):
    """
    Update employee details based on ID
    """    
    try:
        employee = Employee.query.filter_by(id=id).first()
        if employee:
            data = request.get_json()
            employee.name=data['name']
            employee.designation=data['designation']
            db.session.commit()
            return make_response(jsonify({'message': 'employee updated'}), 200)
        return make_response(jsonify({'message': 'employee not found'}), 404)
    except:
        return make_response(jsonify({'message': 'error updating employees'}), 500)

@app.route('/getToken')
def get_token():
    """
    Generate JWT Token
    """
    access_token = create_access_token(identity='admin')
    return make_response(jsonify({'access_token': access_token}),200)

if __name__ == '__main__':
    app.run(debug=True,port=5000)