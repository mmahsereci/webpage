---
layout: page
title: "Publications"
subtitle: ""
permalink: /publications/
feature-img: "assets/img/publications/aurora_02.jpg"
#hide: True

tags: [Page]
---

<div class="pub-img"><img src="./../assets/img/blog/story.jpeg"></div>

**Active Multi-Information Source Bayesian Quadrature**<br>
The paper introduces active learning for Bayesian quadrature when multiple related information sources of variable
cost in input and source are accessible. This setting arises for example when evaluating the integrand requires a 
complex simulation to be run that can be approximated by simulating at lower levels of sophistication and at lesser 
expense. We construct meaningful cost-sensitive multi-source acquisition rates and discuss pitfalls.

<div style="line-height:1%;"><br></div>
*A. Gessner, J. Gonzalez, M. Mahsereci* Proceedings of The 35th Uncertainty in Artificial Intelligence Conference, PMLR 115:712-721, 2020. 

<div class="pub-ul"><ul>
    <li><a class="button-pub" href="http://proceedings.mlr.press/v115/gessner20a.html"><p>Paper</p></a></li>
    <li><a class="button-pub" onclick="CollapseBibTeX('Gessner19')"><p>BibTeX</p></a></li>
</ul></div>

<div class="pub-bib" id="Gessner19">
  <blockquote> 
    <div class="div-name">@inproceedings{Gessner19,
        <div class="div-info">
          title = {Active Multi-Information Source Bayesian Quadrature},<br>
          author = {Gessner, Alexandra and Gonzalez, Javier and Mahsereci, Maren},<br>
          booktitle = {Proceedings of The 35th Uncertainty in Artificial Intelligence Conference},<br>
          pages = {712--721},<br>
          year = {2020},<br>
          editor = {Adams, Ryan P. and Gogate, Vibhav},<br>
          volume = {115},<br>
          series = {Proceedings of Machine Learning Research},<br>
          month = {22--25 Jul},<br>
          publisher = {PMLR}
        </div>  
      }
   </div>
  </blockquote>
</div>

---

<div style="line-height:500%;">
    <br>
</div>




<script>
function CollapseBibTeX(name) {
  var x = document.getElementById(name);
  if (x.style.display == "none" || x.style.display == '') { 
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}
</script>
