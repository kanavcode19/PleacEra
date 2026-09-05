from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(200),
        nullable=False
    )

    branch = db.Column(
        db.String(50)
    )

    graduation_year = db.Column(
        db.Integer
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    experiences = db.relationship(
        "Experience",
        backref="senior",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Company(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    placements = db.relationship(
        "Placement",
        backref="company",
        lazy=True,
        cascade="all, delete-orphan"
    )

    experiences = db.relationship(
        "Experience",
        backref="company",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Placement(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_name = db.Column(
        db.String(100),
        nullable=False
    )

    branch = db.Column(
        db.String(50),
        nullable=False
    )

    package = db.Column(
        db.Float,
        nullable=False
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=False
    )


class Experience(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    experience = db.Column(
        db.Text,
        nullable=False
    )

    year = db.Column(
        db.Integer
    )

    senior_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=False
    )

    questions = db.relationship(
        "Question",
        backref="experience",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Question(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    question = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=False
    )

    experience_id = db.Column(
        db.Integer,
        db.ForeignKey("experience.id"),
        nullable=False
    )