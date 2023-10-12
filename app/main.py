from operator import itemgetter
from tkinter import Button, Menu, Tk, messagebox, ttk
from tkinter.messagebox import showerror

from core.utils import create_frame, ScrollableFrame
from db.crud import (add_amount, add_report, add_type, freezer_to_fridge,
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
            'amount': 'Количество (гр.)',
            'amount_kg': 'Количество (кг.)',
            'count_per_one': 'Количество на одну порцию (гр.)',
            'name': 'Название'
        }

        labels = itemgetter(*columns)(all_cols)
        tree = ttk.Treeview(parent,
                            columns=columns,
                            show='headings')

        # Не работает!
        for i in range(len(labels)):
            tree.heading(i, text=labels[i], anchor='w')

        tree.pack(fill='both', expand=True)

        for row in data:
            if len(labels) > 2:
                values = (row[0], row[1], row[1] / 1000)
            if len(labels) == 1:
                values = (row[0],)
            else:
                values = (row[0], row[1])

            tree.insert('', 'end', values=values)

        return tree

    def _list_types(self) -> None:
        data = get_types(self.session)
        columns = ('name',)
        self.types_tree = self._list_data(data, columns, self.types)

    def _list_total(self) -> None:
        data = get_total(self.session)
        columns = ('name', 'amount', 'amount_kg')
        self.total_tree = self._list_data(data, columns, self.total)

    def _list_fridge(self) -> None:
        data = get_fridge(self.session)
        columns = ('name', 'amount', 'amount_kg')
        self.fridge_tree = self._list_data(data, columns, self.fridge)

    def _list_freezer(self) -> None:
        data = get_freezer(self.session)
        columns = ('name', 'amount', 'amount_kg')
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

        def send_data_and_update():
            type_name = type_entry.get()

            try:
                add_type(self.session, type_name)
                self.types_tree.destroy()
                self._list_types()

            except ValidationError as error:
                showerror('Ошибка!', error.message)

            finally:
                adding_window.destroy()

        type_frame = create_frame(adding_window, 'Введите название вида')
        type_entry = ttk.Entry(type_frame)
        type_entry.pack(anchor='center', fill='x')
        type_frame.pack(anchor='center', fill='x', padx=5, pady=5)

        add_type_button = ttk.Button(adding_window,
                                     text='Добавить',
                                     command=send_data_and_update)
        add_type_button.pack(anchor='center')
        adding_window.focus_force()

    def _open_dish_adding_window(self):
        adding_window = Tk()
        adding_window.title('Добавить вид мяса')
        adding_window.geometry('600x400')
        adding_window.minsize(600, 400)

        def send_data_and_update():
            type_name = type_entry.get()
            count_per_one = count_spinbox.get()
            dish_name = dish_entry.get()

            try:
                add_type(self.session, {'name': type_name,
                                        'count_per_one': count_per_one,
                                        'dish_name': dish_name})
                self.types_tree.destroy()
                self._list_types()

            except ValidationError as error:
                showerror('Ошибка!', error.message)

            finally:
                adding_window.destroy()

        type_frame = create_frame(adding_window, 'Введите название вида')
        type_entry = ttk.Entry(type_frame)
        dish_entry = ttk.Entry(type_frame)
        type_entry.pack(anchor='center', fill='x')
        dish_entry.pack(anchor='center', fill='x')
        type_frame.pack(anchor='center', fill='x', padx=5, pady=5)

        count_frame = create_frame(adding_window,
                                   'Введите количество на порцию (гр.)')
        count_spinbox = ttk.Spinbox(count_frame, from_=1, to=500)
        count_spinbox.pack(anchor='center', fill='x')
        count_frame.pack(anchor='center', fill='x', padx=5, pady=5)

        add_type_button = ttk.Button(adding_window,
                                     text='Добавить',
                                     command=send_data_and_update)
        add_type_button.pack(anchor='center')
        adding_window.focus_force()

    def _open_type_change_window(self):
        adding_window = Tk()
        adding_window.title('Изменить существующий вид мяса')
        adding_window.geometry('600x400')
        adding_window.minsize(600, 400)

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

            amount_frame = create_frame(adding_window,
                                        ('Введите количество '
                                         'на порцию (гр.)'))
            amount_spinbox = ttk.Spinbox(amount_frame,
                                         from_=1,
                                         to=500)
            amount_spinbox.pack(anchor='center', fill='x')
            amount_frame.pack(anchor='center', fill='x', padx=5, pady=5)

            to_fridge_button = ttk.Button(adding_window,
                                          text='Изменить',
                                          command=send_data_and_update)
            to_fridge_button.pack(anchor='center')

        amount_spinbox = None

        type_frame = create_frame(adding_window,
                                  'Выберите изменяемый вид мяса')
        type_combobox = ttk.Combobox(type_frame,
                                     values=get_types_names(self.session),
                                     state='readonly')
        type_combobox.pack(anchor='center', fill='x')
        type_frame.pack(anchor='center', fill='x', padx=5, pady=5)
        type_combobox.bind('<<ComboboxSelected>>', _create_amount_frame)
        adding_window.focus_force()

    def _open_amount_adding_window(self):
        adding_window = Tk()
        adding_window.title('Добавить мясо в базу')
        adding_window.geometry('600x400')
        adding_window.minsize(600, 400)

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

        type_frame = create_frame(adding_window,
                                  'Выберите добавляемый вид мяса')
        type_combobox = ttk.Combobox(type_frame,
                                     values=get_types_names(self.session),
                                     state='readonly')
        type_combobox.pack(anchor='center', fill='x')
        type_frame.pack(anchor='center', fill='x', padx=5, pady=5)

        amount_frame = create_frame(adding_window,
                                    'Введите количество мяса (гр.)')
        amount_spinbox = ttk.Spinbox(amount_frame,
                                     from_=1,
                                     to=999999,
                                     validate='key',
                                     validatecommand=(
                                         amount_frame.register(_is_num), '%P'))
        amount_spinbox.pack(anchor='center', fill='x')
        amount_frame.pack(anchor='center', fill='x', padx=5, pady=5)

        add_amount_button = ttk.Button(adding_window,
                                       text='Добавить',
                                       command=send_data_and_update)
        add_amount_button.pack(anchor='center')
        adding_window.focus_force()

    def _open_freezer_to_fridge_window(self):
        adding_window = Tk()
        adding_window.title('Перенести в холодильник')
        adding_window.geometry('600x400')
        adding_window.minsize(600, 400)

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
                val = int(val)

            except ValueError:

                return False

            if get_type_freezer(self.session, type_combobox.get()) < val:

                return False

            return True

        def _create_amount_frame(event):
            nonlocal amount_spinbox
            nonlocal amount_frame
            nonlocal to_fridge_button

            if amount_frame:
                amount_frame.destroy()

            if to_fridge_button:
                to_fridge_button.destroy()

            type_freezer = get_type_freezer(self.session, type_combobox.get())
            amount_frame = create_frame(adding_window,
                                        ('Введите количество '
                                         'для переноса (гр.)'))
            amount_label = ttk.Label(amount_frame,
                                     text=(f'Сейчас в морозильнике '
                                           f'{type_freezer} гр.'))
            amount_spinbox = ttk.Spinbox(amount_frame,
                                         from_=1,
                                         to=type_freezer,
                                         increment=1,
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

        amount_frame = None
        amount_spinbox = None
        to_fridge_button = None

        type_frame = create_frame(adding_window,
                                  'Выберите переносимый вид мяса')
        type_combobox = ttk.Combobox(type_frame,
                                     values=get_types_names(self.session),
                                     state='readonly')
        type_combobox.pack(anchor='center', fill='x')
        type_frame.pack(anchor='center', fill='x', padx=5, pady=5)
        type_combobox.bind('<<ComboboxSelected>>', _create_amount_frame)
        adding_window.focus_force()

    def _open_fridge_to_freezer_window(self):
        adding_window = Tk()
        adding_window.title('Перенести в морозильник')
        adding_window.geometry('600x400')
        adding_window.minsize(600, 400)

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
                val = int(val)

            except ValueError:

                return False

            if get_type_fridge(self.session, type_combobox.get()) < val:

                return False

            return True

        def _create_amount_frame(event):
            nonlocal amount_spinbox
            nonlocal amount_frame
            nonlocal to_freezer_button

            if amount_frame:
                amount_frame.destroy()

            if to_freezer_button:
                to_freezer_button.destroy()

            type_fridge = get_type_fridge(self.session, type_combobox.get())
            amount_frame = create_frame(adding_window,
                                        ('Введите количество '
                                         'для переноса (гр.)'))
            amount_label = ttk.Label(amount_frame,
                                     text=(f'Сейчас в холодильнике '
                                           f'{type_fridge} гр.'))
            amount_spinbox = ttk.Spinbox(amount_frame,
                                         from_=1,
                                         to=type_fridge,
                                         increment=1,
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
        amount_frame = None
        to_freezer_button = None

        type_frame = create_frame(adding_window,
                                  'Выберите переносимый вид мяса')
        type_combobox = ttk.Combobox(type_frame,
                                     values=get_types_names(self.session),
                                     state='readonly')
        type_combobox.pack(anchor='center', fill='x')
        type_frame.pack(anchor='center', fill='x', padx=5, pady=5)
        type_combobox.bind('<<ComboboxSelected>>', _create_amount_frame)
        adding_window.focus_force()

    def _open_report_window(self):
        adding_window = Tk()
        adding_window.title('Внести отчёт с раздачи')
        adding_window.geometry('600x400')
        adding_window.minsize(600, 400)

        report_frame = ScrollableFrame(adding_window)
        row = 2

        results = {}

        def _add_combobox_and_spinbox():
            nonlocal row
            type_combobox = ttk.Combobox(report_frame.interior,
                                         values=get_types_names(self.session),
                                         state='readonly')
            amount_spinbox = ttk.Spinbox(report_frame.interior,
                                         from_=1,
                                         to=500,
                                         increment=1)
            type_combobox.grid(column=0, row=row, pady=5, padx=5)
            amount_spinbox.grid(column=1, row=row, pady=5, padx=5)

            row += 1

            results[type_combobox] = amount_spinbox

        def click_send_button():
            result = messagebox.askyesno(
                title='Внести отчёт?',
                message='Уверены, что хотите внести информацию из отчёта?',
                icon=messagebox.QUESTION,
                default=messagebox.NO)
            if result:
                send_data_and_update()
            else:
                adding_window.tkraise()
                adding_window.focus_force()

        def send_data_and_update():
            try:
                used_amount = add_report(self.session,
                                         {key.get(): value.get()
                                          for key, value in results.items()
                                          if key.get()})
                messagebox.showinfo('Удачно!', f'{used_amount = }')
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

        ttk.Label(report_frame.interior, text='Вид мяса').grid(column=0,
                                                               row=0,
                                                               pady=5,
                                                               padx=5)
        ttk.Label(report_frame.interior,
                  text='Количество порций').grid(column=1,
                                                 row=0,
                                                 pady=5,
                                                 padx=5)
        _add_combobox_and_spinbox()

        Button(adding_window,
               text='Отправить отчёт',
               command=click_send_button,
               bg='red',
               fg='white').pack(anchor='center')

        Button(adding_window,
               text='Добавить ещё строку',
               command=_add_combobox_and_spinbox,
               bg='green',
               fg='white').pack(anchor='center')

        report_frame.pack(anchor='center', fill='x', padx=5, pady=5)
        adding_window.focus_force()


if __name__ == '__main__':
    root = Tk()
    ui = Interface(root=root)
    ui.run()
