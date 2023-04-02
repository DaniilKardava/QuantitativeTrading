## Index

**Note: It seems like dividend data now comes back with a datetime index instead of a date index. Convert to date format to fix.**

[January 24, 2023](#january-24-2023) : Thoughts on fund structure and behavior.

[January 25, 2023](#january-25-2023) : First look at overnight and intraday returns of SPY and SH portfolio. First look at individual weekday returns of SPY and SH portfolio. 

[January 26, 2023](#january-26-2023) : I analyzed the fund's NAV history and determined that the deviations are baked into the fund holdings themselves. I also observed opposing trends in the NAV changes and real price changes when analyzing individual weekdays.

[January 28, 2023](#january-28-2023) : Defined and interpreted interest rate vs SH + SPY portfolio using a lsrl. Graphed interest rates on top of portfolio returns to view their correlation. Calculated and compared distributions to measure deviations from long term trends in portfolio returns for both NAV and real prices. 

[January 29, 2023](#january-29-2023) : Clarified real portfolio returns with capital constraints. Built and interpreted tables analyzing relationship between portfolio growth and interest rates, separated by direction and leverage. 

[January 30, 2023](#january-30-2023) : Demonstrated overnight portfolio returns in more depth. Determining whether the price accurately reflects NAV could be important for future overnight research. 

[February 1, 2023](#february-1-2023) : Recalculated my LSRL tables to make it easier to analyze the behavior of custom asset combinations. I started to consider the leverage that could be achieved through a short position, and what portfolios could be created to increase my returns. Also began looking at short rebates offered by IBKR as an alternative income source.

[February 3, 2023](#february-3-2023) : IBKR rate calculations, resources, and limitations. 

[February 4, 2023](#february-4-2023) : Built a table of leveraged fund pairs that could be shorted for interest rebates and profitable declines. Brainstormed other profitable portfolios. 

[February 11, 2023](#february-11-2023) : Adressing liquidity concerns for options with extensive histories.

[February 12, 2023](#february-12-2023) : Review of treasury bills and bonds and their connection to Put-Call Parity. Calculating rate of change of the Put-Call Parity relationship and connecting it to the divergence between shares and options.

[February 17, 2023](#february-17-2023) : I begin recreating the short strategy setups with options to obtain leverage. 

[February 18, 2023](#february-18-2023) : Continued to develop profitable option portfolios. Looked into the coordinated deviations across all option strikes.

[February 19, 2023](#february-19-2023) : Looked into overnight and intraday returns of options. Summarized my findings of this entire project.

## January 24, 2023

I tried looking into the structure of leveraged and inverse funds. For the two examples SH and UPRO, the holdings were primarily swap contracts whose details were not 
public. I really don't feel like trying to tackle the question of why a divergence occurs considering that I can only speculate on how the funds operate. I have no idea what amounts are paid out, at what frequency, who stands to benefit, how both parties manage risk, and how that risk management effects supply/demand of other securites.

On the other hand, these funds contain a fair amount of treasury bills which are directly related to interest rates. Unfortunately the funds do not act as expected, a
sudden drop in interest rates during COVID should theoretically boost the value of treasury bills and the value of a short fund which carries them. Yet, a long position in SH and SPY generated instant losses at that moment. 

## January 25, 2023

To restate the performance of SH relative to SPY. When rates are high, the graph of cumulative returns of SH lie above the graph of expected returns of SH. 
I interpret this as a positive constant 'k' being added to each daily return of SH. Therefore a long position in SH and SPY generates 'k' daily return. The 
opposite is true when rates fall below a certain threshold. 

**Follow up question:** 

I recall that the cumulative returns graph of this hedged portfolio was not consistent for each individual day of the week. This complicates the situation 
since it suggests that the difference 'k' varies. 

As a side note, I also recall that cumulative overnight returns were significantly different for each day of the week in other assets. For example, overnight returns preceding Tuesday appear as the top cumulative performers across a wide variety of assets. This is a separate point to address in the overnight returns directory, but may also shed some light here. 

First, lets quickly separate overnight and intraday returns for a hedged portfolio containing SPY and SH (I added the code to today's folder). Notice the symmetry that is also observed in the "overnight returns" directory. I have previously done analysis that showed that the bulk of intraday returns causing symmetry happen at open. This can also be observed in real time using an Alpaca Markets paper trading account. 

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/214770071-c611f637-1213-4a64-8296-fcf28a55c6d7.png" width="250" height="150">
  </kbd>
  
 <kbd>
<img src="https://user-images.githubusercontent.com/102199762/214770134-b838feca-4662-4f8a-a962-921daa54e18d.png" width="250" height="150">
  </kbd>
  
</br>
</br>

Next I added a modified script that displays the total close to close return stratified by weekday. Using a logarithmic scale, here are the cumulative close to close returns graphed for the corresponding day of the week: 0-Monday, 4-Friday. Currently it appears that there is another factor at play separate from interest rates that causes day to day variations even at times of low turmoil.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/214780162-37a38d55-94a3-49f3-9c03-85e17e86b798.png" width="250" height="150">
  </kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/214780208-d2c43841-ba68-4e70-88a3-929a35882d18.png" width="250" height="150">
  </kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/214780260-dfdd7485-89f8-4ef1-8185-556458be88f7.png" width="250" height="150">
  </kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/214780320-2f135e3d-f106-4833-9dfd-b15adc20b776.png" width="250" height="150">
  </kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/214780379-92504433-e909-4875-97ca-f5c0f5837fc9.png" width="250" height="150">
  </kbd>

</br>
</br>

Viewing the graphs above simultaneously:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/214988289-430148a6-778f-4aaf-ae11-fd4c0677f93f.png" width="250" height="150">
  </kbd>
                                                                                                                                          
## January 26, 2023

I remembered that every fund has historic NAV and discount/premium data. I want to understand whether these deviations are a result of traders or the assets within the fund itself.

Had to hand collect data from Y-Charts because exporting to excel costs $300 a month :)

Below are overlapping returns of actual share prices and reported NAV prices, separated by the day of the week. Disregarding the divergence during 2008, there are periods when the trends entirely do not match, like weekend/monday returns post 2020. 

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215012350-515d9be6-d786-44db-b503-c55fb92905ac.png" width="250" height="150">
  </kbd>
 
<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215012458-717607eb-2309-4ab8-8fae-2409cc08cb19.png" width="250" height="150">
  </kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215012519-76e261ec-aea2-471f-ae6a-e4947a683a8d.png" width="250" height="150">
  </kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215012546-07754e70-a695-4d90-9a40-306b8ce53793.png" width="250" height="150">
  </kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215012585-7cabce07-e8c5-4179-b87b-20103a09b012.png" width="250" height="150">
  </kbd>

</br>
</br>

Similarly, here are the overlapping returns by weekday using NAV values. 

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215016839-76c53d84-94a8-4883-aa1b-5ec85a9d8f28.png" width="250" height="150">
  </kbd> 

</br>
</br>

Ok, I'm not sure where I'm going with this. I'll summarize with this main idea: 

At the end of the day, traders are tracking the fair value of the ETF. By looking at the NAV itself, it seems reasonable to think that the swaps have some variable rate component, although I would expect the fund to be paying said rate, and instead it seems to be earning it (I recall potentially the opposite being true for long funds using swaps - turned out to be true). 

On top of this there seems to be a base rate, which fuels divergence even when rates fall to 0. The dilemna is in the fact that there are arbitrage opportunities to earn this difference, and had the returns been greater than the available rates, I wonder if the price would begin to significantly deviate from NAV. This is not just speculation, as the "base rate" leaves room for profit when rates are low, and I'm curious how the market accounts for this. 

I'm willing to accept that the divergence in the returns of NAV weekday charts are insignificant, maybe it is unreasonable to expect them to carry the shape of the combined graph (Verify this officially later). Investigating this further leads to more questions about the fund's actual structure, which I can never confidently answer.

I was more intrigued by the deviations between NAV and real price. The actual price graphs often headed in seperate directions. This itself is not a profitable opportunity to take advantage of since the differences are not large, but the idea is interesting.

## January 28, 2023

So far the answer to my question "why" has just been "because." I made the important distinction that this has less to do with traders and more to do with the fund's real asset value. There are a couple of ways to continue from here:

<ul>
    <li>I want to visualize how the level of leverage and direction of the fund affects its sensitivity to interest rates. A table summarizing the possibilities would be helpful. </li>
    <li>I want a better way to visualize the weekday deviation from the expected return. Comparing the distributions of differences would be a good first step.</li>
    <li>Overlapping interest rates with the return of the portfolio could help me visualize their relationship. </li>
</ul> 

First I graphed the federal funds rate next to the portfolio return:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215291431-f56ed89e-ef68-4d9e-ad94-270f32d6f829.png" width="250" height="150">
  </kbd>

</br>
</br>

Then I correlated the portfolio growth to the federal funds rate. Raw data was too noisy, I settled with a 10 standard deviation gaussian filter:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215301979-7f3df533-c2b5-4ec6-9c07-8937f6f63fec.png" width="250" height="150">
  </kbd>

</br>
</br>

The correlation matrix:
[1. &nbsp; 0.95996237] </br>
 [0.95996237 &nbsp; 1.]
 
The lsrl relating the portfolio returns and current interest rates will be a good way to describe the differences between the funds in my table. Here is the function for Short SPY unlevered (SH):

8.011e-05 x - 3.925e-05

To clarify, the equation above takes interest rates as inputs and outputs expected portfolio change, in this case a portfolio containing equal weights in SH and SPY. When rates are 0, the portfolio shows losses. Returns change sign when interest rates are approximately 0.48994437. 

Before continuing with building these equations, I wanted to compare the NAV changes and real price changes. I used a gaussian filter to smooth out the portfolio returns and calculate the daily price deviations from this trend for both NAV and actual market prices. My intention was to compare the distribution of these differences. 

The distribution representing all the weekdays combined was approximately normally distributed and centered at 0, for both NAV and real prices:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215308912-b4d6eff2-8ff3-471e-9314-94d94a3f5abb.png" width="250" height="150">
  </kbd>

</br>
</br>

The distributions for the individual weekdays are below:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215309098-b7ebf769-46a2-4944-b90c-cbc4f0a50ce3.png" width="250" height="150">
  </kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215309121-2f68bc53-01ac-4684-b3f7-f5e45c53fe7f.png" width="250" height="150">
  </kbd>

</br>
</br>

For both NAV and real prices, analysis of variance returned that there was no significant difference in deviations from average trend by weekday. Note: including 2008 does hurt the accuracy of the test significantly. 

(I'm reading this some time later and I sound insane. First of all, testing sample means completely ignores that I was interested in correlations. The fact that cumulative returns of a single weekday are not fully correlated to interest rates is so blatant I don't understand why I had to run all these fancy tests, and still come to the wrong conclusion. It's clear there are other forces at play but interest rates dictate the main trend.) 

## January 29, 2023

I've established that the fund's behavior is related to its swaps holdings. For my purposes, I've settled that weekdays do not play a significant role in the behavior of portfolio returns. The one thing that still doesn't sit right with me are the overnight/morning returns of the portfolio. 

I know that the portfolio maintains its stable and theoretical return of 0 throughout the day, and that the long term trend occurs as a result of the volatility at night and in the morning. It would be great to visualize real time fluctuations in NAV at open and overnight, since it seems much more likely that such volatility would be caused by traders rather than real asset value. Who knows maybe treasury bills exhibit similar behaviors at market open.  

(Once again sliding in here to add that market open is a busy time for calculating balance sheets, excess and insufficient reserves, and determining short term lending rates between institutions. This could influence the value of the assets held by a fund.)

I'll continue by exploring two more ideas:
<ul>
  <li>First, let's create that table to analyze interest rate effects on the performance of funds for different levels of leverage and direction.</li>
  <li>Second, my analysis so far has only addressed SH. However, the patterns I've observed here are not exactly the same for another inverse SPY ETF like SPDN. This is another element that I will have to explore, as well as the different underlying assets that I am tracking, QQQ instead of SPY for example.</li>
</ul>

Lets begin with the table. The raw data is all smoothed with a 10 standard deviation gaussian filter. The first table below is for short funds tracking SPY. LSRL predicts daily portfolio return as a function of interest rates. 

**Important Clarification**: 

I've often referred to the returns I was measuring as "portfolio growth". This is not accurate. Take for example a triple leveraged fund that tracks SPY. I compare the fund's divergence from its expected return of 3x SPY, but this is not a realistic return I could achieve with limitted capital. If 3 times as much capital is kept in SPY, only 25% of the portfolio is kept in the leveraged fund itself. The real returns are diminished by a factor of "leverage + 1," 4 in this case.

For higher leverage funds it became a question of whether to scale their returns down or to scale the benchmark returns up. While it makes sense to scale the return of the benchmark up to reflect what is ultimately being tracked, if I want to compare leveraged and unleveraged assets, I should compare the returns of the practical portfolios that could be constructed using limited amounts of capital. Generally, the benchmark must be scaled by n/(n+1) and the fund in question should be scaled by 1/(n+1), where n is the leverage factor. 

|Name|Date|Leverage|LSRL|Corr.|X-int.|
|:---:|:---:|:---:|:---:|:---:|:---:|
|SH|2006-06-23|-1x|4.001e-05 x - 1.96e-05|0.96000249|0.48991154|
|SPDN|2016-06-14|-1x|3.954e-05 x - 8.015e-06|0.97147382|0.2027289|
|SDS|2016-07-17|-2x|4.107e-05 x - 1.856e-05|0.9319257|0.45189351|
|SPXU|2009-06-26|-3x|4.379e-05 x - 1.758e-05|0.85118974|0.40153497|
|SPXS|2012-07-01|-3x|4.471e-05 x - 2.381e-05|0.88127941|0.53243616|

Side note: Prior to 2012-07-01, SPXS tracked the Russell 1000. 

Moving on to long funds. Previously I measured a portfolio that was long both SPY and an inverse fund. These naturally hedged eachother, and I could interpret the rate of return as the inverse fund's performance relative to the benchmark. 

Now I am comparing the performance of two long funds and can choose between being short the leveraged fund or the SPY benchmark. To be able to interpret the results as the performance of the leveraged fund relative to the benchmark, I will short SPY. This means we will see losses if the returns of the leveraged fund are lower than expected, and profits if they are higher than expected.  

**Note**: The data starts post 2009 for each asset because the volatility during 2008 is horrendous and ruins the correlation. 

|Name|Date|Leverage|LSRL|Corr.|X-int.|
|:---:|:---:|:---:|:---:|:---:|:---:|
|SSO|2009-01-01|2x|-1.57e-05 x - 1.572e-05|-0.8580109|-1.00158882|
|UPRO|2009-01-01|3x|-2.399e-05 x - 1.638e-05|-0.9052294|-0.68282746|
|SPXL|2012-07-01|3x|-2.018e-05 x - 2.268e-05|-0.71548461|-1.123628|

Prior to 2012-07-01, SPXL tracked the Russell 1000. 

Unlike short funds, long fund returns are inversely related to interest rates. 

I can now numerically show something I observed a long time ago. When rates are high, it is most advantageous to hold a long position in SPY and an inverse fund because they have the highest sensitivity to interest rates. Higher leverage also corresponds to higher sensitivity and larger returns. 

Taking advantage of the fact that both long and short funds underperform their benchmark when interest rates are low (negative intercepts), we can maximize losses by holding an equal position in a long and short fund. Higher leverage corresponds to higher losses, and inverting this portfolio would make our portfolio green. 

## January 30, 2023

There is one more idea I need to demonstrate. I briefly mentioned overnight returns, demonstrating yet again the symmetry between the intraday and overnight periods of the portfolio. I'd like to look at the correlation between federal funds rates and seperate overnight/intraday returns generated by the portfolio. 

**Interesting**:

For example, here is the SPY and SPXU portfolio:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/215685085-afdb4659-caa1-47b9-929f-cfb0e89b3111.png" width="250" height="150">
  </kbd>

</br>
</br>

This trend varies from one example to the next. SPY and UPRO portfolio:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/216150014-7bfe59f3-a26d-4c8b-b8bd-877519d56c26.png" width="250" height="150">
  </kbd>

</br>
</br>

I think it may be more accurate to interpret this symmetry as a cause and effect, where intraday movements correct the price discrepancies that occur overnight, returning the fund to its fair value. As always the question becomes why such overnight returns occur in the first place. 

This is a curious example, because the overnight float is very deliberate, considering that the fund does have a fair value benchmark that it is designed to track. Finding out whether this is an accurate valuation of the fund's holdings or whether this is some form of market manipulation could be the key to understanding overnight returns. 

## February 1, 2023

As it stands, I'm not sure how to continue with this experiment. My curiousity is beginning to turn to the overnight returns phenomena, and I feel as though the last thing left to do here is make it practical. As always a little summary so far:

<ul>
  <li>First, I determined that the trend could be observed in the NAV of the fund. It simply came down to the valuation of the swap contracts, whose details were private. This means I didn't have to brainstorm fancy reasons for this divergence, it was part of the fund itself.</li>
  <li>I observed slight differences after compounding portfolio returns for all seperate days of the week. It seems clear that there are other forces at play, but interest rates are the most significant.</li>
  <li>I summarized the portfolio behavior for different levels of leverage and direction of funds. Importantly, portfolio returns containing short funds were positively correlated with interest rates. Whereas long funds had negative correlations. </li>
  <li>I saw that portfolio returns were consistently positive overnight for leveraged short funds (additional demand for hedging overnight risk?). In any case, finding out whether the price accurately reflects NAV would be a big step.</li>
</ul>

As a side note, I feel like I often find myself trying to reason through why a certain combination of assets produce the best returns for specific interest rate conditions. The previous tables were helpful, but I'd like to convert them back into unscaled versions so that I could easily combine funds and see their total sensitivity to interest rates. 

Below is a summary containing the unscaled LSRLs from the tables above. Essentially, I'm just looking at the pure returns of the fund relative to its true benchmark, and scaling it as needed to form custom combinations.

Here is the short fund table:

|Name|Date|Leverage|LSRL|
|:---:|:---:|:---:|:---:|
|SH|2006-06-23|-1x|8.002e-05 x - 3.92e-05|
|SPDN|2016-06-14|-1x|7.908e-05 x - 1.603e-05|
|SDS|2016-07-17|-2x|1.232e-04 x - 5.568e-05|
|SPXU|2009-06-26|-3x|1.751e-04 x - 7.032e-05|
|SPXS|2012-07-01|-3x|1.788e-04 x - 9.524e-05|

Here is the long fund table:

|Name|Date|Leverage|LSRL|
|:---:|:---:|:---:|:---:|
|SSO|2009-01-01|2x|-4.71e-05 x - 4.716e-05|
|UPRO|2009-01-01|3x|-9.596e-05 x - 6.552-05|
|SPXL|2012-07-01|3x|-8.072e-05 x - 9.072e-05|

From now on, I should be able to roughly resolve questions about the portfolio's behavior by scaling and adding the functions that predict the rate of change of the portfolio. 

Anyway, I was messing around with some hypothetical trades. My idea was to find opportunities where short loan rates were lower than cash interest offered by the brokerage. I wanted to use the fund pairs to hedge any directional risk. On IBKR this could be seen as a positive rebate on a short position:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/216224990-271e7aa0-c52c-40be-b0d1-b510f228bea3.png" width="250" height="150">
  </kbd>

</br>
</br>

This idea went through multiple iterations until it seemed to work:

(For some reason I was under the impression that opening a short position increases my buying power, so most of these ideas weren't even plausible. The ideas discussed below only work in a special case where IBKR offers an interest rate rebate for short positions, which I will show.)

First I considered a short position in SPY, whose cash proceeds would be used to enter a long position in a 3x SPY fund for efficient capital use (Again I was envisioning a cheap loan here). The remaining cash could be put aside to earn interest. Applying what we know, such a position would theoretically generate no profit because the short SPY + long 3x SPY combination would produce losses. 

Next, I considered a short position in SPY and a short position in a Short SPY fund. Once again no profit, since I end up short the portfolio that originally generated gains, and I negate the interest being earned on the cash I receive. 

The trick was to pick a combination that would properly hedge so I could collect cash and earn interest without it being negated by the structure of the portfolio I had built. This could be achieved through a highly leveraged long and short fund, when their sensitivity to interest rates generally negate one another. 

## February 3, 2023

I've spent a lot of time looking at the behavior of this strategy, but I'll try to put it to some use now. The first method was just described above, an example would be a short position in both SQQQ and TQQQ. It would in theory give massive leverage on the cash available to earn interest. The fractional collateral for a short position would multiplty the portfolio returns and the interest earned as a rebate. 

Unfortunately, the rebate is only offered for large accounts, and the current rates are too high to run this strategy.

Below are some references for costs and payments on a short in IBKR:
</ul>
  <li>Short sale interest calculations table: https://www.interactivebrokers.com/en/accounts/fees/interestPaid_Example2.php</li>
  <li>Blended rate calculator: https://www.interactivebrokers.com/en/index.php?f=46377&p=m</li>
  <li>Snapshot of shortable stocks data base: https://ibkr.info/article/2024</li>
  <li>Asset look-up in short data base + historical rates (Requires login): https://portal.interactivebrokers.com/AccountManagement/AmAuthentication?action=CS_SLB</li>
</ul>

## February 4, 2023

Here's a list of some highly leveraged fund pairs that show strong declines overall:
<ul>
  <li>TQQQ/SQQQ : QQQ 3x : Rebate as of 2.4.2034 : 3.3975/3.5363</li>
  <li>UPRO/SPXU : SPY 3x : Rebate as of 2.4.2034 : 2.4002/-1.3054</li>
  <li>SPXL/SPXS : SPY 3x : Rebate as of 2.4.2034 : -0.0733/1.2869</li>
  <li>SOXL/SOXS : Semi-conductor 3x : Rebate as of 2.4.2034 : 4.0298/-0.7123</li>
  <li>TNA/TZA : Small-cap 3x : Rebate as of 2.4.2034 : -0.5106/-1.2477</li>
  <li>TMF/TMV : T-bonds 3x : Rebate as of 2.4.2034 : -2.3617/-18.6809</li>
  <li>LABU/LABD : Biotech 3x : Rebate as of 2.4.2034 : 4.1206/-2.3845</li>
  <li>UDOW/SDOW : DOW30 3x : Rebate as of 2.4.2034 : -2.3713/1.4235</li>
  <li>YINN/YANG : China 3x : Rebate as of 2.4.2034 : 1.4628/-3.8017</li>
  <li>TECL/TECS : Technology 3x : Rebate as of 2.4.2034 : -0.0789/-9.1660</li>
  <li>FAS/FAZ : Financial 3x : Rebate as of 2.4.2034 : 3.7575/-4.5762</li>
  <li>FNGU/FNGD : FANG 3x : Rebate as of 2.4.2034 : -0.9871/-8.1045</li>
</ul>
  
This website has additional pairs: https://etfdb.com/themes/leveraged-3x-etfs/#complete-list&sort_name=three_month_average_volume&sort_order=desc&page=1

Besides the idea of hedging a short position to leverage cash balance, I could also use the basic long SPY + SPXU method, but these returns aren't attractive when they just reflect the benchmark rate (Unless they fill some additional demand for stable returns that can't be met elsewhere). 

On the other hand, stable returns can be generated when rates are low by shorting a combination of a highly leveraged long and short fund. The portfolio return in these scenarios varies significantly for different assets, so I would need to check if the return exceeds the borrow cost on a case by case basis. Once again, if the portfolio returns are greater than borrow rate, the short position would only take a fraction of the capital to set up and the returns would be significantly amplified. 

I don't have many great ideas for how to generate meaningful returns only using shares. Using shorts for leverage is something I only thought of recently, but I still can't find a good application besides the scenarios I mentioned above. I considered using a short position to capture the losses of a leveraged long fund and SPY, but the returns were not very strong. I can't really spin up a portfolio that would naturally profit off a short position when rates are high.
 
Just to recap, shorting is another method of leveraging these returns. This works well if pairing highly leveraged funds when rates are high, since the declining value of such a portfolio works in my favor and allows for the cash to safely earn interest at a rate greater than the borrow cost.

Alternatively, when rates are low, a short position in the same pair produces returns greater than the benchmark returns. If the return after the borrowing cost is large enough, the leverage of the short position could make for significant gains. 

I haven't even touched on leveraging returns with options yet, and before I do, I'd like to take a look at one more element of this portfolio. I've established the symmetry between overnight and intraday returns, and speculated that the intraday returns (mostly occuring at open) correct the deviations that happen at night. I just want to seperate these returns by weekday as well. 

Anova test for difference in mean of overnight weekday return distributions p-value > .7. 

Alright time for options. 

## February 11, 2023

I've been making some changes to the options code backtest. One of the bigger problems I'm facing is understanding what part of the price is a result of active trading versus a stale quote for an illiquid security. Having no data to work with, I have to find the oldest active contracts on Robinhood. Naturally, that means most of the contract's life is completely illiquid. 

For some reason the data returns no volume information. Also the prices are displayed as the mid-point between bid-ask, unless the bid or ask falls to 0 offers, in which case the close price defaults to 1 cent. 

I automated the code to pick the expiration with the longest history, but that hasn't been helpful since the choppiness of the prices overshadow any possible trend. This version of the script has been added to todays folder. 

## February 12, 2023

I'll start by changing the script to look at the first unexpired Friday options so that I can get a more liquid instrument. 

Alright first observation:

Using 410 SPY options expiring on February 17th we see a steady divergence between share returns and option returns.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/218332198-d3b96325-0da6-47a5-8251-a73897a4a31a.png" width="250" height="150">
  </kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/218332273-fc285876-bb6f-4f11-8aee-7c35c44a6e9d.png" width="250" height="150">
  </kbd>

</br>
</br>

I did a little review on bonds to tie it into the Put-Call parity:

First, government bonds. These bonds pay compounding interest and come in two forms: Series EE and Series I. Series I is known for its variable rate component tracking interest rates. Series EE has a fixed rate guaranteed to double your principal in 20 years. Bonds can be cashed in after 12 months, although it does forfeit the last 3 months of interest. A maximum of 10,000 dollars can be invested annually, these bonds have no secondary market. 

Then there are Treasury Bills, aka T-bills. T-bills have a maximum maturity period of 52 weeks. These bills pay no interest, but are sold at a discount to their par value. The difference between the purchase price and the par value is the interest earned. The US Treasury periodically issues new bills and determines prices through auctions. These T-bills have a secondary OTC market. Fluctuating rates affect the prices of T-bills on the secondary market since the discount rate gets updated to reflect the new government policy. 

Treasury notes are similar to T-bills but have longer maturity periods. 

Now, the Put-Call parity states that for options of the same strike/expiration: 

C-P = Spot - Discount x Strike, where Discount is the value of a 1 dollar T-bill maturing at option expiration. 

It is worth looking into scenarios where the equality is violated. It isn't just an arbitrary equation, there are profits to be made when a violation occurs. An imbalance in the equation means assets on one side can be shorted and the other bought if the spreads are low enough. 

Discount is linear and can be defined mathematically in terms of time till expiration as: 

1 - (*i* x time till exp. / 365), where *i* is the interest available on a newly issued 52-week T-bill. 

Quick note on this representation: graphing this in terms of t means that we must move from t=365 to t=0, the present. Even though the derivative above is negative, we would interpret our graph moving in the negative x-direction, and we would reverse the rate of change to represent the gradual positive approach towards 1. 

Then, because we are interested in the change relationship between options and price:

delta(C-P) = delta(Spot - Discount x Strike) or delta(C-P) = delta(Spot) - delta(Discount) x Strike

The change is being measured with respect to days till expiration. The rate of change of Discount is positive and constant. This means that, assuming constant rates, the difference between C-P and the spot price grows negative at a constant rate.  

I'll drop some questions to address as I go:
<ul>
  <li>Initially I thought the stochastic movement of the difference between options and stock price was random, but I remember seeing the same movements across all strikes and across all expiration dates. Why?</li>
  <li>Is it time to look at overnight returns for options?</li>
  <li>What happens to the returns I was initially trying to capture? Different scenarios for long and short position profits?</li>
  <li>Can I ever leverage the difference between the shares and the options?</li>
</ul> 

## February 17, 2023

Ok, let me try to elaborate on the thought above. Paraphrasing my notes here: 

I saw that options steadily diverge from the stock price at the discount rate of T-Bills. This in theory would be another opportunity, but with the C-P returns component falling below the graph of returns of shares, I would generate returns by going long shares and short the Call/Put combination. Going long shares would take away the leveraged component I'm chasing. 

My next thought was to swap out the long shares with long leveraged shares, but I think you can see that this begins to resemble the setup I used for shorting. The leveraged long shares lose value at approximately the rate I'm earning. 

Similarly, leveraging by shorting SH wouldn't work either since a short position in SH loses approximately the rate I'm earning. 

## February 18, 2023

Starting to use options becomes a little more interesting. For a brief moment, forget what we know about the divergence between share prices of funds, and imagine only the divergence between options and shares. To generate a return, we could set up a synthetic short in SPY and a synthetic short in *short* SPY like SH. Below is a clarification on how to think about this.

For example, drawing below, SPY option returns fall below SPY shares. Assuming SH returns are perfectly inverse of SPY, and SH option returns fall even lower, then a synthetic short in SH lies above the SPY benchmark. I earn the steady divergence by owning the assets that form the top return graph, and by shorting the assets that form the bottom return graph.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/226246237-aef872d5-46d8-4495-89ab-8b054dc121e1.jpg" width="250" height="150">
  </kbd>
  
But then again, remember that in practice the SH graph of returns lies above its theoretical return. So while the options underperform the SH shares, the SH shares themselves earn a positive constant on top of their expected return, which at the very least negates each other, although its unclear how much. In practice, I would assume the expected return of the portfolio is 0. While a double short means SH and SPY options both generate returns at the natural rate as a consequence of their discount factor, the total portfolio would be losing that same natural rate as a consequence of losses built into the specific asset combination. 

So far I tried using opposite funds to hedge eachother. Because I will either be long or short both, the effects of the discounting of options will stack up positively or negatively, and so far it has stacked up in a way that clashed with the returns of the asset pair itself. 

However, when hedging two leveraged funds like SQQQ and TQQQ, the synthetic short position in both of these assets will work to earn both the option discount and the asset pair decline. 

On top of this, there is also the thought of using two long funds to hedge one another. Since the asset combination would include one long and one short position, its possible that the discounting of the options would cancel out one another, and I would be left to capture the returns baked into the shares.

For example, hedging QQQ with TQQQ:

This image shows the divergence between option returns and share returns of QQQ. 

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219900823-a2fe172a-1d3f-49e4-a2b6-003e6d17063a.png" width="250" height="150">
  </kbd>
  
</br>
</br>

This image shows the divergence between option returns and share returns of TQQQ. 

  <kbd>
<img src="https://user-images.githubusercontent.com/102199762/219900911-4a9335eb-e791-4647-956c-4dbe8ef36bf4.png" width="250" height="150">
  </kbd>
  
</br>
</br>

This image shows the returns of a short position in TQQQ and QQQ, indicating that in the current high rates environment, this combination produces profits.

  <kbd>
<img src="https://user-images.githubusercontent.com/102199762/219900921-e7fcb3f8-1ac1-4c78-97d9-cc18d86686a6.png" width="250" height="150">
  </kbd>
  
</br>
</br>

This image shows the same trend achieved using options. As anticipated, the returns shine through when the option discounts cancel one another out.  

  <kbd>
<img src="https://user-images.githubusercontent.com/102199762/219900925-23d399de-5fcf-4b5d-86c1-da2bdc090b6f.png" width="250" height="150">
  </kbd>
  
</br>
</br>

The images I just shared show the strategy involving two long funds. The images included in the options_analysis of this project directory show the strategy involving a leveraged long and short fund hedge. The percentage returns are large, but the transaction costs scare me. I also hate the volatility of the returns, which is one of the issues I wanted to address before I go. 

Seeing how ugly and choppy the returns are, it seemed reasonable to consider a portfolio comprised of options across different strike prices to "diversify" and minimize the effects of random variations. 

Although I initially assumed that the volatility was random, I'm not sure how to explain that these deviations happen in-sync across all strike prices. For example, I graphed the "options - shares" returns for SPY strike 5 dollars above and below the ATM strike. They all carried the same pattern of movements:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219905352-358afa62-5478-4de1-839f-285ab6fca328.png" width="250" height="150">
  </kbd>

</br>
</br>

I also looked at further expiration dates and they continued to move in sync, although less so for very old and illiquid options. Here is an image of SPY options expiring in a month:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219907270-1621f027-474d-482b-a85a-17cc80a85b7d.png" width="250" height="150">
  </kbd>

</br>
</br>

Before I take a look at other assets, I noticed something that bothers me a little. According to my understanding of the Put-Call parity, the difference I graphed above should be declining at a constant rate. But similar to this image below for SQQQ and TQQQ, the decline coincides with the graph of share returns:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219908802-7a2e7dce-ca27-4218-b181-18e94a6d51d9.png" width="250" height="150">
  </kbd>

</br>
</br>

For reference, here is the SPY/SH (left) and TQQQ/SQQQ (right) graph:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219908744-db181d24-34bb-42e0-8156-978067b5edb7.png" width="250" height="150">
  </kbd>
  
<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219909064-3eec23ba-4ea2-439b-9dd4-25c3f318cd65.png" width="250" height="150">
  </kbd>

</br>
</br>

I feel a little better saying that this is just a coincidence, because the flatness prior to the decline occurs for every contract with a long history. Even when the move doesn't coincide with pattern in shares, as seen below: 

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219908723-7536ab76-005a-4980-b276-793aeea5d1ee.png" width="250" height="150">
  </kbd>
  
</br>
</br

The movements were exactly the same for SPY and QQQ, not DIA however, which is another major index. It was also liquid and steady across its strikes. I guess that may indicate that the shifts are more related to the constituents of the ETF, rather than market wide conditions. 

## February 19, 2023

I started looking into overnight and intraday returns for options. For example, below are some pics for SPY. 

For SPY, the calls and puts just seem to track the returns of the underlying shares. The images detailing each are below:

This image shows overnight and intraday movements for calls.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219965984-a0a8e993-a932-4f0b-84ba-c825ae60fe29.png" width="250" height="150">
  </kbd>
  
</br>
</br>

This image shows overnight and intraday movements for puts.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219975377-786eb8fa-d651-4544-8c13-9dffdaf7b17b.png" width="250" height="150">
  </kbd>

</br>
</br>

This image shows intraday and overnight movements for the underlying shares.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219975149-42203c41-efa8-4324-8eb8-5abd3c965342.png" width="250" height="150">
  </kbd>

</br>
</br>

But then there are assets like SQQQ which have a more pronounced deviation. The puts and calls don't really track the underlying shares. Share returns on the left, puts and calls middle, night and day options bottom: 

This image shows overnight and intraday share returns.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219977096-8f0dc189-6a12-401e-b313-cdb4524d7987.png" width="250" height="150">
  </kbd>
  
  </br>
</br>

This image shows overnight and intraday returns for puts. 

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/219977139-98336b4f-e754-4760-bcbf-9122cc50c353.png" width="250" height="150">
  </kbd>
  
</br>
</br>

This image shows overnight and intraday returns for calls. 

  <kbd>
<img src="https://user-images.githubusercontent.com/102199762/219977208-3b3bd748-88ac-4a2d-8a57-25ffac6b9185.png" width="250" height="150">
  </kbd>

</br>
</br>

These image show overnight and intraday divergence between options and shares.

  <kbd>
<img src="https://user-images.githubusercontent.com/102199762/219977223-ef22e5a3-3846-4180-943f-f562097c53ac.png" width="250" height="150">
  </kbd>
  
  <kbd>
<img src="https://user-images.githubusercontent.com/102199762/219977197-fe32a6ee-2e1d-490e-a418-7df1d08d3881.png" width="250" height="150">
  </kbd>

</br>
</br>

**Potential ideas**:

<ul>
  <li>Hedging assets to earn a positive rebate on short positions on IBKR. Making sure that the fund combination either also declines or lies flat so it doesn't interfere with the rebate.</li>
  <li>Hedging a synthetic position in a long ETF with an inverse synthetic position in another long ETF. This cancels out the discount factor in the put-call parity and leaves the returns generated through shares.</li>
  <li>Setting up two synthetic short positions in two opposite funds to profit off of the discount rate priced into the options and the direction of the portfolio.</li>
  <li>Placing synthetic long or short position intraday or overnight to capture the trends.</li>
</ul>

So why won't I do these things? The first idea relies completely on IBKR's generosity and requires a large amount of cash to qualify. My understanding is that short proceeds typically do not get this privelage and cannot be used for further investments. 

The second idea should work in theory, and returns generally shine through. However they are so volatile that they appear almost random. In many cases I don't see the steady divergence that I rely on to make this work, whether its because of other factors like priced in borrow rates, or just because the liquidity is too low. In most cases I can't zoom out far enough to see a long term trend because the contracts with long history are just too choppy. 

I've tried to get around the choppiness by diversifying but I already learned that different strikes still move together, and I can't weed out the trend that I want.

For the third idea, the funds I'm most interested in are now trending upwards. Performance wise it should be more consistent than the second idea, since profits come from both the movements of the underlying security and the option discount deviation. But again, there are only a handful of liquid candidates that do not have high  borrowing rates priced into them. 

Well I just threw in the fourth idea because it crossed my mind. I don't have historic intraday options data to tell if it would work. I should put a little effort into learning the IBKR simulator to just automate simple stuff like this and see how it goes. Otherwise I can never really determine how serious spread and slippage is. 

**Alright now potentially useful stuff I've learned**:

<ul>
  <li>Divergence of leveraged and inverse funds relative to their benchmark is priced into the NAV. It has to do with the way funds are structured themselves.</li>
  <li>This divergence is strong during overnight sessions. In this case, it would be valuable to find out whether the divergence is also present in NAV to narrow its cause. who knows maybe it's a play on the difference in liquidity? Being able to influence the price and dump shares back in a more liquid setting? Or creating a better/more predictable setting for market making?</li>
  <li>Put-Call parity deviations happen in unison across all strikes and expirations. Not random. So what causes it?</li>
</ul>





