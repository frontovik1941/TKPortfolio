import tkinter as tk                
from tkinter import font as tkfont
from tkinter import ttk, messagebox, filedialog
from PIL import ImageTk,Image
import user_similarity as sim
import stock_viewer as sv
import pf_manager as pfm
from pandastable import Table
import os

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
        new_frame = page_name(parent=self)
        self.show_new_frame(new_frame)
        
    def switch_stock(self, ticker):
        new_frame = IndivStockViewer(parent=self,stock=ticker)
        self.show_new_frame(new_frame)

    def switch_portfolio(self, portfolio):
        new_frame = PortfolioEdit(parent=self,saved=portfolio)
        self.show_new_frame(new_frame)

    def show_new_frame(self,new_frame):
        self.update_idletasks()
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
                            command=lambda: parent.switch_frame(PortfolioLoad))
        button2 = tk.Button(self,fg='#494949',font=parent.label_font,text="Stock Screener",bd=4,width=20,height=2,
                            command=lambda: parent.switch_frame(StockViewerMain))
        button3 = tk.Button(self,fg='#494949',font=parent.label_font,text="Exit",bd=4,width=20,height=2,
                            command=parent.quit)
        button1.pack()
        button2.pack()
        button3.pack()

class PortfolioLoad(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        tk.Button(self, text="<",font=parent.label_font,width=3,height=1,command=lambda: parent.switch_frame(StartPage)).place(relx=0,rely=0)
        button_frame = tk.Frame(self)
        tk.Button(button_frame,fg='#494949',font=parent.label_font,text="Start New Portfolio",bd=4,width=30,height=2,command=lambda: parent.switch_portfolio(None)).pack()
        tk.Button(button_frame,fg='#494949',font=parent.label_font,text="Load Existing Portfolio",bd=4,width=30,height=2,command=self.ask_fileopen).pack()
        button_frame.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

    def ask_fileopen(self):
        filename = filedialog.askopenfilename(title="Select a File",filetypes=(("CSV","*.csv"),("TXT","*.txt")))
        if filename != "":
            self.parent.switch_portfolio(filename)

class PortfolioEdit(tk.Frame):

    def __init__(self,parent,saved):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        tk.Button(self, text="<",font=parent.label_font,width=3,height=1,command=self.ask_save).place(relx=0,rely=0)

        if(saved == None):
            self.current = pfm.create_new()
        else:
            self.current = pfm.load_existing(saved)

        title_font = tkfont.Font(family='Helvetica Neue', weight='bold',size=26)
        tk.Label(self, text="Portfolio Editor",font=title_font,fg="#444444").place(relx=0.5,rely=0.05,anchor=tk.CENTER)
        
    def ask_save(self):
        ans = messagebox.askyesno("Save and Quit","Would you like to save your portfolio?")
        if(ans == 0):
            self.parent.switch_frame(PortfolioLoad)
        #else:
            #put file save here

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

        #DOW Jones and SPY graphs
        timeframes = ["1d","1w","1m","1y","5y"]
        
        sp500 = tk.Frame(self, width=500, height=300)
        spy_current = tk.Label(sp500, text = "S & P 500 (SPY) " + "%.2f" % sv.get_current('SPY') + " USD", font=entry_font)
        spy_change = tk.Label(sp500, font=entry_font)
        config_updates(spy_change,sv.get_pct_change('SPY'))
        
        spy_current.grid(row=0,column=0,padx=(30,0),columnspan=3)
        spy_change.grid(row=0,column=3,padx=(0,30),columnspan=2)
        tk.Button(sp500,text="1d",width=15,command=lambda: update_graph("1d",'SPY',sp500,5.5,2.2,1,0,1,5)).grid(row=2,column=0,pady=(15,0))
        tk.Button(sp500,text="1w",width=15,command=lambda: update_graph("1w",'SPY',sp500,5.5,2.2,1,0,1,5)).grid(row=2,column=1,pady=(15,0))
        tk.Button(sp500,text="1m",width=15,command=lambda: update_graph("1m",'SPY',sp500,5.5,2.2,1,0,1,5)).grid(row=2,column=2,pady=(15,0))
        tk.Button(sp500,text="1y",width=15,command=lambda: update_graph("1y",'SPY',sp500,5.5,2.2,1,0,1,5)).grid(row=2,column=3,pady=(15,0))
        tk.Button(sp500,text="5y",width=15,command=lambda: update_graph("5y",'SPY',sp500,5.5,2.2,1,0,1,5)).grid(row=2,column=4,pady=(15,0))

        dia = tk.Frame(self, width=500, height=300)
        dia_current = tk.Label(dia, text = "Dow Jones (DIA) " + "%.2f" % sv.get_current('DIA') + " USD", font=entry_font)
        dia_change = tk.Label(dia, font=entry_font)
        config_updates(dia_change,sv.get_pct_change('DIA'))
        
        dia_current.grid(row=0,column=0,padx=(30,0),columnspan=3)
        dia_change.grid(row=0,column=3,padx=(0,30),columnspan=2)
        tk.Button(dia,text="1d",width=15,command=lambda: update_graph("1d",'DIA',dia,5.5,2.2,1,0,1,5)).grid(row=2,column=0,pady=(15,0))
        tk.Button(dia,text="1w",width=15,command=lambda: update_graph("1w",'DIA',dia,5.5,2.2,1,0,1,5)).grid(row=2,column=1,pady=(15,0))
        tk.Button(dia,text="1m",width=15,command=lambda: update_graph("1m",'DIA',dia,5.5,2.2,1,0,1,5)).grid(row=2,column=2,pady=(15,0))
        tk.Button(dia,text="1y",width=15,command=lambda: update_graph("1y",'DIA',dia,5.5,2.2,1,0,1,5)).grid(row=2,column=3,pady=(15,0))
        tk.Button(dia,text="5y",width=15,command=lambda: update_graph("5y",'DIA',dia,5.5,2.2,1,0,1,5)).grid(row=2,column=4,pady=(15,0))

        update_graph("1y","SPY",sp500,5.5,2.2,1,0,1,5)
        update_graph("1y","DIA",dia,5.5,2.2,1,0,1,5)
        
        #blit items on screen
        back_button.grid(row=0,column=0)
        stock_entry.grid(row=0, column=1,columnspan=2,padx=(25,0))
        entry_button.grid(row=0,column=3,padx=(30,0))
        refresh_button.grid(row=0,column=4,padx=(30,0))
        tk.Label(self,text="Today's Market Updates",font=entry_font_bold,fg='#575757').grid(row=1,column=1,pady=(20,15),columnspan=4)
        sp500.grid(row=0,column=5, padx=(20,0), pady=(25,0), rowspan=5)
        dia.grid(row=5,column=5, padx=(20,0), pady=(25,0), rowspan=5)
        
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
            config_updates(self.change,pct_change)
            
    def enter_ticker(self,entry):
        if not sv.stocks[sv.stocks['Symbol'] == entry].empty:
            self.parent.switch_stock(entry)
        else:
            messagebox.showwarning("Warning","Stock Symbol Not Found!")

class IndivStockViewer(tk.Frame):

    def __init__(self, parent, stock):
        tk.Frame.__init__(self, parent)
        title_font = tkfont.Font(family='Helvetica Neue', weight='bold',size=26)
        small_font = tkfont.Font(family='Helvetica Neue', weight='bold',size=18)
        lbl_font = tkfont.Font(family='Bahnschrift Light', size=14)
        lbl_font_bold = tkfont.Font(family='Bahnschrift Light', weight='bold', size=14)
        lbl_small = tkfont.Font(family='Bahnschrift Light', size=12)
        
        self.stock = stock
        self.current = tk.Label(self, text = sv.get_current(self.stock), font=title_font, fg="#444444")
        self.change = tk.Label(self,font=small_font)
        info_frame = tk.Frame(self, width=450, height=550)
        graph_frame = tk.Frame(self, width=500, height=550)
        profile_frame = tk.Frame(self, width=460, height=210)
        financials_frame = tk.Frame(self, width=200, height=210)
        stats_frame = tk.Frame(self, width=450, height=210)

        back_button = tk.Button(self, text="<",font=parent.label_font,width=3,height=1,
                           command=lambda: parent.switch_frame(StockViewerMain))

        stock_info = sv.get_stock_info(self.stock)

        stock_symbol = tk.Label(self, text=stock_info['shortName'] + " (" + self.stock + ")",font=title_font, fg="#444444")
        refresh_button = tk.Button(self,text="Refresh",font=lbl_font,command=lambda: parent.switch_stock(self.stock))
        fullsize_button = tk.Button(self,text="View Full Size",font=lbl_small)

        back_button.place(relx=0,rely=0)
        stock_symbol.place(x=80,y=10)
        fullsize_button.place(x=850,y=15)
        refresh_button.place(x=1180,y=10)
        self.current.place(x=80,y=70)
        self.change.place(x=300,y=75)
        info_frame.place(x=82,y=130)
        graph_frame.place(x=500,y=25)
        financials_frame.place(x=580,y=480)
        profile_frame.place(x=800,y=480)
        stats_frame.place(x=82,y=480)

        #info_frame
        tk.Label(info_frame,text="Previous Close: " + str(sv.get_prev_close(self.stock)), fg="#444444", font=small_font).place(x=0,y=0)

        info_dict = {'Market Cap':'marketCap','52 Week High':'fiftyTwoWeekHigh','P/E Ratio (TTM)':'trailingPE',
                     'EPS (TTM)':'trailingEps','Volume':'regularMarketVolume','Beta (5Y Monthly)':'beta',
                     'Profit Margin':'profitMargins'}

        for count, key in enumerate(info_dict):
            tk.Label(info_frame,text=key + ": ", fg="#444444", font=lbl_font).place(x=0,y=70 + 35*count)
            try:
                if key == 'Market Cap' or key == 'Volume':
                    tk.Label(info_frame,text=str(format_num(stock_info[info_dict[key]])), fg="#444444", width=17, font=lbl_font_bold, anchor="e").place(x=180,y=70 + 35*count)
                elif key == 'Profit Margin':
                    tk.Label(info_frame,text="%.2f" % (stock_info[info_dict[key]] * 100) + "%", fg="#444444", width=17, font=lbl_font_bold, anchor="e").place(x=180,y=70 + 35*count)
                else:
                    tk.Label(info_frame,text="%.2f" % stock_info[info_dict[key]], fg="#444444", width=17, font=lbl_font_bold, anchor="e").place(x=180,y=70 + 35*count)
            except:
                tk.Label(info_frame,text="-", fg="#444444", width=17, font=lbl_font_bold, anchor="e").place(x=180,y=70 + 35*count)

        #stats_frame
        tk.Label(stats_frame,text="Statistics Today",font=lbl_font_bold).place(x=0,y=0)

        stats_dict= {'Market Open':'regularMarketOpen','Day High':'dayHigh','Day Low':'dayLow','Bid':('bid','bidSize')}
        for count, key in enumerate(stats_dict):
            tk.Label(stats_frame,text=key + ": ", fg="#444444", font=lbl_font).place(x=0,y=50 + 35*count)
            if key == 'Bid':
                try:
                    tk.Label(stats_frame,text="%.2f" % stock_info[stats_dict[key][0]] + " x " + str(stock_info[stats_dict[key][1]]), fg="#444444",
                                                  width=17, font=lbl_font_bold, anchor="e").place(x=180,y=50 + 35*count)
                except:
                    tk.Label(stats_frame,text="-", fg="#444444", width=17, font=lbl_font_bold, anchor="e").place(x=180,y=50 + 35*count)
            else:
                try:
                    tk.Label(stats_frame,text="%.2f" % stock_info[stats_dict[key]], fg="#444444", width=17, font=lbl_font_bold, anchor="e").place(x=180,y=50 + 35*count)
                except:
                    tk.Label(stats_frame,text="-", fg="#444444", width=17, font=lbl_font_bold, anchor="e").place(x=180,y=50 + 35*count)

        #graph_frame
        update_graph('1y',self.stock,graph_frame,8,4,0,0,1,7)
        tk.Label(graph_frame,text="",width=15).grid(row=1,column=0,pady=(15,0))
        tk.Button(graph_frame,text="1d",width=15,command=lambda: update_graph("1d",self.stock,graph_frame,8,4,0,0,1,7)).grid(row=1,column=1)
        tk.Button(graph_frame,text="1w",width=15,command=lambda: update_graph("1w",self.stock,graph_frame,8,4,0,0,1,7)).grid(row=1,column=2)
        tk.Button(graph_frame,text="1m",width=15,command=lambda: update_graph("1m",self.stock,graph_frame,8,4,0,0,1,7)).grid(row=1,column=3)
        tk.Button(graph_frame,text="1y",width=15,command=lambda: update_graph("1y",self.stock,graph_frame,8,4,0,0,1,7)).grid(row=1,column=4)
        tk.Button(graph_frame,text="5y",width=15,command=lambda: update_graph("5y",self.stock,graph_frame,8,4,0,0,1,7)).grid(row=1,column=5)
        tk.Label(graph_frame,text="",width=15).grid(row=1,column=6,pady=(15,0))

        #profile_frame
        tk.Label(profile_frame,text="Company Profile",font=lbl_font_bold).place(x=0,y=0)
        tk.Label(profile_frame,text="Sector: " + stock_info['sector'],font=lbl_small).place(x=0,y=60)
        tk.Label(profile_frame,text="Country: " + stock_info['country'],font=lbl_small).place(x=0,y=85)
        tk.Label(profile_frame,text="Address: " + stock_info['address1'],font=lbl_small).place(x=0,y=110)
        tk.Label(profile_frame,text="Website: " + stock_info['website'],font=lbl_small).place(x=0,y=135)
        tk.Label(profile_frame,text="Full-Time Employees: " + str(stock_info['fullTimeEmployees']),font=lbl_small).place(x=0,y=160)

        #financials_frame
        tk.Label(financials_frame,text="Financials",font=lbl_font_bold).grid(row=0,column=0)
        tk.Button(financials_frame,text="Income Statement",font=lbl_small,width=15,command=lambda: self.show_financial("Income Statement",self.stock)).grid(row=1,column=0,pady=(25,0))
        tk.Button(financials_frame,text="Balance Sheet",font=lbl_small,width=15,command=lambda: self.show_financial("Balance Sheet",self.stock)).grid(row=2,column=0,pady=15)
        tk.Button(financials_frame,text="Cash Flow",font=lbl_small,width=15,command=lambda: self.show_financial("Cash Flow",self.stock)).grid(row=3,column=0)
        
        self.update_price()

    def update_price(self):
        self.current.config(text="%.2f" % sv.get_current(self.stock) + "  USD")
        pct_change = sv.get_pct_change(self.stock)
        config_updates(self.change,pct_change)

    def show_financial(self,sheet_type,stock):
        response = messagebox.askokcancel("Notice","Opening in new window. Proceed?")
        if(response == 1):
            display = tk.Toplevel(self)
            display.title(sheet_type)
            display.geometry("800x500")
            display.iconbitmap("Images\icon.ico")
            display.resizable(False, False)
            if(sheet_type == "Income Statement"):
                data = sv.get_income_statement(stock)
            elif(sheet_type == "Balance Sheet"):
                data = sv.get_balance_sheet(stock)
            else:
                data = sv.get_cash_flow(stock)

            data.fillna("NONE",inplace=True)
            frame = tk.Frame(display)
            frame.pack(fill='y',expand=True)
            table = Table(frame,dataframe=data,editable=False,showtoolbar=False, showstatusbar=True, maxcellwidth=175)
            table.showIndex()
            table.show()
            
        else:
            return

def get_graph(timeframe,index,frame,figx,figy):
    tmp = Figure(figsize=(figx,figy),dpi=100)
    tmp.patch.set_facecolor('#F0F0F0')
    tmp_ax = tmp.add_subplot(111)

    info_df = sv.get_historical_data(index,timeframe)
    plot = sns.lineplot(x='timestamp',y='close',lw=0.8,data=info_df,ax=tmp_ax)
    plot.set(xlabel=None,ylabel=None)
    return FigureCanvasTkAgg(tmp, master=frame)

def update_graph(timeframe,index,frame,figx,figy,row,col,rowsp,colsp):
    new_canvas = get_graph(timeframe,index,frame,figx,figy)
    new_canvas.draw()
    new_canvas.get_tk_widget().grid(row=row,column=col,rowspan=rowsp,columnspan=colsp)

def config_updates(label,vals):
    if(vals[0] < 0):
        label.config(text=str(vals[0]) + " (" + str(vals[1]) + "%)" + " ▼")
        label.config(fg="#EF2D2D")
    elif(vals[0] > 0):         
        label.config(text="+" + str(vals[0]) + " (" + str(vals[1]) + "%)" + " ▲")
        label.config(fg="#27D224")
    else:
        label.config(text="+0.00 (0.00%)")
        label.config(fg="#27D224")

def format_num(n):
    suffix = [""," M"," B"," T"]
    vals = [1,1e6,1e9,1e12]
    for i in range(len(vals) - 1):
        if vals[i + 1] > n:
            return str(round(n/vals[i],2)) + suffix[i]
        elif n > vals[-1]:
            return str(round(n/vals[-1],2)) + suffix[-1]
    return ""

if __name__ == "__main__":
    global app
    app = TkPortfolio()
    
    app.geometry("1280x720")
    app.iconbitmap("Images\icon.ico")
    app.title("TKPortfolio")
    app.resizable(False, False)
    app.mainloop()
