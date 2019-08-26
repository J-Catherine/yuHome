from flask import render_template, request, redirect, url_for, abort, current_app
from . import notebook
from ..models import Post, Notebook, Comment
from ..main.forms import NoteSearchForm


@notebook.route('/<name>')
def book(name):
    notebooks = Notebook.query.all()
    notebook = Notebook.query.filter_by(name=name).first()
    if notebook == None:
        abort(404)
    notes = Post.query.filter_by(notebook_id=notebook.id).order_by(Post.id.asc())
    return render_template('notebook/notebook.html', notebook=notebook, notebooks=notebooks, notes=notes)


@notebook.route('/<bookname>/<notename>')
def note_html(bookname, notename):
    notebooks = Notebook.query.all()
    return render_template('notes/' + bookname + '/' + notename + '.html', notebooks=notebooks)


@notebook.route('notes/<keywords>', methods=['Get', 'Post'])
def search(keywords):
    notebooks = Notebook.query.all()
    search = NoteSearchForm()
    if search.validate_on_submit():
        return redirect(url_for('notebook.search', keywords=search.title.data))
    keywords = keywords.split(',')
    posts = Post.query.all()
    notes = []
    for key in keywords:
        for post in posts:
            if post.title != None and key in post.title and post not in notes:
                notes.append(post)
    print(keywords)
    return render_template('notebook/search.html', search=search, notebooks=notebooks, keywords=keywords, notes=notes)
