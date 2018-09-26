"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

def get_all_projects():
    """Gets a list of project titles from database"""

    db_cursor = db.session.execute("SELECT title FROM projects")
    projects = db_cursor.fetchall()

    return projects


def get_all_students():
    """Gets a list of student github usernames from database"""

    db_cursor = db.session.execute("SELECT github FROM students")
    students = db_cursor.fetchall()

    return students


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a GitHub account name, print info about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})

    row = db_cursor.fetchone()

    print("Student: {} {}\nGitHub account: {}" .format(row[0], row[1], row[2]))

    return row


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """

    QUERY = """
        INSERT INTO students (first_name, last_name, github)
          VALUES (:first_name, :last_name, :github)
        """

    db.session.execute(QUERY, {'first_name': first_name,
                               'last_name': last_name,
                               'github': github})
    db.session.commit()

    print("Successfully added student: {} {}" .format(first_name, last_name))

def make_new_project(title, description, max_grade):
    """Add a new project and print confirmation.

    Given a title, description and maximum grade, add project to the
    database and print a confirmation message.
    """

    QUERY = """
        INSERT INTO projects (title, description, max_grade)
          VALUES (:title, :description, :max_grade)
        """

    db.session.execute(QUERY, {'title' : title,
                                'description' : description,
                                'max_grade' : max_grade})
    db.session.commit()

    print("Successfully added project: {} {} {}" 
            .format(title, description, max_grade))



def get_project_by_title(title):
    """Given a project title, print information about the project."""

    QUERY = """
        SELECT title, description, max_grade
        FROM projects
        WHERE title = :title
        """

    db_cursor = db.session.execute(QUERY, {'title': title})

    row = db_cursor.fetchone()

    print("Title: {}\nDescription: {}\nMax Grade: {}" 
        .format(row[0], row[1], row[2]))

    return row


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""

    QUERY = """
        SELECT grade
        FROM grades
        WHERE student_github = :github
          AND project_title = :title
        """

    db_cursor = db.session.execute(QUERY, {'github': github, 'title': title})

    row = db_cursor.fetchone()

    print("Student {} in project {} received grade of {}"
        .format(github, title, row[0]))

    return row


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""

    QUERY_INSERT = """
        INSERT INTO grades (student_github, project_title, grade)
          VALUES (:github, :title, :grade)
        """
    QUERY_UPDATE = """
        UPDATE grades SET grade=:grade 
        WHERE student_github = :github AND project_title= :title"""

    existing_grade = get_grade_by_github_title(github, title)
    if existing_grade[0] is not None:
        db.session.execute(QUERY_UPDATE, {'github': github,
                                            'title': title,
                                            'grade': grade})
        db.session.commit()
    else:
        db.session.execute(QUERY_INSERT, {'github': github,
                                               'title': title,
                                               'grade': grade})

        db.session.commit()

    print("Successfully assigned grade of {} for {} in {}"
        .format(grade, github, title))


def get_grades_by_github(github):
    """Get a list of all grades for a student by their github username"""

    QUERY = """
        SELECT project_title, grade
        FROM grades
        WHERE student_github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})

    rows = db_cursor.fetchall()

    for row in rows:
        print("Student {} received grade of {} for {}"
            .format(github, row[1], row[0]))

    return rows


def get_grades_by_title(title):
    """Get a list of all student grades for a project by its title"""

    QUERY = """
        SELECT student_github, grade
        FROM grades
        WHERE project_title = :title
        """

    db_cursor = db.session.execute(QUERY, {'title': title})

    rows = db_cursor.fetchall()

    for row in rows:
        print("Student {} received grade of {} for {}"
            .format(row[0], row[1], title))

    return rows


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received
    as a command.
    """

    command = None

    while command != "quit":
        input_string = input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args  # unpack!
            make_new_student(first_name, last_name, github)

        elif command == "project":
            title = args[0]
            get_project_by_title(title)

        elif command == "grade":
            github, title = args
            get_grade_by_github_title(github, title)

        elif command == "assign_grade":
            github, title, grade = args
            assign_grade(github, title, grade)

        elif command == "student_grades":
            github = args[0]
            get_grades_by_github(github)

        elif command == "project_grades":
            title = args[0]
            get_grades_by_title(title)


if __name__ == "__main__":
    connect_to_db(app)

    handle_input()

    # To be tidy, we'll close our database connection -- though, since this
    # is where our program ends, we'd quit anyway.

    db.session.close()
