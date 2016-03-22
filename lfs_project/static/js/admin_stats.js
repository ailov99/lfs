/* 
   Generates a barchart of Module - #Visits
   using a record of format [ { module_title : #visits }, ... ]
*/
function gen_modules_barchart(modules_data) {

    // set up chart margins & size
    var margin = {top: 20, right: 20, bottom: 30, left: 40},
	width = 760 - margin.left - margin.right,
	height = 400 - margin.top - margin.bottom;

    var x = d3.scale.ordinal()
	.rangeRoundBands([0, width], .1);

    var y = d3.scale.linear()
	.range([height, 0]);

    var xAxis = d3.svg.axis()
	.scale(x)
	.orient("bottom");

    var yAxis = d3.svg.axis()
	.scale(y)
	.orient("left")
	.ticks(10, ""); // Y step

    var svg = d3.select("body").append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
	.append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top
	      + ")");

    // data mapping, similar to a .tsv()/.csv() call
    // uses an array of Object instead
    x.domain(modules_data.map(function(d) { return d.mod_title; }));
    y.domain([0, d3.max(modules_data, function(d) { return d.hit_count; })]);

    svg.append("g")
	.attr("class", "x axis")
	.attr("transform", "translate(0," + height + ")")
	.call(xAxis);

    svg.append("g")
	.attr("class", "y axis")
	.call(yAxis)
	.append("text")
	.attr("transform", "rotate(-90)")
	.attr("y", 6)
	.attr("dy", ".71em")
	.style("text-anchor", "end")
	.text("Hits");

    svg.selectAll(".bar")
	.data(modules_data)
	.enter().append("rect")
	.attr("class", "bar")
	.attr("x", function(d) { return x(d.mod_title); })
	.attr("width", x.rangeBand())
	.attr("y", function(d) { return y(d.hit_count); })
	.attr("height", function(d) { return height - y(d.hit_count); });
    

    function type(d) {
        d.hit_count = +d.hit_count;
        return d;
    }
}

/*
   Generates a linechart of Day - #Newly_registered_users
   using a record of format [ { Date : #registrations }, ... ]
*/
function gen_regs_linechart(regs_data) {
    
    var margin = {top: 20, right: 20, bottom: 30, left: 50},
	width = 760 - margin.left - margin.right,
	height = 400 - margin.top - margin.bottom;

    var formatDate = d3.time.format("%d-%m-%Y");

    var x = d3.time.scale()
	.range([0, width]);

    var y = d3.scale.linear()
	.range([height, 0]);

    var xAxis = d3.svg.axis()
	.scale(x)
	.orient("bottom");

    var yAxis = d3.svg.axis()
	.scale(y)
	.orient("left");

    var line = d3.svg.line()
	.x(function(d) { return x(formatDate.parse(d.date)); })
	.y(function(d) { return y(d.reg_count); });

    var svg = d3.select("body").append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
	.append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // data mapping, similar to a .tsv()/.csv() call
    // uses an array of Object instead
    x.domain(d3.extent(regs_data, function(d) { return formatDate.parse(d.date); }));
    //y.domain(d3.extent(regs_data, function(d) { return d.reg_count; }));
    // hard-coded y domain range
    var max_hit = 0
    for (var i = 0; i < 7; i++) {
    	if (regs_data[i].reg_count > max_hit)
    		max_hit = regs_data[i].reg_count
    }
    y.domain([0, max_hit + 10]);

    svg.append("g")
	.attr("class", "x axis")
	.attr("transform", "translate(0," + height + ")")
	.call(xAxis);

    svg.append("g")
	.attr("class", "y axis")
	.call(yAxis)
	.append("text")
	.attr("transform", "rotate(-90)")
	.attr("y", 6)
	.attr("dy", ".71em")
	.style("text-anchor", "end")
	.text("New users #");

    svg.append("path")
	.datum(regs_data)
	.attr("class", "line")
	.attr("d", line);

    function type(d) {
	d.date = formatDate.parse(d.date);
	d.reg_count = +d.reg_count;
	return d;
    }
}


/*
   Generates a linechart of Day - #Anonymous user visits of the welcome page
   using a record of format [ { Date : #registrations }, ... ]
*/
function gen_anon_hits_linechart(anon_hits_data) {
    
    var margin = {top: 20, right: 20, bottom: 30, left: 50},
	width = 760 - margin.left - margin.right,
	height = 400 - margin.top - margin.bottom;

    var formatDate = d3.time.format("%d-%m-%Y");

    var x = d3.time.scale()
	.range([0, width]);

    var y = d3.scale.linear()
	.range([height, 0]);

    var xAxis = d3.svg.axis()
	.scale(x)
	.orient("bottom");

    var yAxis = d3.svg.axis()
	.scale(y)
	.orient("left");

    var line = d3.svg.line()
	.x(function(d) { return x(formatDate.parse(d.date)); })
	.y(function(d) { return y(d.anon_hits_count); });

    var svg = d3.select("body").append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
	.append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // data mapping, similar to a .tsv()/.csv() call
    // uses an array of Object instead
    x.domain(d3.extent(anon_hits_data, function(d) { return formatDate.parse(d.date); }));

    // hard-coded y domain range
	var max_hit = 0
    for (var i = 0; i < 7; i++) {
    	if (anon_hits_data[i].anon_hits_count > max_hit)
    		max_hit = anon_hits_data[i].anon_hits_count
    }
    
    y.domain([0, max_hit + 10]);

    svg.append("g")
	.attr("class", "x axis")
	.attr("transform", "translate(0," + height + ")")
	.call(xAxis);

    svg.append("g")
	.attr("class", "y axis")
	.call(yAxis)
	.append("text")
	.attr("transform", "rotate(-90)")
	.attr("y", 6)
	.attr("dy", ".71em")
	.style("text-anchor", "end")
	.text("Anonymous Users Hits #");

    svg.append("path")
	.datum(anon_hits_data)
	.attr("class", "line")
	.attr("d", line);

    function type(d) {
	d.date = formatDate.parse(d.date);
	d.anon_hits_count = +d.anon_hits_count;
	return d;
    }
}
