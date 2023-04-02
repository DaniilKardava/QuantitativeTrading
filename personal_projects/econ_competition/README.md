## AP Economics Investing Competition


At the start of February, our economics class began an investing simulation on a platform called "The Stock Market Game," run by SIFMA. Having worked on my own platform and having seen how difficult it is to replicate the efficiency of markets, I spent some time digging through the game and looking for an edge. Two things stood out to me:

The first issue was a fixed 7% fee on all short positions. The fact that this value was static meant it didn't capture the short demand of specific stocks. While the value was unreasonably high for most liquid stocks and ETFs, it was also ridiculously low for stocks that had short fees in the hundred % range. (After running the strategy it seems as though there is actually no interest being charged on short positions at all.)

The second issue was spreads. While the game received quotes directly from Tradingview, and mimicked the market spreads, they seemed to rely on a single quote for orders qued in after hours and filled at open. 

I'll get one thing out of the way. I was convinced that the game filled after hour orders at the exact open quote. I was wrong. Unfortunately I didn't figure that out until I had committed to running the overnight capture strategy for 3 days, and incurred some serious losses. 

The short strategy keeps a portfolio of the top 20 candidates with the higherst borrowing rates as indicated on Interactive Brokers, that also meet the game criteria of 25 million market cap and 3 dollar share price. 

Because calculations are done in after hours, and transactions are qued for open, the next replacements are not qued until after hours the next day. This is because I want to avoid any unecessary problems with cash balance. I will not send in new orders until I know the amounts for which the previous ones settled for. 

Below is a sample data structure for running the code provided:

![image](https://user-images.githubusercontent.com/102199762/218278412-e4007e8a-b99d-40a7-971e-2dc3371181f9.png)

</br>
</br>

Regarding some corrections I've made in the code. IBKR short data only includes available to borrow securities. Therefore it's necessary to put together a one time list of all securities before appending new data at the end of each day. Missing values are forward filled, since the assumption is that the borrowing will stay near its current value if the available shares fell to 0. 


