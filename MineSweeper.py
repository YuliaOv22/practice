import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror
import time

# Colors by number of mines
colors = {
    0: "#ffffff",
    1: "#5203fc",
    2: "#fc035e",
    3: "#048558",
    4: "#fc5603",
    5: "#03ada5",
    6: "#fc03ba",
    7: "#069142",
    8: "#91067a"
}

images = {
    "mine_image": "Mine.png",
    "flag_image": "Flag.png"
}


class Timer(tk.Frame):
    """ Timer frame widget. """

    def __init__(self, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self._start = 0.0
        self._elapsedtime = 0.0
        self._running = 0
        self.timestr = tk.StringVar()
        self.make_widgets()

    def make_widgets(self):
        """ Make the time label. """
        timer_label = tk.Label(self, textvariable=self.timestr)
        self._set_time(self._elapsedtime)
        timer_label.pack(fill=tk.X, expand=tk.NO, pady=2, padx=2)

    def _update(self):
        """ Update the label with elapsed time. """
        self._elapsedtime = time.time() - self._start
        self._set_time(self._elapsedtime)
        self._timer = self.after(50, self._update)

    def _set_time(self, elap):
        """ Set the time string to Minutes:Seconds """
        minutes = int(elap / 60)
        seconds = int(elap - minutes * 60.0)
        self.timestr.set('%02d:%02d' % (minutes, seconds))

    def start(self):
        """ Start the timer, ignore if running. """
        if not self._running:
            self._start = time.time() - self._elapsedtime
            self._update()
            self._running = 1

    def stop(self):
        """ Stop the timer, ignore if stopped. """
        if self._running:
            self.after_cancel(self._timer)
            self._elapsedtime = time.time() - self._start
            self._set_time(self._elapsedtime)
            self._running = 0


class MinesCounter(tk.Frame):
    """ Mines counter frame widget. """

    def __init__(self, score, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.score = score
        self.label = tk.Label(self)
        self.label.pack()
        self.plus_mine()
        self.minus_mine()

    def plus_mine(self):
        self.score += 1
        self.label["text"] = f"{self.score:02d}"

    def minus_mine(self):
        self.score -= 1
        self.label["text"] = f"{self.score:02d}"


class MyButton(tk.Button):
    """ Make a button. """

    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width=3, background="#e3e3e3", font='Calibri 15 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.count_mine = 0
        self.is_open = False

    def __repr__(self):
        return f'MyButton {self.x} {self.y} {self.number} {self.is_mine}'


class MineSweeper:
    """ Start a game. """

    window = tk.Tk()
    window.title("MineSweeper")
    window.iconphoto(False, tk.PhotoImage(file=images.get("flag_image")))
    ROW = 10
    COLUMNS = 10
    MINES = 20
    IS_GAME_OVER = False
    IS_FIRST_CLICK = True

    def __init__(self):
        self.buttons = []
        self.timer = Timer()
        self.mines_count = MinesCounter(self.MINES)
        self.mines_free_buttons = self.ROW * self.COLUMNS - self.MINES
        for i in range(MineSweeper.ROW + 2):
            temp = []
            for j in range(MineSweeper.COLUMNS + 2):
                btn = MyButton(MineSweeper.window, x=i, y=j)
                btn.config(command=lambda button=btn: self.left_click(button))
                btn.bind("<Button-3>", self.right_click)
                temp.append(btn)
            self.buttons.append(temp)

    def right_click(self, event):
        """ Show/Hide a flag sign by clicking a right button of mouse.
            Count opened mines. """

        if MineSweeper.IS_GAME_OVER:
            return
        if MineSweeper.IS_FIRST_CLICK:
            return

        cur_btn = event.widget

        if cur_btn["state"] == "normal":
            cur_btn["state"] = "disable"
            cur_btn["text"] = "⛳"
            cur_btn["disabledforeground"] = "blue"
            self.mines_count.minus_mine()
        elif cur_btn["text"] == "⛳":
            cur_btn["text"] = ""
            cur_btn["state"] = "normal"
            self.mines_count.plus_mine()

    def left_click(self, clicked_button: MyButton):
        """ Open buttons and show mines count by clicking a left button of mouse.
            Stop the game if clicked the button with mine or opened all button free of mines. """

        img_mine = tk.PhotoImage(file=images.get("mine_image")).subsample(30)

        if MineSweeper.IS_GAME_OVER:
            return

        if MineSweeper.IS_FIRST_CLICK:
            """ First click without mines. Insert mines. Start the timer. """
            self.insert_mines(clicked_button.number)
            self.count_mines_in_buttons()
            # self.print_buttons()
            MineSweeper.IS_FIRST_CLICK = False
            self.timer.start()

        if clicked_button.is_mine:
            """ Click button with the mine. Stop the game and the timer. Show all mines.
                If button without the mine open button/buttons. Breadth first search was used. """

            # clicked_button.config(text="*", background="red", disabledforeground="black")
            clicked_button.config(image=img_mine, disabledforeground="black")
            clicked_button.is_open = True
            MineSweeper.IS_GAME_OVER = True
            self.timer.stop()
            showinfo("Game over", "Вы проиграли!")

            for i in range(1, MineSweeper.ROW + 1):
                for j in range(1, MineSweeper.COLUMNS + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        # btn["text"] = "*"
                        btn["image"] = img_mine
                    btn.config(state="disabled")

        else:
            color = colors.get(clicked_button.count_mine, "black")
            if clicked_button.count_mine:
                clicked_button.config(text=clicked_button.count_mine, disabledforeground=color)
                clicked_button.is_open = True
                self.mines_free_buttons -= 1
            else:
                # clicked_button.config(text="", background="#e1f5f5", disabledforeground=color)
                self.breadth_first_search(clicked_button)

        clicked_button.config(state="disabled")
        clicked_button.config(relief=tk.SUNKEN)

        if self.mines_free_buttons == 0:
            """ Count mines free buttons. Stop the game and the timer if all buttons was opened without mines. 
                Show all mines. """

            MineSweeper.IS_GAME_OVER = True
            self.timer.stop()
            showinfo("Game over", "Вы выиграли!")

            for i in range(1, MineSweeper.ROW + 1):
                for j in range(1, MineSweeper.COLUMNS + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        # btn["text"] = "*"
                        btn["image"] = img_mine
                    btn.config(state="disabled")

        self.window.mainloop()

    def breadth_first_search(self, btn: MyButton):
        """ Check buttons for mines if null open button. """

        queue = [btn]
        while queue:
            cur_btn = queue.pop()
            color = colors.get(cur_btn.count_mine, "black")
            if cur_btn.count_mine:
                cur_btn.config(text=cur_btn.count_mine, disabledforeground=color)
            else:
                cur_btn.config(text="", disabledforeground=color)
            cur_btn.is_open = True
            cur_btn.config(state="disabled", image="")
            cur_btn.config(relief=tk.SUNKEN)
            self.mines_free_buttons -= 1

            if cur_btn.count_mine == 0:
                x, y = cur_btn.x, cur_btn.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        # if not abs(dx - dy) == 1:
                        #    continue
                        next_btn = self.buttons[x + dx][y + dy]
                        if not next_btn.is_open and 1 <= next_btn.x <= MineSweeper.ROW and \
                                1 <= next_btn.y <= MineSweeper.COLUMNS and next_btn not in queue:
                            queue.append(next_btn)

    def reload(self):
        """ Restart the game. """

        [child.destroy() for child in self.window.winfo_children()]
        self.__init__()
        self.create_widgets()
        MineSweeper.IS_FIRST_CLICK = True
        MineSweeper.IS_GAME_OVER = False

    def create_settings_win(self):
        """ Settings: rows, columns, mines. """

        win_settings = tk.Toplevel(self.window)
        win_settings.wm_title("Настройки")

        tk.Label(win_settings, text="Количество строк:", anchor='w', width=20).grid(row=0, column=0)
        row_entry = tk.Entry(win_settings, width=6)
        row_entry.insert(0, MineSweeper.ROW)
        row_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(win_settings, text="Количество столбцов:", anchor='w', width=20).grid(row=1, column=0)
        column_entry = tk.Entry(win_settings, width=6)
        column_entry.insert(0, MineSweeper.COLUMNS)
        column_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(win_settings, text="Количество мин:", anchor='w', width=20).grid(row=2, column=0)
        mines_entry = tk.Entry(win_settings, width=6)
        mines_entry.insert(0, MineSweeper.MINES)
        mines_entry.grid(row=2, column=1, padx=10, pady=10)

        save_btn = tk.Button(win_settings, text="Применить",
                             command=lambda: self.change_settings(row_entry, column_entry, mines_entry))

        save_btn.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    def change_settings(self, row: tk.Entry, column: tk.Entry, mines: tk.Entry):
        """ Check insert values for settings. """

        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror("Ошибка", "Вы ввели неправильное значение!")
            return
        MineSweeper.ROW = int(row.get())
        MineSweeper.COLUMNS = int(column.get())
        MineSweeper.MINES = int(mines.get())
        self.reload()

    def create_widgets(self):
        """ Create widgets: menu, field of buttons, timer, mines counter. """

        """ Menu. """
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Играть", command=self.reload)
        settings_menu.add_command(label="Настройки", command=self.create_settings_win)
        settings_menu.add_command(label="Выход", command=self.window.destroy)
        menubar.add_cascade(label="Файл", menu=settings_menu)

        """ Field of buttons. """
        count = 1
        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMNS + 1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i, column=j, stick="NWES")
                count += 1
        for i in range(1, MineSweeper.ROW + 1):
            tk.Grid.rowconfigure(self.window, i, weight=1)
        for i in range(1, MineSweeper.COLUMNS + 1):
            tk.Grid.columnconfigure(self.window, i, weight=1)

        """ Timer. """
        timer_text = tk.Label(text='Время:')
        timer_text.grid(row=MineSweeper.ROW + 1, column=1, columnspan=MineSweeper.COLUMNS, pady=10, stick='W')
        self.timer.grid(row=MineSweeper.ROW + 1, column=1, columnspan=MineSweeper.COLUMNS, pady=10, padx=40, stick='W')

        """ Mines counter. """
        mine_text = tk.Label(text='Бомбы:')
        mine_text.grid(row=MineSweeper.ROW + 1, column=1, columnspan=MineSweeper.COLUMNS, pady=10, padx=140, stick='W')
        self.mines_count.grid(row=MineSweeper.ROW + 1, column=1, columnspan=MineSweeper.COLUMNS, pady=10, padx=185,
                              stick='W')

    # def open_all_buttons(self):
    #     """ Open all buttons. Use for the game validation. """
    #
    #     for i in range(MineSweeper.ROW + 2):
    #         for j in range(MineSweeper.COLUMNS + 2):
    #             btn = self.buttons[i][j]
    #             if btn.is_mine:
    #                 btn.config(text="*", background="red", disabledforeground="black")
    #             elif btn.count_mine in colors:
    #                 color = colors.get(btn.count_mine, "black")
    #                 btn.config(text=btn.count_mine, fg=color)

    def start(self):
        """ Start the game. """
        self.create_widgets()
        # self.open_all_buttons()
        MineSweeper.window.mainloop()

    # def print_buttons(self):
    #     """ Print all buttons. Use for the game validation. """
    #
    #     for i in range(1, MineSweeper.ROW + 1):
    #         for j in range(1, MineSweeper.COLUMNS + 1):
    #             btn = self.buttons[i][j]
    #             if btn.is_mine:
    #                 print("*", end="")
    #             else:
    #                 print(btn.count_mine, end="")
    #         print()

    def insert_mines(self, number: int):
        """ Insert mines in buttons. """

        index_mines = self.get_mines_places(number)
        # print(index_mines)
        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.number in index_mines:
                    btn.is_mine = True

    def count_mines_in_buttons(self):
        """ Count mines in buttons. """

        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMNS + 1):
                btn = self.buttons[i][j]
                count_mine = 0
                if not btn.is_mine:
                    for row_dx in [-1, 0, 1]:
                        for col_dx in [-1, 0, 1]:
                            neighbour = self.buttons[i + row_dx][j + col_dx]
                            if neighbour.is_mine:
                                count_mine += 1
                btn.count_mine = count_mine

    @staticmethod
    def get_mines_places(exclude_number: int):
        """ Return mines places. """

        indexes = list(range(1, MineSweeper.COLUMNS * MineSweeper.ROW + 1))
        # print(f"Исключаем кнопку {exclude_number}")
        indexes.remove(exclude_number)
        shuffle(indexes)
        return indexes[:MineSweeper.MINES]


game = MineSweeper()
game.start()
