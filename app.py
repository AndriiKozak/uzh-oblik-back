from flask import Flask, request, abort
from http import HTTPStatus
from user import user_manager, authenticate_user
from item import item_manager
from  norm import norm_manager, ObligationDto
from serviceman import serviceman_manager
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from decouple import config
from db import db, ranks, officer_ranks
from flask_cors import CORS
from datetime import timedelta, datetime

datetime_format = "%d.%m.%Y %H:%M:%S"
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return user_manager.get_by_id(user_id)


app = Flask(__name__)
app.secret_key = config("secret_key", "009e5686fbe6267253fa2c0acfae50f6c4b1e0ae3e12184b101d461f32e49b7e")
login_manager.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{config('db_password')}@{config('db_host', '3.71.13.232')}:{config('db_port', '5432')}/uzh"
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
db.init_app(app)
#TODO fix security issue
CORS(app)

with app.app_context():
    db.create_all()

@login_manager.unauthorized_handler
def unauthorized():
    abort(HTTPStatus.UNAUTHORIZED)


@app.route('/users', methods=['POST'])
def authenticate():
    username = request.json.get('username')
    password = request.json.get('password')
    user = user_manager.get_by_id(username)
    if authenticate_user(user, password):
        login_user(user, remember=True)
        return {'username': username, 'password': password}, HTTPStatus.FOUND
    else:
        abort(HTTPStatus.UNAUTHORIZED)


@app.route("/users", methods=['PUT'])
@login_required
def create_user():
    if not current_user.is_admin:
        abort(HTTPStatus.UNAUTHORIZED)
    username = request.json.get('username')
    password = request.json.get('password')
    is_admin = request.json.get('is_admin')
    if username == current_user.get_id():
        abort(HTTPStatus.UNAUTHORIZED)
    user_manager.create_user(username, password, is_admin)
    return {'username': username, 'password': password, "is_admin": is_admin}, HTTPStatus.CREATED


@app.route("/serviceman", methods=['PUT'])
# @login_required
def create_serviceman():
    name = request.json.get('name')
    surname = request.json.get('surname')
    patronymic = request.json.get("patronymic")
    sex = bool(request.json.get('sex'))
    rank = int(request.json.get('rank'))
    group = str(request.json.get('group'))
    id = serviceman_manager.create_service_man(name, surname, patronymic, sex, rank, group)
    return {'id': id}, HTTPStatus.CREATED


@app.route("/serviceman/<id>", methods=['get'])
def get_serviceman(id):
    serviceman = serviceman_manager.get_by_id(id)
    return serviceman.to_dict()

@app.route("/serviceman/<id>/obligation")
def get_serviceman_obligations(id):
    serviceman = serviceman_manager.get_by_id(id)
    norms = norm_manager.get_potential_norms(serviceman)
    obligations = norm_manager.get_obligations(serviceman, norms)
    result = [obligation.to_dict() for item_obligations in obligations.values() for obligation in item_obligations]
    return result

@app.route("/serviceman", methods=['get'])
def get_servicemen():
    return [serviceman.to_dict() for serviceman in serviceman_manager.get_all()]


@app.route("/item", methods=['PUT'])
def create_item():
    name = request.json.get('name')
    returnable = bool(request.json.get('returnable'))
    #term = int(request.json.get('term')) # days
    id = item_manager.create_item(name, returnable, 0)
    return {"id": id}, HTTPStatus.CREATED


@app.route("/item/<id>", methods=['get'])
def get_item(id):
    item = item_manager.get_by_id(id)
    return item.to_dict()


@app.route("/item", methods=['get'])
def get_items():
    return [item.to_dict() for item in item_manager.get_all()]


@app.route("/serviceman/<serviceman_id>/item/<item_id>", methods=['PUT'])
def issue_item(serviceman_id, item_id):
    date = datetime.strptime(request.json.get('date'), "%d.%m.%Y %H:%M:%S")
    size = request.json.get("size")
    serviceman = serviceman_manager.get_by_id(serviceman_id)
    item = item_manager.get_by_id(item_id)
    granted = datetime.now()
    id = serviceman_manager.issue_item(serviceman, item, size, date, granted)
    return {"id": id}, HTTPStatus.CREATED


@app.route("/requirements", methods=['GET'])
def requirements():
    to_date = datetime.strptime(request.args.get("to"), "%Y-%m-%d")
    staff = serviceman_manager.get_all()
    norms = list(norm_manager.get_all())
    obligations = [norm_manager.get_obligations(serviceman, norms, to_date) for serviceman in staff]
    return item_manager.get_requirements(obligations)


"""
@app.route("/norm/draft", methods=['PUT'])
def create_draft():
    return {"draft_id": 42}
"""


@app.route("/norm", methods=['PUT'])
def create_norm():
    genders = request.json.get("genders")
    from_rank = request.json.get("from_rank")
    to_rank = request.json.get("to_rank")
    name = request.json.get("name")
    reason = request.json.get("reason")
    from_date = request.json.get("from")
    to_date = request.json.get("to")
    id = norm_manager.create_norm(genders, from_rank, to_rank, name, reason, from_date, to_date)
    return {"id": id}, HTTPStatus.CREATED


@app.route("/norm/<norm_id>/group", methods=['PUT'])
def create_norm_group(norm_id):
    name = request.json.get("name")
    obligations = [ObligationDto(jobligation["item_id"], jobligation["count"], jobligation["term"]) for jobligation in request.json.get("items")]
    norm_manager.add_group(norm_id, name, obligations)
    return {}, HTTPStatus.CREATED


# отримати всі норми
@app.route("/norm", methods=['GET'])
def get_all_norms():
    return [norm.to_dict() for norm in norm_manager.get_all()]


@app.route("/norm/<norm_id>", methods=['GET'])
def get_norm(norm_id):
    return norm_manager.get_norm(norm_id).to_dict()

"""
@app.route("/group/<group_id>/item", methods=['PUT'])
def add_item(group_id):
    item_id = request.json.get("item_id")
    term = request.json.get("term")
    quantity = request.json.get("quantity")
    return {id: 42}
"""


@app.route("/logout")
@login_required
def logout():
    logout_user()


@app.route("/authorised")
@login_required
def hello_authorised():
    return f"hello {current_user.get_id}"


@app.route("/hello")
def hello():
    return "hello CI/CD!"


@app.route("/ranks", methods=['GET'])
def all_ranks():
    return list(ranks[::-1]+officer_ranks[::-1])

@app.route("groups", method=['GET'])
def all_groups():
    return norm_manager.get_groups()

def test():
    with app.app_context():
        # user_manager.create_user("test", "test", True)
        kozak_id = serviceman_manager.create_service_man("Козак", "Андрій", "Володимирович", True, 13, "друга група")
        from datetime import datetime
        norm_id = norm_manager.create_norm([False, True], 10, 13, "польова форма", "наказ 66 від 19 ДБЯ",
                                           datetime.strptime("2023-11-28", "%Y-%m-%d"), None)
        t_shirt_id = item_manager.create_item("Фуфайка", False)
        t_shirt = item_manager.get_by_id(t_shirt_id)
        norm_manager.add_group(norm_id, "друга група", [ObligationDto(t_shirt_id, 365, 2)])
        kozak = serviceman_manager.get_by_id(kozak_id)
        norms = list(norm_manager.get_potential_norms(kozak))
        issue_date = norm_manager.get_obligations(kozak, norms, datetime.strptime("2025-11-28", "%Y-%m-%d"))[t_shirt_id][0].date
        serviceman_manager.issue_item(kozak, t_shirt, "XXL", issue_date, datetime.now(), 1)
        print(norm_manager.get_obligations(kozak, norms, datetime.strptime("2025-11-28", "%Y-%m-%d")))


if __name__ == '__main__':
    is_test = config("test", False, cast=bool)
    if is_test:
        test()
    else:
        app.run(host='0.0.0.0')
