# INTERFACE MAIN CONSTANTS
BTN_DEFAULT_CUR = 'hand2'
BTN_PLUS_CUR = 'plus'
CHILD_WINDOW_HEIGHT = 400
CHILD_WINDOW_WIDTH = 600
COMBOBOX_SELECTED = '<<ComboboxSelected>>'
CLOSE_WINDOW_PROTOCOL = 'WM_DELETE_WINDOW'
DEFAULT_PADX = DEFAULT_PADY = 5
KEY = 'key'
MAIN_WINDOW_HEIGHT = 600
MAIN_WINDOW_WIDTH = 900
VERSION = '0.2'
MAIN_WINDOW_TITLE = f'Мясосчет v. {VERSION}'
READONLY = 'readonly'
RIGHT_MOUSE_BUTTON = '<Button-3>'
TEAROFF_OPTION = '*tearOff'

# STYLE
ADD_ROW_BUTTON_BG = 'green'
ADD_ROW_BUTTON_FG = 'white'
DANGER_BUTTON_BG = 'red'
DANGER_BUTTON_FG = 'white'
MAIN_THEME = 'winnative'


# MENU LABELS
ADD_DISH_MENU_LABEL = 'Добавить вид блюда'
ADD_MEAT_MENU_LABEL = 'Добавить мясо в базу'
ADD_REPORT_MENU_LABEL = 'Внести отчёт с раздачи'
ADD_TYPE_MENU_LABEL = 'Добавить вид мяса'
CHANGE_DISH_MENU_LABEL = 'Изменить существующий вид блюда'
DELETE_DISH_MENU_LABEL = 'Удалить существующий вид блюда'
DELETE_TYPE_MENU_LABEL = 'Удалить существующий вид мяса'
EDIT_MENU_LABEL = 'Внести изменения в базу'
FREEZER_TO_FRIDGE_MENU_LABEL = 'Перенести из морозильника'
FRIDGE_TO_FREEZER_MENU_LABEL = 'Перенести из холодильника'
SETTINGS_MENU_LABEL = 'Настройки'

# FRAMES TEXT
ADD_BUTTON_TEXT = 'Добавить'
ADD_ROW_REPORT_BUTTON_TEXT = 'Добавить ещё строку'
ADD_AMOUNT_FRAME_ENTRY_TEXT = 'Введите количество мяса (гр.)'
AMOUNT_FRAME_ENTRY_TEXT = 'Введите количество на одну порцию (гр.)'
CHANGE_BUTTON_TEXT = 'Изменить'
CHOOSE_ADD_TYPE_FRAME_TEXT = 'Выберите добавляемый вид мяса'
CHOOSE_DELETE_DISH_FRAME_TEXT = 'Выберите удаляемый вид блюда'
CHOOSE_DELETE_TYPE_FRAME_TEXT = 'Выберите удаляемый вид мяса'
CHOOSE_DISH_FRAME_TEXT = 'Выберите изменяемый вид блюда'
CHOOSE_TYPE_FRAME_TEXT = 'Выберите используемое сырье'
DELETE_DISH_BUTTON_TEXT = 'Удалить вид блюда'
DELETE_TYPE_BUTTON_TEXT = 'Удалить вид мяса'
DISHES_FRAME_ENTRY_TEXT = 'Введите название блюда'
DISHES_FRAME_TEXT = 'Виды блюд'
ERROR_TITLE = 'Ошибка!'
FREEZER_FRAME_TEXT = 'В морозильнике'
FRIDGE_FRAME_TEXT = 'В холодильнике'
MOVE_FRAME_ENTRY_TEXT = 'Введите количество для переноса (гр.)'
MOVE_FRAME_LABEL_TEXT = 'Выберите переносимый вид мяса'
MOVE_BUTTON_TEXT = 'Перенести'
MOVE_FREEZER_LABEL_TEXT = 'Сейчас в морозильнике {type_freezer} гр.'
MOVE_FRIDGE_LABEL_TEXT = 'Сейчас в холодильнике {type_fridge} гр.'
REPORT_DISH_LABEL = 'Вид блюда'
REPORT_DISH_AMOUNT_LABEL = 'Количество порций'
SEND_REPORT_BUTTON_TEXT = 'Отправить отчёт'
TOTAL_FRAME_TEXT = 'Всё мясо'
TYPES_FRAME_ENTRY_TEXT = 'Введите название вида'
TYPES_FRAME_TEXT = 'Виды мяса'

# MESSAGEBOX MESSAGES
DELETE_DISH_MSGBOX_MESSAGE = 'Уверены, что хотите удалить данный вид блюда?'
DELETE_DISH_MSGBOX_TITLE = 'Удалить вид блюда?'
DELETE_TYPE_MSGBOX_MESSAGE = ('ВНИМАНИЕ!\nПри удалении данного вида мяса, '
                              'все связанные с ним виды блюд тоже будут '
                              'удалены!\n'
                              'ВСЯ ИНФОРМАЦИЯ О КОЛИЧЕСТВЕ '
                              'ДАННОГО ВИДА МЯСА ТОЖЕ БУДЕТ УДАЛЕНА!\n'
                              'Уверены, что хотите удалить данный вид мяса?')
DELETE_TYPE_MSGBOX_TITLE = 'Удалить вид мяса?'
REPORT_MSGBOX_EMPTY_TITLE = 'Никаких изменений не внесено!'
REPORT_MSGBOX_EMPTY_MESSAGE = ('Все строки пустые или во всех не выбрано '
                               'одно из полей (количество/блюдо)')
REPORT_MSGBOX_MESSAGE = 'Уверены, что хотите внести информацию из отчёта?'
REPORT_MSGBOX_TITLE = 'Внести отчёт?'
REPORT_MSGBOX_SUCCESS_TITLE = 'Удачно!'
REPORT_MSGBOX_SUCCESS_MESSAGE = ('Мяса вида "{name}" - использовано {amount} '
                                 'гр. ({amount_kg} кг.)\n')

# TREES CONSTANTS
AMOUNT = 'amount'
AMOUNT_KG = 'amount_kg'
COUNT_PER_ONE = 'count_per_one'
NAME = 'name'
TYPE_NAME = 'type_name'

DATA_COLUMNS_LABELS = {
    AMOUNT: 'Количество (гр.)',
    AMOUNT_KG: 'Количество (кг.)',
    COUNT_PER_ONE: 'Количество на одну порцию (гр.)',
    NAME: 'Название',
    TYPE_NAME: 'Используемое сырье'
}

LIST_COLUMNS = {
    'types': (NAME, ),
    'dishes': (NAME, TYPE_NAME, COUNT_PER_ONE),
    'meat': (NAME, AMOUNT, AMOUNT_KG)
}

HEADINGS = 'headings'

# TEXT TO CLASS METHOD/ATTRIBUTE NAME
EDIT_MENU = {
    ADD_REPORT_MENU_LABEL: '_open_report_window',
    ADD_MEAT_MENU_LABEL: '_open_amount_adding_window',
    FREEZER_TO_FRIDGE_MENU_LABEL: '_open_freezer_to_fridge_window',
    FRIDGE_TO_FREEZER_MENU_LABEL: '_open_fridge_to_freezer_window'
}

MAIN_FRAMES = {
    TOTAL_FRAME_TEXT: 'total',
    FRIDGE_FRAME_TEXT: 'fridge',
    FREEZER_FRAME_TEXT: 'freezer',
    TYPES_FRAME_TEXT: 'types',
    DISHES_FRAME_TEXT: 'dishes'
}

SETTINGS_MENU = {
    ADD_TYPE_MENU_LABEL: '_open_type_adding_window',
    ADD_DISH_MENU_LABEL: '_open_dish_adding_window',
    CHANGE_DISH_MENU_LABEL: '_open_dish_change_window',
    DELETE_DISH_MENU_LABEL: '_open_delete_dish_window',
    DELETE_TYPE_MENU_LABEL: '_open_delete_type_window'
}
