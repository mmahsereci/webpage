---
layout:     post
title:      "Invariant Gaussian Processes"
author:     mmahsereci
snippet:    ""
date:       2021-09-06
thumbnail-small:  "/img/2021-09-06-invariant-gp/thumbnail.png"
category:   techblog
tags:       [Blog, Gaussian process]

---

Gaussian processes can be understood as "distributions over functions" providing prior models for
unknown functions. The kernel which identifies the GP can be used to encode known properties of the function such 
as smoothness or stationarity. A somewhat more exotic charcateristic is *invariance to input transformations* 
which we'll explore here.

## What is an invariant function?

I came across the paper of [Wilk et al. 2018](https://proceedings.neurips.cc/paper/2018/file/d465f14a648b3d0a1faa6f447e526c60-Paper.pdf) 
a while ago which introduces Gaussian processes that are invariant
under a finite set of input transformations. 
Let's first see what an invariant function is: A function $$f:\mathbb{X} \rightarrow \mathbb{R}$$ on the domain $$\mathbb{X}\subseteq\mathbb{R}^D$$
is said to be invariant under a bijective transformation 
$$T:\mathbb{X}\rightarrow \mathbb{X}$$ if 
$$f(T(\mathbb{x})) = f(\mathbb{x})$$ holds for all $$\mathbb{x}$$ in $$\mathbb{X}$$.
This simply means that the function $$f$$ takes the same value at $$\mathbb{x}$$ and $$T(\mathbb{x})$$ for all $$\mathbb{x}$$.

> Simple 1D example: $$f(x) = x^2$$ is invariant under flipping the x-axis, i.e., $$f(x) = f(-x)$$ with $$T(x) = -x $$.


### Modelling a black-box function with known invariances

Consider now a function which is invariant under a finite set of $$J$$ transformations $$T_i$$, $$i=1, ..., J$$.
As the invariance under each $$T_i$$ holds for any input $$\mathbb{x}$$ (also inputs that have been transformed), 
the $$T_i$$ must form the group 
$$G_f:=\{T | f(\mathbb{x}) = f(T(\mathbb{x})) \text{ for all } \mathbb{x} \in\mathbb{X}\}$$. 
That is, among others, concatenations $$T_i\circ T_j\circ \dots$$ must also be in $$G_f$$, as well as the identity transform $$T=I$$,
and the inverse transforms $$T_i^{-1}$$. 

> Simple 1D example: $$f(x) = x^2$$. The group $$G_f$$ only contains $$J=2$$
transformations $$G_f = \{T_0, T_1\}$$ with $$T_0(x)=x$$ and $$T_1(x)=-x$$. 
This is because all possible concatenations  $$T_i\circ T_j\circ \dots$$ as well as the inverses $$T_i^{-1}$$ 
collapse back to $$T_0$$ or $$T_1$$ and are thus already in $$G_f$$ (Examples: $$T_1^{-1} = T_1$$, or $$T_1\circ (T_1 \circ T_1) = T_1\circ T_0 = T_1$$ etc). 
In other examples the group-size $$J$$ may be larger.


Given $$G_f$$, the set $$\mathcal{A}(\mathbb{x}):=\{T(\mathbb{x}) | \text{ for all } T\in G_f\}$$ 
is called an *orbit* and is the set of invariant locations induced by $$\mathbb{x}$$.
Thus we can introduce a function $$g: \mathbb{X} \rightarrow \mathbb{R}$$ such that

$$
f(\mathbb{x}) = \sum_{\tilde{\mathbb{x}}\in \mathcal{A}(\mathbb{x})}g(\tilde{\mathbb{x}}).
$$

We can see that any point $$\tilde{\mathbb{x}}\in A(\mathbb{x})$$ induces the identical set 
$$A(\tilde{\mathbb{x}}) = A(\mathbb{x})$$, thus 
$$f(\tilde{\mathbb{x}}) = f(\mathbb{x})$$ for all $$\tilde{\mathbb{x}}\in A(\mathbb{x})$$
(notice that $$G_f$$ includes the identity transform, the trivial invariance for all functions).

We see from the above equation that we do not need to know the form of $$f(\mathbb{x})$$ in order to encode the 
invariance property, simple knowing the set $$G_f$$ is enough. In that sense, $$f(\mathbb{x})$$ can be a black-box function.

## Making it probabilistic (An invariant Gaussian process prior)

If the function $$f$$ is unknown, and we want to learn it from a set of function evaluations, we can treat the 
inference problem probabilistically to account for the uncertainty of value of $$f$$ where $$f(x)$$ is not observed.
In certain circumstance, a good choice of models are Gaussian processes (GPs), especially since they let us 
encode properties of the function leading to sample efficient learning methods.
In our case, the property we want to encode is the invariance of $$f$$ under the group $$G_f$$ as defined above. 
We again follow [Wilk et al. 2018](https://proceedings.neurips.cc/paper/2018/file/d465f14a648b3d0a1faa6f447e526c60-Paper.pdf) (Section 4.1).

In essence, we are free to model the latent function $$g$$ as a Gaussian process, such that $$g\sim\mathcal{G}(m_g, k_g)$$ with mean function $$m_g$$ and 
kernel function $$k_g$$.
Thus, $$f$$ is also a Gaussian process $$f\sim\mathcal{G}(m_f, k_f)$$, as $$f$$ is a linear combination of Gaussian distributed values 
(and Gaussians are closed under linear tranformations). 
The mean function $$m_f$$ and kernel function $$k_f$$ can be easily derived:

$$
    m_f(\mathbb{x}) =\sum_{\tilde{\mathbb{x}}\in \mathcal{A}(\mathbb{x})}m_g(\tilde{\mathbb{x}}),\qquad
    k_f(\mathbb{x}, \mathbb{x}') = \sum_{\tilde{\mathbb{x}}', \tilde{\mathbb{x}}\in \mathcal{A}(\mathbb{x})}  k_g(\tilde{\mathbb{x}}, \tilde{\mathbb{x}}').
$$

GP regression on $$f$$ is straightforward, too, as the above equation simply defines another positive definite kernel $$k_f$$.

We did not tranform the distribton it is sill Gaussian

## 1D example and plot



## other

We'll assume that basics of Gaussian processes (GPs) are known and leave their introduction to another blogpost. 

A Gaussian process (GP) is defined as a collection of random variables every finite subset of which has joint 
Gaussian distribution [2]. In essence this means that even though we are dealing with an infinite dimensional object
we only ever need to work with finite dimensions in practice, e.g., by discretizing the space.

Thus, a Gaussian process can be thought of as an 'infinite Gaussian distribution' and when we marginalize all but 
a finite number of dimensions, we obtain a Gaussian distribution. The covariance kernel fucniton intrdo


## Prior Samples of invariant GPs

Let's create some pretty plots. Below we plot 4 x 8 = 32 samples of invariant Gaussian processes with a 2D input domain.
The samples are from the prior GP not conditions on any data. We can see that the samples obey the invariances encoded.


### Rotations

 ![png]({{ site.baseurl }}/img/2021-09-06-invariant-gp/rotations_00.png)


### Point-symmetry

 ![png]({{ site.baseurl }}/img/2021-09-06-invariant-gp/point_00.png)

### axis-flips

 ![png]({{ site.baseurl }}/img/2021-09-06-invariant-gp/flip-point_00.png)




## References

[1] Wilk et al. 2018 *Learning invariances using the marginal likelihood*, 
    Advances in Neural Information Processing Systems 31, pages 9938–9948.

[2] Rasmussen and Williams 2006. *Gaussian Processes for Machine Learning.* Adaptive Computation and Machine Learning. 
MIT Press, Cambridge, MA, USA.
