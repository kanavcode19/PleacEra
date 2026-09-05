from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for
)

from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models import (
    db,
    User,
    Company,
    Placement,
    Experience,
    Question
)


app = Flask(__name__)




app.config["SECRET_KEY"] = "placement-insights-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///placement.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False




db.init_app(app)




login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))




@app.route("/")
def home():

    return render_template(
        "placement_stats.html"
    )




@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if current_user.is_authenticated:

        if current_user.role == "senior":
            return redirect(
                url_for("senior_dashboard")
            )

    if request.method == "POST":

        email = request.form.get("email")

        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            login_user(user)

            if user.role == "senior":

                return redirect(
                    url_for("senior_dashboard")
                )

            return "Admin dashboard coming soon"

        return render_template(
            "login.html",
            error="Invalid email or password"
        )

    return render_template("login.html")




@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )




@app.route("/senior/dashboard")
@login_required
def senior_dashboard():

    if current_user.role != "senior":

        return "Unauthorized", 403

    experiences = Experience.query.filter_by(
        senior_id=current_user.id
    ).all()

    return render_template(
        "senior/dashboard.html",
        experiences=experiences
    )



@app.route("/placement-stats")
def placement_stats():

    company_name = request.args.get(
        "company",
        ""
    ).strip()

    companies = []

    placements = []

    if company_name:

        companies = Company.query.filter(
            Company.name.ilike(
                f"%{company_name}%"
            )
        ).all()

        if len(companies) == 1:

            placements = Placement.query.filter_by(
                company_id=companies[0].id
            ).all()

    return render_template(
        "student/placement_stats.html",
        companies=companies,
        placements=placements,
        company_name=company_name
    )



@app.route("/company/<int:company_id>")
def company_page(company_id):

    company = Company.query.get_or_404(
        company_id
    )

    placements = Placement.query.filter_by(
        company_id=company.id
    ).all()

    experiences = Experience.query.filter_by(
        company_id=company.id
    ).all()

    questions = Question.query.filter_by(
        company_id=company.id
    ).all()

    # Group questions by category

    grouped_questions = {}

    for question in questions:

        category = question.category

        if category not in grouped_questions:

            grouped_questions[category] = []

        grouped_questions[category].append(
            question
        )

    return render_template(
        "student/company.html",
        company=company,
        placements=placements,
        experiences=experiences,
        grouped_questions=grouped_questions
    )



with app.app_context():

    db.create_all()



if __name__ == "__main__":

    app.run(debug=True)