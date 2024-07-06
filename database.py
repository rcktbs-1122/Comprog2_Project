import sqlite3
class Database:
    def __init__(self):
        self.con = sqlite3.connect('todo.db')
        self.cursor = self.con.cursor()
        self.create_task_table()

    def create_task_table(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks(id integer PRIMARY KEY AUTOINCREMENT, task varcahr(50) NOT NULL, due_date varchar(50), completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)))")


    def create_task(self, task, due_date=None):
        self.cursor.execute("INSERT INTO tasks(task, due_date, completed) VALUES(?, ?, ?)", (task, due_date, 0))
        self.con.commit()

        # Getting the last entered item to add in the list
        created_task = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE task = ? and completed = 0",
                                           (task,)).fetchall()
        return created_task[-1]

    def get_tasks(self, sort_option='task', order='ASC'):
        if sort_option == 'task':
            query = f"SELECT id, task, due_date FROM tasks WHERE completed = 0 ORDER BY task {order}"
        elif sort_option == 'due_date':
            query = f"SELECT id, task, due_date FROM tasks WHERE completed = 0 ORDER BY due_date {order}"
        else:
            query = "SELECT id, task, due_date FROM tasks WHERE completed = 0"

        incomplete_tasks = self.cursor.execute(query).fetchall()

        complete_tasks = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE completed = 1").fetchall()

        return incomplete_tasks, complete_tasks

    def mark_task_as_complete(self, taskid):
        self.cursor.execute("UPDATE tasks SET completed=1 WHERE id=?", (taskid,))
        self.con.commit()

    def mark_task_as_incomplete(self, taskid):
        self.cursor.execute("UPDATE tasks SET completed=0 WHERE id=?", (taskid,))
        self.con.commit()

        task_text = self.cursor.execute("SELECT task FROM tasks WHERE id=?", (taskid,)).fetchall()
        return task_text[0][0]

    def delete_task(self, taskid):
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (taskid,))
        self.con.commit()

    def close_db_connection(self):
        self.con.close()

