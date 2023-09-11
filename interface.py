from operator import itemgetter
from tkinter import Tk, ttk

from db.crud import add_type, get_freezer, get_fridge, get_total, get_types
from db.database import SessionLocal, create_db


class Interface:
    def __init__(self, root: Tk) -> None:
        self.session = SessionLocal()

        self.root = root
        self.root.title('База мяса')
        self.root.minsize(900, 600)
        self.root.geometry('900x600')
        self.root.protocol('WM_DELETE_WINDOW', self.shutdown)

        notebook = ttk.Notebook()
        notebook.pack(expand=True, fill='both')

        self.types = ttk.Frame(notebook)
        self.total = ttk.Frame(notebook)
        self.fridge = ttk.Frame(notebook)
        self.freezer = ttk.Frame(notebook)

        self.types.pack(fill='both', expand=True)
        self.total.pack(fill='both', expand=True)
        self.fridge.pack(fill='both', expand=True)
        self.freezer.pack(fill='both', expand=True)

        notebook.add(self.types, text='Виды мяса')
        notebook.add(self.total, text='Всё мясо')
        notebook.add(self.fridge, text='В холодильнике')
        notebook.add(self.freezer, text='В морозильнике')

        self._list_types()
        self._list_total()
        self._list_fridge()
        self._list_freezer()

        add_button = ttk.Button(self.types,
                                text='Добавить вид мяса',
                                command=self._open_adding_window)
        add_button.pack(anchor='s', fill='both')

    def run(self):
        create_db()
        self.root.mainloop()

    def shutdown(self):
        self.session.close()
        self.root.destroy()

    def _list_data(self,
                   data: list[tuple],
                   columns: tuple[str],
                   parent: callable) -> None:
        all_cols = {
            'amount': 'Количество',
            'count_per_one': 'Количество на одну порцию',
            'name': 'Название'
        }

        labels = itemgetter(*columns)(all_cols)
        tree = ttk.Treeview(parent,
                            columns=columns,
                            show='headings')
        tree.heading(0, text=labels[0], anchor='w')
        tree.heading(1, text=labels[1], anchor='w')

        tree.pack(fill='both', expand=True)

        for row in data:
            tree.insert('', 'end', values=(row[0], row[1]))

    def _list_types(self) -> None:
        data = get_types(self.session)
        columns = ('name', 'count_per_one')
        self._list_data(data, columns, self.types)

    def _list_total(self) -> None:
        data = get_total(self.session)
        columns = ('name', 'amount')
        self._list_data(data, columns, self.total)

    def _list_fridge(self) -> None:
        data = get_fridge(self.session)
        columns = ('name', 'amount')
        self._list_data(data, columns, self.fridge)

    def _list_freezer(self) -> None:
        data = get_freezer(self.session)
        columns = ('name', 'amount')
        self._list_data(data, columns, self.freezer)

    def _open_adding_window(self):
        adding_window = Tk()
        adding_window.title('Добавить вид мяса')
        adding_window.geometry('600x400')
        adding_window.minsize(600, 400)

        @staticmethod
        def _create_frame(label_text):
            frame = ttk.Frame(master=adding_window,
                              borderwidth=1,
                              relief='solid',
                              padding=(8, 10))
            label = ttk.Label(frame, text=label_text)
            label.pack(anchor='nw')

            return frame

        def send_data():
            type_name = type_entry.get()
            count_per_one = count_entry.get()

            add_type(self.session, (type_name, count_per_one))

            adding_window.destroy()

        type_frame = _create_frame('Введите название вида')
        type_entry = ttk.Entry(type_frame)
        type_entry.pack(anchor='nw')
        type_frame.pack(anchor='nw', fill='x', padx=5, pady=5)

        count_frame = _create_frame('Введите количество на порцию')
        count_entry = ttk.Entry(count_frame)
        count_entry.pack(anchor='nw')
        count_frame.pack(anchor='nw', fill='x', padx=5, pady=5)

        add_type_button = ttk.Button(adding_window,
                                     text='Добавить',
                                     command=send_data)
        add_type_button.pack(anchor='nw')


if __name__ == '__main__':
    root = Tk()
    ui = Interface(root=root)
    ui.run()
