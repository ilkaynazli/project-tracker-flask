"""A web application for tracking projects, students, and student grades."""

from flask import Flask, request, render_template

import hackbright

app = Flask(__name__)

@app.route("/student-search")
def get_student_form():
    """Show form for searching for a student"""

    return render_template("student_search.html")

@app.route("/student")
def get_student():
    """Show information about a student."""

    github = request.args.get('github')

    # import pdb; pdb.set_trace()

    first, last, github = hackbright.get_student_by_github(github)

    rows = hackbright.get_grades_by_github(github)

    print(rows)

    return render_template("student_info.html", 
                            first=first,
                            last=last,
                            github=github,
                            grades=rows)


@app.route('/project_info')
def ask_for_project_name():
    """Display a form to get a project name"""

    return render_template("projects.html")


@app.route('/project')
def display_projects():
    """Displays the project information"""

    project_title = request.args.get("title")
    project_info = hackbright.get_project_by_title(project_title.title())

    return render_template("project_info.html", project=project_info)


@app.route("/new_student")
def new_student_form():
    """Display the form for adding a new student"""
    
    return render_template("new_student.html")


@app.route("/add_student", methods=['POST'])
def add_new_student():
    """Add a new student info to students database"""

    first_name = request.form.get('fname')
    last_name = request.form.get('lname')
    github = request.form.get('github')

    hackbright.make_new_student(first_name, last_name, github)

    return render_template("new_student_added.html", 
                            first=first_name, 
                            last=last_name,
                            github=github)







if __name__ == "__main__":
    hackbright.connect_to_db(app)
    app.run(debug=True)

