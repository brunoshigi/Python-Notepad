import tkinter as tk
from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from tkinter import font
import os
import datetime
import json

class CyberpunkNotepad:
    def __init__(self, **kwargs):
        # Initialize main window
        self.__root = tk.Tk()
        self.__root.configure(bg='#120458')  # Dark blue background
        
        # Custom colors for cyberpunk theme
        self.colors = {
            'bg': '#120458',          # Dark blue
            'text_bg': '#1a0061',     # Deeper blue
            'text_fg': '#ff71ce',     # Neon pink
            'menu_bg': '#120458',     # Dark blue
            'menu_fg': '#00ffff',     # Cyan
            'highlight': '#b967ff'     # Purple
        }

        # Window dimensions
        self.__thisWidth = kwargs.get('width', 800)
        self.__thisHeight = kwargs.get('height', 600)
        
        # Initialize UI elements
        self.__thisTextArea = Text(
            self.__root,
            font=('Courier', 12),
            bg=self.colors['text_bg'],
            fg=self.colors['text_fg'],
            insertbackground=self.colors['text_fg'],  # Cursor color
            selectbackground=self.colors['highlight'],
            wrap=WORD
        )
        
        # Create status bar
        self.__statusBar = Label(
            self.__root,
            text="Ready",
            bg=self.colors['bg'],
            fg=self.colors['menu_fg'],
            anchor='w'
        )
        
        # Line numbers
        self.__lineNumbers = Text(
            self.__root,
            width=4,
            bg=self.colors['bg'],
            fg=self.colors['menu_fg'],
            font=('Courier', 12),
        )
        
        # Initialize menus
        self.__createMenus()
        
        # Configure window
        self.__setupWindow()
        
        # File handling
        self.__file = None
        self.__setupAutoSave()
        
        # Initialize themes
        self.__themes = {
            'cyberpunk': {
                'bg': '#120458',
                'text_bg': '#1a0061',
                'text_fg': '#ff71ce',
                'menu_bg': '#120458',
                'menu_fg': '#00ffff',
                'highlight': '#b967ff'
            },
            'vaporwave': {
                'bg': '#330867',
                'text_bg': '#30cfd0',
                'text_fg': '#ff00ff',
                'menu_bg': '#330867',
                'menu_fg': '#00ffff',
                'highlight': '#ff71ce'
            }
        }

    def __setupWindow(self):
        # Window title
        self.__root.title("CyberPad ⚡")
        
        # Center window
        screenWidth = self.__root.winfo_screenwidth()
        screenHeight = self.__root.winfo_screenheight()
        left = (screenWidth / 2) - (self.__thisWidth / 2)
        top = (screenHeight / 2) - (self.__thisHeight / 2)
        self.__root.geometry(f'{self.__thisWidth}x{self.__thisHeight}+{int(left)}+{int(top)}')
        
        # Configure grid
        self.__root.grid_rowconfigure(0, weight=1)
        self.__root.grid_columnconfigure(1, weight=1)
        
        # Place widgets
        self.__lineNumbers.grid(row=0, column=0, sticky='nsew')
        self.__thisTextArea.grid(row=0, column=1, sticky='nsew')
        self.__statusBar.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        # Bind events
        self.__thisTextArea.bind('<Key>', self.__updateLineNumbers)
        self.__thisTextArea.bind('<MouseWheel>', self.__syncScroll)

    def __createMenus(self):
        # Main menu bar
        self.__thisMenuBar = Menu(self.__root, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        
        # File menu
        self.__thisFileMenu = Menu(self.__thisMenuBar, tearoff=0, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        self.__thisFileMenu.add_command(label="New", command=self.__newFile, accelerator="Ctrl+N")
        self.__thisFileMenu.add_command(label="Open", command=self.__openFile, accelerator="Ctrl+O")
        self.__thisFileMenu.add_command(label="Save", command=self.__saveFile, accelerator="Ctrl+S")
        self.__thisFileMenu.add_separator()
        self.__thisFileMenu.add_command(label="Exit", command=self.__quitApplication)
        self.__thisMenuBar.add_cascade(label="File", menu=self.__thisFileMenu)
        
        # Edit menu
        self.__thisEditMenu = Menu(self.__thisMenuBar, tearoff=0, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        self.__thisEditMenu.add_command(label="Cut", command=self.__cut)
        self.__thisEditMenu.add_command(label="Copy", command=self.__copy)
        self.__thisEditMenu.add_command(label="Paste", command=self.__paste)
        self.__thisEditMenu.add_separator()
        self.__thisEditMenu.add_command(label="Find", command=self.__showFindDialog)
        self.__thisEditMenu.add_command(label="Replace", command=self.__showReplaceDialog)
        self.__thisMenuBar.add_cascade(label="Edit", menu=self.__thisEditMenu)
        
        # View menu
        self.__thisViewMenu = Menu(self.__thisMenuBar, tearoff=0, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        self.__thisViewMenu.add_command(label="Toggle Line Numbers", command=self.__toggleLineNumbers)
        self.__thisViewMenu.add_command(label="Toggle Status Bar", command=self.__toggleStatusBar)
        self.__thisMenuBar.add_cascade(label="View", menu=self.__thisViewMenu)
        
        # Theme menu
        self.__thisThemeMenu = Menu(self.__thisMenuBar, tearoff=0, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        self.__thisThemeMenu.add_command(label="Cyberpunk", command=lambda: self.__changeTheme('cyberpunk'))
        self.__thisThemeMenu.add_command(label="Vaporwave", command=lambda: self.__changeTheme('vaporwave'))
        self.__thisMenuBar.add_cascade(label="Theme", menu=self.__thisThemeMenu)
        
        # Help menu
        self.__thisHelpMenu = Menu(self.__thisMenuBar, tearoff=0, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        self.__thisHelpMenu.add_command(label="About", command=self.__showAbout)
        self.__thisMenuBar.add_cascade(label="Help", menu=self.__thisHelpMenu)
        
        self.__root.config(menu=self.__thisMenuBar)

    def __setupAutoSave(self):
        # Auto-save every 5 minutes
        self.__autoSaveInterval = 300000  # 5 minutes in milliseconds
        self.__root.after(self.__autoSaveInterval, self.__autoSave)

    def __autoSave(self):
        if self.__file:
            self.__saveFile()
        self.__updateStatus("Auto-saved")
        self.__root.after(self.__autoSaveInterval, self.__autoSave)

    def __updateLineNumbers(self, event=None):
        # Update line numbers
        lines = self.__thisTextArea.get('1.0', 'end-1c').split('\n')
        line_numbers = '\n'.join(str(i+1).rjust(3) for i in range(len(lines)))
        self.__lineNumbers.delete('1.0', 'end')
        self.__lineNumbers.insert('1.0', line_numbers)

    def __syncScroll(self, event=None):
        # Synchronize scrolling between line numbers and text area
        self.__lineNumbers.yview_moveto(self.__thisTextArea.yview()[0])

    def __toggleLineNumbers(self):
        if self.__lineNumbers.winfo_viewable():
            self.__lineNumbers.grid_remove()
        else:
            self.__lineNumbers.grid()

    def __toggleStatusBar(self):
        if self.__statusBar.winfo_viewable():
            self.__statusBar.grid_remove()
        else:
            self.__statusBar.grid()

    def __updateStatus(self, message):
        self.__statusBar.config(text=message)
        # Clear message after 3 seconds
        self.__root.after(3000, lambda: self.__statusBar.config(text="Ready"))

    def __changeTheme(self, theme_name):
        if theme_name in self.__themes:
            theme = self.__themes[theme_name]
            self.colors = theme
            
            # Update UI colors
            self.__root.configure(bg=theme['bg'])
            self.__thisTextArea.configure(
                bg=theme['text_bg'],
                fg=theme['text_fg'],
                insertbackground=theme['text_fg'],
                selectbackground=theme['highlight']
            )
            self.__statusBar.configure(bg=theme['bg'], fg=theme['menu_fg'])
            self.__lineNumbers.configure(bg=theme['bg'], fg=theme['menu_fg'])
            
            # Update menus
            for menu in [self.__thisFileMenu, self.__thisEditMenu, self.__thisViewMenu, 
                        self.__thisThemeMenu, self.__thisHelpMenu]:
                menu.configure(bg=theme['menu_bg'], fg=theme['menu_fg'])
            
            self.__updateStatus(f"Theme changed to {theme_name}")

    def __showFindDialog(self):
        find_dialog = Toplevel(self.__root)
        find_dialog.title("Find")
        find_dialog.geometry("300x100")
        find_dialog.configure(bg=self.colors['bg'])
        
        Label(find_dialog, text="Find what:", bg=self.colors['bg'], fg=self.colors['menu_fg']).pack(pady=5)
        find_entry = Entry(find_dialog, bg=self.colors['text_bg'], fg=self.colors['text_fg'])
        find_entry.pack(pady=5)
        
        Button(
            find_dialog,
            text="Find",
            command=lambda: self.__findText(find_entry.get()),
            bg=self.colors['menu_bg'],
            fg=self.colors['menu_fg']
        ).pack(pady=5)

    def __findText(self, query):
        # Remove previous tags
        self.__thisTextArea.tag_remove('found', '1.0', END)
        
        if query:
            idx = '1.0'
            while True:
                idx = self.__thisTextArea.search(query, idx, nocase=1, stopindex=END)
                if not idx:
                    break
                lastidx = f'{idx}+{len(query)}c'
                self.__thisTextArea.tag_add('found', idx, lastidx)
                idx = lastidx
            
            self.__thisTextArea.tag_config('found', background=self.colors['highlight'])

    def __showReplaceDialog(self):
        replace_dialog = Toplevel(self.__root)
        replace_dialog.title("Replace")
        replace_dialog.geometry("300x150")
        replace_dialog.configure(bg=self.colors['bg'])
        
        Label(replace_dialog, text="Find what:", bg=self.colors['bg'], fg=self.colors['menu_fg']).pack(pady=5)
        find_entry = Entry(replace_dialog, bg=self.colors['text_bg'], fg=self.colors['text_fg'])
        find_entry.pack(pady=5)
        
        Label(replace_dialog, text="Replace with:", bg=self.colors['bg'], fg=self.colors['menu_fg']).pack(pady=5)
        replace_entry = Entry(replace_dialog, bg=self.colors['text_bg'], fg=self.colors['text_fg'])
        replace_entry.pack(pady=5)
        
        Button(
            replace_dialog,
            text="Replace All",
            command=lambda: self.__replaceText(find_entry.get(), replace_entry.get()),
            bg=self.colors['menu_bg'],
            fg=self.colors['menu_fg']
        ).pack(pady=5)

    def __replaceText(self, find_str, replace_str):
        content = self.__thisTextArea.get(1.0, END)
        new_content = content.replace(find_str, replace_str)
        self.__thisTextArea.delete(1.0, END)
        self.__thisTextArea.insert(1.0, new_content)
        self.__updateStatus(f"Replaced all occurrences of '{find_str}' with '{replace_str}'")

    def __showAbout(self):
        showinfo("CyberPad", "A cyberpunk-themed notepad for the digital age.\n\nFeatures:\n- Auto-save\n- Find & Replace\n- Line numbers\n- Multiple themes\n\nCreated with ♥ in 2024")

    # Maintain existing file operations with updated styling
    def __newFile(self):
        self.__root.title("Untitled - CyberPad ⚡")
        self.__file = None
        self.__thisTextArea.delete(1.0, END)
        self.__updateLineNumbers()
        self.__updateStatus("New file created")

    def __openFile(self):
        self.__file = askopenfilename(defaultextension=".txt",
                                    filetypes=[("All Files", "*.*"),
                                             ("Text Documents", "*.txt")])
        if self.__file:
            self.__root.title(os.path.basename(self.__file) + " - CyberPad ⚡")
            self.__thisTextArea.delete(1.0, END)
            with open(self.__file, "r") as file:
                self.__thisTextArea.insert(1.0, file.read())
            self.__updateLineNumbers()
            self.__updateStatus("File opened successfully")

    def __saveFile(self):
        if not self.__file:
            self.__file = asksaveasfilename(initialfile='Untitled.txt',
                                          defaultextension=".txt",
                                          filetypes=[("All Files", "*.*"),
                                                   ("Text Documents", "*.txt")])
        if self.__file:
            with open(self.__file, "w") as file:
                file.write(self.__thisTextArea.get(1.0, END))
            self.__root.title(os.path.basename(self.__file) + " - CyberPad ⚡")
            self.__updateStatus("File saved successfully")

    def __cut(self):
        self.__thisTextArea.event_generate("<<Cut>>")
        self.__updateStatus("Text cut to clipboard")

    def __copy(self):
        self.__thisTextArea.event_generate("<<Copy>>")
        self.__updateStatus("Text copied to clipboard")

    def __paste(self):
        self.__thisTextArea.event_generate("<<Paste>>")
        self.__updateStatus("Text pasted from clipboard")

    def __quitApplication(self):
        if self.__file and messagebox.askyesno("Save?", "Do you want to save before exiting?"):
            self.__saveFile()
        self.__root.destroy()

    def __setupShortcuts(self):
        # File operations
        self.__thisTextArea.bind('<Control-n>', lambda e: self.__newFile())
        self.__thisTextArea.bind('<Control-o>', lambda e: self.__openFile())
        self.__thisTextArea.bind('<Control-s>', lambda e: self.__saveFile())
        
        # Edit operations
        self.__thisTextArea.bind('<Control-f>', lambda e: self.__showFindDialog())
        self.__thisTextArea.bind('<Control-h>', lambda e: self.__showReplaceDialog())
        
        # Text formatting
        self.__thisTextArea.bind('<Control-l>', lambda e: self.__toggleWordWrap())
        self.__thisTextArea.bind('<Control-plus>', lambda e: self.__changeFontSize(1))
        self.__thisTextArea.bind('<Control-minus>', lambda e: self.__changeFontSize(-1))

    def __toggleWordWrap(self):
        current_wrap = self.__thisTextArea.cget('wrap')
        new_wrap = 'none' if current_wrap == 'word' else 'word'
        self.__thisTextArea.configure(wrap=new_wrap)
        self.__updateStatus(f"Word wrap {'enabled' if new_wrap == 'word' else 'disabled'}")

    def __changeFontSize(self, delta):
        current_font = font.Font(font=self.__thisTextArea['font'])
        new_size = current_font.actual()['size'] + delta
        if 8 <= new_size <= 72:  # Reasonable font size limits
            new_font = font.Font(family=current_font.actual()['family'], size=new_size)
            self.__thisTextArea.configure(font=new_font)
            self.__lineNumbers.configure(font=new_font)
            self.__updateStatus(f"Font size: {new_size}")

    def __showTextStats(self):
        content = self.__thisTextArea.get(1.0, END)
        
        # Calculate statistics
        char_count = len(content) - 1  # Subtract 1 for the final newline
        word_count = len(content.split())
        line_count = len(content.splitlines())
        
        # Create stats window
        stats_dialog = Toplevel(self.__root)
        stats_dialog.title("Text Statistics")
        stats_dialog.geometry("300x200")
        stats_dialog.configure(bg=self.colors['bg'])
        
        # Display statistics
        stats_text = f"""Characters: {char_count}
Words: {word_count}
Lines: {line_count}
Average word length: {char_count/word_count:.1f}
Characters per line: {char_count/line_count:.1f}"""
        
        Label(
            stats_dialog,
            text=stats_text,
            bg=self.colors['bg'],
            fg=self.colors['menu_fg'],
            justify=LEFT,
            font=('Courier', 12)
        ).pack(pady=20, padx=20)
        
        Button(
            stats_dialog,
            text="Close",
            command=stats_dialog.destroy,
            bg=self.colors['menu_bg'],
            fg=self.colors['menu_fg']
        ).pack(pady=10)

    def run(self):
        # Set up keyboard shortcuts
        self.__setupShortcuts()
        
        # Add text stats to View menu
        self.__thisViewMenu.add_separator()
        self.__thisViewMenu.add_command(label="Text Statistics", command=self.__showTextStats)
        
        # Run main application
        self.__root.mainloop()

# Create and run the notepad
if __name__ == "__main__":
    notepad = CyberpunkNotepad(width=800, height=600)
    notepad.run()