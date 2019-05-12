from tkinter import *
from backend import *

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

label_year = Label(window, text="Year", width=8)
title_year=StringVar()
entry_year=Entry(window,textvariable=title_year)

bView=Button(window,text='View all', width=15,command=lambda : listBox.insert(END, view()))
bSearch=Button(window,text='Search entry', width=15,command=lambda : listBox.insert(END, search(title_ID.get(), entry_title.get(),entry_year.get())))
bAdd=Button(window,text='Add entry', width=15)
bUpdate=Button(window,text='Update selected', width=15)
bDelete=Button(window,text='Delete selected', width=15)
bClose=Button(window,text='Close', width=15, command=lambda: window.destroy())

listBox=Listbox(upperFrame)
scrollbar= Scrollbar(upperFrame)

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

listBox.grid(row=0, column=0)
scrollbar.grid(row=0, column=2)

window.mainloop()


