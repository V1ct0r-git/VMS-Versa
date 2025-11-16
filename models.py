from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Date
from sqlalchemy import Enum
from sqlalchemy import Numeric
from sqlalchemy import TIMESTAMP
from sqlalchemy import DateTime

db = SQLAlchemy()


class Car(db.Model):
    __tablename__ = 'Cars'
    CarID = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(30))
    year = db.Column(db.Integer)
    model = db.Column(db.String(20))
    licensePlate = db.Column(db.String(9))
    vin = db.Column(db.String(17))
    engineNumber = db.Column(db.String(20))
    color = db.Column(db.String(20))
    power = db.Column(db.Integer)
    lastMaintenance = db.Column(db.Date)
    nextMaintenance = db.Column(db.Date)
    maintenanceInterval = db.Column(db.Integer, default=10000)
    notes = db.Column(db.Text)
    mileage = db.Column(db.Integer)
    status = db.Column(db.Enum('Active', 'Inactive', 'Maintenance', 'Retired'), default='Active')

class Maintenance(db.Model):
    __tablename__ = 'Maintenance'
    maintenanceID = db.Column(db.Integer, primary_key=True)
    carID = db.Column(db.Integer, db.ForeignKey('Cars.CarID'))
    typeID = db.Column(db.Integer, db.ForeignKey('MaintenanceTypes.typeID'))
    priority = db.Column(db.Enum('low', 'medium', 'high', 'critical'), default='medium')
    userID = db.Column(db.Integer, db.ForeignKey('Users.userID'))
    startDate = db.Column(db.Date)
    completeDate = db.Column(db.Date)
    description = db.Column(db.Text)
    partsCost = db.Column(db.Numeric(10, 2))
    laborCost = db.Column(db.Numeric(10, 2), default=0.00)
    totalCost = db.Column(db.Numeric(10, 2))
    mileageAtService = db.Column(db.Integer)
    nextServiceDate = db.Column(db.Date)
    nextServiceMileage = db.Column(db.Integer)
    status = db.Column(db.Enum('planned', 'in_progress', 'completed', 'cancelled', 'on_hold'), default='planned')
    
    # Связи
    car = db.relationship('Car', backref='maintenances')
    maintenance_type = db.relationship('MaintenanceType', backref='maintenances')
    user = db.relationship('User', backref='maintenances')



    @property
    def calculated_total_cost(self):
        parts = self.partsCost or 0
        labor = self.laborCost or 0
        return parts + labor
    


class MaintenanceType(db.Model):
    __tablename__ = 'MaintenanceTypes'
    typeID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text)
    intervalKm = db.Column(db.Integer)
    intervalDays = db.Column(db.Integer)
    estimatedDuration = db.Column(db.Integer)
    estimatedCost = db.Column(db.Numeric(10, 2))

class Repair(db.Model):
    __tablename__ = 'Repairs'
    repairID = db.Column(db.Integer, primary_key=True)
    repairType = db.Column(db.Enum('engine', 'transmission', 'brakes', 'electrical', 'body', 'other'), default='other')
    priority = db.Column(db.Enum('low', 'medium', 'high', 'critical'), default='medium')
    status = db.Column(db.Enum('planned', 'in_progress', 'completed', 'cancelled'), default='planned')
    warrantyExpiry = db.Column(db.Date)
    carID = db.Column(db.Integer, db.ForeignKey('Cars.CarID'))
    date = db.Column(db.Date)
    reason = db.Column(db.Text)
    description = db.Column(db.Text)
    cost = db.Column(db.Numeric(10, 2))
    serviceName = db.Column(db.String(30))
    
    # Связь
    car = db.relationship('Car', backref='repairs')

class Reminder(db.Model):
    __tablename__ = 'Reminders'
    reminderID = db.Column(db.Integer, primary_key=True)
    # reminderType, isRecurring, recurrenceInterval УДАЛЕНЫ
    priority = db.Column(db.Enum('low', 'medium', 'high', 'critical'), default='medium')
    # createdAt остается
    createdAt = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    # maintenanceID остается
    maintenanceID = db.Column(db.Integer, db.ForeignKey('Maintenance.maintenanceID'))
    # remindDate остается
    remindDate = db.Column(db.Date)
    # message остается
    message = db.Column(db.Text)
    # isRead остается
    isRead = db.Column(db.Enum('true', 'false'))
    
    # Связь
    maintenance = db.relationship('Maintenance', backref='reminders')

class User(db.Model):
    __tablename__ = 'Users'
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    passwordHash = db.Column(db.String(32))
    fullName = db.Column(db.String(30))
    mail = db.Column(db.String(30))
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum('admin', 'mechanic', 'manager'))
    passwordDate = db.Column(db.DateTime)
    isBlocked = db.Column(db.Enum('true', 'false'), default='false')
    loginAttempts = db.Column(db.Integer, default=0)
    lastLoginAttempt = db.Column(db.DateTime)
    blockedUntil = db.Column(db.DateTime)

    def get_id(self):
        return str(self.userID)

    @property
    def is_active(self):
        return self.isBlocked != 'true'

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False