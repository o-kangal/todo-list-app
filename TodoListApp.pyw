# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk  # For combobox
from tkinter import PhotoImage # For window icon
from tkinter import simpledialog, messagebox, scrolledtext # For scrollable text widget
import json
import os

# --- Data Management ---
DATA_FILE = "todolist_data.json"
tasks_data = {} # Main Data Structure: {"List Title": ["Task 1", "Task 2"], ...}

def load_data():
    """Load data while app starting"""
    global tasks_data
    if os.path.exists(DATA_FILE):
        try:
            # Read with UTF-8
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
        except (json.JSONDecodeError, IOError, UnicodeDecodeError) as e:
            messagebox.showerror("Load Error", f"Data file can't read or mulfunctioned:\n{e}\nStarting with default empty file. ")
            tasks_data = {}
    else:
        tasks_data = {}

def save_data():
    """Saves data while app shutdowm or data change."""
    try:
        # Write with UTF-8 and keep none-ASCII characters
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        messagebox.showerror("Save Error", f"Data can't saved: \n{e}")

# --- UI Functions ---

def update_all_display():
    """Show all lists and tasks in main text area."""
    # Make text widget editable
    main_text_area.config(state=tk.NORMAL)
    main_text_area.delete('1.0', tk.END) # Clear content

    # Define bold tags for titles
    main_text_area.tag_configure("list_title", font=("Helvetica", 12, "bold"), spacing1=5, spacing3=5)
    # Define indented tags for tasks
    main_text_area.tag_configure("task_item", lmargin1=20, lmargin2=20, spacing1=2, spacing3=2)

    if not tasks_data:
        main_text_area.insert(tk.END, "No list. Start with 'Add List' button.")
    else:
        for title, tasks in tasks_data.items():
            main_text_area.insert(tk.END, f"{title}:\n", "list_title") # Add title with bold font
            if tasks:
                for task in tasks:
                    main_text_area.insert(tk.END, f"- {task}\n", "task_item") # Add task indented
            else:
                 main_text_area.insert(tk.END, "  (Boş)\n", "task_item") # Mention if it is empty
            main_text_area.insert(tk.END, "\n") # Spaces between lists

    # Make text widget readonly again
    main_text_area.config(state=tk.DISABLED)

    # Update combobox and task selection box
    update_action_widgets()

def update_action_widgets():
    """Updates list selection combobox and task selection combobox."""
    list_titles = list(tasks_data.keys())
    list_combobox['values'] = list_titles

    # Clear task selection list
    task_delete_listbox.delete(0, tk.END)

    # If combobox selected and list is not deleted, load selection list. Else, clear combobox.
    current_selection = list_combobox.get()
    if current_selection in tasks_data:
        list_combobox.set(current_selection) # Keep selection
        # Load selected list's tasks
        for task in tasks_data[current_selection]:
            task_delete_listbox.insert(tk.END, task)
    elif list_titles:
        list_combobox.set(list_titles[0]) # Autoselect first list title
        # Load first list title's tasks in selection box
        for task in tasks_data[list_titles[0]]:
            task_delete_listbox.insert(tk.END, task)
    else:
        list_combobox.set('') # Clear if it is empty

def on_combobox_select(event=None):
     """Reload task selection box when list title selected."""
     selected_title = list_combobox.get()
     task_delete_listbox.delete(0, tk.END) # Önce temizle
     if selected_title in tasks_data:
         for task in tasks_data[selected_title]:
             task_delete_listbox.insert(tk.END, task)

# Title operations

def add_list_title():
    """Adds new list title."""
    new_title = simpledialog.askstring("New Title", "Enter new list title:", parent=root)
    if new_title:
        new_title = new_title.strip()
        if new_title:
            if new_title not in tasks_data:
                tasks_data[new_title] = []
                save_data()
                update_all_display() # Updates all display
                # Autoselect new list in combobox
                list_combobox.set(new_title)
                on_combobox_select() # Update task selection list
            else:
                messagebox.showwarning("Current Title", f"'{new_title}' is already exists.", parent=root)
        else:
             messagebox.showwarning("Invalid name", "List name cannot be empty.", parent=root)

def delete_list_title():
    """Deletes list title and tasks."""
    selected_title = list_combobox.get()
    if not selected_title:
        messagebox.showwarning("No Selection", "Please select a title to delete.", parent=root)
        return

    if selected_title in tasks_data:
        if messagebox.askyesno("Delete List", f"Are you sure about deleting '{selected_title}' list and all its tasks?", parent=root):
            del tasks_data[selected_title]
            save_data()
            update_all_display() # Updates all display
    else:
         messagebox.showerror("Error", "No list to delete!", parent=root)

def update_list_title():
    global tasks_data
    """Updates selected list title."""
    selected_title = list_combobox.get()
    if not selected_title:
        messagebox.showwarning("No Selection", "Please select a list to update.", parent=root)
        return

    new_title = simpledialog.askstring("Update", "Update title", parent=root, initialvalue=selected_title)

    if new_title:
        tasks_data_keys = list(tasks_data.keys())

        tasks_data_values = list(tasks_data.values())
        selected_title_index = tasks_data_keys.index(selected_title)
        tasks_data_keys[selected_title_index] = new_title

        tasks_data = dict(zip(tasks_data_keys,tasks_data_values))
    else:
        messagebox.showwarning("Invalid title", "Title content cannot be empty.", parent=root)

    save_data()
    update_all_display() # Updates all display

def move_title_up():
    global tasks_data
    selected_title = list_combobox.get()

    if not selected_title:
        messagebox.showwarning("List not selected", "Please select list first.", parent=root)
        return

    keys = list(tasks_data.keys())
    values = list(tasks_data.values())
    selected_title_index = keys.index(selected_title)

    if selected_title_index > 0:
        keys[selected_title_index], keys[selected_title_index - 1] = keys[selected_title_index - 1], keys[selected_title_index]
        values[selected_title_index], values[selected_title_index - 1] = values[selected_title_index - 1], values[selected_title_index]
        tasks_data = dict(zip(keys, values))
    else:
        messagebox.showwarning("List cannot moved", "List is already at the top.", parent=root)

    save_data()
    update_all_display()

def move_title_down():
    global tasks_data
    selected_title = list_combobox.get()

    if not selected_title:
        messagebox.showwarning("List not selected", "Please select list first.", parent=root)
        return

    keys = list(tasks_data.keys())
    values = list(tasks_data.values())
    selected_title_index = keys.index(selected_title)

    if selected_title_index < len(keys) - 1:
        keys[selected_title_index], keys[selected_title_index + 1] = keys[selected_title_index + 1], keys[selected_title_index]
        values[selected_title_index], values[selected_title_index + 1] = values[selected_title_index + 1], values[selected_title_index]
        tasks_data = dict(zip(keys, values))
    else:
        messagebox.showwarning("List cannot moved", "List is already at the bottom.", parent=root)

    save_data()
    update_all_display()


# Task operations

def add_task():
    """Adds new task to the selected list."""
    selected_title = list_combobox.get()
    if not selected_title:
        messagebox.showwarning("List Not Selected", "Please select a list to add new task.", parent=root)
        return

    if selected_title not in tasks_data:
         messagebox.showerror("Error", f"Selected list '{selected_title}' not exists anymore.", parent=root)
         update_all_display() # Relaod display to fix it
         return

    new_task = simpledialog.askstring("New Task", f"Enter a new task for '{selected_title}' list:", parent=root)
    if new_task:
        new_task = new_task.strip()
        if new_task :
            tasks_data[selected_title].append(new_task)
            save_data()
            update_all_display() # Updates all display
            # Update task selection box (if same list is selected)
            if list_combobox.get() == selected_title:
                 on_combobox_select()
        else:
            messagebox.showwarning("Invalid Task", "Task content cannot be empty.", parent=root)

def delete_task():
    """Deletes selected task (Selected from task selection box)."""
    selected_title = list_combobox.get()
    selected_task_indices = task_delete_listbox.curselection()

    if not selected_title:
        messagebox.showwarning("List Not Selected", "Please select the title of task first.", parent=root)
        return
    if not selected_task_indices:
        messagebox.showwarning("Task Not Selected", "Please select the task first.", parent=root)
        return

    selected_task_index = selected_task_indices[0]
    selected_task = task_delete_listbox.get(selected_task_index)

    if selected_title in tasks_data:
         # Be sure that task is still in the list (Rarely, race conditions may occur.)
        if selected_task in tasks_data[selected_title]:
            if messagebox.askyesno("Delete Task", f"Are you sure about deleting '{selected_task}' task?", parent=root):
                tasks_data[selected_title].remove(selected_task)
                save_data()
                update_all_display() # Updates all display
                # Update task selection box
                on_combobox_select()
        else:
            messagebox.showerror("Error", "Cannot find the task in this list!", parent=root)
            # Update to fix it
            on_combobox_select()
    else:
         messagebox.showerror("Error", "Cannot find the list of this task!", parent=root)
         update_all_display()

def update_task():
    """Updates selected task (Selected from task selection box)."""
    selected_title = list_combobox.get()
    selected_task_indices = task_delete_listbox.curselection()

    if not selected_title:
        messagebox.showwarning("List Not Selected", "Please select the title of task first.", parent=root)
        return
    if not selected_task_indices:
        messagebox.showwarning("Task Not Selected", "Please select the task first.", parent=root)
        return

    selected_task_index = selected_task_indices[0]
    selected_task = task_delete_listbox.get(selected_task_index)

    if selected_title in tasks_data:
         # Be sure that task is still in the list (Rarely, race conditions may occur.)
        if selected_task in tasks_data[selected_title]:
            new_task = simpledialog.askstring("Update", "Update task", parent=root, initialvalue=selected_task)
            if new_task:
                new_task = new_task.strip()
                if new_task :
                    index_of_selected_task = tasks_data[selected_title].index(selected_task)
                    tasks_data[selected_title][index_of_selected_task] = new_task
                    save_data()
                    update_all_display() # Updates all display
                    # Update task selection box if selected list is same
                    if list_combobox.get() == selected_title:
                        on_combobox_select()
                else:
                    messagebox.showwarning("Invalid Task", "Task content cannot be empty.", parent=root)
        else:
            messagebox.showerror("Error", "Cannot find the task in this list!", parent=root)
            # Tutarsızlığı düzeltmek için güncelle
            on_combobox_select()
    else:
         messagebox.showerror("Error", "Cannot find the list of this task!", parent=root)
         update_all_display()

def move_task_up():
    selected_title = list_combobox.get()
    selected_task_indices = task_delete_listbox.curselection()
    if not selected_title:
        messagebox.showwarning("List Not Selected", "Please select the title of task first.", parent=root)
        return
    if not selected_task_indices:
        messagebox.showwarning("Task Not Selected", "Please select the task first.", parent=root)
        return

    selected_task_index = selected_task_indices[0]
    selected_task = task_delete_listbox.get(selected_task_index)

    selected_task_data_index = tasks_data[selected_title].index(selected_task)

    if selected_task_data_index > 0:
        tasks_data[selected_title][selected_task_data_index],tasks_data[selected_title][selected_task_data_index-1] = tasks_data[selected_title][selected_task_data_index-1],tasks_data[selected_title][selected_task_data_index]
    else:
        messagebox.showwarning("Task cannot moved", "Task is already at the top.", parent=root)

    save_data()
    update_all_display()

def move_task_down():
    selected_title = list_combobox.get()
    selected_task_indices = task_delete_listbox.curselection()
    if not selected_title:
        messagebox.showwarning("List Not Selected", "Please select the title of task first.", parent=root)
        return
    if not selected_task_indices:
        messagebox.showwarning("Task Not Selected", "Please select the task first.", parent=root)
        return

    selected_task_index = selected_task_indices[0]
    selected_task = task_delete_listbox.get(selected_task_index)

    selected_task_data_index = tasks_data[selected_title].index(selected_task)

    if selected_task_data_index < (len(tasks_data[selected_title])-1):
        tasks_data[selected_title][selected_task_data_index],tasks_data[selected_title][selected_task_data_index+1] = tasks_data[selected_title][selected_task_data_index+1],tasks_data[selected_title][selected_task_data_index]
    else:
        messagebox.showwarning("Task cannot moved", "Task is already at the bottom.", parent=root)

    save_data()
    update_all_display()

def move_task():
    selected_title = list_combobox.get()
    selected_task_indices = task_delete_listbox.curselection()
    if not selected_title:
        messagebox.showwarning("List Not Selected", "Please select the title of task first.", parent=root)
        return
    if not selected_task_indices:
        messagebox.showwarning("Task Not Selected", "Please select the task first.", parent=root)
        return

    selected_task_index = selected_task_indices[0]
    selected_task = task_delete_listbox.get(selected_task_index)

    selected_task_data_index = tasks_data[selected_title].index(selected_task)

    popup = tk.Toplevel()
    popup.wm_title("Window")

    popup_button_frame = tk.Frame(popup, bd=1, relief=tk.SUNKEN)
    popup_button_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    list_combobox_popup = ttk.Combobox(popup_button_frame, state="readonly", width=20)
    list_combobox_popup.pack(side=tk.LEFT, padx=5)

    list_titles = list(tasks_data.keys())
    list_combobox_popup['values'] = list_titles
    list_combobox_popup.set(list_titles[0])


    def popup_button_move_clicked():
        new_selected_title = list_combobox_popup.get()
        tasks_data[new_selected_title].append(selected_task)
        tasks_data[selected_title].pop(selected_task_data_index)
        save_data()
        update_all_display()
        popup.destroy()

    popup_button_move = tk.Button(popup_button_frame, text="Move", command=popup_button_move_clicked, width=8)
    popup_button_move.pack(side=tk.LEFT, padx=5)




# --- Main Window and UI Components ---
root = tk.Tk()
root.title("To-Do List App")
root.geometry("700x550") # Adjust window size

import glob
icon_file = glob.glob('Todo List App.png')
if(len(icon_file) == 1):
    p1 = PhotoImage(file = 'Todo List App.png')
    root.iconphoto(False, p1)

# Loads data
load_data()

# --- Upper Control Area ---
control_frame = tk.Frame(root, pady=10)
control_frame.pack(fill=tk.X)

# Adding new list
add_list_button = tk.Button(control_frame, text="New List", command=add_list_title, width=15)
add_list_button.pack(side=tk.LEFT, padx=5)

# List Selection / Deletion
list_combobox = ttk.Combobox(control_frame, state="readonly", width=20)
list_combobox.pack(side=tk.LEFT, padx=5)
list_combobox.bind("<<ComboboxSelected>>", on_combobox_select)


move_title_frame = tk.Frame(control_frame)
move_title_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

move_title_button_up = tk.Button(move_title_frame, text="\u25B2", command=move_title_up, width=2, height=1)
move_title_button_up.pack(side=tk.TOP, padx=5)
move_title_button_down = tk.Button(move_title_frame, text="\u25BC", command=move_title_down, width=2, height=1)
move_title_button_down.pack(side=tk.BOTTOM, padx=5)


delete_list_button = tk.Button(control_frame, text="Delete", command=delete_list_title, width=8)
delete_list_button.pack(side=tk.LEFT, padx=5)

update_list_button = tk.Button(control_frame, text="Update", command=update_list_title, width=8)
update_list_button.pack(side=tk.LEFT, padx=5)

# --- Main Task View Area ---
main_text_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
main_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

main_text_area = scrolledtext.ScrolledText(main_text_frame, wrap=tk.WORD, state=tk.DISABLED, padx=5, pady=5)
# Make initially 'DISABLED' to prevent direct keyboard input.
main_text_area.pack(fill=tk.BOTH, expand=True)


# --- Task Management Area ---
task_action_frame = tk.Frame(root, pady=10)
task_action_frame.pack(fill=tk.X)

# Add New Task (To Selected List)
add_task_button = tk.Button(task_action_frame, text="New Task", command=add_task, width=20)
add_task_button.pack(side=tk.LEFT, padx=10)

# Task Selection / Deletion
delete_task_frame = tk.Frame(task_action_frame)
delete_task_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

task_delete_label = tk.Label(delete_task_frame, text="Select Task:")
task_delete_label.pack(side=tk.LEFT, padx=(0,5))

task_delete_listbox = tk.Listbox(delete_task_frame, height=4, exportselection=False) # exportselection is important
task_delete_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)

move_task_frame = tk.Frame(delete_task_frame)
move_task_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

move_task_button_up = tk.Button(move_task_frame, text="\u25B2", command=move_task_up, width=2, height=1)
move_task_button_up.pack(side=tk.TOP, padx=5)
move_task_button_down = tk.Button(move_task_frame, text="\u25BC", command=move_task_down, width=2, height=1)
move_task_button_down.pack(side=tk.BOTTOM, padx=5)

delete_task_button = tk.Button(delete_task_frame, text="Delete", command=delete_task, width=8)
delete_task_button.pack(side=tk.LEFT, padx=5)

update_task_button = tk.Button(delete_task_frame, text="Update", command=update_task, width=8)
update_task_button.pack(side=tk.LEFT, padx=5)

move_task_button = tk.Button(delete_task_frame, text="Move", command=move_task, width=8)
move_task_button.pack(side=tk.LEFT, padx=5)


# --- Beginning & Ending ---
update_all_display() # Show all data and fill combobox in the beginning

# Save data at the end
root.protocol("WM_DELETE_WINDOW", lambda: (save_data(), root.destroy()))

root.mainloop()