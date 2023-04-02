## Index

[March 25, 2023](#march-25-2023) : Summarize potential strategies and possible theories for overnight occurance. Look at data alternatives, brokerage policies, and pre-post-market hours.

[March 26, 2023](#march-26-2023) : Assessed extended hours liquidity. Analyzed pre and post-market return components of overnight periods. 

## March 25, 2023

To begin, I've been looking primarily at my options for analyzing overnight sessions. 

I have two objectives: to figure out why overnight drifts exist and how to profit off of them. 

Regarding the profiting objective here is a list of my ideas so far:
<ul>
  <li>Finding assets whos morning correction was weaker than the overnight trend. I primarily wanted to look at stocks with a large retail trading base, since presumably they would be less aware of underlying trends.</li>
  <li>Looking beyond stocks with clear trends. Specifically taking advantage of strong correlations between overnight and intraday returns to make profit instead.</li>
  <li>Analyzing intraday returns without the busiest morning minutes. These periods often have weak returns and can provide opportunities for theta strategies.</li>
  <li>The easiest method would be to offload shares acquired at close during after hours.</li>
</ul>

My current theories:
<ul>
  <li>After finding the edge case where overnight portfolio returns of hedged asset pairs were consistently positive, I thought that disqualified a lot of leading theories around company announcements and earnings. I later realized this was primarily true for inverse funds, where additional demand could be explained by downside protection.</li>
  <li>Since the case above doesn't explain the phenomenon for individual stocks, I considered the idea that someone may try to take advantage of asymmetric liquidity to accumulate unrealized profits during after hours, only to dump the shares on investors at market open.</li>
  <li>I also think that my focus should be primarily on overnight sessions that trend. The symmetry at open is less important for random movements, as it can be explained by a correction after a period of low liquidity.</li>
</ul>

Regardless what I work on, I'll need to look in detail at overnight sessions. So far here are some data sources I can use: NASDAQ, Yfinance, ThinkOrSwim, or Barchart.
  
NASDAQ only has single day pre and post market data on their chart. However, the data itself contains good information, including precise share amounts and prices. 

Yfinance is easier to access and intraday data is available as far as 60 days back. Unfortunately volume data isn't provided for pre and post hours.

Barchart and ThinkOrSwim both have methods for extracting low timeframe data with both pre and post-market sessions. Barchart also offers spread data, but per-load limits makes accessing some hours impossible. 

I'm used to thinking of a day as being split up into the day and night session. But the night session itself can be broken into the pre and post-market session, the pre-market starting as early as 4 am ET on some brokerages, and the post-market ending at 8 pm ET.

That means the price doesn't flow from close to open, but makes another jump between 8pm and 4am. 

From looking at these periods, it seems like there isn't as big of a barrier to transacting as I thought, unless the transactions recorded are done privately and I cannot be cut in. Most brokerages offer the service with 2:30 hours before open and 4 hours following close. 

## March 26, 2023

Below is an image taken from ThinkOrSwim showing the state of the order book in pre-market trading. It also illustrates a jump between post and pre-market hours. Spreads appear thin but liquidity is low, only a few thousand dollars can be moved. 

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/227794290-ec50f6ff-1598-4245-af07-fd9772373d47.png" width="250" height="150">
</kbd>

</br>
</br>

On one hand that shows how easy it is to impact price, on the other hand it puts a cap on the scalability of this strategy, unless the portfolio is constructed across many assets. 

Correction, the order book may be flawed. Below is an image of spread data provided by BarChart. It shows significantly higher liquidity in TQQQ.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/227797915-d991721a-7f21-4fe2-aada-a33f61aa2414.png" width="250" height="150">
</kbd>

</br>
</br>

The volume in the ThinkOrSwim application also supports the claim of sufficient liquidity:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/227798363-85bb1aa1-c253-445d-be68-cec9eb5c6114.png" width="250" height="150">
</kbd>

</br>
</br>

So does similar data on NASDAQ, with many large transactions:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/227798459-62f49e06-18d8-46af-8937-2b7c55f94d88.png" width="250" height="150">
</kbd>

</br>
</br>

I wanted to figure out how much the pre-post market gap contributed to the overnight session drift. I provided some sample code to test this with yfinance, but only got a small sample due to data limitations.

I used BarChart's data to check instead. From looking at four assets: SPXU, WKEY, VMAR, and SPY, I couldn't find a clear common trend among them. The images are below, in no particular order. They include total overnight returns, post-pre market jumps, pre, and post-market returns:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228491885-66022a5a-3779-45b4-8dcd-855d7419b169.png" width="250" height="150">
</kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228491576-38ab97da-acfd-423c-9de1-6faad9cc0efd.png" width="250" height="150">
</kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228491717-04175ecb-c383-4cd6-bdeb-4cfe999cf65d.png" width="250" height="150">
</kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228491443-bfeb6472-cb45-4ca7-ab82-7d16d09f2128.png" width="250" height="150">
</kbd>


</br>
</br>

WKEY is an interesting case. An illiquid swiss company traded on a foreign exchange. The returns happen entirely between the post-pre market gap. Significant negative returns then follow the gap in pre-market hours. 

I'll note that for the more liquid stocks, overnight returns primarily coincided with pre-market hours. 

Since I couldn't identify any commonality between these different assets, I'm going to try to tackle it one group at a time. 


## March 29, 2023

To start, let's address dividends. They are priced "instantaneously" in the post-pre market overnight gap, since the post-market session prior to the ex-date still gives dividend eligibility. The drop can be easily observed in a stable asset such as USFR, short term treasury bills. 

As a general explanation, IBKR identifies the after hours session as part of the same trading say, therefore the trade settlement timeline is the same. 

My confusion arises mainly from TD Ameritrade's 24/5 trading service for liquid assets, detailed here: [TD Services](https://www.tdameritrade.com/tools-and-platforms/after-hours-trading.html)

The TD Ameritrade OnDemand tool suggests that the dividend correction will still occur 4 hours after market close, which is the standard end time for after-hours sessions. I don't have any immediate ideas in this department, but I at least feel that seeing what goes on in this period can provide some clues, although markets seem too dry at that time to give any clear picture. I would also like to understand how retail traders moving prices between 8pm and 4am can arrive at the same price target for pre-market open as the rest of the world. 

Back to my analysis. The first "group" in mind were inverse pair portfolios. Unfortunately, even here there is no single trend. 

(A promise to myself to write readable code. For my own sake and for the sake of everyone around me, follow naming conventions, use classes, and use functions.)

First is the class of SPY pairs: SH, SDS, SPXU, and SPXS.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228634411-7ed243e8-ae31-4010-8030-6e3a2f2e721b.png" width="250" height="150">
</kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228634532-7671bf6f-93c8-4626-8e95-77759e2a00ca.png" width="250" height="150">
</kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228634693-d48b24ea-7399-4c6e-a7cf-f332c60ccb02.png" width="250" height="150">
</kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228635969-f4601bc0-3cf1-462e-80f8-56c52cf352e9.png" width="250" height="150">
</kbd>

</br>
</br>

All assets observe symmetry between post-pre gaps and pre-market returns. SH returns aggregate in post-market hours, while SDS, SPXU, and SPXS are primarily formed in pre-market. I assume the difference in graphs between the assets is just randomness in the open price of the pre-market session, not to mention my data isn't perfect, although SH completely reverses the trends in the other pairs. The important part is the correction that follows.

Second is the QQQ class: PSQ and SQQQ.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228638475-75d4acb6-e781-42b7-b7dc-312facf39112.png" width="250" height="150">
</kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228638661-d2bf28c3-aba6-4d48-8fe0-cb9a11012320.png" width="250" height="150">
</kbd>

</br>
</br>

With the exception of the sudden gaps caused by low liquidity in PSQ, the sessions trend together. Once again, the unleveraged inverse fund shows returns in post-market hours. 

Finally, the DIA class: DOG, DXD, SDOW.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228644272-6a6c7075-7629-4aed-aeda-9b1c0664dd5f.png" width="250" height="150">
</kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228644479-3ddf2c31-5474-4184-8e61-bf10b8e27463.png" width="250" height="150">
</kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/228644630-c73b1c91-1988-4c3e-afb1-c0bd06c972cb.png" width="250" height="150">
</kbd>

</br>
</br>

I can't draw any clear conclusions from this yet. For now I'd say that although the asset classes all reach a similar return outcome, the individual session returns are unrelated. At the same time, because these difference occur as a result of an instantaneous change for the pre-market session open, they likely get fixed very fast as well. 

So far, I've only measured the divergence of pairs with one asset being the target benchmark itself. This way I could assess purely the performance of the short funds and test the theory that additional overnight demand formed for hedging. Unfortunately, going forward, many of the pairs do not have an unleveraged benchmark, and I will be testing them against their leveraged counterparts.  

The problem with this is that leveraged long funds have their own strong overnight returns. I just can't put my finger on what may be causing it, and the trends are not completely synchronous across different assets. It'd be nice to just have 100 datasets to run correlations against, makes me think I should save the "why" till that day comes, and just focus on making the idea profitable for now.

It's time to learn a little about ETF structures. The main process as I understand it is called creation and redemption. An ETF Sponsor partners with a broker who will distribute ETF shares. They issue shares to the broker in lots called creation units, and in exchange they receive either the proportional assets or cash to create the required portfolio on their end. 

The broker relies on the demand for the shares on the secondary market so that they can offload their risk to individual investors. They monitor this demand closely to assemble and redeem the excess shares for their original basket of assets, causing a fluctuating share number in the secondary market.

The articles address that because of the need to assemble a basket of underlying assets, the liquidity of the fund significantly depends on the liquidity of the underlying. 

Regarding leveraged ETF's, I assume that because they measure returns close to close, then rebalancing is conducted in after hours. I'm not sure how they manage to move that much money. 

Back to the analysis. I realized once again that I had forgotten to scale the returns down to replicate capital constraints, the returns above are typically in the 2% range. I won't share the rest of the pairs then since these aren't real opportunities after costs, except maybe the SOXS/SOXL pair which is delivering close to 15% annually and has liquidity. Of course even these returns are too little to withstand a daily spread, so I really need to understand the deal with mid-point orders not getting filled properly. 

To conclude, many of the popular ETF's maintain high liquidity at night, and if spreads can be avoided altogether, then there is potential to form some well paying portfolios. 

In fact from now on I'm going to assume 0 spreads. I will either be able to get filled at mid-point because my opportunity window is large, or none of these strategies will ever work. Now onto individual stocks. Since liquidity seems to be an issue for any asset below at least 10 million average share volume

## March 30, 2023

I completely forgot the sub-penny quote regulation, Rule 612. That's the issue really. For assets with price in the double digits, the accumulated spreads become significant. More competitive bids cannot be set, either I stand in line with NBBO or I eat the spread.

It seems like after 20 years, this rule, and many changes to the order execution system are being discussed by the SEC: [hearing.](https://www.sec.gov/os/sunshine-act-notices/sunshine-act-notice-open-12142022#:~:text=94%2D409%2C%20that%20the%20Securities,at%20www.sec.gov.)

Right now, the strategies discussed would not be easy to execute, as I don't know the probability of getting a fill when waiting at the NBBO. 

Alright, the effects of spread and slippage need to be determined on a case by case basis depending on the strategy. A few overnight inverse fund combinations offer high returns, but the spreads cannot be split, and using market orders will incur substantial losses. Assume now that for a strategy like this that slippage is random. In otherwords during my opportunity window, the price will not continuosly escape my buy limit by moving upward, or downward for a sell limit. In that case, I would be disadvantaged as resetting each limit order at the new NBBO would reset my time priority, placing me behind faster institutional systems. 

Excluding the scenario where the price runs away from me, then despite being last in line, my order must still be filled for the price to fall below my offer. So it still seems like this will be feasable, especially for a group that can be first in line with faster systems. Once again this would assume all the price fluctuations that occur in the process of not being fully hedged are random in the long run.

Now, despite not understanding where overnight returns come from for individual stocks and ETFs, I'd like to take a look at potential opportunities to capture them. 

The immediate problem is that most of the candidates have low overnight, and often intraday, liquidity. For more liquid assets, I'll assume the same approach as described for the ETF portfolios. 

For less liquid assets, I need to understand how many shares can be moved overnight, and how to deal with spreads. Ok, I hate to leave these unfinished, but my future is very uncertain and I'll need to leave this. 

Just so I stop beating around the bush. Find an asset, check which part of the night the returns come, and if there are corrections. Find the best time to sell, check volume through ThinkOrSwim, split the spread down the middle. It's really easier to just test these things than pretend like I'll never know if it will work or not. 

No time to figure out the "whys." I had one other idea: capture option theta decay since returns tend to aggregate at open, offsetting overnight returns. 

And right as I was about to give up... I ran WKEY through my intraday analysis. The intraday declines did not start at open as anticipated. Instead they began at 11:20 AM EST precisely, aka the Swiss market close. 

Don't really know what to do with that info. Anyway, I'm hoping for a big SEC overhaul in the near future anyway so that would make most of my struggles here a waste of time. Regarding the RL model, since I can't split the middle, I guess I can't improve the SPY performance without more research. I was hoping I could split the middle on FX currencies since spreads weren't in single units of whatever denomination they use. Plus I already had good FX models. Crypto too maybe. 

When I return:
<ul>
<li>Analyze the overnight and intraday returns **timing** for hedged funds.</li>
<li>Look into the behaviors of international and OTC stocks.</li>
<li>Come up with a clear system for offloading shares overnight for individual stocks</li>
<li>Clarify the distribution of intraday returns (most of my data is recent and overnight/intraday returns haven't been reliable over that period)</li>
</ul>
