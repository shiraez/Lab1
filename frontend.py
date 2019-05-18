from Tkinter import *
from backend import *
from tkinter import messagebox

def logModification(var,*args):
    print('variable '+var+' has been modified')

window=Tk()

upperFrame = Frame(window)

e1_value=StringVar()

label_title = Label(window, text="Title", width=8)
title_value=StringVar()
entry_title=Entry(window,textvariable=title_value)

label_ID = Label(window, text="ID", width=8)
title_ID=StringVar()
entry_ID=Entry(window,textvariable=title_ID)

label_year = Label(window, text="Genres", width=8)
title_year=StringVar()
entry_year=Entry(window,textvariable=title_year)

def viewall():
    listBox.delete(0, END)
    rows = view()
    for row in rows:
        listBox.insert(END, ', '.join(row))

def searchHen():
    listBox.delete(0, END)
    rows = search(title_ID.get(), entry_title.get(),entry_year.get())
    for row in rows:
        listBox.insert(END, ', '.join(row))

def updateSelected():
     text = list(listBox.get(0,END))
     index = listBox.curselection()
     record = listBox.get(listBox.curselection()).split(",")
     id = record[0] if (title_ID.get() == "") else title_ID.get()
     title = record[1] if (entry_title.get() == "") else entry_title.get()
     genres = record[2]if (entry_year.get() == "") else entry_year.get()
     try:
         update(id, title, genres)
     except Exception:
         messagebox.showinfo("Error", "The ID isn't valid")
         return
     listBox.delete(index)
     listBox.insert(index, "{}, {}, {}".format(id, title, genres))



def add_entry():
    listBox.delete(0, END)
    if title_ID.get() == "" or entry_title.get() == "" or entry_year.get() == "":
        messagebox.showinfo("Error", "You need to add all field")

    else:
        if len(search(title_ID.get(), "", "")) >0:
            messagebox.showinfo("Error", "ID already exist")
            return
        try:
            insert_to_db(title_ID.get(), entry_title.get(),entry_year.get())
        except Exception:
            messagebox.showinfo("Error", "the record isn't valid")
            return
        listBox.insert(END, "{}, {}, {}".format(title_ID.get(), entry_title.get(), entry_year.get()))

def delete_entry():
    index = listBox.curselection()
    record = listBox.get(index).split(",")
    id = record[0]
    title = record[1]
    genres = record[2]
    # try:
    delete(id, title, genres)
    # except Exception:
    #     messagebox.showinfo("Error", "The record isn't valid")
    listBox.delete(index)





bView=Button(window,text='View all', width=15,command=viewall)
# bView=Button(window,text='View all', width=15,command=lambda : listBox.insert(END, view()))
bSearch=Button(window,text='Search entry', width=15,command=searchHen)
bAdd=Button(window,text='Add entry', width=15, command=add_entry)
bUpdate=Button(window,text='Update selected', width=15,command=updateSelected)
bDelete=Button(window,text='Delete selected', width=15,command=delete_entry)
bClose=Button(window,text='Close', width=15, command=lambda: window.destroy())

listBox=Listbox(upperFrame, width=35)
scrollbar= Scrollbar(upperFrame, orient="vertical")

label_title.grid(row=0,column=0)
entry_title.grid(row=0,column=1)
label_year.grid(row=0,column=2)
entry_year.grid(row=0,column=3)
label_ID.grid(row=1,column=0)
entry_ID.grid(row=1,column=1)

bView.grid(row=2,column=3)
bSearch.grid(row=3,column=3)
bAdd.grid(row=4,column=3)
bUpdate.grid(row=5,column=3)
bDelete.grid(row=6,column=3)
bClose.grid(row=7,column=3)

upperFrame.grid(row=3, column=0, rowspan=5, columnspan=3)

# listBox.grid(row=0, column=0, columnspan=3)
listBox.pack(side="left", fill="y")
scrollbar.config(command=listBox.yview)
scrollbar.pack(side="right", fill="y")
listBox.config(yscrollcommand=scrollbar.set)

window.mainloop()




