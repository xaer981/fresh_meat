import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        vscrollbar = ttk.Scrollbar(self, orient='vertical')
        vscrollbar.pack(fill='y', side='right', expand=False)
        canvas = tk.Canvas(self,
                           bd=0,
                           highlightthickness=0,
                           yscrollcommand=vscrollbar.set,
                           width=600,
                           height=400)
        canvas.pack(side='left', fill='both', expand=True)
        vscrollbar.config(command=canvas.yview)

        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0,
                                           0,
                                           window=interior,
                                           anchor='nw')

        def _bound_to_mousewheel(event):
            canvas.bind_all('<MouseWheel>', _on_mousewheel)

        def _unbound_to_mousewheel(event):
            canvas.unbind_all('<MouseWheel>')

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        def _configure_interior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion='0 0 %s %s' % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
        canvas.bind('<Enter>', _bound_to_mousewheel)
        canvas.bind_all('<MouseWheel>', _on_mousewheel)
        canvas.bind('<Leave>', _unbound_to_mousewheel)


def create_frame(master: ttk.Frame, label_text: str) -> ttk.Frame:
    frame = ttk.Frame(master=master,
                      borderwidth=1,
                      relief='solid',
                      padding=(8, 10))
    label = ttk.Label(frame, text=label_text)
    label.pack(anchor='center')

    return frame


def generate_interface_center_x_y(screen_width: int,
                                  screen_height: int,
                                  win_width: int,
                                  win_height: int) -> tuple[int]:
    x = (screen_width / 2) - (win_width / 2)
    y = (screen_height / 2) - (win_height / 2)

    return int(x), int(y)
