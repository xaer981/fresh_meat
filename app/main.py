from collections import defaultdict
from operator import itemgetter
from tkinter import Button, Menu, Tk, messagebox, ttk
from tkinter.constants import BOTH, CENTER, END, N, W, X
from tkinter.messagebox import showerror

import constants
from core.utils import (ScrollableFrame, create_frame,
                        generate_interface_center_x_y)
from db.crud import crud
from db.database import SessionLocal, create_db
from db.exceptions import ValidationError


class Interface:
    def __init__(self, root: Tk) -> None:
        create_db()
        self.session = SessionLocal()

        # root
        self.root = root
        self.root.title(constants.MAIN_WINDOW_TITLE)
        self.root.protocol(constants.CLOSE_WINDOW_PROTOCOL, self.shutdown)
        self.root.option_add(constants.TEAROFF_OPTION, False)

        # sizes
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x, y = generate_interface_center_x_y(screen_width,
                                             screen_height,
                                             constants.MAIN_WINDOW_WIDTH,
                                             constants.MAIN_WINDOW_HEIGHT)
        self.root.minsize(constants.MAIN_WINDOW_WIDTH,
                          constants.MAIN_WINDOW_HEIGHT)
        self.root.geometry(f'{constants.MAIN_WINDOW_WIDTH}'
                           f'x{constants.MAIN_WINDOW_HEIGHT}'
                           f'+{x}'
                           f'+{y}')

        self.child_win_x, self.child_win_y = generate_interface_center_x_y(
            screen_width,
            screen_height,
            constants.CHILD_WINDOW_WIDTH,
            constants.CHILD_WINDOW_HEIGHT)

        # menu
        main_menu = Menu()
        edit_menu = Menu()
        settings_menu = Menu()

        # create edit menu
        for label, command in constants.EDIT_MENU.items():
            edit_menu.add_command(label=label,
                                  command=getattr(self, command))

        # create settings menu
        for label, command in constants.SETTINGS_MENU.items():
            if label == constants.DELETE_DISH_MENU_LABEL:
                settings_menu.add_separator()
            settings_menu.add_command(label=label,
                                      command=getattr(self, command))

        main_menu.add_cascade(label=constants.EDIT_MENU_LABEL,
                              menu=edit_menu)
        main_menu.add_cascade(label=constants.SETTINGS_MENU_LABEL,
                              menu=settings_menu)

        self.root.config(menu=main_menu)

        # notebook
        notebook = ttk.Notebook()
        notebook.pack(expand=True, fill=BOTH)

        self.types = ttk.Frame(notebook)
        self.total = ttk.Frame(notebook)
        self.fridge = ttk.Frame(notebook)
        self.freezer = ttk.Frame(notebook)
        self.dishes = ttk.Frame(notebook)

        # pack frames & add them to notebook
        for text, frame in constants.MAIN_FRAMES.items():
            obj = getattr(self, frame)
            obj.pack(fill=BOTH, expand=True)
            notebook.add(obj, text=text)

        # styling
        style = ttk.Style()
        style.theme_use(constants.MAIN_THEME)

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
        labels = itemgetter(*columns)(constants.DATA_COLUMNS_LABELS)

        tree = ttk.Treeview(parent,
                            columns=columns,
                            show=constants.HEADINGS)
        if isinstance(labels, str):
            tree.heading(0, text=labels, anchor=W)
        else:
            for i in range(len(labels)):
                tree.heading(i, text=labels[i], anchor=W)

        tree.pack(fill=BOTH, expand=True)

        for row in data:
            values = ([*row, row[1] / 1000]
                      if not isinstance(labels, str) and constants.AMOUNT_KG
                      in columns
                      else [*row])
            tree.insert('', END, values=values)

        return tree

    def _list_types(self) -> None:
        data = crud.get_types(self.session)
        columns = constants.LIST_COLUMNS['types']
        self.types_tree = self._list_data(data, columns, self.types)
        self.types_tree.bind(
            constants.RIGHT_MOUSE_BUTTON,
            lambda event: self._types_popup_menu(event, self.types_tree))

    def _list_dishes(self) -> None:
        data = crud.get_dishes(self.session)
        columns = constants.LIST_COLUMNS['dishes']
        self.dishes_tree = self._list_data(data, columns, self.dishes)
        self.dishes_tree.bind(
            constants.RIGHT_MOUSE_BUTTON,
            lambda event: self._dishes_popup_menu(event, self.dishes_tree))

    def _list_total(self) -> None:
        data = crud.get_total(self.session)
        columns = constants.LIST_COLUMNS['meat']
        self.total_tree = self._list_data(data, columns, self.total)
        self.total_tree.bind(
            constants.RIGHT_MOUSE_BUTTON,
            lambda event: self._meat_popup_menu(event, self.total_tree))

    def _list_fridge(self) -> None:
        data = crud.get_fridge(self.session)
        columns = constants.LIST_COLUMNS['meat']
        self.fridge_tree = self._list_data(data, columns, self.fridge)
        self.fridge_tree.bind(
            constants.RIGHT_MOUSE_BUTTON,
            lambda event: self._meat_popup_menu(event, self.fridge_tree))

    def _list_freezer(self) -> None:
        data = crud.get_freezer(self.session)
        columns = constants.LIST_COLUMNS['meat']
        self.freezer_tree = self._list_data(data, columns, self.freezer)
        self.freezer_tree.bind(
            constants.RIGHT_MOUSE_BUTTON,
            lambda event: self._meat_popup_menu(event, self.freezer_tree))

    def _list_all(self) -> None:
        self._list_types()
        self._list_dishes()
        self._list_total()
        self._list_fridge()
        self._list_freezer()

    def _update_all_trees(self) -> None:
        self.types_tree.destroy()
        self.dishes_tree.destroy()
        self.fridge_tree.destroy()
        self.freezer_tree.destroy()
        self.total_tree.destroy()

        self._list_all()

    def _meat_popup_menu(self, event, tree: ttk.Treeview):
        row_id = tree.identify_row(event.y)
        tree.selection_set(row_id)

        menu = Menu(tree, tearoff=0)
        menu.add_command(label=constants.FREEZER_TO_FRIDGE_MENU_LABEL,
                         command=self._open_freezer_to_fridge_window)
        menu.add_command(label=constants.FRIDGE_TO_FREEZER_MENU_LABEL,
                         command=self._open_fridge_to_freezer_window)
        menu.post(event.x_root, event.y_root)

    def _dishes_popup_menu(self, event, tree: ttk.Treeview):
        row_id = tree.identify_row(event.y)
        tree.selection_set(row_id)

        menu = Menu(tree, tearoff=0)
        menu.add_command(label=constants.ADD_DISH_MENU_LABEL,
                         command=self._open_dish_adding_window)
        menu.add_command(label=constants.CHANGE_DISH_MENU_LABEL,
                         command=self._open_dish_change_window)
        menu.add_separator()
        menu.add_command(label=constants.DELETE_DISH_MENU_LABEL,
                         command=self._open_delete_dish_window)
        menu.post(event.x_root, event.y_root)

    def _types_popup_menu(self, event, tree: ttk.Treeview):
        row_id = tree.identify_row(event.y)
        tree.selection_set(row_id)

        menu = Menu(tree, tearoff=0)
        menu.add_command(label=constants.ADD_TYPE_MENU_LABEL,
                         command=self._open_type_adding_window)
        menu.add_separator()
        menu.add_command(label=constants.DELETE_TYPE_MENU_LABEL,
                         command=self._open_delete_type_window)
        menu.post(event.x_root, event.y_root)

    def _open_type_adding_window(self):
        adding_window = Tk()
        adding_window.title(constants.ADD_TYPE_MENU_LABEL)
        adding_window.minsize(constants.CHILD_WINDOW_WIDTH,
                              constants.CHILD_WINDOW_HEIGHT)
        adding_window.geometry(f'{constants.CHILD_WINDOW_WIDTH}'
                               f'x{constants.CHILD_WINDOW_HEIGHT}'
                               f'+{self.child_win_x}'
                               f'+{self.child_win_y}')

        def send_data_and_update():
            type_name = type_entry.get()

            try:
                crud.add_type(self.session, type_name)
                self.types_tree.destroy()
                self._list_types()

            except ValidationError as error:
                showerror(constants.ERROR_TITLE, error.message)

            finally:
                adding_window.destroy()

        type_frame = create_frame(adding_window,
                                  constants.TYPES_FRAME_ENTRY_TEXT)
        type_entry = ttk.Entry(type_frame)
        type_entry.pack(anchor=CENTER, fill=X)
        type_frame.pack(anchor=CENTER,
                        fill=X,
                        padx=constants.DEFAULT_PADX,
                        pady=constants.DEFAULT_PADY)

        add_type_button = ttk.Button(adding_window,
                                     text=constants.ADD_BUTTON_TEXT,
                                     cursor=constants.BTN_DEFAULT_CUR,
                                     command=send_data_and_update)
        adding_window.bind('<Return>', lambda event: send_data_and_update())
        add_type_button.pack(anchor=CENTER)
        adding_window.focus_force()

    def _open_dish_adding_window(self):
        adding_window = Tk()
        adding_window.title(constants.ADD_DISH_MENU_LABEL)
        adding_window.minsize(constants.CHILD_WINDOW_WIDTH,
                              constants.CHILD_WINDOW_HEIGHT)
        adding_window.geometry(f'{constants.CHILD_WINDOW_WIDTH}'
                               f'x{constants.CHILD_WINDOW_HEIGHT}'
                               f'+{self.child_win_x}'
                               f'+{self.child_win_y}')

        def send_data_and_update():
            type_name = type_combobox.get()
            count_per_one = amount_spinbox.get()
            dish_name = dish_name_entry.get()

            try:
                crud.add_dish(self.session, {'name': type_name,
                                             'count_per_one': count_per_one,
                                             'dish_name': dish_name})
                self.dishes_tree.destroy()
                self._list_dishes()

            except ValidationError as error:
                showerror(constants.ERROR_TITLE, error.message)

            finally:
                adding_window.destroy()

        def _create_amount_frame(event):
            nonlocal amount_spinbox
            nonlocal amount_frame
            nonlocal dish_name_frame
            nonlocal dish_name_entry
            nonlocal add_dish_button

            if amount_frame:
                amount_frame.destroy()

            if dish_name_frame:
                dish_name_frame.destroy()

            if add_dish_button:
                add_dish_button.destroy()

            amount_frame = create_frame(adding_window,
                                        constants.AMOUNT_FRAME_ENTRY_TEXT)
            dish_name_frame = create_frame(adding_window,
                                           constants.DISHES_FRAME_ENTRY_TEXT)
            amount_spinbox = ttk.Spinbox(amount_frame,
                                         from_=1,
                                         to=500,
                                         increment=1,
                                         validate=constants.KEY,
                                         validatecommand=(
                                             amount_frame.register(
                                                 _is_num),
                                             '%P'))
            amount_spinbox.pack(anchor=CENTER, fill=X)
            dish_name_entry = ttk.Entry(dish_name_frame)
            dish_name_entry.pack(anchor=CENTER, fill=X)
            amount_frame.pack(anchor=CENTER,
                              fill=X,
                              padx=constants.DEFAULT_PADX,
                              pady=constants.DEFAULT_PADY)
            dish_name_frame.pack(anchor=CENTER,
                                 fill=X,
                                 padx=constants.DEFAULT_PADX,
                                 pady=constants.DEFAULT_PADY)

            add_dish_button = ttk.Button(adding_window,
                                         text=constants.ADD_BUTTON_TEXT,
                                         cursor=constants.BTN_DEFAULT_CUR,
                                         command=send_data_and_update)
            adding_window.bind('<Return>',
                               lambda event: send_data_and_update())
            add_dish_button.pack(anchor=CENTER)

        def _is_num(val):
            try:
                val = int(val)

            except ValueError:

                return False

            if val > 500:

                return False

            return True

        amount_frame = None
        dish_name_frame = None
        amount_spinbox = None
        add_dish_button = None
        dish_name_entry = None

        type_frame = create_frame(adding_window,
                                  constants.CHOOSE_TYPE_FRAME_TEXT)
        type_combobox = ttk.Combobox(type_frame,
                                     values=crud.get_types_names(self.session),
                                     state=constants.READONLY)
        type_combobox.pack(anchor=CENTER, fill=X)
        type_frame.pack(anchor=CENTER,
                        fill=X,
                        padx=constants.DEFAULT_PADX,
                        pady=constants.DEFAULT_PADY)
        type_combobox.bind(constants.COMBOBOX_SELECTED, _create_amount_frame)

        adding_window.focus_force()

    def _open_dish_change_window(self):
        adding_window = Tk()
        adding_window.title(constants.CHANGE_DISH_MENU_LABEL)
        adding_window.minsize(constants.CHILD_WINDOW_WIDTH,
                              constants.CHILD_WINDOW_HEIGHT)
        adding_window.geometry(f'{constants.CHILD_WINDOW_WIDTH}'
                               f'x{constants.CHILD_WINDOW_HEIGHT}'
                               f'+{self.child_win_x}'
                               f'+{self.child_win_y}')

        def send_data_and_update():
            dish_name = type_combobox.get()
            count_per_one = amount_spinbox.get()

            try:
                crud.update_dish(self.session, {'name': dish_name,
                                                'count_per_one':
                                                    count_per_one})
                self.dishes_tree.destroy()
                self._list_dishes()

            except ValidationError as error:
                showerror(constants.ERROR_TITLE, error.message)

            finally:
                adding_window.destroy()

        def _create_amount_frame(event):
            nonlocal amount_spinbox
            nonlocal amount_frame
            nonlocal apply_change_button

            if amount_frame:
                amount_frame.destroy()

            if apply_change_button:
                apply_change_button.destroy()

            amount_frame = create_frame(adding_window,
                                        constants.AMOUNT_FRAME_ENTRY_TEXT)
            amount_spinbox = ttk.Spinbox(amount_frame,
                                         from_=1,
                                         to=500)
            amount_spinbox.pack(anchor=CENTER, fill=X)
            amount_frame.pack(anchor=CENTER,
                              fill=X,
                              padx=constants.DEFAULT_PADX,
                              pady=constants.DEFAULT_PADY)

            apply_change_button = ttk.Button(adding_window,
                                             text=constants.CHANGE_BUTTON_TEXT,
                                             cursor=constants.BTN_DEFAULT_CUR,
                                             command=send_data_and_update)
            adding_window.bind('<Return>',
                               lambda event: send_data_and_update())
            apply_change_button.pack(anchor=CENTER)

        amount_spinbox = None
        amount_frame = None
        apply_change_button = None

        type_frame = create_frame(adding_window,
                                  constants.CHOOSE_DISH_FRAME_TEXT)
        type_combobox = ttk.Combobox(type_frame,
                                     values=crud.get_dishes_names(
                                         self.session),
                                     state=constants.READONLY)
        type_combobox.pack(anchor=CENTER, fill=X)
        type_frame.pack(anchor=CENTER,
                        fill=X,
                        padx=constants.DEFAULT_PADX,
                        pady=constants.DEFAULT_PADY)
        type_combobox.bind(constants.COMBOBOX_SELECTED, _create_amount_frame)
        adding_window.focus_force()

    def _open_amount_adding_window(self):
        adding_window = Tk()
        adding_window.title(constants.ADD_MEAT_MENU_LABEL)
        adding_window.minsize(constants.CHILD_WINDOW_WIDTH,
                              constants.CHILD_WINDOW_HEIGHT)
        adding_window.geometry(f'{constants.CHILD_WINDOW_WIDTH}'
                               f'x{constants.CHILD_WINDOW_HEIGHT}'
                               f'+{self.child_win_x}'
                               f'+{self.child_win_y}')

        def send_data_and_update():
            type_name = type_combobox.get()
            amount = amount_spinbox.get()

            try:
                crud.add_amount(self.session, {'name': type_name,
                                               'amount': amount})
                self.freezer_tree.destroy()
                self.fridge_tree.destroy()
                self.total_tree.destroy()
                self._list_freezer()
                self._list_fridge()
                self._list_total()

            except ValidationError as error:
                showerror(constants.ERROR_TITLE, error.message)

            finally:
                adding_window.destroy()

        def _is_num(val):
            try:
                val = int(val)

            except ValueError:

                return False

            if val > 999999:

                return False

            return True

        type_frame = create_frame(adding_window,
                                  constants.CHOOSE_ADD_TYPE_FRAME_TEXT)
        type_combobox = ttk.Combobox(type_frame,
                                     values=crud.get_types_names(self.session),
                                     state=constants.READONLY)
        type_combobox.pack(anchor=CENTER, fill=X)
        type_frame.pack(anchor=CENTER,
                        fill=X,
                        padx=constants.DEFAULT_PADX,
                        pady=constants.DEFAULT_PADY)

        amount_frame = create_frame(adding_window,
                                    constants.ADD_AMOUNT_FRAME_ENTRY_TEXT)
        amount_spinbox = ttk.Spinbox(amount_frame,
                                     from_=1,
                                     to=999999,
                                     validate=constants.KEY,
                                     validatecommand=(
                                         amount_frame.register(_is_num), '%P'))
        amount_spinbox.pack(anchor=CENTER, fill=X)
        amount_frame.pack(anchor=CENTER,
                          fill=X,
                          padx=constants.DEFAULT_PADX,
                          pady=constants.DEFAULT_PADY)

        add_amount_button = ttk.Button(adding_window,
                                       text=constants.ADD_BUTTON_TEXT,
                                       cursor=constants.BTN_DEFAULT_CUR,
                                       command=send_data_and_update)
        add_amount_button.pack(anchor=CENTER)
        adding_window.bind('<Return>',
                           lambda event: send_data_and_update())
        adding_window.focus_force()

    def _open_freezer_to_fridge_window(self):
        adding_window = Tk()
        adding_window.title(constants.FREEZER_TO_FRIDGE_MENU_LABEL)
        adding_window.minsize(constants.CHILD_WINDOW_WIDTH,
                              constants.CHILD_WINDOW_HEIGHT)
        adding_window.geometry(f'{constants.CHILD_WINDOW_WIDTH}'
                               f'x{constants.CHILD_WINDOW_HEIGHT}'
                               f'+{self.child_win_x}'
                               f'+{self.child_win_y}')

        def send_data_and_update():
            type_name = type_combobox.get()
            amount = amount_spinbox.get()

            try:
                crud.freezer_to_fridge(self.session, {'name': type_name,
                                                      'amount': amount})
                self.freezer_tree.destroy()
                self.fridge_tree.destroy()
                self.total_tree.destroy()
                self._list_freezer()
                self._list_fridge()
                self._list_total()

            except ValidationError as error:
                showerror(constants.ERROR_TITLE, error.message)

            finally:
                adding_window.destroy()

        def _is_num_and_less_than_now(val):
            try:
                val = int(val)

            except ValueError:

                return False

            if crud.get_type_freezer(self.session, type_combobox.get()) < val:

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

            type_freezer = crud.get_type_freezer(self.session,
                                                 type_combobox.get())
            amount_frame = create_frame(adding_window,
                                        constants.MOVE_FRAME_ENTRY_TEXT)
            amount_label = ttk.Label(amount_frame,
                                     text=((constants.MOVE_FREEZER_LABEL_TEXT
                                            .format(type_freezer=type_freezer))
                                           ))
            amount_spinbox = ttk.Spinbox(amount_frame,
                                         from_=1,
                                         to=type_freezer,
                                         increment=1,
                                         validate=constants.KEY,
                                         validatecommand=(
                                             amount_frame.register(
                                                 _is_num_and_less_than_now),
                                             '%P'))
            amount_spinbox.pack(anchor=CENTER, fill=X)
            amount_label.pack(anchor=N)
            amount_frame.pack(anchor=CENTER,
                              fill=X,
                              padx=constants.DEFAULT_PADX,
                              pady=constants.DEFAULT_PADY)

            to_fridge_button = ttk.Button(adding_window,
                                          text=constants.MOVE_BUTTON_TEXT,
                                          cursor=constants.BTN_DEFAULT_CUR,
                                          command=send_data_and_update)
            to_fridge_button.pack(anchor=CENTER)
            adding_window.bind('<Return>',
                               lambda event: send_data_and_update())

        amount_frame = None
        amount_spinbox = None
        to_fridge_button = None

        type_frame = create_frame(adding_window,
                                  constants.MOVE_FRAME_LABEL_TEXT)
        type_combobox = ttk.Combobox(type_frame,
                                     values=crud.get_types_names(self.session),
                                     state=constants.READONLY)
        type_combobox.pack(anchor=CENTER, fill=X)
        type_frame.pack(anchor=CENTER,
                        fill=X,
                        padx=constants.DEFAULT_PADX,
                        pady=constants.DEFAULT_PADY)
        type_combobox.bind(constants.COMBOBOX_SELECTED, _create_amount_frame)
        adding_window.focus_force()

    def _open_fridge_to_freezer_window(self):
        adding_window = Tk()
        adding_window.title(constants.FRIDGE_TO_FREEZER_MENU_LABEL)
        adding_window.minsize(constants.CHILD_WINDOW_WIDTH,
                              constants.CHILD_WINDOW_HEIGHT)
        adding_window.geometry(f'{constants.CHILD_WINDOW_WIDTH}'
                               f'x{constants.CHILD_WINDOW_HEIGHT}'
                               f'+{self.child_win_x}'
                               f'+{self.child_win_y}')

        def send_data_and_update():
            type_name = type_combobox.get()
            amount = amount_spinbox.get()

            try:
                crud.fridge_to_freezer(self.session, {'name': type_name,
                                                      'amount': amount})
                self.freezer_tree.destroy()
                self.fridge_tree.destroy()
                self.total_tree.destroy()
                self._list_freezer()
                self._list_fridge()
                self._list_total()

            except ValidationError as error:
                showerror(constants.ERROR_TITLE, error.message)

            finally:
                adding_window.destroy()

        def _is_num_and_less_than_now(val):
            try:
                val = int(val)

            except ValueError:

                return False

            if crud.get_type_fridge(self.session, type_combobox.get()) < val:

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

            type_fridge = crud.get_type_fridge(self.session,
                                               type_combobox.get())
            amount_frame = create_frame(adding_window,
                                        constants.MOVE_FRAME_ENTRY_TEXT)
            amount_label = ttk.Label(amount_frame,
                                     text=(constants.MOVE_FRIDGE_LABEL_TEXT
                                           .format(type_fridge=type_fridge)))
            amount_spinbox = ttk.Spinbox(amount_frame,
                                         from_=1,
                                         to=type_fridge,
                                         increment=1,
                                         validate=constants.KEY,
                                         validatecommand=(
                                             amount_frame.register(
                                                 _is_num_and_less_than_now),
                                             '%P'))
            amount_spinbox.pack(anchor=CENTER, fill=X)
            amount_label.pack(anchor=N)
            amount_frame.pack(anchor=CENTER,
                              fill=X,
                              padx=constants.DEFAULT_PADX,
                              pady=constants.DEFAULT_PADY)

            to_freezer_button = ttk.Button(adding_window,
                                           text=constants.MOVE_BUTTON_TEXT,
                                           cursor=constants.BTN_DEFAULT_CUR,
                                           command=send_data_and_update)
            to_freezer_button.pack(anchor=CENTER)
            adding_window.bind('<Return>',
                               lambda event: send_data_and_update())

        amount_spinbox = None
        amount_frame = None
        to_freezer_button = None

        type_frame = create_frame(adding_window,
                                  constants.MOVE_FRAME_LABEL_TEXT)
        type_combobox = ttk.Combobox(type_frame,
                                     values=crud.get_types_names(self.session),
                                     state=constants.READONLY)
        type_combobox.pack(anchor=CENTER, fill=X)
        type_frame.pack(anchor=CENTER,
                        fill=X,
                        padx=constants.DEFAULT_PADX,
                        pady=constants.DEFAULT_PADY)
        type_combobox.bind(constants.COMBOBOX_SELECTED, _create_amount_frame)
        adding_window.focus_force()

    def _open_report_window(self):
        adding_window = Tk()
        adding_window.title(constants.ADD_REPORT_MENU_LABEL)
        adding_window.minsize(constants.CHILD_WINDOW_WIDTH,
                              constants.CHILD_WINDOW_HEIGHT)
        adding_window.geometry(f'{constants.CHILD_WINDOW_WIDTH}'
                               f'x{constants.CHILD_WINDOW_HEIGHT}'
                               f'+{self.child_win_x}'
                               f'+{self.child_win_y}')

        report_frame = ScrollableFrame(adding_window)
        row = 2

        results = {}

        def _add_combobox_and_spinbox():
            nonlocal row
            type_combobox = ttk.Combobox(report_frame.interior,
                                         values=crud.get_dishes_names(
                                             self.session),
                                         state=constants.READONLY)
            amount_spinbox = ttk.Spinbox(report_frame.interior,
                                         from_=1,
                                         to=500,
                                         increment=1)
            type_combobox.grid(column=0,
                               row=row,
                               padx=constants.DEFAULT_PADX,
                               pady=constants.DEFAULT_PADY)
            amount_spinbox.grid(column=1,
                                row=row,
                                padx=constants.DEFAULT_PADX,
                                pady=constants.DEFAULT_PADY)

            row += 1

            results[type_combobox] = amount_spinbox

        def click_send_button():
            result = messagebox.askyesno(
                title=constants.REPORT_MSGBOX_TITLE,
                message=constants.REPORT_MSGBOX_MESSAGE,
                icon=messagebox.QUESTION,
                default=messagebox.NO)
            if result:
                send_data_and_update()
            else:
                adding_window.tkraise()
                adding_window.focus_force()

        def send_data_and_update():
            try:
                data = defaultdict(int)
                for key, value in results.items():
                    if key.get() and value.get():
                        data[key.get()] += int(value.get())
                used_amount = crud.add_report(self.session, data)

                if used_amount:
                    title = constants.REPORT_MSGBOX_SUCCESS_TITLE
                    message = [constants.REPORT_MSGBOX_SUCCESS_MESSAGE.format(
                        name=name,
                        amount=amount,
                        amount_kg=amount / 1000)
                        for name, amount
                        in used_amount.items()
                    ]
                else:
                    title = constants.REPORT_MSGBOX_EMPTY_TITLE
                    message = constants.REPORT_MSGBOX_EMPTY_MESSAGE

                messagebox.showinfo(title, message)
                self.freezer_tree.destroy()
                self.fridge_tree.destroy()
                self.total_tree.destroy()
                self._list_freezer()
                self._list_fridge()
                self._list_total()

            except ValidationError as error:
                showerror(constants.ERROR_TITLE, error.message)

            finally:
                adding_window.destroy()

        ttk.Label(report_frame.interior,
                  text=constants.REPORT_DISH_LABEL).grid(
            column=0,
            row=0,
            padx=constants.DEFAULT_PADX,
            pady=constants.DEFAULT_PADY
        )
        ttk.Label(report_frame.interior,
                  text=constants.REPORT_DISH_AMOUNT_LABEL).grid(
            column=1,
            row=0,
            padx=constants.DEFAULT_PADX,
            pady=constants.DEFAULT_PADY
        )
        _add_combobox_and_spinbox()

        Button(adding_window,
               text=constants.SEND_REPORT_BUTTON_TEXT,
               command=click_send_button,
               cursor=constants.BTN_DEFAULT_CUR,
               bg=constants.DANGER_BUTTON_BG,
               fg=constants.DANGER_BUTTON_FG).pack(anchor=CENTER)

        Button(adding_window,
               text=constants.ADD_ROW_REPORT_BUTTON_TEXT,
               command=_add_combobox_and_spinbox,
               cursor=constants.BTN_PLUS_CUR,
               bg=constants.ADD_ROW_BUTTON_BG,
               fg=constants.ADD_ROW_BUTTON_FG).pack(anchor=CENTER)

        adding_window.bind('<Return>',
                           lambda event: click_send_button())

        report_frame.pack(anchor=CENTER,
                          fill=X,
                          padx=constants.DEFAULT_PADX,
                          pady=constants.DEFAULT_PADY)
        adding_window.focus_force()

    def _open_delete_dish_window(self):
        adding_window = Tk()
        adding_window.title(constants.DELETE_DISH_MENU_LABEL)
        adding_window.minsize(constants.CHILD_WINDOW_WIDTH,
                              constants.CHILD_WINDOW_HEIGHT)
        adding_window.geometry(f'{constants.CHILD_WINDOW_WIDTH}'
                               f'x{constants.CHILD_WINDOW_HEIGHT}'
                               f'+{self.child_win_x}'
                               f'+{self.child_win_y}')

        def send_data_and_update():
            dish_name = type_combobox.get()

            try:
                crud.delete_dish(self.session, dish_name)
                self.dishes_tree.destroy()
                self._list_dishes()

            except ValidationError as error:
                showerror(constants.ERROR_TITLE, error.message)

            finally:
                adding_window.destroy()

        def click_send_button():
            result = messagebox.askyesno(
                title=constants.DELETE_DISH_MSGBOX_TITLE,
                message=constants.DELETE_DISH_MSGBOX_MESSAGE,
                icon=messagebox.QUESTION,
                default=messagebox.NO)
            if result:
                send_data_and_update()
            else:
                adding_window.tkraise()
                adding_window.focus_force()

        type_frame = create_frame(adding_window,
                                  constants.CHOOSE_DELETE_DISH_FRAME_TEXT)
        type_combobox = ttk.Combobox(type_frame,
                                     values=crud.get_dishes_names(
                                         self.session),
                                     state=constants.READONLY)
        type_combobox.pack(anchor=CENTER, fill=X)
        type_frame.pack(anchor=CENTER,
                        fill=X,
                        padx=constants.DEFAULT_PADX,
                        pady=constants.DEFAULT_PADY)

        Button(adding_window,
               text=constants.DELETE_DISH_BUTTON_TEXT,
               command=click_send_button,
               cursor=constants.BTN_DEFAULT_CUR,
               bg=constants.DANGER_BUTTON_BG,
               fg=constants.DANGER_BUTTON_FG).pack(anchor=CENTER)

        adding_window.bind('<Return>',
                           lambda event: click_send_button())

        adding_window.focus_force()

    def _open_delete_type_window(self):
        adding_window = Tk()
        adding_window.title(constants.DELETE_TYPE_MENU_LABEL)
        adding_window.minsize(constants.CHILD_WINDOW_WIDTH,
                              constants.CHILD_WINDOW_HEIGHT)
        adding_window.geometry(f'{constants.CHILD_WINDOW_WIDTH}'
                               f'x{constants.CHILD_WINDOW_HEIGHT}'
                               f'+{self.child_win_x}'
                               f'+{self.child_win_y}')

        def send_data_and_update():
            type_name = type_combobox.get()

            try:
                crud.delete_type(self.session, type_name)

                self._update_all_trees()

            except ValidationError as error:
                showerror(constants.ERROR_TITLE, error.message)

            finally:
                adding_window.destroy()

        def click_send_button():
            result = messagebox.askyesno(
                title=constants.DELETE_TYPE_MSGBOX_TITLE,
                message=constants.DELETE_TYPE_MSGBOX_MESSAGE,
                icon=messagebox.WARNING,
                default=messagebox.NO)
            if result:
                send_data_and_update()
            else:
                adding_window.tkraise()
                adding_window.focus_force()

        type_frame = create_frame(adding_window,
                                  constants.CHOOSE_DELETE_TYPE_FRAME_TEXT)
        type_combobox = ttk.Combobox(type_frame,
                                     values=crud.get_types_names(self.session),
                                     state=constants.READONLY)
        type_combobox.pack(anchor=CENTER, fill=X)
        type_frame.pack(anchor=CENTER,
                        fill=X,
                        padx=constants.DEFAULT_PADX,
                        pady=constants.DEFAULT_PADY)

        Button(adding_window,
               text=constants.DELETE_TYPE_BUTTON_TEXT,
               command=click_send_button,
               cursor=constants.BTN_DEFAULT_CUR,
               bg=constants.DANGER_BUTTON_BG,
               fg=constants.DANGER_BUTTON_FG).pack(anchor=CENTER)
        adding_window.bind('<Return>',
                           lambda event: click_send_button())

        adding_window.focus_force()


if __name__ == '__main__':
    root = Tk()
    ui = Interface(root=root)
    ui.run()
