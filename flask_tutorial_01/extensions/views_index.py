#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, render_template, redirect, url_for, flash
from werkzeug.wrappers import Response

from sqlalchemy.sql import func

from ..main import app, db
from ..forms.message import MessageForm
from ..models.message import Message


# ===== Interface =====

def render_ext(template_name_or_list, default=None, message="", format=None, **context):
    format = format or request.values.get('format')

    result = "success"
    if isinstance(message, tuple):
        message, result = message

#     if format == 'json':
#         return jsonify(dict(
#             result = result,
#             message = message,
#             **context
#         ))

    if message:
        flash(message, result or "success")

    if isinstance(default, Response) and not format:
        return default

    return "No template defined!" if not template_name_or_list else \
        render_template(template_name_or_list,
            modal = format == 'modal',
            **context
        )


# ===== Routes =====

@app.route("/", methods=['GET', 'POST'])
def messages():
    if not db.engine.dialect.has_table(db.engine, "messages"):
        db.create_all()

    return render_template("message/messages.html",
        messages = db.session.query(Message).filter_by(deleted=False).limit(15).all(),
        total = db.session.query(func.count(Message.id)).filter_by(deleted=False).scalar(),
    )


@app.route("/add", methods=['GET', 'POST'])
def message_add():
    form = MessageForm(request.form)

    if request.method == 'POST':
        if form.validate():
            message = Message(
                author = form.author.data,
                message = form.message.data,
            )
            db.session.add(message)
            db.session.commit()

            return render_ext("base.html",
                default = redirect(url_for('messages')),
                message = "The message successfully added!",
            )

        else:
            return render_ext("message/add_edit.html",
                default = redirect(url_for('messages')),
                message = ("Please check your data entered!", "warning"),
                caption = "Add a message",
                form = form,
            )

    return render_ext("message/add_edit.html",
        caption = "Add a message",
        form = form,
    )


@app.route("/edit", methods=['GET', 'POST'])
def message_edit():
    id = request.values.get('id')
    message = db.session.query(Message).filter_by(id=id, deleted=False).first()

    if not message:
        return render_ext("base.html",
            default = redirect(url_for('messages')),
            message = ("The message not found or deleted!", "warning"),
        )

    form = MessageForm(request.form, message, "Update")

    if request.method == 'POST':
        if form.validate():
            message.author = form.author.data
            message.message = form.message.data
            db.session.commit()

            return render_ext("message/add_edit.html",
                default = redirect(url_for('messages')),
                message = "The message successfully updated!",
                caption = "Edit the message",
                form = form,
            )

        else:
            return render_ext("message/add_edit.html",
                default = redirect(url_for('messages')),
                message = ("Please check your data entered!", "warning"),
                caption = "Edit the message",
                form = form,
            )

    return render_ext("message/add_edit.html",
        caption = "Edit the message",
        form = form,
    )


@app.route("/delete", methods=['GET', 'POST'])
def message_delete():
    id = request.values.get('id')
    message = db.session.query(Message).filter_by(id=id, deleted=False).first()

    if not message:
        return render_ext("base.html",
            default = redirect(url_for('messages')),
            message = ("The message not found or deleted!", "warning"),
        )

    message.deleted = True
    db.session.commit()

    return render_ext("base.html",
        default = redirect(url_for('messages')),
        message = ("The message successfully deleted!", "dark"),
    )
