---
layout:     post
title:      "Percentiles & Confidence Intervals"
author:     mmahsereci
snippet:    ""
date:       2021-09-01
thumbnail-small:  "/img/2021-09-01-confidence-intervals/thumbnail.png"
category:   techblog
tags:       [Statistics, Blog]

---

Fix the image paths

### Confidence Intervals: SE and Probability

The standard error as defined above informs us about the expected variability of the statistic $$\bar{x}_n$$.
In combination with another assumption on the distribution of $$\bar{x}_n$$ we can use the SE to 
formulate a statement of probability. That is we can articulate with what probability the interval 
$$\bar{x}_n \pm SE[\bar{x}_n]$$ covers the true value $$\mu$$ for a sample of size $$n$$.
The assumption we require is that $$\bar{x}_n$$ is normal distributed with mean $$\mu$$ (WHAT ABOUT THE indentical ditribtion?).
Assuming a normal distribution seems quite specific, but it is often valid at least approximately in particular if
$$\bar{x}_n$$ is some kind of sum or average (as is the case in our coin toss example) and $$n$$ not too small 
approx $$> 100$$. (The normal approximation is a topic for another post).

and variance $$\sigma^2_n$$.

In essence the idea is the normal approximattion

requires the normal approximation. perhaps for another post.

 ![png]({{ site.baseurl }}/img/2021-09-01-confidence-intervals/01.png)

 ![png]({{ site.baseurl }}/img/2021-09-01-confidence-intervals/06.png)

 ![png]({{ site.baseurl }}/img/2021-09-01-confidence-intervals/07.png)

There is more to confidence intervals, for example they can be defined for skewe distirubtions, too. but 
that is the topic of another blog post.

