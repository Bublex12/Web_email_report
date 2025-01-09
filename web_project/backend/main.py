from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, '../frontend/src/templates')


app = Flask(__name__, template_folder=template_dir)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:a241411-=96@localhost/bet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Модель для отчетов
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sql_code = db.Column(db.Text, nullable=False)
    recipients = db.Column(db.Text, nullable=False)  # Храним как строку (через запятую)
    cron_schedule = db.Column(db.String(100), nullable=False)

    def __init__(self, name, sql_code, recipients, cron_schedule):
        self.name = name
        self.sql_code = sql_code
        self.recipients = recipients
        self.cron_schedule = cron_schedule

# Схема для сериализации/десериализации
class ReportSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'sql_code', 'recipients', 'cron_schedule')

report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)

# HTML страница для создания отчета
@app.route('/')
def index():
    return render_template('index.html')

# Роуты API
@app.route('/reports', methods=['POST'])
def add_report():
    name = request.form['name']
    sql_code = request.form['sql_code']
    recipients = request.form['recipients']
    cron_schedule = request.form['cron_schedule']

    new_report = Report(name, sql_code, recipients, cron_schedule)
    db.session.add(new_report)
    db.session.commit()

    return jsonify({"message": "Report created successfully"})

@app.route('/reports', methods=['GET'])
def get_reports():
    all_reports = Report.query.all()
    return reports_schema.jsonify(all_reports)


@app.route('/list-files', methods=['GET'])
def list_files():
    project_dir = os.path.dirname(os.path.abspath(__file__))  # Текущая директория проекта
    files_structure = []

    for root, dirs, files in os.walk(project_dir):
        relative_path = os.path.relpath(root, project_dir)
        files_structure.append({
            "folder": relative_path,
            "subfolders": dirs,
            "files": files
        })

    return jsonify(files_structure)

@app.route('/reports/<id>', methods=['GET'])
def get_report(id):
    report = Report.query.get(id)
    return report_schema.jsonify(report)

@app.route('/reports/<id>', methods=['PUT'])
def update_report(id):
    report = Report.query.get(id)

    report.name = request.json['name']
    report.sql_code = request.json['sql_code']
    report.recipients = request.json['recipients']
    report.cron_schedule = request.json['cron_schedule']

    db.session.commit()
    return report_schema.jsonify(report)

@app.route('/reports/<id>', methods=['DELETE'])
def delete_report(id):
    report = Report.query.get(id)
    db.session.delete(report)
    db.session.commit()

    return jsonify({"message": "Report deleted successfully"})


# Точка входа
if __name__ == '__main__':
    # Создание базы данных
    with app.app_context():
        db.create_all()
    app.run(debug=True)

