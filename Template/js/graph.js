
 function getDocWidth()
  {
          var x = 0;
          if (self.innerHeight)
          {
                  x = self.innerWidth;
          }
          else if (document.documentElement && document.documentElement.clientHeight)
          {
                  x = document.documentElement.clientWidth;
          }
          else if (document.body)
          {
                  x = document.body.clientWidth;
          }
          return x;
  }

  function getDocHeight()
  {
          var y = 0;
          if (self.innerHeight)
          {
                  y = self.innerHeight;
          }
          else if (document.documentElement && document.documentElement.clientHeight)
          {
                  y = document.documentElement.clientHeight;
          }
          else if (document.body)
          {
                  y = document.body.clientHeight;
          }
          return y;
  }

function rescaleGraph() {
	var w = 560;
	var h = 700;
	// for debug purposes...
	// console.log('rescaling with width=' + w + 'px & height=' + h + 'px')
	svg.attr("width", w);
	svg.attr("height", h);
	force.size([w, h]);
        d3.select("body").select("svg").attr("width", w);
        d3.select("body").select("svg").attr("height", h);

	// experiment: energize the graph to center itself...
	force.alpha(force.alpha() + .03)
}

function positionNodes() {
	// Initialize node positions to prevent strange starts...
	nodes.forEach(function(d, i) {
	  d.x = ((w / n) * i) + (w / (n/2)) ;
	  d.y = (h / 2) + ((Math.random() - 0.5) * (h/2));
	});
}

function freezeNodes() {
	nodes.forEach(function(d, i) {
	  d.fixed = 1;
	});
}

function thawNodes() {
	nodes.forEach(function(d, i) {
	  d.fixed = 0;
	});
}

var toggleColor = (function(){
   var currentColor = "#ccc"; 
    return function(){
        currentColor = currentColor == "#ccc" ? "yellow" : "#ccc";
        d3.select(this).style("fill", currentColor);
    }
})();

function exportToSvg(form_action) {

	serializer = new XMLSerializer();
	serialized = serializer.serializeToString(document.getElementById('mainSVG'));

	// Create form and post
	var form = document.createElement("form");
	form.setAttribute("method", "post");
	form.setAttribute("action", form_action);
	form.setAttribute("target", "_blank");

	var hiddenField = document.createElement("input");
	hiddenField.setAttribute("type", "hidden");
	hiddenField.setAttribute("name", "svgInnerHTML");
	hiddenField.setAttribute("value", serialized);

	form.appendChild(hiddenField);

	document.body.appendChild(form);
	form.submit();
}

//window.onload = function() {
//	var t=setTimeout(rescaleGraph, 20);
//};

window.onresize = function(event) {
	rescaleGraph();
}
 function setColormap(colorstring) {

         path.attr('style','stroke: '+colorstring+';');
     }

