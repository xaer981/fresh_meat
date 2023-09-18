from operator import itemgetter
from tkinter import Menu, Tk, ttk

from db.crud import (add_amount, add_type, get_freezer, get_fridge, get_total,
                     get_types, get_types_names)
from db.database import SessionLocal, create_db


class Interface:
    def __init__(self, root: Tk) -> None:
        create_db()
        self.session = SessionLocal()

        # root
        self.root = root
        self.root.title('База мяса')
        self.root.minsize(900, 600)
        self.root.geometry('900x600')
        self.root.protocol('WM_DELETE_WINDOW', self.shutdown)
        self.root.option_add('*tearOff', False)

        # menu
        main_menu = Menu()
        edit_menu = Menu()
        settings_menu = Menu()

        edit_menu.add_command(label='Добавить мясо в базу',
                              command=self._open_amount_adding_window)
        edit_menu.add_command(label='Изменить количество в базе')

        settings_menu.add_command(label='Добавить вид мяса',
                                  command=self._open_type_adding_window)
        settings_menu.add_command(label='Изменить существующий вид мяса')

        main_menu.add_cascade(label='Внести изменения в базу', menu=edit_menu)
        main_menu.add_cascade(label='Настройки', menu=settings_menu)

        self.root.config(menu=main_menu)

        # notebook
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

        # list data from DB
        self._list_all()

    def run(self):
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

        return tree

    def _list_types(self) -> None:
        data = get_types(self.session)
        columns = ('name', 'count_per_one')
        self.types_tree = self._list_data(data, columns, self.types)

    def _list_total(self) -> None:
        data = get_total(self.session)
        columns = ('name', 'amount')
        self.total_tree = self._list_data(data, columns, self.total)

    def _list_fridge(self) -> None:
        data = get_fridge(self.session)
        columns = ('name', 'amount')
        self.fridge_tree = self._list_data(data, columns, self.fridge)

    def _list_freezer(self) -> None:
        data = get_freezer(self.session)
        columns = ('name', 'amount')
        self.freezer_tree = self._list_data(data, columns, self.freezer)

    def _list_all(self) -> None:
        self._list_types()
        self._list_total()
        self._list_fridge()
        self._list_freezer()

    def _open_type_adding_window(self):
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
            label.pack(anchor='center')

            return frame

        def send_data_and_update():
            type_name = type_entry.get()
            count_per_one = int(count_spinbox.get())

            add_type(self.session, {'name': type_name,
                                    'count_per_one': count_per_one})
            self.types_tree.destroy()
            self._list_types()

            adding_window.destroy()

        type_frame = _create_frame('Введите название вида')
        type_entry = ttk.Entry(type_frame)
        type_entry.pack(anchor='center', fill='x')
        type_frame.pack(anchor='center', fill='x', padx=5, pady=5)

        count_frame = _create_frame('Введите количество на порцию (гр.)')
        count_spinbox = ttk.Spinbox(count_frame, from_=1, to=500)
        count_spinbox.pack(anchor='center', fill='x')
        count_frame.pack(anchor='center', fill='x', padx=5, pady=5)

        add_type_button = ttk.Button(adding_window,
                                     text='Добавить',
                                     command=send_data_and_update)
        add_type_button.pack(anchor='center')

    def _open_amount_adding_window(self):
        adding_window = Tk()
        adding_window.title('Добавить мясо в базу')
        adding_window.geometry('600x400')
        adding_window.minsize(600, 400)

        @staticmethod
        def _create_frame(label_text):
            frame = ttk.Frame(master=adding_window,
                              borderwidth=1,
                              relief='solid',
                              padding=(8, 10))
            label = ttk.Label(frame, text=label_text)
            label.pack(anchor='center')

            return frame

        def send_data_and_update():
            type_name = type_combobox.get()
            amount = amount_spinbox.get()

            add_amount(self.session, {'name': type_name,
                                      'amount': amount})
            self.freezer_tree.destroy()
            self.total_tree.destroy()
            self._list_freezer()
            self._list_total()

            adding_window.destroy()

        def _is_num(val):
            try:
                float(val)

            except ValueError:

                return False

            return True

        type_frame = _create_frame('Выберите добавляемый вид мяса')
        type_combobox = ttk.Combobox(type_frame,
                                     values=get_types_names(self.session),
                                     state='readonly')
        type_combobox.pack(anchor='center', fill='x')
        type_frame.pack(anchor='center', fill='x', padx=5, pady=5)

        amount_frame = _create_frame('Введите количество мяса (кг.)')
        amount_spinbox = ttk.Spinbox(amount_frame,
                                     from_=0.5,
                                     to=500,
                                     increment=0.5,
                                     validate='key',
                                     validatecommand=(
                                         amount_frame.register(_is_num), '%P'))
        amount_spinbox.pack(anchor='center', fill='x')
        amount_frame.pack(anchor='center', fill='x', padx=5, pady=5)

        add_type_button = ttk.Button(adding_window,
                                     text='Добавить',
                                     command=send_data_and_update)
        add_type_button.pack(anchor='center')


if __name__ == '__main__':
    root = Tk()
    ui = Interface(root=root)
    ui.run()
