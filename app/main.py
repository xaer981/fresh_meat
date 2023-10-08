from operator import itemgetter
from tkinter import Menu, Tk, ttk
from tkinter.messagebox import showerror

from core.utils import ScrollableFrame
from db.crud import (add_amount, add_type, freezer_to_fridge,
                     fridge_to_freezer, get_freezer, get_fridge, get_total,
                     get_type_freezer, get_type_fridge, get_types,
                     get_types_names, update_type)
from db.database import SessionLocal, create_db
from db.exceptions import ValidationError


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

        edit_menu.add_command(label='Внести отчёт с раздачи',
                              command=self._open_report_window)
        edit_menu.add_command(label='Добавить мясо в базу',
                              command=self._open_amount_adding_window)
        edit_menu.add_command(label='Перенести из морозильника',
                              command=self._open_freezer_to_fridge_window)
        edit_menu.add_command(label='Перенести из холодильника',
                              command=self._open_fridge_to_freezer_window)

        settings_menu.add_command(label='Добавить вид мяса',
                                  command=self._open_type_adding_window)
        settings_menu.add_command(label='Изменить существующий вид мяса',
                                  command=self._open_type_change_window)

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

        notebook.add(self.total, text='Всё мясо')
        notebook.add(self.fridge, text='В холодильнике')
        notebook.add(self.freezer, text='В морозильнике')
        notebook.add(self.types, text='Виды мяса')

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
            'amount': 'Количество (кг.)',
            'count_per_one': 'Количество на одну порцию (гр.)',
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
            count_per_one = count_spinbox.get()

            try:
                add_type(self.session, {'name': type_name,
                                        'count_per_one': count_per_one})
                self.types_tree.destroy()
                self._list_types()

            except ValidationError as error:
                showerror('Ошибка!', error.message)

            finally:
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

    def _open_type_change_window(self):
        adding_window = Tk()
        adding_window.title('Изменить существующий вид мяса')
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
            count_per_one = amount_spinbox.get()

            try:
                update_type(self.session, {'name': type_name,
                                           'count_per_one': count_per_one})
                self.types_tree.destroy()
                self._list_types()

            except ValidationError as error:
                showerror('Ошибка!', error.message)

            finally:
                adding_window.destroy()

        def _create_amount_frame(event):
            nonlocal amount_spinbox
            amount_frame = _create_frame('Введите количество '
                                         'на порцию (гр.)')
            amount_spinbox = ttk.Spinbox(amount_frame,
                                         from_=0.5,
                                         to=500,
                                         increment=0.5)
            amount_spinbox.pack(anchor='center', fill='x')
            amount_frame.pack(anchor='center', fill='x', padx=5, pady=5)

            to_fridge_button = ttk.Button(adding_window,
                                          text='Изменить',
                                          command=send_data_and_update)
            to_fridge_button.pack(anchor='center')

        amount_spinbox = None

        type_frame = _create_frame('Выберите изменяемый вид мяса')
        type_combobox = ttk.Combobox(type_frame,
                                     values=get_types_names(self.session),
                                     state='readonly')
        type_combobox.pack(anchor='center', fill='x')
        type_frame.pack(anchor='center', fill='x', padx=5, pady=5)
        type_combobox.bind('<<ComboboxSelected>>', _create_amount_frame)

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

            try:
                add_amount(self.session, {'name': type_name,
                                          'amount': amount})
                self.freezer_tree.destroy()
                self.total_tree.destroy()
                self._list_freezer()
                self._list_total()

            except ValidationError as error:
                showerror('Ошибка!', error.message)

            finally:
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

        add_amount_button = ttk.Button(adding_window,
                                       text='Добавить',
                                       command=send_data_and_update)
        add_amount_button.pack(anchor='center')

    def _open_freezer_to_fridge_window(self):
        adding_window = Tk()
        adding_window.title('Перенести в холодильник')
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

            try:
                freezer_to_fridge(self.session, {'name': type_name,
                                                 'amount': amount})
                self.freezer_tree.destroy()
                self.fridge_tree.destroy()
                self.total_tree.destroy()
                self._list_freezer()
                self._list_fridge()
                self._list_total()

            except ValidationError as error:
                showerror('Ошибка!', error.message)

            finally:
                adding_window.destroy()

        def _is_num_and_less_than_now(val):
            try:
                val = float(val)

            except ValueError:

                return False

            if get_type_freezer(self.session, type_combobox.get()) < val:

                return False

            return True

        def _create_amount_frame(event):
            nonlocal amount_spinbox
            type_freezer = get_type_freezer(self.session, type_combobox.get())
            amount_frame = _create_frame('Введите количество '
                                         'для переноса (кг.)')
            amount_label = ttk.Label(amount_frame,
                                     text=(f'Сейчас в морозильнике '
                                           f'{type_freezer} кг.'))
            amount_spinbox = ttk.Spinbox(amount_frame,
                                         from_=0.5,
                                         to=type_freezer,
                                         increment=0.5,
                                         validate='key',
                                         validatecommand=(
                                            amount_frame.register(
                                                _is_num_and_less_than_now),
                                            '%P'))
            amount_spinbox.pack(anchor='center', fill='x')
            amount_label.pack(anchor='n')
            amount_frame.pack(anchor='center', fill='x', padx=5, pady=5)

            to_fridge_button = ttk.Button(adding_window,
                                          text='Перенести',
                                          command=send_data_and_update)
            to_fridge_button.pack(anchor='center')

        amount_spinbox = None
        type_frame = _create_frame('Выберите переносимый вид мяса')
        type_combobox = ttk.Combobox(type_frame,
                                     values=get_types_names(self.session),
                                     state='readonly')
        type_combobox.pack(anchor='center', fill='x')
        type_frame.pack(anchor='center', fill='x', padx=5, pady=5)
        type_combobox.bind('<<ComboboxSelected>>', _create_amount_frame)

    def _open_fridge_to_freezer_window(self):
        adding_window = Tk()
        adding_window.title('Перенести в морозильник')
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

            try:
                fridge_to_freezer(self.session, {'name': type_name,
                                                 'amount': amount})
                self.freezer_tree.destroy()
                self.fridge_tree.destroy()
                self.total_tree.destroy()
                self._list_freezer()
                self._list_fridge()
                self._list_total()

            except ValidationError as error:
                showerror('Ошибка!', error.message)

            finally:
                adding_window.destroy()

        def _is_num_and_less_than_now(val):
            try:
                val = float(val)

            except ValueError:

                return False

            if get_type_fridge(self.session, type_combobox.get()) < val:

                return False

            return True

        def _create_amount_frame(event):
            nonlocal amount_spinbox
            type_fridge = get_type_fridge(self.session, type_combobox.get())
            amount_frame = _create_frame('Введите количество '
                                         'для переноса (кг.)')
            amount_label = ttk.Label(amount_frame,
                                     text=(f'Сейчас в холодильнике '
                                           f'{type_fridge} кг.'))
            amount_spinbox = ttk.Spinbox(amount_frame,
                                         from_=0.5,
                                         to=type_fridge,
                                         increment=0.5,
                                         validate='key',
                                         validatecommand=(
                                            amount_frame.register(
                                                _is_num_and_less_than_now),
                                            '%P'))
            amount_spinbox.pack(anchor='center', fill='x')
            amount_label.pack(anchor='n')
            amount_frame.pack(anchor='center', fill='x', padx=5, pady=5)

            to_freezer_button = ttk.Button(adding_window,
                                           text='Перенести',
                                           command=send_data_and_update)
            to_freezer_button.pack(anchor='center')

        amount_spinbox = None
        type_frame = _create_frame('Выберите переносимый вид мяса')
        type_combobox = ttk.Combobox(type_frame,
                                     values=get_types_names(self.session),
                                     state='readonly')
        type_combobox.pack(anchor='center', fill='x')
        type_frame.pack(anchor='center', fill='x', padx=5, pady=5)
        type_combobox.bind('<<ComboboxSelected>>', _create_amount_frame)

    def _open_report_window(self):
        adding_window = Tk()
        adding_window.title('Внести отчёт с раздачи')
        adding_window.geometry('600x400')
        adding_window.minsize(600, 400)

        report_frame = ScrollableFrame(adding_window)
        for i in range(20):
            type_combobox = ttk.Combobox(report_frame.interior,
                                         values=i,
                                         state='readonly')
            type_combobox.grid(column=0, row=i, pady=5, padx=5)
            type_amount = ttk.Spinbox(report_frame.interior,
                                      from_=1,
                                      to=500,
                                      increment=1)
            type_amount.grid(column=1, row=i, pady=5, padx=5)

        report_frame.pack(anchor='center', fill='x', padx=5, pady=5)


if __name__ == '__main__':
    root = Tk()
    ui = Interface(root=root)
    ui.run()
