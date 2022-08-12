import tkinter as tk                
from tkinter import font as tkfont
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk,Image
import user_similarity as sim
import stock_viewer as sv

# For Visualization
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.pyplot import Figure
import seaborn as sns
sns.set_style('darkgrid')

class TkPortfolio(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.label_font = tkfont.Font(family='Bahnschrift', size=18)
        self._frame = None
        self.switch_frame(StartPage)
    
    def switch_frame(self, page_name):
        self.update_idletasks()
        
        new_frame = page_name(parent=self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(side="top", fill="both", expand=True)
        
    def switch_stock(self, ticker):
        '''Show a frame for the given page name'''
        new_frame = IndivStockViewer(parent=self,stock=ticker)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(side="top", fill="both", expand=True)
        
    def quit(self):
        self.destroy()

class StartPage(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        logo_img = ImageTk.PhotoImage(Image.open("Images\logo.png"))
        logo_lbl = tk.Label(self,image=logo_img)
        logo_lbl.image = logo_img
        logo_lbl.pack(side="top", fill="x", pady=10)
        
        button1 = tk.Button(self,fg='#494949',font=parent.label_font,text="Portfolio Creator",bd=4,width=20,height=2,
                            command=lambda: parent.switch_frame(PageTwo))
        button2 = tk.Button(self,fg='#494949',font=parent.label_font,text="Stock Tracker",bd=4,width=20,height=2,
                            command=lambda: parent.switch_frame(StockViewerMain))
        button3 = tk.Button(self,fg='#494949',font=parent.label_font,text="Exit",bd=4,width=20,height=2,
                            command=parent.quit)
        button1.pack()
        button2.pack()
        button3.pack()

class StockViewerMain(tk.Frame):

    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, parent)
        entry_font = tkfont.Font(family='Bahnschrift Light', size=16)
        entry_font_bold = tkfont.Font(family='Bahnschrift Light', size=16, weight='bold')

        def handle_enter(e):
            entry = stock_entry.get().upper()
            if not sv.stocks[sv.stocks['Symbol'] == entry].empty:
                parent.switch_stock(entry)
            else:
                messagebox.showwarning("Warning","Stock Symbol Not Found!")

        def handle_click(e):
            if stock_entry.get() == default_txt:
                stock_entry.delete(0,tk.END)
            stock_entry.config(foreground='black')

        def handle_key(e):
            recommend = sim.get_autofill(stock_entry.get())
            stock_entry['values'] = recommend

        search_img = ImageTk.PhotoImage(file = "Images\search.png")
        back_button = tk.Button(self, text="<",font=parent.label_font,width=3,height=1,
                   command=lambda: parent.switch_frame(StartPage))
        entry_button = tk.Button(self,image=search_img,bd=0,command=lambda: self.enter_ticker(stock_entry.get().upper()))
        refresh_button = tk.Button(self,text="Refresh",font=entry_font,command=lambda: parent.switch_frame(StockViewerMain))
        entry_button.image = search_img
        
        #user input
        stock_entry = ttk.Combobox(self, foreground='grey', values=[],
                                   background='white',width=30, font=entry_font)
        default_txt = "Search - Example: \"MSFT\""
        stock_entry.insert(0, default_txt)
        stock_entry.config(foreground='grey')
        stock_entry.bind("<Return>", handle_enter)
        stock_entry.bind("<Button-1>", handle_click)
        stock_entry.bind("<KeyRelease>", handle_key)
        ##

        #DOW Jones and SPY graphs
        timeframes = ["1d","1w","1m","1y","5y"]
        
        sp500 = tk.Frame(self, width=500, height=300)
        spy_current = tk.Label(sp500, text = "S & P 500 (SPY) " + "%.2f" % sv.get_current('SPY') + " USD", font=entry_font)
        spy_change = tk.Label(sp500, font=entry_font)
        self.config_updates(spy_change,sv.get_pct_change('SPY'))
        
        spy_fig = Figure(figsize=(5.5,2.2),dpi=100)
        spy_fig.patch.set_facecolor('#F0F0F0')
        spy_ax = spy_fig.add_subplot(111)
        plot = sns.lineplot(x='timestamp',y='close',lw=0.8,data=sv.get_historical_data('SPY',"1y"),ax=spy_ax)
        plot.set(xlabel=None,ylabel=None)
        spy_canvas = FigureCanvasTkAgg(spy_fig, master=sp500)
        
        spy_current.grid(row=0,column=0,padx=(30,0),columnspan=3)
        spy_change.grid(row=0,column=3,padx=(0,30),columnspan=2)
        spy_canvas.get_tk_widget().grid(row=1,column=0,columnspan=5)
        
        for count,val in enumerate(timeframes):
            tk.Button(sp500,text=val,width=15).grid(row=2,column=count,pady=(15,0))

        dia = tk.Frame(self, width=500, height=300)
        dia_current = tk.Label(dia, text = "Dow Jones (DIA) " + "%.2f" % sv.get_current('DIA') + " USD", font=entry_font)
        dia_change = tk.Label(dia, font=entry_font)
        self.config_updates(dia_change,sv.get_pct_change('DIA'))
        
        dia_fig = Figure(figsize=(5.5,2.2),dpi=100)
        dia_fig.patch.set_facecolor('#F0F0F0')
        dia_ax = dia_fig.add_subplot(111)
        plot = sns.lineplot(x='timestamp',y='close',lw=0.8,data=sv.get_historical_data('DIA',"1y"),ax=dia_ax)
        plot.set(xlabel=None,ylabel=None)
        dia_canvas = FigureCanvasTkAgg(dia_fig, master=dia)
        
        dia_current.grid(row=0,column=0,padx=(30,0),columnspan=3)
        dia_change.grid(row=0,column=3,padx=(0,30),columnspan=2)
        dia_canvas.get_tk_widget().grid(row=1,column=0,columnspan=5)
        
        for count,val in enumerate(timeframes):
            tk.Button(dia,text=val,width=15).grid(row=2,column=count,pady=(15,0))
        
        #blit items on screen
        back_button.grid(row=0,column=0)
        stock_entry.grid(row=0, column=1,columnspan=2,padx=(25,0))
        entry_button.grid(row=0,column=3,padx=(30,0))
        refresh_button.grid(row=0,column=4,padx=(30,0))
        tk.Label(self,text="Today's Market Updates",font=entry_font_bold,fg='#575757').grid(row=1,column=1,pady=(20,15),columnspan=4)
        sp500.grid(row=0,column=5, padx=(45,0), pady=(15,0), rowspan=5)
        dia.grid(row=5,column=5, padx=(45,0), pady=(15,0), rowspan=5)
        
        for count,val in enumerate(sv.gen_random_8()):
            tmp = self.stockPreview(val,self)
            tmp.subframe.grid(row=count+2,column=1,pady=(15,0),padx=10,columnspan=4)
            tmp.update_price()
            
    class stockPreview:
        def __init__(self, stock, instance_main):
            display_font = tkfont.Font(family='Bahnschrift Light', size=18)
            display_font_small = tkfont.Font(family='Bahnschrift Light', size=15)
            self.stock = stock
            self.subframe = tk.Frame(instance_main)
            self.current = tk.Label(self.subframe,font=display_font_small,width=15)
            self.change = tk.Label(self.subframe,font=display_font_small,width=15)
            self.main = instance_main
            
            ticker = tk.Button(self.subframe,text=self.stock,font=display_font,width=13,
                               command=lambda: instance_main.enter_ticker(self.stock))

            ticker.grid(row=0,column=0)
            self.current.grid(row=0,column=1,padx=(15,0))
            self.change.grid(row=0,column=2)
            
        def update_price(self):
            self.current.config(text="%.2f" % sv.get_current(self.stock) + "  USD")
            pct_change = sv.get_pct_change(self.stock)
            self.main.config_updates(self.change,pct_change)
            
    def enter_ticker(self,entry):
        if not sv.stocks[sv.stocks['Symbol'] == entry].empty:
            self.parent.switch_stock(entry)
        else:
            messagebox.showwarning("Warning","Stock Symbol Not Found!")

    def config_updates(self,label,vals):
        if(vals[0] < 0):
            label.config(text=str(vals[0]) + " (" + str(vals[1]) + "%)" + " ▼")
            label.config(fg="#EF2D2D")
        elif(vals[0] > 0):         
            label.config(text="+" + str(vals[0]) + " (" + str(vals[1]) + "%)" + " ▲")
            label.config(fg="#27D224")
        else:
            label.config(text="+0.00 (0.00%)")
            label.config(fg="#27D224")

class IndivStockViewer(tk.Frame):

    def __init__(self, parent, stock):
        tk.Frame.__init__(self, parent)
        self.stock = stock

        back_button = tk.Button(self, text="<",font=parent.label_font,width=3,height=1,
                           command=lambda: parent.switch_frame(StockViewerMain))
        stock_symbol = tk.Label(self, text=self.stock)
        current_price = tk.Label(self, text = sv.get_current(self.stock))
        stock_symbol.grid(row=0,column=1)
        current_price.grid(row=0,column=2)
        back_button.grid(row=0,column=0)

class PageTwo(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        button = tk.Button(self, text="Go to the start page",
                           command=lambda: parent.switch_frame(StartPage))
        button.pack()


if __name__ == "__main__":
    global app
    app = TkPortfolio()
    app.geometry("1280x720")
    app.iconbitmap("Images\icon.ico")
    app.title("TKPortfolio")
    app.mainloop()
