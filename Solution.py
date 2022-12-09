import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import pandas as pd


def total_returns(all_data, num_stocks, initial_portfolio_value):
    # Start a list that will keep track of the portfolios % change day by day
    percent_change = []
    # for each day
    num_days = len(all_data[0]) - 1
    for i in range(1, num_days):
        # declare a list that will hold all the prices for the stocks
        new_prices = []
        # For each stock
        indx = 0
        for dataframe in all_data:
            indx = indx + 1
            # grab the prices for all the stocks at the current day
            new_prices.append(dataframe.iloc[i]["Open"])

        # calculate the new value of the portfolio
        new_value = np.dot(num_stocks, new_prices)

        # calculate the difference
        diff = new_value - initial_portfolio_value

        # calculate the percent change
        percent_change.append(diff / initial_portfolio_value)

    return percent_change


def daily_returns(all_data, num_stocks, initial_portfolio_value):
    # Start a list that will keep track of the portfolios % change day by day
    percent_chage = []
    cash_values = []
    # for each day
    for i in range(1, len(all_data[0]) - 1):
        # declare a list that will hold all the prices for the stocks
        new_prices = []
        # For each stock
        for dataframe in all_data:
            # grab the prices for all the stocks at the current day
            new_prices.append(dataframe.iloc[i]["Open"])

        # calculate the new value of the portfolio
        new_value = np.dot(num_stocks, new_prices)
        cash_values.append(new_value)

        # calculate the difference
        diff = new_value - initial_portfolio_value

        initial_portfolio_value = new_value
        # calculate the percent change
        percent_chage.append(diff / initial_portfolio_value)

    return percent_chage, cash_values


def plot_cash_value(cash_values, spvalue, dates):
    plt.plot(dates, cash_values, label='Portfolio Cash Value')
    plt.plot(dates, spvalue, label='S&P 500 Cash Value')
    plt.xlabel("Dates")
    plt.ylabel("Cash Value of Portfolio vs S&P 500")
    plt.legend()
    plt.title("Cash Value of Portfolio")
    fig = plt.figure(figsize=(5, 5),
                     dpi=100)
    newWindow = tk.Toplevel(window)
    canvas = FigureCanvasTkAgg(fig,
                               master=newWindow)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().pack()



def plot_returns(dates, drl, startindex=0):
    point = drl[startindex]
    x1 = dates[startindex]
    for i in range(startindex, len(drl) - 1):
        nextPoint = drl[i]
        xs = [x1, dates[i]]
        ys = [point, nextPoint]
        if nextPoint < point:
            # negative slope
            plt.plot(xs, ys, color='r')

        else:
            # positive or horizontial slope
            plt.plot(xs, ys, color='g')
        x1 = dates[i]
        point = nextPoint

    plt.title("Daily Returns of Portfolio")
    plt.xlabel("Date")
    plt.ylabel("% Change")
    fig = plt.figure(figsize=(5, 5),
                     dpi=100)
    newWindow = tk.Toplevel(window)
    canvas = FigureCanvasTkAgg(fig,
                               master=newWindow)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().pack()


def return_data(drl):
    num_pos_days = 0
    num_neg_days = 0
    point = drl[0]
    for i in range(1, len(drl) - 1):
        nextPoint = drl[i]

        if nextPoint < point:
            # negative slope
            num_neg_days = num_neg_days + 1

        else:
            # positive or horizontial slope
            num_pos_days = num_pos_days + 1

        point = nextPoint
    return num_pos_days, num_neg_days


def adjust_dataframes(all_data):
    # check to make sure the latest date matches for all stocks
    shortest_length = len(all_data[0])
    first_date = all_data[0].index[0]
    latest_date = first_date
    for j in range(1, len(all_data)):
        # if the amount of data is lower than the first (we can use < because it cannot be longer than
        # since we specified a start date. It can only be equal to or less than)
        current_dataframe_length = len(all_data[j])
        if current_dataframe_length < shortest_length:
            # if the lengths are different set the shortest length equal to the new length
            shortest_length = current_dataframe_length

            # grab the starting date of the new dataframe
            latest_date = all_data[j].index[0]

    # make sure that all dataframes start at the correct date
    updated_data = []
    for frame in all_data:
        updated_data.append(frame.loc[latest_date:])

    return updated_data, latest_date


def performance(tickers, weights, init_investment, start_date, plot=False, daily_return_plot_start_idx=0):
    init_value = []
    num_stocks = []
    init_stock_price = []
    all_data = []

    # grab all the data we need
    for ticker in tickers:
        all_data.append(yf.download(ticker, start=start_date, interval="1d"))

    updated_data, latest_date = adjust_dataframes(all_data)

    all_data = updated_data
    # grab SPY data
    spy = yf.download("SPY", start=start_date, interval='1d')

    # start price of SPY
    spy_start_price = spy.loc[latest_date]["Open"]

    # number of shares of SPY that could be bought
    num_spy_shares = init_investment / spy_start_price

    # initial cash value
    init_spy_value = num_spy_shares * spy_start_price

    # End SPY price (most current infor)
    end_spy_price = spy.iloc[len(spy) - 1]["Open"]

    # set the spy dataframe equal to the subframe that starts at the earliest date available that all stocks
    # were available to trade.
    spy = spy.loc[latest_date:]

    # for each dataframe
    indexer = 0
    data = ""
    for frame in all_data:
        cash_value = weights[indexer] * init_investment
        # initial stock price is of that position on the open
        init_stock_price.append(frame.iloc[0]["Open"])

        # number of stocks that could be purchased given the amount of cash for that position
        num_stocks.append(round(cash_value / frame.iloc[0]["Open"], 2))

        # initial cash value (should be close to the cash value that was determined above, maybe a few cents or dollars off)
        init_value.append(num_stocks[indexer] * init_stock_price[indexer])
        # Print info
        data += (f"Number of Stocks of {tickers[indexer]}: {num_stocks[indexer]} @ {round(init_stock_price[indexer], 2)}/share\n")
        data += (f"Cash Value: ${round(init_value[indexer], 2)}, Percent of Portfolio: {weights[indexer] * 100}%\n")
        data +=("-------------------------------------------------\n")
        indexer = indexer + 1

    # Calculate change in portfolio
    # take the DOT product of the number of stocks and stock prices, this gives us the initial cash value of the portfolio
    # Again, this should be around the same amount as the initial cash invested
    initial_portfolio_value = np.dot(num_stocks, init_stock_price)

    # Start a list that will keep track of the portfolios % change day by day
    percent_chage = total_returns(all_data, num_stocks, initial_portfolio_value)

    daily_returns_list, cash_value = daily_returns(all_data, num_stocks, initial_portfolio_value)

    # calculate change in S&P
    spy_change = []
    spy_cash = []
    # for each day
    for i in range(1, len(spy) - 1):
        # get the S&P price
        next_day_price = spy.iloc[i]["Open"]

        # get the new value of the S&P position
        next_day_value = num_spy_shares * next_day_price
        spy_cash.append(next_day_value)
        # calculate the difference
        diff = next_day_value - init_spy_value

        # append
        spy_change.append(diff / init_spy_value)

    # Print S&P position information
    data +=(f"Number of SPY Shares: {round(num_spy_shares, 2)} @ {round(spy_start_price, 2)}/share\n")
    data +=(f"Cash Value: ${round(init_spy_value, 2)}\n")
    data +=(f"End Cash Value: ${round(num_spy_shares * end_spy_price, 2)}\n")
    temp1 = (((num_spy_shares * end_spy_price) - init_spy_value) / init_spy_value) * 100
    data +=(f"Percent Chage: {round(temp1, 2)}%\n")
    data +=("-------------------------------------------------\n")

    # calculate change in portfolio
    data +=(f"Initial Portfolio Cash Value : ${round(initial_portfolio_value, 2)}\n")

    # same as above but just for the end value
    end_prices = []
    for dataframe in all_data:
        end_prices.append(dataframe.iloc[len(dataframe) - 1]["Open"])

    # calculating end value of portfolio
    endval = round(np.dot(end_prices, num_stocks), 2)

    # printing information
    data +=(f"End Portfolio Cash Value: ${endval}\n")
    temp = ((endval - initial_portfolio_value) / initial_portfolio_value) * 100
    data +=(f"Percent Change: {round(temp, 2)}%\n")
    data +=(f"Diff between S&P: {round(temp - temp1, 2)}%\n")

    spy_indicies_to_plot = spy.index[:len(spy.index) - 2]

    # plot results
    if plot == True:
        plt.plot(spy_indicies_to_plot, spy_change, color='b', label="S&P 500 ETF")
        plt.plot(spy_indicies_to_plot, percent_chage, color='red', label="My Portfolio")
        plt.ylabel("% change")
        plt.xlabel("Date")
        plt.title("Total % change in Portfolio Value vs S&P 500")
        plt.legend()
        fig = plt.figure(figsize=(5, 5),
                         dpi=100)
        newWindow = tk.Toplevel(window)
        canvas = FigureCanvasTkAgg(fig,
                                   master=newWindow)
        canvas.draw()

        # placing the canvas on the Tkinter window
        canvas.get_tk_widget().pack()


        plot_returns(spy.index, daily_returns_list, daily_return_plot_start_idx)
        plot_cash_value(cash_value, spy_cash, spy_indicies_to_plot)

    pos_days, neg_days = return_data(daily_returns_list)
    data +=(f"Number of positive gain days: {pos_days} days\n")
    data +=(f"Number of negative gain days: {neg_days} days\n")
    anotherWindow = tk.Toplevel(window)
    anotherWindow.geometry("400x500")
    label = Label(anotherWindow, text=data)

    # this creates a new label to the GUI
    label.pack()
    print(data)
    return spy_change, percent_chage, spy.index, latest_date, daily_returns_list


def div_performance(stocks, weights, init_invest, recurring_deposit, recurring_rate, start_prices,
                    start_ann_div_per_share, div_freq, div_cagr, stock_cagr, per, forcast_length_in_years):
    init_shares = []
    forcast_length_in_months = 12 * forcast_length_in_years
    dataframes = []
    for i in range(len(stocks)):
        init_shares_stock = (init_invest * weights[i]) / start_prices[i]
        init_shares.append(init_shares_stock)
        d = {
            "year": 1,
            "month": 1,
            "deposit": init_invest * weights[i],
            'price': start_prices[i],
            "purchased shares": init_shares[i],
            'dividend': 0,
            'dividend shares': 0,
            'Cumlative Shares': init_shares[i],
            'Ann. Div/Share': start_ann_div_per_share[i],
            'Value of Shares': init_shares[i] * start_prices[i]
        }
        dataframes.append(pd.DataFrame(d, index=[0]))
        dataframes[-1].name = stocks[i]
    totals = {
        "year": 1,
        "month": 1,
        "deposit": init_invest,
        "purchased shares": sum(init_shares),
        'dividend': 0,
        'dividend shares': 0,
        'Cumlative Shares': sum(init_shares),
        'Ann. Div/Share': sum(start_ann_div_per_share),
        'Value of Shares': np.dot(init_shares, start_prices)
    }
    fidx = 0
    for frame in dataframes:
        for i in range(1, forcast_length_in_months):
            # determine the year value
            if frame.iloc[i - 1]['month'] == 12:
                current_year = frame.iloc[i - 1]['year'] + 1
            else:
                current_year = frame.iloc[i - 1]['year']

            # determine the month
            if frame.iloc[i - 1]['month'] != 12:
                current_month = frame.iloc[i - 1]['month'] + 1
            else:
                current_month = 1

            # Determine Deposit
            if np.mod(current_month, 12 / recurring_rate) == 0:
                # we are in a deposit month
                deposit = recurring_deposit * weights[fidx]
            else:
                deposit = 0

                # determine the price
            price = frame.iloc[i - 1]['price'] + frame.iloc[i - 1]['price'] * ((stock_cagr[fidx] / 100) / 12)

            purchased_shares = deposit / price

            if np.mod(current_month, 12 / div_freq[fidx]) == 0:
                div = frame.iloc[i - 1]['Cumlative Shares'] * frame.iloc[i - 1]['Ann. Div/Share'] / (div_freq[fidx])
            else:
                div = 0

            div_shares = div / price

            cum_shares = div_shares + purchased_shares + frame.iloc[i - 1]['Cumlative Shares']

            if frame.iloc[i - 1]['month'] == 12:
                # update div
                new_div = frame.iloc[i - 1]['Ann. Div/Share'] + frame.iloc[i - 1]['Ann. Div/Share'] * (
                            div_cagr[fidx] / 100)
            else:
                new_div = frame.iloc[i - 1]['Ann. Div/Share']

            value = cum_shares * price

            row = [current_year, current_month, deposit, price, purchased_shares, div, div_shares, cum_shares, new_div,
                   value]

            frame.loc[len(frame)] = row
        fidx = fidx + 1

    totals = pd.DataFrame(totals, index=[0])
    for r in range(1, len(dataframes[0])):

        deposit = 0
        purchased = 0
        divs = 0
        div_shares = 0
        shares = 0
        divPerShare_ann = 0
        value = 0

        if frame.iloc[r - 1]['month'] == 12:
            current_year = frame.iloc[r - 1]['year'] + 1
        else:
            current_year = frame.iloc[r - 1]['year']

        # determine the month
        if frame.iloc[i - 1]['month'] != 12:
            current_month = frame.iloc[r - 1]['month'] + 1
        else:
            current_month = 1

        for frame in dataframes:
            deposit = deposit + frame.iloc[r]['deposit']
            purchased = purchased + frame.iloc[r]['purchased shares']
            divs = divs + frame.iloc[r]['dividend']
            div_shares = div_shares + frame.iloc[r]['dividend shares']
            shares = shares + frame.iloc[r]['Cumlative Shares']
            divPerShare_ann = divPerShare_ann + frame.iloc[r]['Ann. Div/Share']
            value = value + frame.iloc[r]['Value of Shares']
        row = [current_year, current_month, deposit, purchased, divs, div_shares, shares, divPerShare_ann, value]
        totals.loc[len(totals)] = row

    return totals, dataframes



def show_sector_exposure(stocks, weights):
    sect_totals = {}
    for t in stocks:
        idx = stocks.index(t)
        obj = yf.Ticker(t)
        d = obj.get_info()
        ty = d['quoteType']

        # if the ticker is an ETF or mutual fund, we need to grab the weights of that security
        if ty == 'MUTUALFUND' or ty == 'ETF':
            # grab the sector weights in
            sectWeights = d['sectorWeightings']
            sw = {}
            for dic in sectWeights:
                k = list(dic.keys())
                sw[k[0]] = dic[k[0]]

            # rename all to be same as other dictionary
            # unfortunately the sectors are spelled differently with different case and underscores
            # need to remove and spell the same as the equity security types in order to match

            temp = {}
            for s in sw.keys():
                if s == 'realestate':
                    temp["Real Estate"] = sw[s]

                elif s == 'consumer_cyclical':
                    temp['Consumer Cyclical'] = sw[s]

                elif s == 'basic_materials':
                    temp["Basic Materials"] = sw[s]

                elif s == 'consumer_defensive':
                    temp['Consumer Defensive'] = sw[s]

                elif s == 'technology':
                    temp['Technology'] = sw[s]

                elif s == 'communication_services':
                    temp['Communication Services'] = sw[s]

                elif s == 'financial_services':
                    temp['Financial Services'] = sw[s]

                elif s == 'utilities':
                    temp['Utilities'] = sw[s]

                elif s == 'industrials':
                    temp['Industrials'] = sw[s]

                elif s == 'energy':
                    temp['Energy'] = sw[s]

                else:
                    temp['Health Care'] = sw[s]

            # loop through temp dictionary and check if the sector has been added to the sector values yet
            for key in temp.keys():
                # if there is not already a sector in the dictionary, add it
                if key not in sect_totals.keys():
                    sect_totals[key] = weights[idx]
                # else add it to the current value
                else:
                    sect_totals[key] = sect_totals[key] + weights[idx]
        else:
            # for equity security types (stocks)
            # grab the sector
            sect = d['sector']

            # check to see if it is in the dictionary
            if sect not in sect_totals.keys():
                sect_totals[sect] = weights[idx]
            else:
                sect_totals[sect] = sect_totals[sect] + weights[idx]

    # display
    plt.pie(sect_totals.values(), labels=sect_totals.keys())

    my_circle = plt.Circle((0, 0), 0.7, color='white')
    p = plt.gca()
    p.add_artist((my_circle))
    fig = plt.figure(figsize=(6, 6),
                 dpi=100)
    newWindow = tk.Toplevel(window)
    canvas = FigureCanvasTkAgg(fig,
                               master=newWindow)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().pack()

#Making Tkinter from now on

import tkinter as tk

window = tk.Tk()
logo = tk.PhotoImage(file= "iconbitmap.gif")
window.call('wm', 'iconphoto', window._w, logo)
window.title("Portfolio Comparison")

window.geometry("862x579")
window.configure(bg="#3A7FF6")

canvas = tk.Canvas(
    window, bg="#3A7FF6", height=579, width=862,
    bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)
canvas.create_rectangle(431, 0, 431 + 431, 0 + 579, fill="#FCFCFC", outline="")
canvas.create_rectangle(40, 160, 40 + 60, 160 + 5, fill="#FCFCFC", outline="")

text_box_bg = tk.PhotoImage(file= "TextBox_Bg.png")
stocks_entry_img = canvas.create_image(650.5, 167.5, image=text_box_bg)
weights_entry_img = canvas.create_image(650.5, 248.5, image=text_box_bg)
cash_img = canvas.create_image(650.5, 329.5, image=text_box_bg)
date_img = canvas.create_image(650.5, 410.5, image=text_box_bg)

stocks_entry = tk.Entry(bd=0, bg="#F6F7F9",fg="#000716",  highlightthickness=0)
stocks_entry.place(x=490.0, y=137+25, width=321.0, height=35)
stocks_entry.focus()

weights_entry = tk.Entry(bd=0, bg="#F6F7F9", fg="#000716",  highlightthickness=0)
weights_entry.place(x=490.0, y=218+25, width=321.0, height=35)

cash_entry = tk.Entry(bd=0, bg="#F6F7F9", fg="#000716", highlightthickness=0)
cash_entry.place(x=490.0, y=299+25, width=321.0, height=35)

date_entry = tk.Entry(bd=0, bg="#F6F7F9", fg="#000716", highlightthickness=0)
date_entry.place(x=490.0, y=380+25, width=321.0, height=35)



canvas.create_text(
    490.0, 156.0, text="Stocks", fill="#515486",
    font=("Arial-BoldMT", int(13.0)), anchor="w")
canvas.create_text(
    490.0, 234.5, text="Weights", fill="#515486",
    font=("Arial-BoldMT", int(13.0)), anchor="w")
canvas.create_text(
    490.0, 315.5, text="Cash",
    fill="#515486", font=("Arial-BoldMT", int(13.0)), anchor="w")
canvas.create_text(
    490.0, 396.5, text="Date",
    fill="#515486", font=("Arial-BoldMT", int(13.0)), anchor="w")
canvas.create_text(
    646.5, 477.5, text="Generate",
    fill="#FFFFFF", font=("Arial-BoldMT", int(13.0)))
canvas.create_text(
    573.5, 88.0, text="Enter the details.",
    fill="#515486", font=("Arial-BoldMT", int(22.0)))

title = tk.Label(
    text="Welcome to Portfolio Comparison!", bg="#3A7FF6",
    fg="white", font=("Arial-BoldMT", int(20.0)))
title.place(x=27.0, y=120.0)

info_text = tk.Label(
    text='''Greetings! With new investment tools becoming 
available such as creating your own "index"    
or "fund" (Fidelity FidFolio for example), 
you may want to see the historical performance
of your intended composition before investing. 
This tool helps you with above-mentioned. 
It's as easy as cooking ramen, Add all your ticker 
and their desired weights seperated by a comma, 
Pick a start date and initial cash investment and voila.\n\n\n''',
    bg="#3A7FF6", fg="white", justify="left",
    font=("Georgia", int(16.0)))

info_text.place(x=27.0, y=200.0)

import webbrowser

def know_more_clicked(event):
    instructions = (
        "https://github.com/ParthJadhav/Tkinter-Designer/"
        "blob/master/docs/instructions.md")
    webbrowser.open_new_tab(instructions)

know_more = tk.Label(
    text="Click here for instructions",
    bg="#3A7FF6", fg="white", cursor="hand2")
know_more.place(x=27, y=420)
know_more.bind('<Button-1>', know_more_clicked)

from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
def btn_clicked():
    stocks = stocks_entry.get()
    weights = weights_entry.get()
    cash = cash_entry.get()
    date = date_entry.get()
    if not stocks:
        tk.messagebox.showerror(
            title="Empty Fields!", message="Please enter Stocks using ',' delimiter.")
        return
    stocks = stocks.split(",")

    if not weights:
        tk.messagebox.showerror(
            title="Empty Fields!", message="Please enter Weights using ',' delimiter.")
        return
    weights = weights.split(",")
    weights = list(map(float,weights))
    if len(stocks) != len(weights):
        tk.messagebox.showerror(
            title="Stocks and Weight Mismatch!", message="Please enter equal amount of stocks and weights.")
        return

    if not cash:
        tk.messagebox.showerror(
            title="Empty Fields!", message="Please enter Cash.")
        return

    if not cash.isnumeric():
        tk.messagebox.showerror(
            title="Incorrect Value!", message="Please Round-off cash to nearest Integer.")
        return
    cash = int(cash)

    if not date:
        tk.messagebox.showerror(
            title="Empty Fields!", message="Please enter Date using YEAR-MONTH-DATE format.")
        return
    print("Stocks:",stocks,type(stocks))
    print("Weights:",weights,type(weights))
    print("Cash:",cash,type(cash))
    print("Date:",date,type(date))
    show_sector_exposure(stocks, weights)

    spy_changes, portfolio_chages, dates, startdate, daily_return_list = performance(stocks, weights, cash, date, plot=True)

generate_btn_img = tk.PhotoImage(file= "generate.png")

generate_btn = tk.Button(
    image=generate_btn_img, borderwidth=0, highlightthickness=0,
    command=btn_clicked, relief="flat")
generate_btn.place(x=557, y=477, width=180, height=55)

window.resizable(False, False)
window.mainloop()
print("Ran")

