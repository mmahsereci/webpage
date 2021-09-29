---
layout: page
title: "Projects"
subtitle: ""
permalink: /projects/
#feature-img: "assets/img/projects/01a.png"
feature-img: "assets/img/projects/06.jpg"

tags: [Page]
---


# Research

<div class="projects">
    <div class="project-teaser">
        <div class="project-img">
            <img alt="Hallo" src="./../assets/img/projects/03.png">
        </div>
    </div>
</div>

## Stochastic Optimization

Empirical risk minimization for hiigh-dimensiona lobejctives, potetntiallhy a lot f data, stochsticity.
how can we even make progress in those spaces. It makes sens eto me than information or handling en noise is crucual
.Related pruning: how do we use the information of te optimizer to solve other simulatenous talsk, suh as orunig or overfitting.

I am ahighly motivated by these questions

<ul style="list-style: none; margin: 0; padding: 0; display: inline-flex; font-size: 0.9em">
    <li><a class="button-projects" href=""><p>Thesis</p></a></li>
    <li><a class="button-projects" href=""><p>Papers</p></a></li>
</ul>



<div class="projects">
    <div class="project-teaser">
        <div class="project-img">
            <img alt="Hallo" src="./../assets/img/projects/01.png">
        </div>
    </div>
</div>

## Probabilistic Numerics 

sjfsfjsfiljfsal jflsfjafslafk fslfjlksdj safd  fjslfjlaf  

<ul style="list-style: none; margin: 0; padding: 0; display: inline-flex; font-size: 0.9em">
    <li><a class="button-projects" href=""><p>Papers</p></a></li>
</ul>


<div class="projects">
    <div class="project-teaser">
        <div class="project-img">
            <img alt="Hallo" src="./../assets/img/projects/bq.png">
        </div>
    </div>
</div>

## Bayesian Qudrature

The counter part to optmization. Instea dof geedy, local diff, we need the iverse traform which is unforntualy not easy to get.
But it is  the bsis of inference, and we puld get the road smoothed if we ever were to make progress.

<ul style="list-style: none; margin: 0; padding: 0; display: inline-flex; font-size: 0.9em">
    <li><a class="button-projects" href=""><p>Papers</p></a></li>
</ul>


<hr style="border:2px solid gray"> 

# Open Source Software

<div class="projects">
    <div class="project-teaser">
        <div class="project-img">
            <img alt="Hallo" src="./../assets/img/projects/city.png">
        </div>
    </div>
</div>

## EmuKit
I am one of the original authors and co-maintainer of the 
[EmuKit](https://github.com/EmuKit/emukit) Python library. 
EmuKit is a highly adaptable Python toolkit for decision-making under uncertainty. Its core components is an 
active learning loop that unifies several active machine learning methods such as experimental design, 
Bayesian optimization and Bayesian quadrature. 
EmuKit's design allows the user to customize the active learning algorithms quickly, 
by switching out or adding new components, and even to wrap 
a custom surrogate models via an interface. Read more on EmuKit's structure 
[here](https://emukit.github.io/about/) or check it out on [GitHub](https://github.com/EmuKit/emukit).

<ul style="list-style: none; margin: 0; padding: 0; display: inline-flex; font-size: 0.9em">
    <li><a class="button-projects" href="https://github.com/EmuKit/emukit"><p>Code</p></a></li>
    <li><a class="button-projects" href="https://emukit.github.io/"><p>Site</p></a></li>
    <li><a class="button-projects" href="https://ml4physicalsciences.github.io/2019/files/NeurIPS_ML4PS_2019_113.pdf"><p>Paper</p></a></li>
    <li><a class="button-projects" onclick="CollapseBibTeX('BibEntryEmukit')"><p>BibTeX</p></a></li>
</ul>

<div id="BibEntryEmukit" style="display: none; color: #e6db74;">
  <blockquote style="border: 0px solid #666; padding: 10px; background-color: #2E3440;"> 
    <div style="margin-left: 0.5em;">
      @inproceedings{emukit2019,
        <div style="margin-left: 2em;">
          author = {Paleyes, Andrei and Pullin, Mark and Mahsereci, Maren and Lawrence, Neil and González, Javier},<br>
          title = {Emulation of physical processes with Emukit},<br>
          booktitle = {Second Workshop on Machine Learning and the Physical Sciences, NeurIPS},<br>
          year = {2019}
        </div>  
      }
   </div>
  </blockquote>
</div>


<div class="projects">
    <div class="project-teaser">
        <div class="project-img">
            <img alt="Hallo" src="./../assets/img/projects/probnum_logo_dark_txtright.svg">
        </div>
    </div>
</div>

## ProbNum

I am a contributor and maintainer of the [ProbNum](https://github.com/probabilistic-numerics/probnum) Python library.
ProbNum provides numerical solvers for linear systems, intractable integrals and ordinary differential equations.
In cotrast to classic solvers, 
ProbNum solvers not only estimate the solution of the numerical problem, but also its uncertainty (numerical error) which 
arises from finite computational resources, discretization and stochastic input. 
The estimated numerical uncertainty can be used in downstream decisions.

Lower level structure of ProbNum includes: A module for random variables and random variable arithmetics;
(memory-)efficient and lazy implementation of linear operators that integrate with random variables;
filtering and smoothing for probabilistic state-space models, mostly variants of Kalman filters.


<ul style="list-style: none; margin: 0; padding: 0; display: inline-flex; font-size: 0.9em">
    <li><a class="button-projects" href="https://github.com/probabilistic-numerics/probnum"><p>Code</p></a></li>
    <li><a class="button-projects" href="http://www.probabilistic-numerics.org"><p>Site</p></a></li>
</ul>



<script>
function CollapseBibTeX(name) {
  var x = document.getElementById(name);
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}
</script>
