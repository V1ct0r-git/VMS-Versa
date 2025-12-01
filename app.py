from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, send_from_directory, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models import db, Car, Maintenance, MaintenanceType, Repair, Reminder, User
import hashlib
from typing import Optional
import secrets
import subprocess
import glob
import traceback
from datetime import datetime, timedelta, date
from sqlalchemy import Enum, text, func
from system_info import SYSTEM_INFO, TECHNOLOGY_VERSIONS, MODULES, get_system_info
import random
import os
from urllib.parse import urlparse
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
import base64
import re
import requests


# Настройки Flask
app = Flask(__name__)
app.secret_key = "21232f297a57a5a743894a0e4a801fc3"

# заранее закодированная строка с данными для подключения к базе
encrypted_string = "bXlzcWwrcHlteXNxbDovL1NjaGxlZ2VsOjEwX29TbUAxMzQuOTAuMTY3LjQyOjEwMzA2L3Byb2plY3RfU2NobGVnZWw="
connection_string = base64.b64decode(encrypted_string).decode()

# Настройки SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Инициализация SQLAlchemy
db.init_app(app)


# Настройки Flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "basic"


# Настройки куки
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)


# Указываем путь к папке backup
BACKUP_DIR = os.path.join(app.root_path, 'backup')

# Указываем путь к списку избранных бэкапов
FAVORITES_FILE = os.path.join(BACKUP_DIR, 'favorites.json')



# Функции

# Создаёт напоминания для ТО, у которых их ещё нет
def create_daily_reminders():
    try:
        with app.app_context():  # ← Обязательно в контексте приложения
            # Настройки: за сколько дней создавать напоминания
            PRIORITY_REMINDER_DAYS = {
                'critical': 14,
                'high': 7,
                'medium': 3,
                'low': 1
            }
            
            # Получаем текущую дату
            today = date.today()
            
            # Находим все ТО, которые не завершены и не отменены
            active_maintenance = Maintenance.query.filter(
                Maintenance.status != 'completed',
                Maintenance.status != 'cancelled'
            ).all()
            
            created_count = 0
            for maintenance in active_maintenance:
                # Проверяем, существует ли уже напоминание для этого ТО
                existing_reminder = Reminder.query.filter_by(
                    maintenanceID=maintenance.maintenanceID
                ).first()
                
                if not existing_reminder:
                    # Рассчитываем дату напоминания
                    reminder_days = PRIORITY_REMINDER_DAYS.get(maintenance.priority, 1)
                    reminder_date = maintenance.startDate - timedelta(days=reminder_days)
                    
                    # Убедимся, что дата напоминания не раньше, чем завтра
                    tomorrow = today + timedelta(days=1)
                    if reminder_date < tomorrow:
                        reminder_date = tomorrow
                    
                    # Генерируем сообщение
                    car = maintenance.car  # ← Автомобиль получаем через отношение
                    message = f"ТО '{maintenance.maintenance_type.name}' для {car.brand} {car.model} ({car.licensePlate}) запланировано на {maintenance.startDate.strftime('%d.%m.%Y')}, приоритет: {maintenance.priority}"
                    
                    # Создаём новое напоминание (только существующие поля!)
                    new_reminder = Reminder(
                        maintenanceID=maintenance.maintenanceID,
                        message=message,
                        priority=maintenance.priority,  # ← Приоритет как в ТО
                        remindDate=reminder_date,
                        isRead='false'  # ← Только 'true' или 'false' как строки
                    )
                    
                    db.session.add(new_reminder)
                    created_count += 1
            
            if created_count > 0:
                db.session.commit()
                print(f"DEBUG: Создано {created_count} напоминаний")
            else:
                print("DEBUG: Напоминаний не создано")
                
    except Exception as e:
        with app.app_context():  # ← Контекст и для rollback
            db.session.rollback()
        print(f"ERROR: Ошибка при создании напоминаний: {str(e)}")


# Извлекает настройки БД из SQLALCHEMY_DATABASE_URI для бэкапирования
def get_db_config():
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    parsed = urlparse(uri)
    return {
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port or 3306,
        'database': parsed.path.lstrip('/')  # Убираем начальный '/'
    }


# Избранное для бэкапов
def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        # Создаём файл с пустым списком
        with open(FAVORITES_FILE, 'w') as f:
            json.dump({"favorites": []}, f)
        return set()

    try:
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('favorites', []))
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        # Если файл повреждён — создаём заново
        with open(FAVORITES_FILE, 'w') as f:
            json.dump({"favorites": []}, f)
        return set()

def save_favorites(favorites):
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump({"favorites": list(favorites)}, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении избранного: {e}")

def is_auto_backup_created_today():
    """
    Проверяет, был ли создан автоматический бэкап сегодня.
    """
    today = datetime.now().date()
    backup_pattern = os.path.join(BACKUP_DIR, f"auto_backup_{today.strftime('%Y%m%d')}_*.sql")
    today_auto_backups = glob.glob(backup_pattern)
    return len(today_auto_backups) > 0

def is_favorite(filename):
    return filename in load_favorites()

def toggle_favorite(filename):
    favorites = load_favorites()
    if filename in favorites:
        favorites.remove(filename)
    else:
        favorites.add(filename)
    save_favorites(favorites)

# Функция для обеспечения ежедневного автоматического бэкапа
def ensure_daily_auto_backup():
    """
    Проверяет, был ли создан автоматический бэкап сегодня.
    Если нет и текущее время >= 8:00, создает его.
    """
    now = datetime.now()
    if now.hour < 8:
        print(f"Время {now.strftime('%H:%M:%S')} — автоматический бэкап не будет создан до 8:00 утра.")
        return

    if is_auto_backup_created_today():
        print("Автоматический бэкап за сегодня уже был создан. Пропускаем.")
        return

    # Создаем бэкап
    scheduled_backup()

# Функция, вызываемая планировщиком для автоматического бэкапа.
def scheduled_backup():
    """
    Функция, вызываемая планировщиком или вручную для автоматического бэкапа.
    Создает бэкап только если текущее время >= 8:00.
    """
    now = datetime.now()
    if now.hour < 8:
        print(f"Время {now.strftime('%H:%M:%S')} — бэкап не будет создан до 8:00 утра.")
        return # Выходим, если еще не 8 утра

    # Проверяем еще раз, не создался ли бэкап с момента начала проверки в get_backup_list
    if is_auto_backup_created_today():
        print("Автоматический бэкап за сегодня уже был создан. Пропускаем.")
        return

    try:
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        filename = f"auto_backup_{timestamp}.sql"
        filepath = os.path.join(BACKUP_DIR, filename)

        db_config = get_db_config()

        cmd = [
            'mysqldump',
            f"--host={db_config['host']}",
            f"--port={db_config['port']}",
            f"--user={db_config['user']}",
            f"--password={db_config['password']}",
            '--single-transaction',
            '--routines',
            '--triggers',
            db_config['database']
        ]

        with open(filepath, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, check=False)

        if result.returncode != 0:
            if os.path.exists(filepath):
                os.remove(filepath)
            error_msg = result.stderr.strip() or "Неизвестная ошибка при создании бэкапа."
            print(f"Ошибка при автоматическом бэкапе: {error_msg}")
        else:
            print(f"Автоматический бэкап создан: {filename}")
    except Exception as e:
        print(f"Ошибка в scheduled_backup: {e}")
        traceback.print_exc()



# Маршруты

# Перенаправление на страницу входа, при заходе на главную страницу
@app.route('/')
def index():
    return redirect(url_for('login'))


# Маршрут: информационная панель
@app.route('/dashboard')
@login_required
def dashboard():
    # Статистика по автомобилям
    total_cars = db.session.query(db.func.count(Car.CarID)).scalar()
    active_cars = db.session.query(db.func.count(Car.CarID)).filter(Car.status == 'Active').scalar()
    maintenance_cars = db.session.query(db.func.count(Car.CarID)).filter(Car.status == 'Maintenance').scalar()
    retired_cars = db.session.query(db.func.count(Car.CarID)).filter(Car.status == 'Retired').scalar()

    # Предстоящие ТО (в течение 30 дней)
    today = datetime.today().date()
    upcoming_date = today + timedelta(days=30)
    upcoming_maintenance = db.session.query(db.func.count(Car.CarID)).filter(
        Car.nextMaintenance <= upcoming_date,
        Car.status == 'Active'
    ).scalar()

    # Просроченные ТО
    overdue_maintenance = db.session.query(db.func.count(Car.CarID)).filter(
        Car.nextMaintenance < today,
        Car.status == 'Active'
    ).scalar()

    # Недавние записи ТО (последние 5) - теперь с ID для перехода
    recent_maintenance = Maintenance.query.options(
        db.joinedload(Maintenance.car),
        db.joinedload(Maintenance.maintenance_type),
        db.joinedload(Maintenance.user)
    ).order_by(Maintenance.startDate.desc()).limit(5).all()
    
    recent_activities = []
    for m in recent_maintenance:
        recent_activities.append({
            'car_brand': m.car.brand,
            'car_model': m.car.model,
            'date': m.startDate.strftime('%d.%m.%Y') if m.startDate else '—',
            'type_name': m.maintenance_type.name,
            'cost': m.totalCost or 0.0,
            'mechanic_name': m.user.fullName,
            'maintenance_id': m.maintenanceID
        })

    # Последние напоминания (по дате создания)
    latest_reminders = Reminder.query.options(
        db.joinedload(Reminder.maintenance).joinedload(Maintenance.car)
    ).order_by(Reminder.createdAt.desc()).limit(5).all()

    latest_reminders_list = []
    for r in latest_reminders:
        latest_reminders_list.append({
            'message': r.message,
            'remindDate': r.remindDate,
            'car_brand': r.maintenance.car.brand if r.maintenance and r.maintenance.car else '—',
            'car_model': r.maintenance.car.model if r.maintenance and r.maintenance.car else '—',
            'reminderID': r.reminderID,
            'createdAt': r.createdAt 
        })

    # Статистика по приоритетам ТО
    high_priority = db.session.query(db.func.count(Maintenance.maintenanceID)).filter(Maintenance.priority == 'high').scalar()
    medium_priority = db.session.query(db.func.count(Maintenance.maintenanceID)).filter(Maintenance.priority == 'medium').scalar()
    low_priority = db.session.query(db.func.count(Maintenance.maintenanceID)).filter(Maintenance.priority == 'low').scalar()
    critical_priority = db.session.query(db.func.count(Maintenance.maintenanceID)).filter(Maintenance.priority == 'critical').scalar()

    stats = {
        'total_cars': total_cars,
        'active_cars': active_cars,
        'maintenance_cars': maintenance_cars,
        'retired_cars': retired_cars,
        'upcoming_maintenance': upcoming_maintenance,
        'overdue_maintenance': overdue_maintenance,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'critical_priority': critical_priority
    }

    return render_template('dashboard.html', 
                         username=current_user.fullName,
                         stats=stats,
                         recent_activities=recent_activities,
                         latest_reminders=latest_reminders_list)


# Маршрут: Ремонт
@app.route('/repairs')
@login_required
def repairs():
    # Получаем параметры фильтрации
    car_id = request.args.get('car_id', '')
    status = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Параметры сортировки
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Пагинация
    page = int(request.args.get('page', 1))
    per_page = 10

    # Формируем запрос
    query = Repair.query.options(
        db.joinedload(Repair.car)
    )
    
    # Фильтры
    if car_id:
        query = query.filter(Repair.carID == int(car_id))
    
    if status:
        query = query.filter(Repair.status == status)
    
    if type_filter:
        query = query.filter(Repair.repairType == type_filter)
    
    if date_from:
        query = query.filter(Repair.date >= date_from)
    
    if date_to:
        query = query.filter(Repair.date <= date_to)
    
    # Проверяем разрешенные столбцы для сортировки
    allowed_sort_columns = ['date', 'priority', 'status', 'cost', 'repairType']
    if sort_by not in allowed_sort_columns:
        sort_by = 'date'
    
    # Сортировка
    if sort_by == 'date':
        if sort_order == 'asc':
            query = query.order_by(Repair.date.asc())
        else:
            query = query.order_by(Repair.date.desc())
    elif sort_by == 'priority':
        if sort_order == 'asc':
            query = query.order_by(Repair.priority.asc())
        else:
            query = query.order_by(Repair.priority.desc())
    elif sort_by == 'status':
        if sort_order == 'asc':
            query = query.order_by(Repair.status.asc())
        else:
            query = query.order_by(Repair.status.desc())
    elif sort_by == 'cost':
        if sort_order == 'asc':
            query = query.order_by(Repair.cost.asc())
        else:
            query = query.order_by(Repair.cost.desc())
    elif sort_by == 'repairType':
        if sort_order == 'asc':
            query = query.order_by(Repair.repairType.asc())
        else:
            query = query.order_by(Repair.repairType.desc())
    else:
        # по умолчанию сортировка по дате
        if sort_order == 'asc':
            query = query.order_by(Repair.date.asc())
        else:
            query = query.order_by(Repair.date.desc())

    # Выполняем запрос для подсчета общего количества
    total = query.count()
    
    # Рассчитываем offset для пагинации
    offset = (page - 1) * per_page
    
    # Получаем записи для текущей страницы
    repairs_list = query.offset(offset).limit(per_page).all()

    # Получаем список всех автомобилей для фильтра
    vehicles = Car.query.order_by(Car.brand, Car.model).all()

    # Получаем список всех типов ремонтов
    repair_types = [row[0] for row in db.session.query(Repair.repairType).distinct().order_by(Repair.repairType).all()]

    # Получаем информацию об отфильтрованном автомобиле
    filtered_vehicle = None
    if car_id:
        filtered_vehicle = Car.query.filter_by(CarID=int(car_id)).first()

    # Статистика
    stats_query = Repair.query
    
    if car_id:
        stats_query = stats_query.filter(Repair.carID == int(car_id))
    if type_filter:
        stats_query = stats_query.filter(Repair.repairType == type_filter)
    if date_from:
        stats_query = stats_query.filter(Repair.date >= date_from)
    if date_to:
        stats_query = stats_query.filter(Repair.date <= date_to)

    # Подсчёт статистики
    planned_count = stats_query.filter(Repair.status == 'planned').count()
    in_progress_count = stats_query.filter(Repair.status == 'in_progress').count()
    completed_count = stats_query.filter(Repair.status == 'completed').count()
    cancelled_count = stats_query.filter(Repair.status == 'cancelled').count()
    
    total_cost = db.session.query(db.func.sum(Repair.cost)).scalar() or 0.0

    stats = {
        'total': total,
        'planned': planned_count,
        'in_progress': in_progress_count,
        'completed': completed_count,
        'cancelled': cancelled_count,
        'total_cost': float(total_cost)
    }

    # Рассчитываем общее количество страниц
    total_pages = (total + per_page - 1) // per_page

    # Создаем объект, имитирующий пагинацию для шаблона
    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
        
        @property
        def has_prev(self):
            return self.page > 1
        
        @property
        def has_next(self):
            return self.page < self.pages

    repairs = Pagination(repairs_list, page, per_page, total)

    return render_template('repairs/repairs.html',
                         repairs=repairs,
                         vehicles=vehicles,
                         repair_types=repair_types,
                         filtered_vehicle=filtered_vehicle,
                         car_id=car_id,
                         status=status,
                         type_filter=type_filter,
                         date_from=date_from,
                         date_to=date_to,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         stats=stats,
                         sort_by=sort_by,
                         sort_order=sort_order)

# Маршрут: Добавить ремонт
@app.route('/repairs/add', methods=['GET', 'POST'])
@login_required
def add_repair():
    if request.method == 'POST':
        car_id = int(request.form['car_id'])
        repair_type = request.form['repair_type']
        priority = request.form['priority']
        date = request.form['date'] or None
        reason = request.form['reason']
        description = request.form['description']
        cost = float(request.form['cost']) if request.form['cost'] else 0
        status = request.form['status']
        warranty_expiry = request.form['warranty_expiry'] or None
        service_name = request.form['service_name']

        # Создаем новый ремонт
        repair = Repair(
            carID=car_id,
            repairType=repair_type,
            priority=priority,
            status=status,
            warrantyExpiry=warranty_expiry,
            date=date,
            reason=reason,
            description=description,
            cost=cost,
            serviceName=service_name
        )

        db.session.add(repair)
        db.session.commit()

        flash('Ремонт успешно добавлен!', 'success')
        return redirect(url_for('repairs'))

    # Получаем список автомобилей для формы
    vehicles = Car.query.order_by(Car.brand, Car.model).all()
    
    return render_template('repairs/add_repair.html', vehicles=vehicles)

# Маршрут: Просмотр ремонта
@app.route('/repairs/view/<int:repair_id>')
@login_required
def view_repair(repair_id):
    repair = Repair.query.options(
        db.joinedload(Repair.car),
    ).filter_by(repairID=repair_id).first_or_404()
    
    return render_template('repairs/view_repair.html', repair=repair)

# Маршрут: Редактирование ремонта
@app.route('/repairs/edit/<int:repair_id>', methods=['GET', 'POST'])
@login_required
def edit_repair(repair_id):
    repair = Repair.query.get_or_404(repair_id)
    
    if request.method == 'POST':
        repair.carID = int(request.form['car_id'])
        repair.repairType = request.form['repair_type']
        repair.priority = request.form['priority']
        repair.status = request.form['status']
        repair.warrantyExpiry = request.form['warranty_expiry'] or None
        repair.date = request.form['date'] or None
        repair.reason = request.form['reason']
        repair.description = request.form['description']
        repair.cost = float(request.form['cost']) if request.form['cost'] else 0
        repair.serviceName = request.form['service_name']

        db.session.commit()
        flash('Ремонт успешно обновлен!', 'success')
        return redirect(url_for('repairs'))

    # Получаем список автомобилей для формы
    vehicles = Car.query.order_by(Car.brand, Car.model).all()
    
    return render_template('repairs/edit_repair.html', repair=repair, vehicles=vehicles)


# Маршрут: Транспорт
@app.route('/vehicles')
@login_required
def vehicles():
    # Получаем параметры фильтрации
    status = request.args.get('status', '')
    brand = request.args.get('brand', '')
    year_from = request.args.get('year_from', '')
    year_to = request.args.get('year_to', '')
    mileage_min = request.args.get('mileage_min', '')
    mileage_max = request.args.get('mileage_max', '')
    
    # Параметры сортировки
    sort_by = request.args.get('sort_by', 'brand')  # По умолчанию — по марке
    sort_order = request.args.get('sort_order', 'asc')  # По умолчанию — по возрастанию
    
    # Пагинация
    page = int(request.args.get('page', 1))
    per_page = 10

    # Формируем запрос с фильтрами
    query = Car.query
    
    if status:
        query = query.filter(Car.status == status)
    
    if brand:
        query = query.filter(Car.brand == brand)
    
    if year_from:
        query = query.filter(Car.year >= int(year_from))
    
    if year_to:
        query = query.filter(Car.year <= int(year_to))
    
    if mileage_min:
        query = query.filter(Car.mileage >= int(mileage_min))
    
    if mileage_max:
        query = query.filter(Car.mileage <= int(mileage_max))
    
    # Определяем поле для сортировки
    allowed_sort_columns = ['brand', 'year', 'mileage', 'status']
    if sort_by not in allowed_sort_columns:
        sort_by = 'brand'
    
    # Применяем сортировку
    if sort_by == 'brand':
        if sort_order == 'asc':
            query = query.order_by(Car.brand.asc())
        else:
            query = query.order_by(Car.brand.desc())
    elif sort_by == 'year':
        if sort_order == 'asc':
            query = query.order_by(Car.year.asc())
        else:
            query = query.order_by(Car.year.desc())
    elif sort_by == 'mileage':
        if sort_order == 'asc':
            query = query.order_by(Car.mileage.asc())
        else:
            query = query.order_by(Car.mileage.desc())
    elif sort_by == 'status':
        if sort_order == 'asc':
            query = query.order_by(Car.status.asc())
        else:
            query = query.order_by(Car.status.desc())
    else:
        # по умолчанию сортировка по марке
        if sort_order == 'asc':
            query = query.order_by(Car.brand.asc())
        else:
            query = query.order_by(Car.brand.desc())

    # Выполняем запрос для подсчета общего количества
    total = query.count()
    
    # Рассчитываем offset для пагинации
    offset = (page - 1) * per_page
    
    # Получаем записи для текущей страницы
    cars_list = query.offset(offset).limit(per_page).all()

    # Получаем список уникальных марок для фильтра
    brands = [row[0] for row in db.session.query(Car.brand).distinct().order_by(Car.brand).all()]

    # Статистика
    stats = {
        'total': total,
        'active': db.session.query(db.func.count(Car.CarID)).filter(Car.status == 'Active').scalar(),
        'inactive': db.session.query(db.func.count(Car.CarID)).filter(Car.status == 'Inactive').scalar(),
        'maintenance': db.session.query(db.func.count(Car.CarID)).filter(Car.status == 'Maintenance').scalar(),
        'retired': db.session.query(db.func.count(Car.CarID)).filter(Car.status == 'Retired').scalar()
    }

    # Рассчитываем общее количество страниц
    total_pages = (total + per_page - 1) // per_page

    # Создаем объект, имитирующий пагинацию для шаблона
    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
        
        @property
        def has_prev(self):
            return self.page > 1
        
        @property
        def has_next(self):
            return self.page < self.pages

    cars = Pagination(cars_list, page, per_page, total)

    # Формируем query string для пагинации (сохраняем параметры фильтрации и сортировки)
    query_params = request.args.copy()
    if 'page' in query_params:
        query_params.pop('page')
    query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()]) if query_params else ''

    return render_template('vehicles/vehicles.html',
                         cars=cars, 
                         status=status,
                         brand=brand,
                         year_from=year_from,
                         year_to=year_to,
                         mileage_min=mileage_min,
                         mileage_max=mileage_max,
                         brands=brands,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         query_string=query_string,
                         stats=stats,
                         sort_by=sort_by,
                         sort_order=sort_order)

# Маршрут: Просмотр транспорта
@app.route('/vehicle/view/<int:car_id>')
@login_required
def vehicle_detail(car_id):
    car = Car.query.filter_by(CarID=car_id).first()
    
    if not car:
        flash('Автомобиль не найден', 'error')
        return redirect(url_for('vehicles'))
    
    # История пробега — у нас только одна запись: текущий пробег
    # Мы можем показать дату последнего ТО и следующего
    mileage_history = [
        {
            'maintenanceDate': car.lastMaintenance,
            'mileage': car.mileage
        }
    ]
    
    return render_template('vehicles/vehicle_detail.html', car=car, mileage_history=mileage_history, username=current_user.fullName)

# Маршрут: Редактирование транспорта
@app.route('/vehicle/edit/<int:car_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(car_id):
    car = Car.query.filter_by(CarID=car_id).first()
    
    if not car:
        flash('Автомобиль не найден', 'error')
        return redirect(url_for('vehicles'))
    
    if request.method == 'POST':
        brand = request.form['brand']
        model = request.form['model']
        year = request.form['year']
        license_plate = request.form['license_plate']
        color = request.form['color']
        mileage = request.form['mileage']
        status = request.form['status']
        
        try:
            # Проверка и преобразование числовых значений
            year_int = int(year)
            mileage_int = int(mileage)
            
            # Проверка на отрицательные значения
            if year_int < 1886:  # Первый автомобиль был создан в 1886 году
                flash('Год выпуска не может быть меньше 1886', 'error')
                return render_template('vehicles/edit_vehicle.html', car=car, username=current_user.fullName)
            
            if mileage_int < 0:
                flash('Пробег не может быть отрицательным', 'error')
                return render_template('vehicles/edit_vehicle.html', car=car, username=current_user.fullName)
            
            # Обновление данных автомобиля
            car.brand = brand
            car.model = model
            car.year = year_int
            car.licensePlate = license_plate
            car.color = color
            car.mileage = mileage_int
            car.status = status
            
            db.session.commit()
            flash('Информация об автомобиле обновлена', 'success')
            return redirect(url_for('vehicle_detail', car_id=car_id))
        
        except ValueError as e:
            db.session.rollback()
            flash('Некорректное значение года или пробега. Пожалуйста, введите числовые значения.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении автомобиля: {str(e)}', 'error')
    
    return render_template('vehicles/edit_vehicle.html', car=car, username=current_user.fullName)

# Маршрут: Добавление транспорта
@app.route('/vehicles/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            brand = request.form['brand']
            model = request.form['model']
            year = request.form['year']
            license_plate = request.form['license_plate']
            vin = request.form['vin']
            engine_number = request.form['engine_number']
            color = request.form['color']
            power = request.form['power']
            mileage = request.form['mileage']
            status = request.form.get('status', 'Active')  # По умолчанию Active
            notes = request.form.get('notes', '')
            
            # Валидация обязательных полей
            if not brand or not model or not year or not license_plate:
                flash('Заполните все обязательные поля!', 'error')
                return render_template('add_vehicle.html', username=current_user.fullName)
            
            # Проверка уникальности VIN и номера двигателя
            if vin:
                existing_vin = Car.query.filter_by(vin=vin).first()
                if existing_vin:
                    flash('VIN уже существует в системе!', 'error')
                    return render_template('add_vehicle.html', username=current_user.fullName)
            
            if engine_number:
                existing_engine = Car.query.filter_by(engineNumber=engine_number).first()
                if existing_engine:
                    flash('Номер двигателя уже существует в системе!', 'error')
                    return render_template('add_vehicle.html', username=current_user.fullName)
            
            # Создаем новый автомобиль
            new_car = Car(
                brand=brand,
                model=model,
                year=int(year),
                licensePlate=license_plate,
                vin=vin or None,
                engineNumber=engine_number or None,
                color=color or None,
                power=int(power) if power else None,
                mileage=int(mileage) if mileage else 0,
                status=status,
                notes=notes or None,
                lastMaintenance=None,
                nextMaintenance=None,
                maintenanceInterval=10000  # По умолчанию 10000 км
            )
            
            db.session.add(new_car)
            db.session.commit()
            
            flash('Автомобиль успешно добавлен!', 'success')
            return redirect(url_for('vehicle_detail', car_id=new_car.CarID))
            
        except ValueError as e:
            db.session.rollback()
            flash('Проверьте правильность ввода числовых значений!', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении автомобиля: {str(e)}', 'error')
    
    return render_template('vehicles/add_vehicle.html', username=current_user.fullName)


# Маршрут: Механики
@app.route('/mechanics')
@login_required
def mechanics():
    # Получаем всех механиков (пользователей с ролью mechanic)
    mechanics_list = User.query.filter(User.role == 'mechanic').order_by(User.fullName).all()
    
    # Статистика
    total_mechanics = User.query.filter(User.role == 'mechanic').count()
    active_mechanics = User.query.filter(User.role == 'mechanic', User.isBlocked == 'false').count()
    inactive_mechanics = User.query.filter(User.role == 'mechanic', User.isBlocked == 'true').count()
    
    # Всего ТО (все записи в таблице Maintenance)
    total_maintenance = Maintenance.query.count()
    
    # Добавляем количество выполненных ТО для каждого механика
    for mechanic in mechanics_list:
        mechanic.completed_maintenance_count = Maintenance.query.filter(
            Maintenance.userID == mechanic.userID,
            Maintenance.status == 'completed'
        ).count()
        # Добавляем текущую нагрузку (в процессе)
        mechanic.current_workload = Maintenance.query.filter(
            Maintenance.userID == mechanic.userID,
            Maintenance.status.in_(['in_progress', 'planned'])
        ).count()
        # Добавляем общую стоимость выполненных работ
        total_cost = db.session.query(db.func.sum(Maintenance.totalCost)).filter(
            Maintenance.userID == mechanic.userID,
            Maintenance.status == 'completed'
        ).scalar()
        mechanic.total_earnings = float(total_cost or 0.0)
    
    stats = {
        'total_mechanics': total_mechanics,
        'active_mechanics': active_mechanics,
        'inactive_mechanics': inactive_mechanics,
        'total_maintenance': total_maintenance
    }
    
    return render_template('mechanics/mechanics.html',
                         mechanics=mechanics_list,
                         stats=stats,
                         username=current_user.fullName)

# Маршрут: Просмотр механика
@app.route('/mechanic/view/<int:mechanic_id>')
@login_required
def view_mechanic(mechanic_id):
    mechanic = User.query.filter_by(userID=mechanic_id).first()
    
    if not mechanic:
        flash('Механик не найден!', 'error')
        return redirect(url_for('mechanics'))
    
    # Получаем последние 6 работ механика
    recent_maintenance = Maintenance.query.filter_by(userID=mechanic.userID).order_by(Maintenance.startDate.desc()).limit(6).all()
    
    # Добавляем статистику
    mechanic.completed_maintenance_count = Maintenance.query.filter(
        Maintenance.userID == mechanic.userID,
        Maintenance.status == 'completed'
    ).count()
    
    mechanic.current_workload = Maintenance.query.filter(
        Maintenance.userID == mechanic.userID,
        Maintenance.status.in_(['in_progress', 'planned'])
    ).count()
    
    total_cost = db.session.query(db.func.sum(Maintenance.totalCost)).filter(
        Maintenance.userID == mechanic.userID,
        Maintenance.status == 'completed'
    ).scalar()
    mechanic.total_earnings = float(total_cost or 0.0)
    
    return render_template('mechanics/view_mechanic.html', 
                         mechanic=mechanic,
                         recent_maintenance=recent_maintenance,
                         username=current_user.fullName)


# Маршрут: ТО
@app.route('/maintenance')
@login_required
def maintenance_records():
    # Получаем параметры фильтрации и сортировки
    car_id = request.args.get('car_id')
    type_filter = request.args.get('type')
    user_id = request.args.get('user_id')
    status_filter = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    sort_by = request.args.get('sort_by', 'startDate')
    sort_order = request.args.get('sort_order', 'desc')

    allowed_sort_columns = ['startDate', 'priority', 'status', 'totalCost']
    if sort_by not in allowed_sort_columns:
        sort_by = 'startDate'

    page = int(request.args.get('page', 1))
    per_page = 10

    # Базовый запрос
    query = Maintenance.query.options(
        db.joinedload(Maintenance.car),
        db.joinedload(Maintenance.maintenance_type),
        db.joinedload(Maintenance.user)
    )

    # Если пользователь - механик, фильтруем по его ID
    if current_user.role == 'mechanic':
        query = query.filter(Maintenance.userID == current_user.userID)

    # Фильтрация
    if car_id:
        query = query.filter(Maintenance.carID == int(car_id))

    if type_filter:
        query = query.join(MaintenanceType).filter(MaintenanceType.name == type_filter)

    # Если пользователь не механик, учитываем фильтр по пользователю
    if user_id and current_user.role != 'mechanic':
        query = query.filter(Maintenance.userID == int(user_id))

    if status_filter:
        query = query.filter(Maintenance.status == status_filter)

    if date_from:
        query = query.filter(Maintenance.startDate >= date_from)

    if date_to:
        query = query.filter(Maintenance.startDate <= date_to)

    # Сортировка
    if sort_by == 'startDate':
        query = query.order_by(Maintenance.startDate.asc() if sort_order == 'asc' else Maintenance.startDate.desc())
    elif sort_by == 'priority':
        query = query.order_by(Maintenance.priority.asc() if sort_order == 'asc' else Maintenance.priority.desc())
    elif sort_by == 'status':
        query = query.order_by(Maintenance.status.asc() if sort_order == 'asc' else Maintenance.status.desc())
    elif sort_by == 'totalCost':
        query = query.order_by(Maintenance.totalCost.asc() if sort_order == 'asc' else Maintenance.totalCost.desc())

    total = query.count()
    offset = (page - 1) * per_page
    records = query.offset(offset).limit(per_page).all()

    # Данные для фильтров
    vehicles = Car.query.order_by(Car.brand, Car.model).all()
    
    # Если пользователь - механик, показываем только его
    if current_user.role == 'mechanic':
        mechanics = [current_user]
    else:
        mechanics = User.query.filter_by(role='mechanic').order_by(User.fullName).all()
    
    types = MaintenanceType.query.order_by(MaintenanceType.name).all()

    # Информация об отфильтрованных элементах
    filtered_vehicle = Car.query.filter_by(CarID=int(car_id)).first() if car_id else None
    
    # Если пользователь - механик, он видит только свои работы, не показываем сообщение о фильтрации по механику
    if current_user.role == 'mechanic':
        filtered_mechanic = current_user
    else:
        filtered_mechanic = User.query.filter_by(userID=int(user_id)).first() if user_id else None

    # Статистика
    stats_query = Maintenance.query.options(
        db.joinedload(Maintenance.maintenance_type)
    )

    # Применяем фильтр по механику для статистики
    if current_user.role == 'mechanic':
        stats_query = stats_query.filter(Maintenance.userID == current_user.userID)

    if car_id:
        stats_query = stats_query.filter(Maintenance.carID == int(car_id))
    if type_filter:
        stats_query = stats_query.join(MaintenanceType).filter(MaintenanceType.name == type_filter)
    if user_id and current_user.role != 'mechanic':
        stats_query = stats_query.filter(Maintenance.userID == int(user_id))
    if status_filter:
        stats_query = stats_query.filter(Maintenance.status == status_filter)
    if date_from:
        stats_query = stats_query.filter(Maintenance.startDate >= date_from)
    if date_to:
        stats_query = stats_query.filter(Maintenance.startDate <= date_to)

    planned_count = stats_query.join(MaintenanceType).filter(MaintenanceType.name == 'Плановое ТО').count()
    unplanned_count = stats_query.join(MaintenanceType).filter(MaintenanceType.name == 'Замена масла').count()
    total_cost = db.session.query(db.func.sum(Maintenance.totalCost)).join(MaintenanceType).filter(
        MaintenanceType.name.in_(['Плановое ТО', 'Замена масла'])
    ).scalar() or 0.0

    stats = {
        'total': total,
        'planned': planned_count,
        'unplanned': unplanned_count,
        'total_cost': float(total_cost)
    }

    return render_template('maintenance/maintenance.html',
                         records=records,
                         vehicles=vehicles,
                         mechanics=mechanics,
                         types=types,
                         filtered_vehicle=filtered_vehicle,
                         filtered_mechanic=filtered_mechanic,
                         car_id=car_id,
                         type_filter=type_filter,
                         user_id=user_id,
                         status_filter=status_filter,
                         date_from=date_from,
                         date_to=date_to,
                         page=page,
                         per_page=per_page,
                         total=total,
                         stats=stats,
                         sort_by=sort_by,
                         sort_order=sort_order)

# Маршрут: Обновление статуса ТО
@app.route('/maintenance/update_status/<int:record_id>', methods=['POST'])
@login_required
def update_maintenance_status(record_id):
    maintenance = Maintenance.query.filter_by(maintenanceID=record_id).first_or_404()
    
    # Проверяем права доступа
    if current_user.role != 'mechanic' or maintenance.userID != current_user.userID:
        flash('У вас нет прав для изменения этой записи', 'error')
        return jsonify({'success': False, 'message': 'Нет прав доступа'})
    
    try:
        # Получаем новые значения
        new_status = request.json.get('status')
        new_description = request.json.get('description')
        
        if new_status:
            # Проверяем допустимые статусы
            allowed_statuses = ['planned', 'in_progress', 'completed', 'cancelled', 'on_hold']
            if new_status not in allowed_statuses:
                return jsonify({'success': False, 'message': 'Недопустимый статус'})
            
            # Логика перехода между статусами
            old_status = maintenance.status
            maintenance.status = new_status
            
            # Устанавливаем дату начала при переходе в "in_progress"
            if new_status == 'in_progress' and old_status != 'in_progress':
                if not maintenance.startDate:
                    maintenance.startDate = datetime.now()
            
            # Устанавливаем дату завершения при переходе в "completed"
            if new_status == 'completed':
                maintenance.completeDate = datetime.now()
            
            # Сбрасываем дату завершения при выходе из "completed"
            if new_status != 'completed' and old_status == 'completed':
                maintenance.completeDate = None
        
        if new_description is not None:
            maintenance.description = new_description
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Статус успешно обновлён'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

# Маршрут: Просмотр ТО
@app.route('/maintenance/view/<int:record_id>')
@login_required
def view_maintenance(record_id):
    maintenance = Maintenance.query.options(
        db.joinedload(Maintenance.car),
        db.joinedload(Maintenance.maintenance_type),
        db.joinedload(Maintenance.user)
    ).filter_by(maintenanceID=record_id).first_or_404()
    
    # Проверяем права доступа
    can_edit = current_user.role == 'mechanic' and maintenance.userID == current_user.userID
    
    return render_template('maintenance/view_maintenance.html', 
                         maintenance=maintenance,
                         can_edit=can_edit)
    
# Маршрут: Просмотр типов ТО
@app.route('/maintenance/types')
@login_required
def maintenance_types():
    types = MaintenanceType.query.order_by(MaintenanceType.name).all()
    return render_template('maintenance/maintenance_types.html', types=types, username=current_user.fullName)

# Маршрут: Добавление типов ТО
@app.route('/maintenance/types/add', methods=['GET', 'POST'])
@login_required
def add_maintenance_type():
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form.get('description', '')
            estimated_cost = float(request.form.get('estimated_cost', 0) or 0)
            estimated_duration = float(request.form.get('estimated_duration', 0) or 0)

            new_type = MaintenanceType(
                name=name,
                description=description,
                estimatedCost=estimated_cost,
                estimatedDuration=estimated_duration
            )

            db.session.add(new_type)
            db.session.commit()

            flash('Тип ТО успешно добавлен', 'success')
            return redirect(url_for('maintenance_types'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении: {str(e)}', 'error')

    return render_template('maintenance/add_maintenance_type.html', username=current_user.fullName)

# Маршрут: просмотр типов ТО
@app.route('/maintenance/types/edit/<int:type_id>', methods=['GET', 'POST'])
@login_required
def edit_maintenance_type(type_id):
    maintenance_type = MaintenanceType.query.get_or_404(type_id)

    if request.method == 'POST':
        try:
            maintenance_type.name = request.form['name']
            maintenance_type.description = request.form.get('description', '')
            maintenance_type.estimatedCost = float(request.form.get('estimated_cost', 0) or 0)
            maintenance_type.estimatedDuration = float(request.form.get('estimated_duration', 0) or 0)

            db.session.commit()
            flash('Тип ТО успешно обновлён', 'success')
            return redirect(url_for('maintenance_types'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении: {str(e)}', 'error')

    return render_template('maintenance/edit_maintenance_type.html', type=maintenance_type, username=current_user.fullName)

# Маршрут: Удаление типов То
@app.route('/maintenance/types/delete/<int:type_id>', methods=['POST'])
@login_required
def delete_maintenance_type(type_id):
    try:
        maintenance_type = MaintenanceType.query.get_or_404(type_id)
        db.session.delete(maintenance_type)
        db.session.commit()
        flash('Тип ТО успешно удалён', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении: {str(e)}', 'error')
    
    return redirect(url_for('maintenance_types'))

# Маршрут: добавление ТО
@app.route('/maintenance/add', methods=['GET', 'POST'])
@login_required
def add_maintenance():
    if request.method == 'POST':
        try:
            car_id = int(request.form['car_id'])
            type_id = int(request.form['type_id'])  # ← Убедись, что это так
            priority = request.form['priority']
            user_id = int(request.form['user_id'])  # ← Изменил на 'user_id', как в шаблоне
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            complete_date = None
            if request.form.get('complete_date'):
                complete_date = datetime.strptime(request.form['complete_date'], '%Y-%m-%d').date()
            description = request.form.get('description', '')
            mileage_at_service = int(request.form.get('mileage_at_service', 0) or 0)
            next_service_date = None
            if request.form.get('next_service_date'):
                next_service_date = datetime.strptime(request.form['next_service_date'], '%Y-%m-%d').date()
            next_service_mileage = int(request.form.get('next_service_mileage', 0) or 0)
            status = request.form.get('status', 'planned')

            # Получаем тип работы
            maintenance_type = MaintenanceType.query.get(type_id)
            if not maintenance_type:
                raise ValueError("Тип работы не найден")

            # Автоматически подставляем стоимость
            parts_cost = float(maintenance_type.estimatedCost)
            estimated_duration = float(maintenance_type.estimatedDuration)

            # Рассчитываем стоимость работ (например, 500 ₽ за час)
            LABOR_RATE_PER_HOUR = 500.0
            labor_cost = estimated_duration * LABOR_RATE_PER_HOUR

            # Итоговая стоимость
            total_cost = parts_cost + labor_cost

            # Создаём запись
            new_record = Maintenance(
                carID=car_id,
                typeID=type_id,
                priority=priority,
                userID=user_id,  # ← userID, как в модели
                startDate=start_date,
                completeDate=complete_date,
                description=description,
                partsCost=parts_cost,
                laborCost=labor_cost,
                # totalCost=total_cost,  # ← если totalCost — генерируемое поле, убираем
                mileageAtService=mileage_at_service,
                nextServiceDate=next_service_date,
                nextServiceMileage=next_service_mileage,
                status=status
            )

            db.session.add(new_record)
            db.session.commit()

            flash('Запись ТО успешно добавлена', 'success')
            return redirect(url_for('maintenance_records'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при сохранении: {str(e)}', 'error')

    # Логика для GET-запроса
    vehicles = Car.query.order_by(Car.brand, Car.model).all()
    types = MaintenanceType.query.order_by(MaintenanceType.name).all()
    mechanics = User.query.filter_by(role='mechanic').order_by(User.fullName).all()

    return render_template('maintenance/add_maintenance.html',
                           vehicles=vehicles,  # ← Передаём как vehicles
                           types=types,
                           mechanics=mechanics,
                           username=current_user.fullName)


@app.route('/reminders')
@login_required
def reminders():
    # Получаем параметры фильтрации
    priority = request.args.get('priority', '')
    is_read = request.args.get('is_read', '')
    is_sent = request.args.get('is_sent', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    show_completed = request.args.get('show_completed', 'false').lower() == 'true'

    # Автоматически устанавливаем date_to в сегодняшнюю дату, если не задано И date_from не задано
    if not date_to and not date_from:
        date_to = date.today().strftime('%Y-%m-%d')

    # Параметры сортировки
    sort_by = request.args.get('sort_by', 'remindDate')
    sort_order = request.args.get('sort_order', 'desc')

    # Пагинация
    page = int(request.args.get('page', 1))
    per_page = 10

    # --- НАЧАЛО: Логика для механика ---
    is_mechanic = current_user.role == 'mechanic'
    if is_mechanic:
        # Присоединяем таблицу Maintenance и добавляем условие на userID
        query = db.session.query(Reminder).join(Maintenance).filter(Maintenance.userID == current_user.userID)
        # Фильтр: только не прочитанные (если is_read == 'false'), или все (если is_read == 'true')
        if is_read == 'true':
            query = query.filter(Reminder.isRead == 'true')
        elif is_read == 'false':
            query = query.filter(Reminder.isRead == 'false')

        # Фильтр: только не отправленные (если is_sent == 'false'), или все (если is_sent == 'true')
        if is_sent == 'true':
            query = query.filter(Reminder.isSent == 'true')
        elif is_sent == 'false':
            query = query.filter(Reminder.isSent == 'false')

        # Фильтр: только для незавершенных ТО (если show_completed не true)
        if not show_completed:
            query = query.filter(Maintenance.completeDate.is_(None))
    else:
        # Для не-механиков: используем обычный запрос
        query = db.session.query(Reminder).outerjoin(Maintenance)  # ← Используем outerjoin, чтобы не терять напоминания без ТО
        # Применяем обычные фильтры (для не-механиков is_read из URL используется как есть)
        if is_read == 'true':
            query = query.filter(Reminder.isRead == 'true')
        elif is_read == 'false':
            query = query.filter(Reminder.isRead == 'false')

        # Фильтр: только не отправленные (если is_sent == 'false'), или все (если is_sent == 'true')
        if is_sent == 'true':
            query = query.filter(Reminder.isSent == 'true')
        elif is_sent == 'false':
            query = query.filter(Reminder.isSent == 'false')

        # --- НОВОЕ: Фильтр show_completed для НЕ-механиков ---
        # Применяется к основному запросу для администраторов/менеджеров
        if not show_completed:
            query = query.filter(Maintenance.completeDate.is_(None))

    # --- Обычные фильтры (работают для всех, включая механиков) ---
    if priority:
        query = query.filter(Reminder.priority == priority)
    if date_from:
        query = query.filter(Reminder.remindDate >= date_from)
    if date_to:
        query = query.filter(Reminder.remindDate <= date_to)

    # Проверяем разрешенные столбцы для сортировки
    allowed_sort_columns = ['remindDate', 'priority']
    if sort_by not in allowed_sort_columns:
        sort_by = 'remindDate'

    # Применяем сортировку
    if sort_by == 'remindDate':
        if sort_order == 'asc':
            query = query.order_by(Reminder.remindDate.asc())
        else:
            query = query.order_by(Reminder.remindDate.desc())
    elif sort_by == 'priority':
        if sort_order == 'asc':
            query = query.order_by(Reminder.priority.asc())
        else:
            query = query.order_by(Reminder.priority.desc())
    else:
        if sort_order == 'asc':
            query = query.order_by(Reminder.remindDate.asc())
        else:
            query = query.order_by(Reminder.remindDate.desc())

    # --- ОТЛАДКА: Выводим SQL запрос ---
    print(f"DEBUG: SQL Query (без LIMIT/OFFSET): {query}")
    print(f"DEBUG: SQL Query Parameters: {query.statement.compile().params}") # Параметры запроса

    # Выполняем запрос для подсчета общего количества
    total = query.count()
    print(f"DEBUG: Общее количество после фильтрации: {total}") # Отладка

    # --- НОВОЕ: Используем paginate вместо offset/limit ---
    # Получаем объект пагинации
    reminders_pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False # Не вызывать 404, если page > pages
    )

    # --- Статистика ---
    # Для механика: статистика только по его напоминаниям, с учетом фильтров (прочитано, его ТО, статус ТО)
    if is_mechanic:
        base_stats_query = db.session.query(Reminder).join(Maintenance).filter(Maintenance.userID == current_user.userID)
        stats_query = base_stats_query
        if is_read == 'true':
            stats_query = stats_query.filter(Reminder.isRead == 'true')
        elif is_read == 'false':
            stats_query = stats_query.filter(Reminder.isRead == 'false')
        if not show_completed: # Статистика для механика тоже учитывает его фильтр
             stats_query = stats_query.filter(Maintenance.completeDate.is_(None))
        if is_sent == 'true':
            stats_query = stats_query.filter(Reminder.isSent == 'true')
        elif is_sent == 'false':
            stats_query = stats_query.filter(Reminder.isSent == 'false')
        if date_to:
             stats_query = stats_query.filter(Reminder.remindDate <= date_to)
        if priority:
            stats_query = stats_query.filter(Reminder.priority == priority)

        total_filtered = stats_query.count()
        read_filtered = stats_query.filter(Reminder.isRead == 'true').count()
        not_read_filtered = stats_query.filter(Reminder.isRead == 'false').count()
        high_priority_filtered = stats_query.filter(Reminder.priority == 'high').count()
        critical_priority_filtered = stats_query.filter(Reminder.priority == 'critical').count()

        stats = {
            'total': total_filtered,
            'read': read_filtered,
            'not_read': not_read_filtered,
            'high_priority': high_priority_filtered,
            'critical_priority': critical_priority_filtered
        }
    else: # Статистика для администраторов/менеджеров
        stats_query = db.session.query(Reminder).outerjoin(Maintenance)
        if priority:
            stats_query = stats_query.filter(Reminder.priority == priority)
        if is_read == 'true':
            stats_query = stats_query.filter(Reminder.isRead == 'true')
        elif is_read == 'false':
            stats_query = stats_query.filter(Reminder.isRead == 'false')
        if is_sent == 'true':
            stats_query = stats_query.filter(Reminder.isSent == 'true')
        elif is_sent == 'false':
            stats_query = stats_query.filter(Reminder.isSent == 'false')
        if date_from:
            stats_query = stats_query.filter(Reminder.remindDate >= date_from)
        if date_to:
            stats_query = stats_query.filter(Reminder.remindDate <= date_to)

        # --- НОВОЕ: Фильтр show_completed для статистики НЕ-механиков ---
        if not show_completed:
            stats_query = stats_query.filter(Maintenance.completeDate.is_(None))

        stats = {
            'total': total,
            'read': stats_query.filter(Reminder.isRead == 'true').count(),
            'not_read': stats_query.filter(Reminder.isRead == 'false').count(),
            'high_priority': stats_query.filter(Reminder.priority == 'high').count(),
            'critical_priority': stats_query.filter(Reminder.priority == 'critical').count()
        }

    return render_template('reminders/reminders.html',
                           reminders=reminders_pagination,
                           stats=stats,
                           type_filter='', # Убрано
                           priority=priority,
                           is_read=is_read,
                           is_sent=is_sent,
                           date_from=date_from,
                           date_to=date_to,
                           show_completed=show_completed,
                           sort_by=sort_by,
                           sort_order=sort_order
                           )

# Маршрут: Просмотр напоминания
@app.route('/reminder/view/<int:reminder_id>')
@login_required
def view_reminder(reminder_id):
    reminder = Reminder.query.filter_by(reminderID=reminder_id).first()
    
    if not reminder:
        flash('Напоминание не найдено', 'error')
        return redirect(url_for('reminders'))
    
    return render_template('reminders/view_reminder.html', reminder=reminder, username=current_user.fullName)

# Маршрут: Отметить напоминание как прочитанное
@app.route('/reminders/mark_read/<int:reminder_id>', methods=['POST'])
@login_required
def mark_as_read(reminder_id):
    reminder = Reminder.query.filter_by(reminderID=reminder_id).first()
    
    if not reminder:
        return {'success': False, 'error': 'Напоминание не найдено'}

    # Проверка роли пользователя
    if current_user.role != 'mechanic':
        return {'success': False, 'error': 'Недостаточно прав для выполнения этого действия'}

    # Отмечаем как прочитанное
    reminder.isRead = 'true'

    try:
        db.session.commit()
        return {'success': True}
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при сохранении напоминания: {e}")
        return {'success': False, 'error': 'Ошибка при сохранении изменений'}

# Маршрут: Редактирование напоминания
@app.route('/reminder/edit/<int:reminder_id>', methods=['GET', 'POST'])
@login_required
def edit_reminder(reminder_id):
    reminder = Reminder.query.filter_by(reminderID=reminder_id).first()
    
    if not reminder:
        flash('Напоминание не найдено', 'error')
        return redirect(url_for('reminders'))
    
    if request.method == 'POST':
        try:
            reminder.priority = request.form['priority']
            reminder.remindDate = datetime.strptime(request.form['remind_date'], '%Y-%m-%d').date() if request.form['remind_date'] else None
            reminder.message = request.form['message']
            
            db.session.commit()
            flash('Напоминание обновлено', 'success')
            return redirect(url_for('view_reminder', reminder_id=reminder_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении: {str(e)}', 'error')
    
    return render_template('reminders/edit_reminder.html', reminder=reminder, username=current_user.fullName)

# Маршрут: Удаление напоминания
@app.route('/reminder/delete/<int:reminder_id>', methods=['POST'])
@login_required
def delete_reminder(reminder_id):
    try:
        reminder = Reminder.query.filter_by(reminderID=reminder_id).first()
        if reminder:
            db.session.delete(reminder)
            db.session.commit()
            flash('Напоминание успешно удалено!', 'success')
        else:
            flash('Напоминание не найдено!', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении напоминания: {str(e)}', 'error')
    
    return redirect(url_for('reminders'))



# Маршрут: Главная страница отчетов
@app.route('/reports')
@login_required
def reports():
    # Получаем список всех автомобилей для фильтра
    cars = Car.query.order_by(Car.brand, Car.model).all()
    
    # Собираем статистику
    total_cars = db.session.query(db.func.count(Car.CarID)).scalar()
    active_cars = db.session.query(db.func.count(Car.CarID)).filter(Car.status == 'Active').scalar()
    maintenance_cars = db.session.query(db.func.count(Car.CarID)).filter(Car.status == 'Maintenance').scalar()
    retired_cars = db.session.query(db.func.count(Car.CarID)).filter(Car.status == 'Retired').scalar()

    # Статистика по приоритетам ТО (это то, что тебе не хватало!)
    priority_stats = {
        'critical': db.session.query(db.func.count(Maintenance.maintenanceID)).filter(Maintenance.priority == 'critical').scalar(),
        'high': db.session.query(db.func.count(Maintenance.maintenanceID)).filter(Maintenance.priority == 'high').scalar(),
        'medium': db.session.query(db.func.count(Maintenance.maintenanceID)).filter(Maintenance.priority == 'medium').scalar(),
        'low': db.session.query(db.func.count(Maintenance.maintenanceID)).filter(Maintenance.priority == 'low').scalar()
    }

    # Статистика по типам ТО
    maintenance_types_stats = []
    types = MaintenanceType.query.all()
    for mt in types:
        count = db.session.query(db.func.count(Maintenance.maintenanceID)).filter(Maintenance.typeID == mt.typeID).scalar()
        total_cost = db.session.query(db.func.sum(Maintenance.totalCost)).filter(Maintenance.typeID == mt.typeID).scalar() or 0.0
        maintenance_types_stats.append((mt.name, count, total_cost))

    # Статистика по механикам
    mechanic_stats = []
    mechanics = User.query.filter_by(role='mechanic').all()
    for mech in mechanics:
        count = db.session.query(db.func.count(Maintenance.maintenanceID)).filter(Maintenance.userID == mech.userID).scalar()
        total_cost = db.session.query(db.func.sum(Maintenance.totalCost)).filter(Maintenance.userID == mech.userID).scalar() or 0.0
        mechanic_stats.append((mech.fullName, count, total_cost))

    # Общая стоимость всех работ
    total_cost = db.session.query(db.func.sum(Maintenance.totalCost)).scalar() or 0.0

    # Создаем словарь stats, который передадим в шаблон
    stats = {
        'cars': cars,
        'total_cars': total_cars,
        'active_cars': active_cars,
        'maintenance_cars': maintenance_cars,
        'retired_cars': retired_cars,
        'total_maintenance': db.session.query(db.func.count(Maintenance.maintenanceID)).scalar(),
        'total_cost': total_cost,
        'priority_stats': priority_stats,  # <-- Вот он! Ключ, которого не хватало!
        'maintenance_types_stats': maintenance_types_stats,
        'mechanic_stats': mechanic_stats
    }

    return render_template('reports/reports.html', stats=stats, active_report='dashboard')

# Маршрут: Генерация отчёта
@app.route('/reports/generate', methods=['POST'])
@login_required
def generate_report_handler():
    data = request.get_json()
    report_type = data.get('report_type')
    date_from = data.get('date_from') or None # Преобразуем пустую строку в None
    date_to = data.get('date_to') or None
    car_id = data.get('car_id')

    # Для отчета "История работ по автомобилю"
    if report_type == 'car_history':
        if not car_id:
            return jsonify({'success': False, 'error': 'Необходимо выбрать автомобиль для отчета "История работ по автомобилю".'}), 400

        try:
            # Вызов хранимой процедуры
            sql_call = text("CALL GetCarHistoryReport(:car_id, :date_from, :date_to)")
            result = db.session.execute(sql_call, {
                'car_id': int(car_id),
                'date_from': date_from,
                'date_to': date_to
            })

            # Получаем результат
            columns = list(result.keys())
            rows = result.fetchall()
            result_data = [dict(zip(columns, row)) for row in rows]

            return jsonify({'success': True, 'rows': result_data})

        except Exception as e:
            print(f"Ошибка при выполнении процедуры GetCarHistoryReport: {e}")
            return jsonify({'success': False, 'error': 'Ошибка выполнения запроса отчета.'}), 500

    # Для отчета "Производительность механиков"
    elif report_type == 'mechanic_performance':
        # Проверка обязательных параметров
        if not date_from or not date_to:
            return jsonify({'success': False, 'error': 'Для отчета "Производительность механиков" необходимо указать даты начала и окончания периода.'}), 400

        try:
            # Вызов хранимой процедуры
            sql_call = text("CALL GetMechanicPerformanceReport(:date_from, :date_to)")
            result = db.session.execute(sql_call, {
                'date_from': date_from,
                'date_to': date_to
            })

            # Получаем результат
            columns = list(result.keys())
            rows = result.fetchall()
            result_data = [dict(zip(columns, row)) for row in rows]

            return jsonify({'success': True, 'rows': result_data})

        except Exception as e:
            print(f"Ошибка при выполнении процедуры GetMechanicPerformanceReport: {e}")
            return jsonify({'success': False, 'error': 'Ошибка выполнения запроса отчета.'}), 500
        
    # Для отчета "Журнал работ"
    elif report_type == 'maintenance_log':
        if not date_from or not date_to:
            return jsonify({'success': False, 'error': 'Для отчета "Журнал работ" необходимо указать даты начала и окончания периода.'}), 400

        try:
            sql_call = text("CALL GetMaintenanceLogReport(:date_from, :date_to)")
            result = db.session.execute(sql_call, {
                'date_from': date_from,
                'date_to': date_to
            })

            columns = list(result.keys())
            rows = result.fetchall()
            result_data = [dict(zip(columns, row)) for row in rows]

            return jsonify({'success': True, 'rows': result_data})

        except Exception as e:
            print(f"Ошибка при выполнении процедуры GetMaintenanceLogReport: {e}")
            return jsonify({'success': False, 'error': 'Ошибка выполнения запроса отчета.'}), 500
        
    # Для отчета "Затраты за период"
    elif report_type == 'costs_by_period':
        if not date_from or not date_to:
            return jsonify({'success': False, 'error': 'Для отчета "Затраты за период" необходимо указать даты начала и окончания периода.'}), 400

        try:
            print(f"Выполняется процедура GetCostsByPeriodMonthlyReport с параметрами: date_from={date_from}, date_to={date_to}")
            sql_call = text("CALL GetCostsByPeriodMonthlyReport(:date_from, :date_to)")
            result = db.session.execute(sql_call, {
                'date_from': date_from,
                'date_to': date_to
            })

            # Получаем все строки
            rows = result.mappings().all()
            print(f"Получено {len(rows)} строк")

            # Группируем данные по категориям
            maintenance_data = {}
            repairs_data = {}

            for row in rows:
                row_dict = dict(row)
                category = row_dict.get('category')
                month_year = row_dict.get('month_year')
                total_cost = float(row_dict.get('total_cost', 0))

                if category == 'Maintenance':
                    maintenance_data[month_year] = total_cost
                elif category == 'Repairs':
                    repairs_data[month_year] = total_cost

            # Получаем список всех месяцев (уникальные значения из обоих словарей)
            all_months = sorted(set(list(maintenance_data.keys()) + list(repairs_data.keys())))

            # Вычисляем итоговые суммы
            total_maintenance_cost = sum(maintenance_data.values())
            total_repair_cost = sum(repairs_data.values())
            total_cost = total_maintenance_cost + total_repair_cost

            # Формируем ответ
            response_data = {
                'success': True,
                'rows': [{
                    'total_maintenance_cost': total_maintenance_cost,
                    'total_repair_cost': total_repair_cost,
                    'total_cost': total_cost,
                    'months': all_months,
                    'maintenance_data': maintenance_data,
                    'repairs_data': repairs_data
                }]
            }

            print("Ответ подготовлен успешно")
            return jsonify(response_data)

        except Exception as e:
            error_msg = f"Ошибка при выполнении процедуры GetCostsByPeriodMonthlyReport: {str(e)}"
            print(error_msg)
            return jsonify({'success': False, 'error': error_msg}), 500
        
    elif report_type == 'fleet_summary':
        try:
            # Вызов хранимой процедуры
            sql_call = text("CALL GetFleetSummaryReport()")
            result = db.session.execute(sql_call)

            # Получаем результат
            columns = list(result.keys())
            rows = result.fetchall()
            result_data = [dict(zip(columns, row)) for row in rows]

            return jsonify({'success': True, 'rows': result_data})

        except Exception as e:
            print(f"Ошибка при выполнении процедуры GetFleetSummaryReport: {e}")
            return jsonify({'success': False, 'error': 'Ошибка выполнения запроса отчета.'}), 500

    # Если тип отчета не поддерживается
    else:
        return jsonify({'success': False, 'error': f'Тип отчета "{report_type}" не поддерживается.'}), 400

# Маршрут: Отчёт история автомобиля
@app.route('/reports/car_history')
@login_required
def report_car_history():
    # Получи список автомобилей
    cars = Car.query.order_by(Car.brand, Car.model).all()
    # Передай его в шаблон как часть 'stats' или отдельно
    # В шаблоне car_history.html используем stats.cars
    stats = {'cars': cars} # Создаём минимальный 'stats' только для списка автомобилей
    return render_template('reports/car_history.html', stats=stats, active_report='car_history')

# Маршрут: Отчёт производительность механиков
@app.route('/reports/mechanic_performance')
@login_required
def report_mechanic_performance():
    # Получаем список механиков
    mechanics = User.query.filter_by(role='mechanic').order_by(User.fullName).all()
    stats = {'mechanics': mechanics}
    return render_template('reports/mechanic_performance.html', stats=stats, active_report='mechanic_performance')

# Маршрут: Отчёт история ТО
@app.route('/reports/maintenance_log')
@login_required
def report_maintenance_log():
    # Для этого отчёта нам не нужен список автомобилей, поэтому передаём пустой stats
    stats = {}
    return render_template('reports/maintenance_log.html', stats=stats, active_report='maintenance_log')

# Маршрут: Отчёт затраты за период
@app.route('/reports/costs_by_period')
@login_required
def report_costs_by_period():
    # Для этого отчёта нам не нужен список автомобилей, поэтому передаём пустой stats
    stats = {}
    return render_template('reports/costs_by_period.html', stats=stats, active_report='costs_by_period')

# Маршрут: Отчёт систематизация
@app.route('/reports/fleet_summary')
@login_required
def report_fleet_summary():
    # Заглушка: рендерит базовый шаблон с сообщением
    # Или реализуй логику получения сводки по автопарку
    return render_template('reports/fleet_summary.html', active_report='fleet_summary')


# Маршрут: Ручной запуск автосоздания напоминания
@app.route('/admin/reminders/generate-manual', methods=['POST'])
@login_required
def generate_reminders_manual():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Доступ запрещен'})
    
    try:
        create_daily_reminders()  # Функция, которую ты уже создал
        return jsonify({'success': True, 'message': 'Напоминания созданы успешно'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

# Маршрут: Админ панель
@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Доступ запрещен! Требуются права администратора.', 'error')
        return redirect(url_for('dashboard'))
    
    # Статистика системы
    total_users = db.session.query(db.func.count(User.userID)).scalar()
    total_cars = db.session.query(db.func.count(Car.CarID)).scalar()
    total_maintenance = db.session.query(db.func.count(Maintenance.maintenanceID)).scalar()
    total_reminders = db.session.query(db.func.count(Reminder.reminderID)).scalar()
    
    # Активные пользователи
    active_users = db.session.query(db.func.count(User.userID)).filter(User.isBlocked == 'false').scalar()
    blocked_users = db.session.query(db.func.count(User.userID)).filter(User.isBlocked == 'true').scalar()
    
    # Последние действия
    recent_activities = []
    
    stats = {
        'total_users': total_users,
        'total_cars': total_cars,
        'total_maintenance': total_maintenance,
        'total_reminders': total_reminders,
        'active_users': active_users,
        'blocked_users': blocked_users
    }
    
    return render_template('admin/admin.html', 
                         username=current_user.fullName,
                         stats=stats)


# Маршрут: Верификация ФИО
@app.route('/admin/verify-fullname')
@login_required
def admin_verify_fullname():
    if current_user.role != 'admin':
        flash('Доступ запрещен! Требуются права администратора.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('admin/verify_fullname.html', 
                         username=current_user.fullName)

# API маршрут для получения данных с внешнего сервера
@app.route('/api/get-fullname')
@login_required
def get_fullname():
    if current_user.role != 'admin':
        return {'error': 'Доступ запрещен'}, 403
    
    try:
        response = requests.get('http://prb.sylas.ru/TransferSimulator/fullName', timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Добавляем результаты проверки
        verification_results = verify_fullname(data.get('value', ''))
        
        return {
            'success': True,
            'data': data,
            'verification': verification_results
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }, 500

def verify_fullname(full_name):
    """Функция проверки ФИО"""
    if not full_name or not isinstance(full_name, str):
        return {
            'received_data': False,
            'format_check': False,
            'cyrillic_check': False,
            'capital_letters_check': False,
            'error': 'Неверный формат данных'
        }
    
    # Проверка формата (три части)
    parts = re.split(r'\s+', full_name.strip())
    format_check = len(parts) == 3
    
    # Проверка только кириллицы
    cyrillic_regex = re.compile(r'^[а-яёА-ЯЁ\s]+$')
    cyrillic_check = cyrillic_regex.match(full_name.strip()) is not None
    
    # Проверка заглавных букв
    capital_letters_check = all(part and part[0] == part[0].upper() for part in parts)
    
    return {
        'received_data': True,
        'full_name': full_name,
        'format_check': format_check,
        'cyrillic_check': cyrillic_check,
        'capital_letters_check': capital_letters_check,
        'parts': parts
    }
    
# Маршрут: Админ панель создание напоминаний
@app.route('/admin/reminders/generate', methods=['POST'])
@login_required
def generate_reminders():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Доступ запрещен'})
    
    try:
        create_daily_reminders()
        return jsonify({'success': True, 'message': 'Напоминания созданы успешно'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

# Маршрут: Админ панель пользователи
@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.order_by(User.fullName).all()
    return render_template('admin/admin_users.html', 
                         users=users, 
                         username=current_user.fullName)

# Маршрут: Админ панель просмотр пользователя
@app.route('/admin/user/<int:user_id>')
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/view_user.html', user=user, current_user_obj=current_user)

# Маршрут: Админ панель блокировка пользователя
@app.route('/admin/user/<int:user_id>/toggle_block', methods=['POST'])
@login_required
def toggle_user_block(user_id):
    if current_user.role != 'admin':
        return {'success': False, 'error': 'Доступ запрещен'}
    
    user = User.query.filter_by(userID=user_id).first()
    if user:
        user.isBlocked = 'true' if user.isBlocked == 'false' else 'false'
        if user.isBlocked == 'false':
            user.blockedUntil = None
        db.session.commit()
        return {'success': True}
    return {'success': False, 'error': 'Пользователь не найден'}

# Маршрут: Админ панель удаление пользователя
@app.route('/admin/user/delite/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return {'success': False, 'error': 'Доступ запрещен'}
    
    user = User.query.filter_by(userID=user_id).first()
    if user and user.userID != current_user.userID:  # Не позволяем удалить самого себя
        try:
            db.session.delete(user)
            db.session.commit()
            return {'success': True}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    return {'success': False, 'error': 'Пользователь не найден или нельзя удалить себя'}

# Маршрут: Админ панель редактирование пользователя
@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            user.fullName = request.form['full_name']
            user.mail = request.form['email']
            user.phone = request.form.get('phone') or None
            user.role = request.form['role']
            user.isBlocked = request.form['is_blocked']
            
            db.session.commit()
            flash('Данные пользователя успешно обновлены!', 'success')
            return redirect(url_for('view_user', user_id=user.userID))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении данных пользователя: {str(e)}', 'error')
    
    return render_template('admin/edit_user.html', user=user, current_user_obj=current_user)

# Маршрут: Админ бэкап
@app.route('/admin/backup')
def admin_backup():
    backups = get_backup_list()
    return render_template('admin/admin_backup.html', backups=backups)

def extract_date_from_filename(filename):
    # Ищем дату в формате YYYYMMDD_HHMMSS
    match = re.search(r'(\d{8})_(\d{6})', filename)
    if match:
        date_str = match.group(1)  # YYYYMMDD
        time_str = match.group(2)  # HHMMSS
        # Форматируем в YYYY-MM-DD HH:MM:SS
        formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
        return datetime.strptime(formatted, '%Y-%m-%d %H:%M:%S')
    return None

def get_backup_list():
    # Проверяем, нужно ли создать автоматический бэкап за сегодня
    ensure_daily_auto_backup()

    backup_pattern = os.path.join(BACKUP_DIR, "*.sql")
    backup_files = glob.glob(backup_pattern)
    backups = []
    for f in backup_files:
        try:
            stat = os.stat(f)
            size = stat.st_size
            if size == 0:
                print(f"Предупреждение: бэкап {filename_base} имеет размер 0 байт — возможно, он пустой или поврежден.")
                continue  # Пропускаем этот файл

            # Получаем дату из имени файла
            filename_base = os.path.basename(f)
            mtime = extract_date_from_filename(filename_base)

            if mtime is None:
                print(f"Не удалось извлечь дату из файла: {filename_base}, используем дату модификации")
                mtime = datetime.fromtimestamp(stat.st_mtime)

            # Вычисляем разницу в днях
            now = datetime.now()
            days_old = int((now - mtime).total_seconds() // (24 * 3600))

            is_too_recent = days_old < 7
            is_favorite = filename_base in load_favorites()

            # Определяем тип бэкапа из имени файла
            is_auto = filename_base.startswith('auto_')
            source_label = "Автоматически" if is_auto else "Вручную"

            # Подсчёт таблиц и INSERT-записей
            tables = 0
            inserts = 0
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                    for line in file:
                        if 'CREATE TABLE' in line.upper():
                            tables += 1
                        elif 'INSERT INTO' in line.upper():
                            inserts += 1
            except Exception as e:
                print(f"Ошибка при чтении файла {f}: {e}")

            # Сохраняем исходное время для сортировки
            backups.append({
                'name': filename_base,
                'size': size,
                'date_str': mtime.strftime('%d.%m.%Y %H:%M:%S'),  # Для отображения
                'date_obj': mtime,                                # Для сортировки
                'days_old': days_old,
                'is_too_recent': is_too_recent,
                'is_favorite': is_favorite,
                'source_label': source_label,
                'tables': tables,
                'inserts': inserts
            })
        except Exception as e:
            print(f"Ошибка при обработке бэкапа {f}: {e}")
            continue

    # Сортируем по объекту datetime (корректно!)
    backups.sort(key=lambda x: x['date_obj'], reverse=True)

    return backups

# Маршрут: Админ логика создания бэкапа
@app.route('/admin/backup/create', methods=['POST'])
def create_backup():
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"manual_backup_{timestamp}.sql"
        filepath = os.path.join(BACKUP_DIR, filename)

        db_config = get_db_config()

        # Команда mysqldump
        cmd = [
            'mysqldump',
            f"--host={db_config['host']}",
            f"--port={db_config['port']}",
            f"--user={db_config['user']}",
            f"--password={db_config['password']}",
            '--single-transaction',
            '--routines',
            '--triggers',
            db_config['database']
        ]

        with open(filepath, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, check=False)

        if result.returncode != 0:
            # Если ошибка — удаляем файл и возвращаем сообщение
            if os.path.exists(filepath):
                os.remove(filepath)
            error_msg = result.stderr.strip() or "Неизвестная ошибка при создании бэкапа."
            return jsonify({"success": False, "message": error_msg}), 500

        # Успешно создано
        return jsonify({
            "success": True,
            "message": f"Бэкап успешно создан: {filename}",
            "filename": filename
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

# Маршрут: Админ удаление бэкапа
@app.route('/admin/backup/delete', methods=['POST'])
def delete_backup():
    data = request.get_json()
    filename = data.get('filename')
    filepath = os.path.join(BACKUP_DIR, filename)

    if not os.path.exists(filepath):
        return jsonify({"success": False, "message": "Файл не найден."}), 404

    # Получаем время последнего изменения файла
    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
    days_old = (datetime.now() - mtime).days if (datetime.now() - mtime).days >= 0 else 0

    if days_old < 7:
        return jsonify({
            "success": False,
            "message": f"Нельзя удалить бэкап, ему всего {days_old} дней. Минимальный срок хранения — 7 дней."
        }), 400

    try:
        os.remove(filepath)
        return jsonify({"success": True, "message": f"Файл {filename} удалён."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
# Маршрут: Админ скачивание бэкапа
@app.route('/admin/backup/download/<filename>')
@login_required
def download_backup(filename):
    filepath = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"success": False, "message": "Файл не найден."}), 404
    return send_from_directory(BACKUP_DIR, filename, as_attachment=True)

# Маршрут: Админ добавление/удаление бэкапа из избранного
@app.route('/admin/backup/toggle-favorite', methods=['POST'])
@login_required
def toggle_favorite_backup():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({"success": False, "message": "Не указан файл."}), 400

    toggle_favorite(filename)
    return jsonify({"success": True, "message": "Статус избранного изменён."})


# Маршрут: Настройки
@app.route('/settings')
@login_required
def settings():
    # Получаем статистику системы
    total_cars = db.session.query(db.func.count(Car.CarID)).scalar()
    total_maintenance = db.session.query(db.func.count(Maintenance.maintenanceID)).scalar()
    total_reminders = db.session.query(db.func.count(Reminder.reminderID)).scalar()
    total_users = db.session.query(db.func.count(User.userID)).scalar()
    
    stats = {
        'total_cars': total_cars,
        'total_maintenance': total_maintenance,
        'total_reminders': total_reminders,
        'total_users': total_users
    }
    
    # Получаем информацию о системе
    system_info = get_system_info()
    
    return render_template('settings/general.html', 
                         username=current_user.fullName,
                         current_user_obj=current_user,
                         stats=stats,
                         system_info=system_info)

# Маршрут: Настройки профиля
@app.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile_settings():
    if request.method == 'POST':
        try:
            current_user.fullName = request.form['full_name']
            current_user.mail = request.form['email']
            current_user.phone = request.form['phone']
            
            db.session.commit()
            flash('Профиль успешно обновлен!', 'success')
            return redirect(url_for('profile_settings'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении профиля: {str(e)}', 'error')
    
    return render_template('settings/profile.html', 
                         username=current_user.fullName,
                         current_user_obj=current_user)

# Маршрут: Настройки пароля
@app.route('/settings/password', methods=['GET', 'POST'])
@login_required
def password_settings():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Проверяем старый пароль
        old_password_hash = hashlib.md5(old_password.encode('utf-8')).hexdigest()
        if current_user.passwordHash != old_password_hash:
            flash('Неверный старый пароль!', 'error')
            return render_template('settings/security.html', 
                                 username=current_user.fullName,
                                 current_user_obj=current_user)
        
        # Проверяем совпадение новых паролей
        if new_password != confirm_password:
            flash('Новые пароли не совпадают!', 'error')
            return render_template('settings/security.html', 
                                 username=current_user.fullName,
                                 current_user_obj=current_user)
        
        # Проверяем длину пароля
        if len(new_password) < 6:
            flash('Пароль должен содержать не менее 6 символов!', 'error')
            return render_template('settings/security.html', 
                                 username=current_user.fullName,
                                 current_user_obj=current_user)
        
        try:
            # Обновляем пароль
            current_user.passwordHash = hashlib.md5(new_password.encode('utf-8')).hexdigest()
            current_user.passwordDate = datetime.now()
            
            db.session.commit()
            flash('Пароль успешно изменен!', 'success')
            return redirect(url_for('password_settings'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при изменении пароля: {str(e)}', 'error')
    
    return render_template('settings/security.html', 
                         username=current_user.fullName,
                         current_user_obj=current_user)

# Маршрут: Системная информация
@app.route('/system-info')
@login_required
def system_info_page():
    system_info = get_system_info()
    return render_template('system/system_info.html', 
                         username=current_user.fullName,
                         system_info=system_info)

# Маршрут: Информация о сайте
@app.route('/about')
def about():
    system_info = get_system_info()
    return render_template('system/about.html', 
                         username=current_user.fullName if current_user.is_authenticated else None,
                         system_info=system_info)

# Маршрут: Помощь
@app.route('/help')
def help():
    return render_template('system/help.html', username=current_user.fullName if current_user.is_authenticated else None)

# Маршрут: Контакты
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Обработка отправки формы обратной связи
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Здесь можно добавить логику отправки сообщения
        # Пока просто покажем сообщение об успехе
        flash('Ваше сообщение успешно отправлено. Администрация свяжется с вами в ближайшее время.', 'success')
        return redirect(url_for('contact'))
    
    # Получаем всех администраторов
    admin_users = User.query.filter_by(role='admin').all()
    return render_template('system/contact.html', 
                         username=current_user.fullName if current_user.is_authenticated else None,
                         admin_users=admin_users)

# Маршрут: Для установки флага прохождения капчи в сессии
@app.route('/login/captcha_passed', methods=['POST'])
def captcha_passed():
    try:
        # Получаем порядок из JSON-тела запроса (отправляется из JS)
        data = request.get_json()
        captcha_order_str = data.get('captcha_order', '')
        captcha_order = [int(x) for x in captcha_order_str.split(',') if x.isdigit()] if captcha_order_str else []

        # Проверяем, совпадает ли порядок с правильным
        correct_order = [1, 2, 3, 4]
        if captcha_order == correct_order:
            # Устанавливаем флаг в сессии
            session['captcha_passed'] = True
            print("DEBUG: captcha_passed set to True via AJAX") # Лог
            return {'success': True}, 200
        else:
            # Неправильный порядок, не устанавливаем флаг
            print("DEBUG: captcha_passed AJAX received wrong order") # Лог
            return {'success': False, 'error': 'Неправильный порядок'}, 400

    except Exception as e:
        print(f"DEBUG: captcha_passed AJAX error: {e}") # Лог
        return {'success': False, 'error': 'Внутренняя ошибка сервера'}, 500


# Маршрут: Вход в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("DEBUG: Session ID = ", session.get('_id'))
    print("DEBUG: Full session = ", dict(session))
    # Проверяем, прошла ли капча в текущей сессии
    captcha_passed = session.get('captcha_passed', False)
    print("DEBUG: captcha_passed in session =", captcha_passed)

    # Генерируем случайный порядок для частей капчи, если капча не пройдена
    parts_order = list(range(1, 5))
    if not captcha_passed:
        random.shuffle(parts_order)

    if request.method == 'POST':
        # Проверяем, отправлена ли форма логина/пароля
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username and password:
            # Капча уже должна быть пройдена
            if not captcha_passed:
                flash('Сначала пройдите проверку безопасности.', 'error')
                print("DEBUG: captcha not passed, returning captcha form")
                return render_template('auth/login.html', captcha_passed=False, parts_order=parts_order) # Путь к шаблону

            print("DEBUG: captcha passed, checking login/password")
            # Проверяем логин и пароль
            password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

            # Проверяем, заблокирован ли пользователь временно
            blocked_user = User.query.filter(
                User.username == username,
                User.blockedUntil > datetime.now()
            ).first()
            if blocked_user and blocked_user.blockedUntil:
                flash(f'Аккаунт заблокирован до {blocked_user.blockedUntil.strftime("%d.%m.%Y %H:%M")}', 'error')
                return render_template('auth/login.html', captcha_passed=True, parts_order=parts_order) # Путь к шаблону

            # Проверяем логин и пароль
            user = User.query.filter(
                User.username == username,
                User.passwordHash == password_hash
            ).first()

            if user and user.isBlocked == 'false':
                # Успешный вход
                user.loginAttempts = 0
                user.lastLoginAttempt = None
                user.blockedUntil = None
                db.session.commit()
                session.permanent = False
                login_user(user, remember=False)
                return redirect(url_for('dashboard'))
            else:
                # Неудачная попытка — только если пользователь существует
                user = User.query.filter_by(username=username).first()
                if user:
                    user.loginAttempts = (user.loginAttempts or 0) + 1
                    user.lastLoginAttempt = datetime.now()
                    if user.loginAttempts >= 3:
                        if not user.blockedUntil:
                            blocked_until = datetime.now() + timedelta(minutes=15)
                            user.blockedUntil = blocked_until
                            db.session.commit()
                            flash(f'Аккаунт заблокирован на 15 минут! Попробуйте позже.', 'error')
                        else:
                            user.isBlocked = 'true'
                            user.blockedUntil = None
                            db.session.commit()
                            flash('Аккаунт заблокирован навсегда!', 'error')
                    else:
                        flash(f'Неверный логин или пароль! Попытка {user.loginAttempts} из 3', 'error')
                else:
                    # Если пользователя не существует — просто показываем ошибку
                    flash('Неверный логин или пароль!', 'error')
                db.session.commit()
                # Капча уже пройдена, не требуем снова
                return render_template('auth/login.html', captcha_passed=True, parts_order=parts_order)

        # Если отправлена капча (а не логин/пароль)
        else:
            if not captcha_passed:
                captcha_order_str = request.form.get('captcha_order', '')
                captcha_order = [int(x) for x in captcha_order_str.split(',') if x.isdigit()] if captcha_order_str else []
                correct_order = [1, 2, 3, 4]
                if captcha_order != correct_order:
                    flash('Проверка безопасности не пройдена. Попробуйте снова.', 'error')
                    return render_template('auth/login.html', captcha_passed=False, parts_order=parts_order)

                # Если капча пройдена, сохраняем это в сессии
                session['captcha_passed'] = True
                print("DEBUG: captcha_passed set to True")
                print("DEBUG: Full session after setting captcha_passed = ", dict(session))
                captcha_passed = True
                # Перезапускаем процесс ввода логина/пароля
                parts_order = list(range(1, 5))
                return render_template('auth/login.html', captcha_passed=True, parts_order=parts_order)

    return render_template('auth/login.html', captcha_passed=captcha_passed, parts_order=parts_order)

# Маршрут: Выход из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



# Допы

# добавление встроенных функций Python min и max в глобальную область видимости шаблонов Jinja2
app.jinja_env.globals.update(min=min, max=max)


# Глобальная переменная для доступа к информации о системе из любого шаблона
@app.context_processor
def inject_system_info():

    return dict(system_info=get_system_info())


# Загрузка выгрузка пользователя из системы для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.query.filter_by(userID=int(user_id)).first()
        if user:
            return user
        return None
    except Exception as e:
        print(f"Error loading user: {e}")
        return None



# Планировщик для всех задач
scheduler = BackgroundScheduler()

# Задача: ежедневный бэкап в 8:00
scheduler.add_job(
    func=scheduled_backup,
    trigger=CronTrigger(hour=8, minute=0),
    id='daily_backup',
    name='Создание ежедневного резервного копирования в 8:00 утра',
    replace_existing=True
)

# Задача: ежедневные напоминания в 8:05
scheduler.add_job(
    func=create_daily_reminders,
    trigger=CronTrigger(hour=8, minute=5),
    id='daily_reminders',
    name='Создание ежедневных напоминаний',
    replace_existing=True
)

scheduler.start()

# Проверка пропущенных задач при запуске (для бэкапа и напоминаний)
ensure_daily_auto_backup()
create_daily_reminders()

# Убедимся, что планировщик останавливается при завершении приложения
atexit.register(lambda: scheduler.shutdown())



# Запрет запуска в качестве модуля, только напрямую
if __name__ == '__main__':
    app.run(debug=True)
