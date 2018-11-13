var links;
var my_nodes;
d3.json('graph.json', function(error, data) {
 console.log(data)
  var links = data['links']
  var my_nodes = data['nodes']


//sort links by source, then target
links.sort(function(a,b) {
    if (a.source > b.source) {return 1;}
    else if (a.source.id < b.source.id) {return -1;}
    else {
        if (a.target.id > b.target.id) {return 1;}
        if (a.target.id < b.target.id) {return -1;}
        else {return 0;}
    }
});


//any links with duplicate source and target get an incremented 'linknum'
for (var i=0; i<links.length; i++) {
    if (i != 0 &&
        links[i].source.id == (links[i-1].source.id ) &&
        links[i].target.id == (links[i-1].target.id )) {
            links[i].linknum = links[i-1].linknum + 1;
        }
    else {links[i].linknum = 1;};
};



// Compute the distinct nodes from the links.
links.forEach(function(link) {
  link.source = my_nodes[link.source] ;
  link.target = my_nodes[link.target] ;
});

var w = 3500,
    h = 3500;

var force = d3.layout.force()
    .nodes(d3.values(my_nodes))
    .links(links)
    .size([w, h])
    .linkDistance(300)
    .charge(-2500)
    .on("tick", tick)
	.start()
    

var svg = d3.select("body").append("svg:svg")
    .attr("width", w)
    .attr("height", h);

// Per-type markers, as they don't inherit styles.
svg.append("svg:defs").selectAll("marker")
    .data(["suit", "licensing", "resolved"])
  .enter().append("svg:marker")
    .attr("id", String)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15)
    .attr("refY", -1.5)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
  .append("svg:path")
    .attr("d", "M0,-5L10,0L0,5");

var c20c = d3.scale.category20c();

var path = svg.append("svg:g").selectAll("path")
    .data(force.links())
  .enter().append("svg:path")
    .attr("class", function(d) {return "link " + d.group; })
    .attr("stroke", function(d){return c20c(parseInt(d.group))});

var circle = svg.append("svg:g").selectAll("circle")
    .data(force.nodes())
  .enter().append("svg:circle")
    .attr("r", function(d) { return d.count ; })
    .call(force.drag)
    .on("mouseover", function(d) {
  d3.select(this).transition().attr("r", d.count + 5);
  d3.selectAll("path.link").transition().style('stroke-width', function(l) {
    if (d === l.source || d === l.target)
      return 2.5;
    else
      return 1.5;
    }).style('opacity', function(l){
    if (d === l.source || d === l.target)
      return 1;
    else
      return 0.05;
    });
})                  
.on("mouseout", function(d) {
  d3.select(this).transition().attr("r", d.count);
  path.style('stroke-width', 1.5);
	d3.selectAll("path.link")
  .transition()
  .style("opacity", 0.1);
});

var text = svg.append("svg:g").selectAll("g")
    .data(force.nodes())
  .enter().append("svg:g");

// A copy of the text with a thick white stroke for legibility.
text.append("svg:text")
    .attr("x", 8)
    .attr("y", ".31em")
    .attr("class", "shadow")
    .text(function(d) { if (d.count > 1 ){return d.id}; })
    ;

text.append("svg:text")
    .attr("x", 8)
    .attr("y", ".31em")
    .text(function(d) { if (d.count > 1 ){return d.id}  })
    ;
    

// Use elliptical arc path segments to doubly-encode directionality.
function tick() {
  path.attr("d", function(d) {
    var dx = d.target.x - d.source.x,
        dy = d.target.y - d.source.y,
        dr = 75/d.linknum;  //linknum is defined above
    return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
  });

  circle.attr("transform", function(d) {
    return "translate(" + d.x + "," + d.y + ")";
  });

  text.attr("transform", function(d) {
    return "translate(" + d.x + "," + d.y + ")";
  });
}});
