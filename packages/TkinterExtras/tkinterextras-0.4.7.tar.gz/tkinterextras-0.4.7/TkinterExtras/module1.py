from collections import defaultdict
import tkinter as tk
from tkinter import Tk, Frame, StringVar, OptionMenu, Label, Entry, messagebox, Button, END, ttk, Listbox
from typing import Optional, Union, Callable

class DropdownMenu:
    def __init__(self, root:Union[Tk, Frame], options: list[str], default: str = "Select an option") -> None:
        self.root = root
        self.options = options
        self.__default = default

        self.__selectedOption = StringVar()
        self.__selectedOption.set(self.__default)

        self.dropdownMenu = OptionMenu(self.root, self.__selectedOption, *self.options)
    
    @property
    def selectedOption(self) -> str:
        return self.__selectedOption.get()
    
    @property
    def default(self) -> str:
        return self.__default

    def Select(self, selection:str) -> None:
        if selection in self.options or selection == self.default:
            self.__selectedOption.set(selection)

    def bind(self, func: Callable[[str], None]) -> None:
        def callback(*args):
            func(self.selectedOption)
        self.__selectedOption.trace_add("write", callback)

    def pack(self, anchor = "w") -> None:
        self.dropdownMenu.pack(anchor=anchor) # type: ignore
    
    def grid(self, row:int, column:int, sticky: str = "nw") -> None:
        self.dropdownMenu.grid(row=row, column=column, sticky=sticky)

class EditableTable:
    def __init__(self, root:Union[Tk, Frame], numRows: int, numCols: int, maxRows: int | None = None, maxCols: int | None = None, rowHeaders: list[str] | None = None, colHeaders: list[str] | None = None, headerFontSize: int = 20, cellFontSize: int = 10, cellWidth: int = 10, editableRows: list[bool] | None = None, editableCols: list[bool] | None = None, cellBorderWidth: int = 1, entryValidateFunction: Callable[[str, str], bool] | None = None) -> None:
        self.root = root
        self.MIN_ROWS = 2 if colHeaders != None else 1
        self.MIN_COLS = 2 if rowHeaders != None else 1
        self.numRows = numRows
        self.numCols = numCols
        self.maxRows = maxRows if maxRows != None and 1 <= maxRows else None
        self.maxCols = maxCols if maxCols != None and 1 <= maxCols else None
        self.rowHeaders = rowHeaders
        self.colHeaders = colHeaders
        self.headerFontSize = headerFontSize
        self.cellFontSize = cellFontSize
        self.cellWidth = cellWidth
        self.editableRows = editableRows
        self.editableCols = editableCols
        self.cellBorderWidth = cellBorderWidth
        self.entryValidateFunction = entryValidateFunction
        self.entryValidateCommand = self.root.register(self.entryValidateFunction) #type: ignore

        self.cells = {}
        self.data: defaultdict[tuple[int, int], str] = defaultdict(str)

        # Frames
        self.tableFrame = Frame(self.root)
        self.buttonsFrame = Frame(self.root)
        # Pack Frames
        self.tableFrame.pack(anchor="w")
        self.buttonsFrame.pack(anchor="w")

        # Widgets
        self.addRowButton = Button(self.buttonsFrame, text="Add Row", command=self.AddRow) if rowHeaders == None else None
        self.removeRowButton = Button(self.buttonsFrame, text="Remove Row", command=self.RemoveRow) if rowHeaders == None else None

        self.addColButton = Button(self.buttonsFrame, text="Add Column", command=self.AddColumn) if colHeaders == None else None
        self.removeColButton = Button(self.buttonsFrame, text="Remove Column", command=self.RemoveColumn) if colHeaders == None else None
        # Pack Widgets
        if self.addRowButton != None: self.addRowButton.pack(anchor="w")
        if self.removeRowButton != None: self.removeRowButton.pack(anchor="w")
        if self.addColButton != None: self.addColButton.pack(anchor="w")
        if self.removeColButton != None: self.removeColButton.pack(anchor="w")

        self.RenderTable()
    
    def RenderTable(self):
        self.data = defaultdict(str)
        for row in range(self.numRows):
            for col in range(self.numCols):
                if (col, row) not in self.cells.keys(): continue
                cell = self.cells[(col, row)]
                cellType = type(cell)
                if cellType == Entry:
                    self.data[(col, row)] = cell.get() #type: ignore
                elif cellType == Label:
                    self.data[(col, row)] = cell["text"]
        for cell in self.cells.values(): cell.destroy()
        self.cells: dict[tuple[int, int], Label|Entry] = {}
        for row in range(self.numRows):
            for col in range(self.numCols):
                if self.rowHeaders != None and self.colHeaders != None:
                    if row == 0 and col == 0: continue
                    elif row == 0:
                        label = Label(self.tableFrame, text=self.colHeaders[col-1], font=("Helvetica", self.headerFontSize))
                    elif col == 0:
                        label = Label(self.tableFrame, text=self.rowHeaders[row-1], font=("Helvetica", self.headerFontSize))
                    else:
                        if ((self.editableRows != None and self.editableRows[row]) or (self.editableRows == None)) and ((self.editableCols != None and self.editableCols[col]) or (self.editableCols == None)):
                            label = Entry(self.tableFrame, font=("Helvetica", self.cellFontSize), validate="key", validatecommand=(self.entryValidateCommand, '%S', '%P'), width=self.cellWidth)
                            label.insert(0, self.data[(col, row)])
                        else:
                            label = Label(self.tableFrame, text=self.data[(col, row)], font=("Helvetica", self.cellFontSize), borderwidth=self.cellBorderWidth, relief="solid", width=self.cellWidth)
                elif self.rowHeaders != None:
                    if col == 0:
                        label = Label(self.tableFrame, text=self.rowHeaders[row], font=("Helvetica", self.headerFontSize))
                    else:
                        if ((self.editableRows != None and self.editableRows[row]) or (self.editableRows == None)) and ((self.editableCols != None and self.editableCols[col]) or (self.editableCols == None)):
                            label = Entry(self.tableFrame, font=("Helvetica", self.cellFontSize), validate="key", validatecommand=(self.entryValidateCommand, '%S', '%P'), width=self.cellWidth)
                            label.insert(0, self.data[(col, row)])
                        else:
                            label = Label(self.tableFrame, text=self.data[(col, row)], font=("Helvetica", self.cellFontSize), borderwidth=self.cellBorderWidth, relief="solid", width=self.cellWidth)
                elif self.colHeaders != None:
                    if row == 0:
                        label = Label(self.tableFrame, text=self.colHeaders[row], font=("Helvetica", self.headerFontSize))
                    else:
                        if ((self.editableRows != None and self.editableRows[row]) or (self.editableRows == None)) and ((self.editableCols != None and self.editableCols[col]) or (self.editableCols == None)):
                            label = Entry(self.tableFrame, font=("Helvetica", self.cellFontSize), validate="key", validatecommand=(self.entryValidateCommand, '%S', '%P'), width=self.cellWidth)
                            label.insert(0, self.data[(col, row)])
                        else:
                            label = Label(self.tableFrame, text=self.data[(col, row)], font=("Helvetica", self.cellFontSize), borderwidth=self.cellBorderWidth, relief="solid", width=self.cellWidth)
                else:
                    if ((self.editableRows != None and self.editableRows[row]) or (self.editableRows == None)) and ((self.editableCols != None and self.editableCols[col]) or (self.editableCols == None)):
                        label = Entry(self.tableFrame, font=("Helvetica", self.cellFontSize), validate="key", validatecommand=(self.entryValidateCommand, '%S', '%P'), width=self.cellWidth)
                        label.insert(0, self.data[(col, row)])
                    else:
                        label = Label(self.tableFrame, text=self.data[(col, row)], font=("Helvetica", self.cellFontSize), borderwidth=self.cellBorderWidth, relief="solid", width=self.cellWidth)

                self.cells[(col, row)] = label
        for (col, row), label in self.cells.items():
            label.grid(column=col, row=row)
    
    def GetData(self, col: int, row: int) -> str:
        if (col, row) not in self.cells.keys(): return ""
        cell = self.cells[(col, row)]
        cellType = type(cell)
        if cellType == Entry:
            return cell.get() #type: ignore
        elif cellType == Label:
            return cell["text"]
        return ""
    def SetData(self, col: int, row: int, value: str, updateTable: bool = True) -> None:
        if (col, row) not in self.cells.keys(): return
        cell = self.cells[(col, row)]
        cellType = type(cell)
        if cellType == Entry:
            cell.delete(0, END) #type: ignore
            cell.insert(0, value) #type: ignore
        elif cellType == Label:
            cell["text"] = value
        if updateTable: self.RenderTable()

    def AddColumn(self) -> None:
        if self.maxCols != None and self.numCols >= self.maxCols: return
        self.numCols += 1
        self.RenderTable()
    def RemoveColumn(self) -> None:
        if self.numCols > self.MIN_COLS:
            self.numCols -= 1
            self.RenderTable()
        else:
            messagebox.showwarning("Warning", "Cannot remove the last column!")
    def AddRow(self) -> None:
        if self.maxRows != None and self.numRows >= self.maxRows: return
        self.numRows += 1
        self.RenderTable()
    def RemoveRow(self) -> None:
        if self.numRows > self.MIN_ROWS:
            self.numRows -= 1
            self.RenderTable()
        else:
            messagebox.showwarning("Warning", "Cannot remove the last row")
    
    def pack(self, anchor="w") -> None:
        self.root.pack(anchor=anchor) #type: ignore
    def grid(self, row: int, column: int, sticky: str = "nw") -> None:
        self.root.grid(row=row, column=column, sticky=sticky) #type: ignore

class NumericalEntry:
    def __init__(self, root:Union[Tk, Frame], font:tuple) -> None:
        self.root = root
        self.entry = Entry(self.root, font=font, validate="key", validatecommand=(self.root.register(self.validate), '%P'))
    
    @property
    def value(self) -> int:
        val = self.entry.get()
        return int(val) if val.isdigit() else 0

    def validate(self, newValue: str) -> bool:
        return (newValue == "") or (newValue.isdigit() and int(newValue) > 0)

    def pack(self, anchor="w") -> None:
        self.entry.pack(anchor=anchor) #type: ignore
    
    def grid(self, row: int, column: int, sticky: str = "nw") -> None:
        self.entry.grid(row=row, column=column, sticky=sticky) #type: ignore

class ProgressBar:
    def __init__(self, root: Union[Tk, Frame], steps: int, length: int) -> None:
        self.root = root
        self.steps = steps
        self.currentStep = 0
        
        self._bar = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=length,
            mode="determinate",
            maximum=self.steps
        )
    
    def reset(self, newNumSteps: Union[int, None] = None) -> None:
        if newNumSteps != None:
            if newNumSteps < 0:
                raise ValueError("Number of steps must be non-negative")
            self.steps = newNumSteps
            self._bar['maximum'] = self.steps
        self.currentStep = 0
        self._bar['value'] = 0
        self.root.update_idletasks()
    
    def step(self, amount: int = 1) -> None:
        self.currentStep = min(self.currentStep + amount, self.steps)
        self._bar['value'] = self.currentStep
        self.root.update_idletasks()
    
    def setStep(self, step: int) -> None:
        if 0 <= step <= self.steps:
            self.currentStep = step
            self._bar['value'] = self.currentStep
            self.root.update_idletasks()
    
    def isComplete(self) -> bool:
        return self.currentStep >= self.steps
    
    def progressPercent(self) -> float:
        return (self.currentStep / self.steps) * 100 if self.steps > 0 else 0.0
    
    def getBar(self) -> ttk.Progressbar:
        return self._bar

    def pack(self, anchor="w") -> None:
        self._bar.pack(anchor=anchor)  # type: ignore
    
    def grid(self, row: int, column: int, sticky: str = "nw") -> None:
        self._bar.grid(row=row, column=column, sticky=sticky)

class ReorderList(Frame):
    def __init__(
            self,
            root: Union[Tk, Frame],
            items: list[str],
            onReorder: Optional[Callable[[list[str]], None]] = None,
            *listbox_args,
            **frame_kwargs
    ):
        super().__init__(root, **frame_kwargs)

        self.items = items
        self.onReorder = onReorder

        self._scrollbar = ttk.Scrollbar(self, orient="vertical")
        self._listbox = Listbox(
            self,
            selectmode=tk.SINGLE,
            yscrollcommand=self._scrollbar.set,
            activestyle="none",
            exportselection=False,
            *listbox_args
        )
        self._scrollbar.config(command=self._listbox.yview)

        # layout
        self._listbox.grid(row=0, column=0, sticky="nsew")
        self._scrollbar.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # populate
        self._refreshListbox()

        # drag state
        self._dragIndex: Optional[int] = None

        # event bindings for drag and drop
        self._listbox.bind("<Button-1>", self._onButtonPress)
        self._listbox.bind("<B1-Motion>", self._onMotion)
        self._listbox.bind("<ButtonRelease-1>", self._onButtonRelease)

        # support keyboard reordering with Up, Down, Ctrl+Up and Ctrl+Down
        self._listbox.bind("<Up>", self._onUp)
        self._listbox.bind("<Down>", self._onDown)
        self._listbox.bind("<Control-Up>", self._onCtrlUp)
        self._listbox.bind("<Control-Down>", self._onCtrlDown)
    
    def getOrder(self) -> list[str]:
        return list(self.items)
    
    def getSelectedItemIndex(self) -> int:
        selection = self._listbox.curselection()
        if not selection:
            return -1
        return selection[0]
    
    def setItems(self, newItems: list[str]) -> None:
        self.items = newItems
        self._refreshListbox()
    
    def bindListbox(self, sequence: str, func: Callable[[tk.Event], None]) -> None:
        self._listbox.bind(sequence, func)

    def pack(self, *args, **kwargs) -> None:
        super().pack(*args, **kwargs)
    
    def grid(self, *args, **kwargs) -> None:
        super().grid(*args, **kwargs)
    
    def place(self, *args, **kwargs) -> None:
        super().place(*args, **kwargs)
    
    def _selectIndex(self, index: int) -> None:
        n = len(self.items)
        if n == 0: return
        index = max(0, min(index, n - 1))
        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(index)
        self._listbox.activate(index)
        self._listbox.see(index)
    
    def _refreshListbox(self) -> None:
        self._listbox.delete(0, tk.END)
        for it in self.items: self._listbox.insert(tk.END, it)
    
    def _onButtonPress(self, event: tk.Event) -> None:
        try:
            self._listbox.focus_set()
        except Exception:
            pass
        idx = self._listbox.nearest(event.y)
        n = len(self.items)
        if idx < 0 or idx >= n:
            self._dragIndex = None
            return
        self._dragIndex = idx
        # self._listbox.selection_clear(0, tk.END)
        # self._listbox.selection_set(idx)
        # self._listbox.activate(idx)
    
    def _onMotion(self, event: tk.Event) -> None:
        if self._dragIndex is None:
            return
        
        targetIdx = self._listbox.nearest(event.y)
        # clamp target
        targetIdx = max(0, min(targetIdx, len(self.items) - 1))
        if targetIdx == self._dragIndex:
            return
        
        # Move item in the underlying list
        item = self.items.pop(self._dragIndex)
        self.items.insert(targetIdx, item)

        # refresh listbox and keep the moved item selected
        self._refreshListbox()
        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(targetIdx)
        self._listbox.activate(targetIdx)

        self._dragIndex = targetIdx
    
    def _onButtonRelease(self, event: tk.Event) -> None:
        if self._dragIndex is None:
            return
        
        self._dragIndex = None
        
        if self.onReorder:
            try:
                self.onReorder(self.getOrder())
            except Exception:
                import traceback
                traceback.print_exc()
    
    def _onUp(self, event: tk.Event) -> None:
        sel = self._listbox.curselection()
        if not sel:
            self._selectIndex(len(self.items) - 1)
            return
        i = sel[0]
        if i > 0:
            self._selectIndex(i - 1)
    
    def _onDown(self, event: tk.Event) -> None:
        sel = self._listbox.curselection()
        if not sel:
            self._selectIndex(0)
            return
        i = sel[0]
        if i < len(self.items) - 1:
            self._selectIndex(i + 1)
    
    def _onCtrlUp(self, event: tk.Event) -> None:
        sel = self._listbox.curselection()
        if not sel:
            return
        i = sel[0]
        if i == 0:
            return
        self.items[i-1], self.items[i] = self.items[i], self.items[i-1]
        self._refreshListbox()
        self._listbox.selection_set(i-1)
        self._listbox.activate(i-1)
        if self.onReorder:
            try:
                self.onReorder(self.getOrder())
            except Exception:
                import traceback
                traceback.print_exc()
    
    def _onCtrlDown(self, event: tk.Event) -> None:
        sel = self._listbox.curselection()
        if not sel:
            return
        i = sel[0]
        if i >= len(self.items) - 1:
            return
        self.items[i+1], self.items[i] = self.items[i], self.items[i+1]
        self._refreshListbox()
        self._listbox.selection_set(i+1)
        self._listbox.activate(i+1)
        if self.onReorder:
            try:
                self.onReorder(self.getOrder())
            except Exception:
                import traceback
                traceback.print_exc()