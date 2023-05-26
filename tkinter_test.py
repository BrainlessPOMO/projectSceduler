from tkinter import ttk, filedialog, messagebox
import tkinter as tk
from ttkthemes import ThemedTk
from os.path import exists
from dbSetup import get_data
import datetime

root = ThemedTk()
root.title("Your Projects")


class Window:
    def __init__(self, master):
        global project_data
        project_data = get_data()

        self.title = tk.Label(
            master=master, text="Projects Organizer", font=("Helvetica", "24"))
        self.title.pack(pady=12, padx=10)

        # Define Style
        self.style = ttk.Style(master)
        self.style.theme_use("breeze")

        # Make Scrollable Frame
        # self.scrollableFrame = ScrollableFrame(master)

        treeview_columns = ('id', 'project_name', 'days_left', 'progress')
        self.treeview = ttk.Treeview(
            master=master, columns=treeview_columns, show='headings')

        self.treeview.heading('id', text='ID')
        self.treeview.column(
            "id", anchor=tk.CENTER, stretch=tk.NO, width=50)

        self.treeview.heading('project_name', text='Project Name')
        self.treeview.column(
            "project_name", anchor=tk.CENTER, stretch=tk.YES, width=200)

        self.treeview.heading('days_left', text='Days Left')
        self.treeview.column("days_left", anchor=tk.CENTER,
                             stretch=tk.NO, width=70)

        self.treeview.heading('progress', text='Progress')
        self.treeview.column("progress", anchor=tk.CENTER,
                             stretch=tk.NO, width=70)

        # Append data into ScrollableFrame
        for project in project_data:
            current_date = datetime.datetime.now()
            ending_date = datetime.datetime.strptime(
                project[2], "%Y-%m-%d %H:%M:%S")

            date_diff = ending_date - current_date
            date_diff = date_diff.days
            changed_project = (project[0], project[1],
                               date_diff, f"{project[3]}%")

            self.treeview.insert('', tk.END, values=changed_project)
        self.treeview.pack()

    def get_attr(self):
        return self

    def changer(self, theme):
        self.style.theme_use(theme)


class ScrollableFrame:
    def __init__(self, master) -> None:
        self.main_scrollable_frame = tk.Frame(master=master, borderwidth=5)
        self.main_scrollable_frame.pack(
            pady=12, padx=10, fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(self.main_scrollable_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.scrollbar = ttk.Scrollbar(
            self.main_scrollable_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))

        self.treeview_frame = tk.Frame(self.canvas)

        self.canvas.create_window(
            (0, 0), window=self.treeview_frame, anchor="nw")

    def getFrame(self):
        return self.treeview_frame


class Project:
    def __init__(self, data, master) -> None:
        column_width = 30
        padY = 12
        padX = 15
        self.id = data[0]

        self.project_frame = tk.Frame(master=master, borderwidth=5)
        self.project_frame.pack(pady=padY, padx=padX)

        self.name = tk.Label(master=self.project_frame,
                             text=data[1], font=("Helvetica", "12"))
        self.name.grid(column=0, row=data[0], pady=padY, padx=padX)

        date_diff = data[2]

        if "days" not in data[2]:
            current_date = datetime.datetime.now()
            ending_date = datetime.datetime.strptime(
                data[2], "%Y-%m-%d %H:%M:%S")

            date_diff = ending_date - current_date
            date_diff = f"{date_diff.days} days"

        self.date = tk.Label(master=self.project_frame,
                             font=("Helvetica", "12"), text=date_diff)
        self.date.grid(column=1, row=data[0], pady=padY, padx=padX)

        if data[3] != 150:
            self.progress = ttk.Progressbar(
                master=self.project_frame, mode="determinate", orient="horizontal", length=column_width*4)
            self.progress["value"] = data[3]
            self.progress.grid(column=2, row=data[0], pady=padY, padx=padX)
        else:
            self.progress = tk.Label(master=self.project_frame,
                                     text="progress", font=("Helvetica", "12"))
            self.progress.grid(column=2, row=data[0], pady=padY, padx=padX)

        if data[0] != 0:
            self.date = tk.Button(master=self.project_frame,
                                  text="Change progress", command=self.getProjectId)
            self.date.grid(column=3, row=data[0], pady=padY, padx=padX)
        else:
            self.date = tk.Label(master=self.project_frame,
                                 text="Change Progress Value", font=("Helvetica", "12"))
            self.date.grid(column=3, row=data[0], pady=padY, padx=padX)

    def getProjectId(self):
        print(self.id)


try:
    root.iconphoto(False, tk.PhotoImage(file='icon.png'))
except:
    pass

width = 700  # Width
height = 450  # Height

screen_width = root.winfo_screenwidth()  # Width of the screen
screen_height = root.winfo_screenheight()  # Height of the screen

# Calculate Starting X and Y coordinates for Window
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)

root.geometry('%dx%d+%d+%d' % (width, height, x, y))

global mainWindow
mainWindow = Window(root)

root.mainloop()
