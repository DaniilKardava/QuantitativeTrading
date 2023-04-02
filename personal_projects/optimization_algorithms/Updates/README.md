## Index

[February 19, 2023](#february-19-2023) : Initial thoughts and plans regarding efficacy of algorithms in out of sample data. 

[February 20, 2023](#february-20-2023) : Compared out-of-sample performance to in-sample performance for the volatility minimization algorithm. 

[February 22, 2023](#february-22-2023) : Testing the efficacy of the hedging algorithm. 

[February 23, 2023](#february-23-2023) : Hedging algorithm demonstration and optimization algorithm improvements. 

[February 24, 2023](#february-24-2023) : Added 0 volatility cash term. 

[February 26, 2023](#february-26-2023) : Added concurrent solver with random guess vectors. Rewrote algorithms with scipy's fast optimize function that supports inequality constraints. Changed my task to maximization of the sharpe ratio while maintaining a minimum return. 

[March 4, 2023](#march-4-2023) : Generated a large sample to measure algorithm performance. Compared out-of-sample, in-sample, and 0 optimization. 

[March 8, 2023](#march-8-2023) : Analyzed algorithm performance for validation periods of annual and semi-annual lengths. 

[March 9, 2023](#march-9-2023) : Correlated in-sample and out-of-sample outperformance. 

[March 10, 2023](#march-10-2023) : Compared quarterly, semi-annual, annual, and every other year validation length. 

[March 11, 2023](#march-11-2023) : Repeating tests for a new sample of assets. 

[March 17, 2023](#march-17-2023) : Continued tests for new sample of assets. Calculated conditions under which optimization was favorable. 

[March 18, 2023](#march-18-2023) : Continued tests for new sample of assets. Compared different validation length performance. 

[March 19, 2023](#march-19-2023) : Compared output of 100 concurrent guess vectors against 25 concurrent guess vectors.

[March 23, 2023](#march-23-2023) : Concluding thoughts.

## February 19, 2023

There is really only one thing I want to know here. Do the optimization algorithms have any use for out-of-sample data? Once we establish that, then the ideas can start flowing in. 

I'll start with the volatility minimization portfolio. I think it would be good to break down the training data into subsamples and measure their volatility. Then I could compare them to subsamples from the validation phase. 

Now that I think about it, it would be nice to visualize the portfolio volatility for out-of-sample data as a function of time away from the end of the training sample. That way I could see if the effects of the optimization gradually wear off. 

## February 20, 2023

I did both of the things I mentioned above, visualizing the trailing portfolio volatility both during and after the training phase. Unfortunately I'm realizing that market variance is a huge confounding variable. I'm thinking of extending my training set and comparing it to the portfolio that stopped training earlier. 

I have a choice here, since I wasn't sure whether I should be comparing the OOS data to a model trained up to and including this data, or a model trained exclusively on this data. I'm choosing the first case, but I can't entirely formulate why. 

Ok so I created a script to compare two hardcoded solutions. One solution was generated from optimizing up to and including my period of interest, while the second solution was generated from optimizing only up to my period of interest. 

I graph the overlapping portfolio volatilities, sharpes, and pvalues returned by a levenes test, a measure of difference in volatility. I saved the code under today's date with the name "INvsOUT". 

This is pretty exciting. So far the portfolio of 4 assets: SPY, QQQ, TLT, and GLD, has shown that there is an extended period of comparable performance between the portfolio trained on that time range and the portfolio trained up to that time range. 

This image shows a comparison of the volatility of the in-sample portfolio and the out-of-sample portfolio.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/220213377-f2b03f33-1b1d-47bc-9943-3a8661069e9e.png" width="250" height="150">
  </kbd>

</br>
</br>

This image shows a comparison of the sharpe ratios of the in-sample portfolio and the out-of-sample portfolio.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/220213396-d09a1818-2c83-4634-89c7-95ea7643d7f8.png" width="250" height="150">
  </kbd>

</br>
</br>

This image shows a two sided significance test of difference in volatility as a function of time away from validation start. 

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/220213408-5ddb3520-b6dd-42ca-b52a-bd962acc617d.png" width="250" height="150">
  </kbd>

</br>
</br>

This image shows the portfolio returns of the in-sample and out-of-sample asset allocations.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/220213434-17368aef-c3b0-4866-bda5-baaeafe2e2c5.png" width="250" height="150">
  </kbd>

</br>
</br>

I'm still working with constraints that set my returns precisely equal to SPY and my sum of assets precisely equal to 1. In its current state, the algorithm is pretty weak and does a bad job with a larger pool of assets. 

Modifying my constraints would be the first step towards building a more practical algorithm. In the meantime, I want to apply similar analysis methods to my hedging algorithm.

Specifically I want to know if there is any advantage to using a custom generated portfolio to track a target curve after the training period ends. I think that just checking for a correlation between the portfolio and the target would be a good metric.

## February 22, 2023

Last time I came to the conclusion that I should measure the performance of the hedging algorithm by looking at its correlation to the target. These results could them be compared to the assets correlation with a broad market index. 

Unfortunately the broad market index showed superior correlation almost every time. The optimization algorithm seems to be nothing more than a fancy math tool. 

## February 23, 2023

I want to test some general ideas for the hedging algorithm. First, I'd like to show that more assets can provide a stronger hedge. For example, 10 random assets to hedge KO vs 150 random assets to hedge KO:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/220981044-32d7b880-8a21-48a0-b20f-f1ddd9f6e55b.png" width="250" height="150">
  </kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/220980448-d125dfa9-7d43-4811-8db9-2b3822bfa39b.png" width="250" height="150">
  </kbd>

</br>
</br>

But obviously it didn't help for the out of sample region, plus it takes a long time to solve such a large system of equations.

I just thought of a potential work around to the constraints issue. If I maximize sharpe, I will incorporate volatility and returns into a single equation. On top of this, the weights can later be scaled without affecting the sharpe ratio. 

I also redefined the weight terms in the volatility function to behave as percentages by dividing every variable by the sum of the of all variables. This naturally makes their sum 1. The code has been added above. 

## February 24, 2023

I did some more thinking and added a cash asset term. However, so far this has hurt results. 

## February 26, 2023

I've realized that the guess vector is going to be pretty important and I want to run multiple solvers concurrently with different guesses. In this new verion I've also ranked outputs by the highest sharpe. Now the cash term doesn't get in the way, and the algo converges to whatever solution was optimal without it. 

I've also been working on rewriting the main function to incorporate returns by using the sharpe metric. I was struggling to use sympy's equation solver after removing constraints. For some reason the solver always returned equal weights. I stumbled upon the scipy optimization library and was able to get something running. 

I tested scipy's minimize function on my lagrangian equation from the volatility minimization algorithm, and found that the execution time was much faster.

I was curious whether I should indicate my constraints separately or pass the lagrangian. After a little reading I settled on passing constraints separately, since scipy was optimized to solve specific types of problems using difference methods. On top of this, I can pass inequality constraints! 

I also realized that simply maximizing a sharpe equation without constraints won't always work, like in the presence of a bond ETF. I will maintain a returns constraint that sets a target which can realistically be leveraged. The weight constraint will be built into the main function and I will keep the cash term.

## March 4, 2023

I don't see any other way to test the difference in sharpes between the in and out-of-sample data other than doing many trial runs. I wrapped everything in a massive loop to increment the years, measure the differences, and analyze the final distrubution. To speed up the process, I've decreased the number of tickers to 10. 

So far I've been measuring differences on a daily basis. However, the volatility in output is extremeley high and I think it will be more efficient to only look at the final values after a certain period of time. 

Here's the distribution measuring the difference in sharpes between an in-sample and out-of-sample portfolio:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/222932446-b2a850a6-451b-4fc5-929d-558661e4e4ff.png" width="480" height="300">
  </kbd>
  
</br>
</br>

The distribution was centered at .118 with a standard deviation of .321. This mean was significantly greater than 0.

## March 8, 2023

Now I've started working with end of period values. I looked at the annual and the semi-annual distributions. 

Here are the statistics for the annual "in-sample - out-of-sample" sharpe differences:

Data points: 90

In-sample - out-of-sample sharpe mean: 0.08465056074414269

Standard deviation of difference in sharpes: 0.19162744773711293

P-value significance that mean is greater than 0: 3.561650285922841e-05

Below are the "in-sample - out-of-sample" semi-annual distribution statistics:

Data-points: 140

In-sample - out-of-sample sharpe mean: 0.1269307578230602

Standard deviation of difference in sharpes: 0.3149992967686759

P-value significance that mean is greater than 0: 2.4960415060582343e-06

## March 9, 2023

I need to understand whether a larger in-sample outperformance relative to an equal weights portfolio correlates with a larger out-of-sample outperformance. Using a scatter and a correlation matrix, I will analyze the performance gaps between in-sample and equal weights, and the corresponding gap between in-sample and out-of-sample. 

I also want to analyze the direct out-of-sample outperformance relative to 0 optimization.

I recalculated the annual statistics with 260 data points.

In-sample - out-of-sample sharpe mean: 0.09522029484277714

Standard deviation of difference in sharpes: 0.19842689710803676

P-value significance that mean is greater than 0: 1.245113770408026e-13

The correlation between the gaps was .4. Once again, this correlation measures the relationship between the "in-sample - equal weights performance gap" and the "in-sample - out-of-sample performance gap." A scatter was plotted with the first measurement on the X-axis and the second measurement on the Y-axis. 

After fitting a regression line to the data, I calculated a slope of .42. For every point increase in the in-sample outperformance relative to 0 optimization, the in-sample only outperformed out-of-sample weights by an additional .4 points. A small slope indicates stronger out-of-sample performance, while a slope near one suggests that optimization has no benefit in practice. 

The scatter described in the paragraph above:

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/224441647-8c5bb3f5-43a3-4ea5-a5d0-690556c2fa5c.png" width="250" height="150">
  </kbd>

</br>
</br>

For now, rather than calculating the distribution and mean given by the difference in out-of-sample and 0 optimization, I chose to find the regression line predicting out-of-sample output as a function of 0 optimization. The slope of this regression is 1.02, indicating that out-of-sample performance was 2% higher than 0 optimization.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/224441293-f8f14d2b-1f3d-418d-b002-7e7332a8a374.png" width="250" height="150">
  </kbd>

## March 10, 2023

Below are the "in-sample - out-of-sample" statistics for the semi-annual validation period, containing 280 data points:

In-sample - out-of-sample sharpe mean: 0.08670459489363255

Standard deviation of difference in sharpes: 0.32837301737229646

P-value significance that mean is greater than 0: 3.6407160764599414e-06

Please refer to the last log for an explanation of these metrics.

The in-sample and out-of-sample outperformance correlation coefficient: .562.

The slope of the regression line: .56.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/224465415-378ff839-a016-4379-a6b8-f7fd8007fb29.png" width="250" height="150">
  </kbd>

</br>
</br>

The slope of the regression line grew larger, but this isn't the full picture. In the future, I will analyze the intercept and calculate at what cutoff point in-sample outperformance translates to out-of-sample outperformance. 

For now, the important statistic is still direct comparison between out-of-sample and 0 optimization. The slope of the regression relating 0 optimization to out-of-sample performance is still 1.02. The image is shown below.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/224466093-348242d1-3969-406f-ad09-55a878c6a6d5.png" width="250" height="150">
  </kbd>

</br>
</br>

I will move on to quarterly recalculations. Here are the statistics for the "in-sample - out-of-sample" data, 320 data points:

In-sample - out-of-sample sharpe mean: 0.1097899238216193

Standard deviation of difference in sharpes: 0.4903462360790972

P-value significance that mean is greater than 0: 3.9543941669932146e-05

The in-sample and out-of-sample outperformance correlation coefficient: .476.

The slope of the regression line: .449.

This time the slope of the regression relating 0 optimization to out-of-sample performance is .96, indicating the out-of-sample performance is worse than no optimization.

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/224505479-b7effed5-0f00-4dcb-86f6-2dc49a997445.png" width="250" height="150">
  </kbd>

<kbd>
<img src="https://user-images.githubusercontent.com/102199762/224505499-39c3feb8-ce0e-47bf-8e51-dcec147bc79b.png" width="250" height="150">
  </kbd>

</br>
</br>

I also neglected to measure the significance of my slopes. I've calculated p-values for the hypothesis that my slope is greater than 1.

Annual data p-value: 0.008808.

Semi-annual p-value: 0.06898.

Quarterly p-value: 0.99367. 

Annual had the strongest performance, so I went ahead and measured "in-sample - out-of-sample sharpe differences" for a 2 year validation period. I collected 110 data points: 

In-sample - out-of-sample sharpe mean: 0.06362166092517994

Standard deviation of difference in sharpes: 0.10647237178614419

P-value significance that mean is greater than 0: 4.3072978028452465e-09

The in-sample and out-of-sample outperformance correlation coefficient: .38.

The slope of the regression line: .28.

This time the slope of the regression relating 0 optimization to out-of-sample performance was 1.07, indicating that out-of-sample performance is much stronger than no optimization. On top of this, optimization often allocates capital to cash reserves, so returns could be larger than indicated. The p-value for the hypothesis "slope is greater than 1" is .0003.

Unfortunately, the high variability in output makes this impractical, even if there is an edge to be realized. It makes me wonder whether dropping to a lower timeframe would allow for more frequent optimization and realization of an edge. 

## March 11, 2023

I've been thinking about the volatility algorithm, which I haven't worked with in a while. I just wanted to record some ideas relating to options trading. If I could establish a relationship between an equal weights portfolio and an optimized portfolio, as I have done with my sharpe algorithms, I could set up potential mean reverting trades to trade volatility convergence and divergence.

I'm going to rerun my tests with another group of 10 assets to try to validate my findings and compare outputs. 

I will also check for a correlation between train length and out-of-sample outperformance. 

These are the new assets that I'm working with:

["CAR", "CMG", "EFX", "GRMN", "FIS", "LULU", "MNST", "PHM", "TRIP", "WDC"]

## March 17, 2023

I repeated the annual validation length for my new sample of tickers:

Data points: 420
</br>
--------- In vs Out ---------
</br>
In - Out Sharpe diff means: 0.24340357538571405
</br>
In - Out Sharpe diff std dev: 0.3431871457598067
</br>
Paired test in-out, in greater than out p_value: 2.8224249579696344e-39
</br>
---------- In Sample Outperformance vs Out Sample Outperformace ----------
</br>
LOBF Slope: 0.5729356388892592
</br>
Constant: 0.11881699217768041
</br>
--------- Equal vs Out of Sample ------------
</br>
LOBF Slope: 0.8867607639350045
</br>
P-value slope greater than 1: 0.9999999999999988
</br>
-------- Out of sample vs Equal Sample -----------
</br>
Out-Equal Sharpe diff means: -0.02595055841234592
</br>
Out-Equal Sharpe diff std dev: 0.32046366603133486
</br>
Paired test out-equal, in greater than out p_value: 0.9509247918030413
</br>
----------- Train Length vs Outperformance -----------
</br>
Train length and difference slope: 0.022526153954125407
</br>
Train length and difference slope p-value: 0.4323127626727965
</br>
--------- In vs Equal ---------
</br>
In - Equal Sharpe diff means: 0.21745301697336814
</br>
In - Equal Sharpe diff std dev: 0.32153062149458805

For this sample of tickers, I observed a higher in-sample outperformance, which indicates that the tickers themselves play a big role in potential outcomes. I also did not find that optimization had any superior performance in practice. 

I also made a more rigorous interpretation of my "In Sample Outperformance vs Out Sample Outperformace" metrics. In order to justify optimization, the in-sample outperformance relative to no optimization must have a larger gap than the in-sample outperformance relative to out-of-sample. This is simply saying that out-of-sample performance must lie closer to in-sample performance than 0 optimization does. In other words out-of-sample lies above 0 optimization. 

In terms of an inequality, where x is the in-sample outperformance relative to 0 optimization:
</br>
x > .6x + .1

This inequality is satisfied by x > .25. The optimization is inferior to no optimization when in-sample outperformance is lower than .25 points. We can never know what in-sample outperformance will be beforehand since these metrics form over the same period of time. 

## March 18, 2023

At the end of the day, it appears as though this algorithm will only be viable if the out of sample performance is greater than equal weights and there are no other metrics that can compensate for this basic truth. On my end, I can control duration between optimization, the portfolio size, and possibly the length of optimization if that turns out to be meaningful. 

On my end, I can control duration between optimization and portfolio size. I have not seen an indication that shorter periods of validation correspond to stronger performance. In fact I've seen the opposite in my last sample of 10. 

The other variable that I can adjust is the size of my portfolio. In theory I would expect a larger number of assets to carry more potential for optimization outperformance.

I have recalculated the semi-annual statistics for this sample of assets, but I could not find significant improvements of any sort.

Data points: 400
</br>
--------- In vs Out ---------
</br>
In - Out Sharpe diff means: 0.20785887360055147
</br>
In - Out Sharpe diff std dev: 0.5078753226393615
</br>
Paired test in-out, in greater than out p_value: 1.9840170956911415e-15
</br>
---------- In Sample Outperformance vs Out Sample Outperformace ----------
</br>
LOBF Slope: 0.5215527398976123
</br>
Constant: 0.12046391687018529
</br>
--------- Equal vs Out of Sample ------------
</br>
LOBF Slope: 0.9000871050487083
</br>
P-value slope greater than 1: 0.9999999590747808
</br>
-------- Out of sample vs Equal Sample -----------
</br>
Out-Equal Sharpe diff means: -0.04029201018512201
</br>
Out-Equal Sharpe diff std dev: 0.4978287258909757
</br>
Paired test out-equal, in greater than out p_value: 0.9466317052166262
</br>
----------- Train Length vs Outperformance -----------
</br>
Train length and difference slope: 0.0027423019195362635
</br>
Train length and difference slope p-value: 0.857090667159636
</br>
--------- In vs Equal ---------
</br>
In - Equal Sharpe diff means: 0.16756686341542945
</br>
In - Equal Sharpe diff std dev: 0.4841482238022425

Below are the quarterly validation period statistics. Once again, no significant improvements:

Data points: 440
</br>
--------- In vs Out ---------
</br>
In - Out Sharpe diff means: 0.21196922270167912
</br>
In - Out Sharpe diff std dev: 0.7364953607408956
</br>
Paired test in-out, in greater than out p_value: 1.7384223479264307e-09
</br>
---------- In Sample Outperformance vs Out Sample Outperformace ----------
</br>
Positive slope indicates a higher outperformance carries on to out of sample
</br>
LOBF Slope: 0.434089910807246
</br>
Constant: 0.10375500120723045
</br>
--------- Equal vs Out of Sample ------------
</br>
LOBF Slope: 0.9200896287754847
</br>
P-value slope greater than 1: 0.9998356316559165
</br>
-------- Out of sample vs Equal Sample -----------
</br>
Out-Equal Sharpe diff means: 0.03732065665352269
</br>
Out-Equal Sharpe diff std dev: 0.7880736780551163
</br>
Paired test out-equal, in greater than out p_value: 0.16081464543138774
</br>
----------- Train Length vs Outperformance -----------
</br>
Train length and difference slope: 0.006943360412923838
</br>
Train length and difference slope p-value: 0.43893133659175976
</br>
--------- In vs Equal ---------
</br>
In - Equal Sharpe diff means: 0.24928987935520178
</br>
In - Equal Sharpe diff std dev: 0.7723536178761351

I also analyzed 2 year validation periods, since the last sample of 10 looked promising. Unfortunately, there was no significant improvement in performance either:

Data points: 115
</br>
--------- In vs Out ---------
</br>
In - Out Sharpe diff means: 0.21074556589696378
</br>
In - Out Sharpe diff std dev: 0.18885444516457633
</br>
Paired test in-out, in greater than out p_value: 4.72362686740098e-22
</br>
---------- In Sample Outperformance vs Out Sample Outperformace ----------
</br>
Positive slope indicates a higher outperformance carries on to out of sample
</br>
LOBF Slope: 0.4038357503486878
</br>
Constant: 0.14166165612933412
</br>
--------- Equal vs Out of Sample ------------
</br>
LOBF Slope: 0.9639705731492537
</br>
P-value slope greater than 1: 0.8960922212296147
</br>
-------- Out of sample vs Equal Sample -----------
</br>
Out-Equal Sharpe diff means: -0.03967623954836816
</br>
Out-Equal Sharpe diff std dev: 0.20108251304261662
</br>
Paired test out-equal, in greater than out p_value: 0.9813328205572348
</br>
--------- In vs Equal ---------
</br>
In - Equal Sharpe diff means: 0.17106932634859562
</br>
In - Equal Sharpe diff std dev: 0.1574542177841414

## March 19, 2023

For this new sample of 10 assets, I haven't found any benefit provided by optimization. Changing my validation length didn't improve performance either, so I'm left to expand my number of assets. 

To speed up the process, I will begin by analyzing solutions with only 25 concurrent guess vectors.

These are the annual statistics using 25 concurrent solvers. They aren't very uplifting. I'm going to try returning to 100 solvers to compare the performance levels:

Data points: 200
</br>
--------- In vs Out ---------
</br>
In - Out Sharpe diff means: 0.1171549301284836
</br>
In - Out Sharpe diff std dev: 0.2476199291893711
</br>
Paired test in-out, in greater than out p_value: 1.2073395511749557e-10
</br>
---------- In Sample Outperformance vs Out Sample Outperformace ----------
</br>
Positive slope indicates a higher outperformance carries on to out of sample
</br>
LOBF Slope: 0.8335374889089654
</br>
Constant: 0.04094082316906274
</br>
--------- Equal vs Out of Sample ------------
</br>
LOBF Slope: 0.9782609359252692
</br>
P-value slope greater than 1: 0.9622927638792448
</br>
-------- Out of sample vs Equal Sample -----------
</br>
Out-Equal Sharpe diff means: -0.025720402019641014
</br>
Out-Equal Sharpe diff std dev: 0.18912412293434624
</br>
Paired test out-equal, in greater than out p_value: 0.9717593520102491
</br>
----------- Train Length vs Outperformance -----------
</br>
Train length and difference slope: 0.012529337492633017
</br>
Train length and difference slope p-value: 0.23045139635079714
</br>
--------- In vs Equal ---------
</br>
In - Equal Sharpe diff means: 0.09143452810884259
</br>
In - Equal Sharpe diff std dev: 0.1956989700539512

I've rerun the same annual statistics with 100 concurrent solvers. No improvements, so I will run future analysis with only 25 solvers:

Data points: 210
</br>
--------- In vs Out ---------
</br>
In - Out Sharpe diff means: 0.14544601100814436
</br>
In - Out Sharpe diff std dev: 0.23576804239152305
</br>
Paired test in-out, in greater than out p_value: 1.1989340864306247e-16
</br>
---------- In Sample Outperformance vs Out Sample Outperformace ----------
</br>
Positive slope indicates a higher outperformance carries on to out of sample
</br>
LOBF Slope: 0.6516229314828214
</br>
Constant: 0.07809160480894144
</br>
--------- Equal vs Out of Sample ------------
</br>
LOBF Slope: 0.9755689575966511
</br>
P-value slope greater than 1: 0.9676293442313664
</br>
-------- Out of sample vs Equal Sample -----------
</br>
Out-Equal Sharpe diff means: -0.042081928891002665
</br>
Out-Equal Sharpe diff std dev: 0.20972988337530013
</br>
Paired test out-equal, in greater than out p_value: 0.9979394462496423
</br>
----------- Train Length vs Outperformance -----------
</br>
Train length and difference slope: 0.018487902324688235
</br>
Train length and difference slope p-value: 0.16116583847315535
</br>
--------- In vs Equal ---------
</br>
In - Equal Sharpe diff means: 0.10336408211714171
</br>
In - Equal Sharpe diff std dev: 0.19558274550072197

## March 23, 2023

Suffice to say that neither semi-annual nor quarterly validation periods showed different results, although this has already been established previously. I acknowledge that this is a math problem with lots of existing research. I am not helping myself by trying to solve it with my limitted math education, and should instead go learn some linear algebra. 

In conclusion, I have not been able to show that this algorithm has superior out of sample performance. Validation lengths had no effect on algorithm performance, train length had no effect on performance, and doubling the portfolio size did not improve performance either. 

I don't think these tests have been very rigorous. My point is that I don't really have the stats background to do this efficiently and confidently. 
