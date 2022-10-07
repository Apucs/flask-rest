from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from tensorboard import summary

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)

class TodoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    summary = db.Column(db.String(500))


# with app.app_context():
#     db.create_all()
#     print("DB created")


# todos = {
#     1: {
#         "task": "Write hello world program",
#         "summary":"write the code using python"
#     },
#     2: {
#         "task": "Task 2",
#         "summary":"writing task 2"
#     },
#     3: {
#         "task": "Task 3",
#         "summary":"writing task 3"
#     }
# }

task_post_args = reqparse.RequestParser()
task_post_args.add_argument("task", type=str, help="Task is required", required=True)
task_post_args.add_argument("summary", type=str, help="Summary is required", required=True)

task_put_args = reqparse.RequestParser()
task_put_args.add_argument("task", type=str)
task_put_args.add_argument("summary", type=str)


resource_fields = {
    'id': fields.Integer,
    'task': fields.String,
    'summary': fields.String
}

class ToDoList(Resource):
    def get(self):
        tasks = TodoModel.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"task": task.task, "summary": task.summary}

        return todos
    # def get(self):
    #     return todos

class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        task = TodoModel.query.filter_by(id=todo_id).first()

        if not task:
            abort(404, message="Could not find task with that id")
        
        return task

    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        task = TodoModel.query.filter_by(id=todo_id).first()
        if task:
            abort(409, message="Task id taken...")

        todo = TodoModel(id=todo_id, task=args['task'], summary=args['summary'])

        db.session.add(todo)
        db.session.commit()
        return todo, 201

    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_put_args.parse_args()

        task = TodoModel.query.filter_by(id=todo_id).first()

        if not task:
            abort(404, message="Task doesn't exist, cannot update")

        if args['task']:
            task.task = args['task']
        if args['summary']:
            task.summary = args['summary']
        db.session.commit()

        return task

        # if todo_id not in todos:
        #     abort(404, message="Task doesn't exist, cannot update")
        
        # if args["task"]:
        #     todos[todo_id]["task"] = args["task"]
        
        # if args["summary"]:
        #     todos[todo_id]["summary"] = args["summary"]

        # return todos[todo_id], 201

    @marshal_with(resource_fields)
    def delete(self, todo_id):
        task = TodoModel.query.filter_by(id=todo_id).first()

        if not task:
            abort(404, message="Task doesn't exist, cannot delete")
        
        db.session.delete(task)
        db.session.commit()
        return 'Todo Deleted', 204
        # del todos[todo_id]
        # return todos, 204


api.add_resource(ToDo, '/todos/<int:todo_id>')
api.add_resource(ToDoList, '/todos')

if __name__ == '__main__':
    app.run(debug=True, port=4000)