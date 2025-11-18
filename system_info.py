"""
Файл с информацией о системе, версиях и зависимостях
"""
import platform
import sys
from datetime import datetime

# Основная информация о системе
SYSTEM_INFO = {
    'name': 'Верса',
    'version': '0.2.0',
    'full_name': 'Система управления автотранспортом "Верса"',
    'description': 'Современная система управления автотранспортом, разработанная для эффективного контроля за техническим состоянием транспортных средств, планирования технического обслуживания и управления механиками.',
    'development_status': 'alpha',
    'release_date': 'xxxx-xx-xx',
    'last_update': '2025-11-18',
    'license': 'Proprietary',
    'author': 'Шлегель Виктор Алексеевич',
    'company': 'Верса',
    'website': 'https://versa-system.ru',
    'support_email': 'support@versa-system.ru',
    'documentation_url': 'https://docs.versa-system.ru',
    'api_url': 'https://api.versa-system.ru'
}

# Информация о версиях технологий
TECHNOLOGY_VERSIONS = {
    'python': sys.version,
    'flask': '2.3.3',
    'sqlalchemy': '2.0.21',
    'mysql': '8.0+',
    'pymysql': '1.1.0',
    'flask_login': '0.6.3',
    'flask_sqlalchemy': '3.0.5',
    'jinja2': '3.1.2',
    'werkzeug': '2.3.7',
    'chartjs': '4.4.0',
    'font_awesome': '6.0.0',
    'apscheduler': '3.10.4',
    'requests': '2.31.0'
}

# Информация о зависимостях
DEPENDENCIES = [
    'Flask==2.3.3',
    'Flask-Login==0.6.3',
    'Flask-SQLAlchemy==3.0.5',
    'PyMySQL==1.1.0',
    'SQLAlchemy==2.0.21',
    'Werkzeug==2.3.7',
    'Jinja2==3.1.2',
    'python-dotenv==1.0.0',
    'APScheduler==3.10.4',
    'requests==2.31.0'
]

# Информация о модулях системы
MODULES = {
    'vehicles': {
        'name': 'Управление транспортом',
        'version': '0.1.1',
        'description': 'Модуль для управления автомобилями, их статусами и информацией'
    },
    'maintenance': {
        'name': 'Техническое обслуживание',
        'version': '0.1.1',
        'description': 'Модуль для планирования и отслеживания технического обслуживания'
    },
    'reminders': {
        'name': 'Напоминания',
        'version': '0.1.0',
        'description': 'Модуль для автоматического создания и управления напоминаниями'
    },
    'users': {
        'name': 'Управление пользователями',
        'version': '0.1.0',
        'description': 'Модуль для управления пользователями и ролями'
    },
    'reports': {
        'name': 'Отчеты',
        'version': '1.0.1',
        'description': 'Модуль для генерации отчетов и аналитики'
    },
    'admin': {
        'name': 'Администрирование',
        'version': '0.1.1',
        'description': 'Модуль администрирования системы с функцией проверки внешних данных'
    },
    'settings': {
        'name': 'Настройки',
        'version': '0.1.1',
        'description': 'Модуль настроек пользователя и системы'
    },
    'backup': {
        'name': 'Резервное копирование',
        'version': '0.1.1',
        'description': 'Модуль автоматического резервного копирования данных'
    },
    'external_api':{
        'name': 'Внешнее API',
        'version': '0.1.0',
        'description': 'Модуль для взаимодействия с внешними серверами и проверки данных'
    }
}

# Информация о системных требованиях
SYSTEM_REQUIREMENTS = {
    'os': platform.system(),
    'os_version': platform.release(),
    'architecture': platform.architecture()[0],
    'processor': platform.processor(),
    'python_version': sys.version_info,
    'memory': 'Не менее 2 ГБ RAM',
    'disk_space': 'Не менее 500 МБ свободного места',
    'database': 'MySQL 8.0+ или совместимая база данных',
    'scheduler': 'APScheduler для автоматических задач',
    'network': 'Доступ к интернету для проверки внешних данных'
}

# Информация о лицензировании
LICENSE_INFO = {
    'type': 'Proprietary License',
    'usage': 'Коммерческое использование',
    'distribution': 'Закрытый исходный код',
    'support': 'Платная техническая поддержка',
    'updates': 'Регулярные обновления'
}

def get_system_info():
    """Возвращает всю информацию о системе"""
    return {
        'system': SYSTEM_INFO,
        'technology_versions': TECHNOLOGY_VERSIONS,
        'dependencies': DEPENDENCIES,
        'modules': MODULES,
        'requirements': SYSTEM_REQUIREMENTS,
        'license': LICENSE_INFO
    }

def get_version():
    """Возвращает текущую версию системы"""
    return SYSTEM_INFO['version']

def get_system_name():
    """Возвращает название системы"""
    return SYSTEM_INFO['name']

def get_full_name():
    """Возвращает полное название системы"""
    return SYSTEM_INFO['full_name']

def get_release_date():
    """Возвращает дату релиза"""
    return SYSTEM_INFO['release_date']

def get_last_update():
    """Возвращает дату последнего обновления"""
    return SYSTEM_INFO['last_update']