(function(exports) {

  var form = d3.select("#search"),
      inputs = form.selectAll("*[name]"),
      formatPrice = d3.format(",.02f"),
      formatCommas = d3.format(","),
      api = new hourglass.API(),
      $search = $("#labor_category"),
      resultsTable = d3.select("#results-table")
        .style("display", "none"),
      sortHeaders = resultsTable.selectAll("thead th")
        .call(setupColumnHeader),
      loadingIndicator = form.select(".loading-indicator"),
      request;

  form.on("submit", function onsubmit() {
    // stop the form from submitting
    d3.event.preventDefault();
    submit(true);
  });

  form.on("reset", function onsubmit() {
    // XXX we shouldn't have to do this...
    // shouldn't a reset input clear them?
    inputs.each(function() {
      // FIXME: if this.type === "checkbox", toggle this.checked
      this.value = "";
    });
    submit(true);
  });

  inputs.on("change", function onchange() {
    submit(true);
  });

  initialize();

  window.addEventListener("popstate", popstate);

  function initialize() {
    popstate();

    var autoCompReq;
    $search.autoComplete({
      minChars: 2,
      delay: 5,
      cache: true,
      source: function(term, done) {
        // console.log("search:", term);
        if (autoCompReq) autoCompReq.abort();
        autoCompReq = api.get({
          uri: "search",
          data: {q: term},
        }, function(error, result) {
          autoCompReq = null;
          if (error) return done([]);
          var categories = result.slice(0, 20).map(function(d) {
            return {
              term: d.labor_category,
              count: d.count
            };
          });
          return done(categories);
        });
      },
      renderItem: function(item, search) {
        var re = new RegExp("(" + search.split(" ").join("|") + ")", "gi"),
            term = item.term || item;
        return [
          '<div class="autocomplete-suggestion" data-val="' + term + '">',
            '<span class="term">', term.replace(re, "<b>$1</b>"), '</span>',
            '<span class="count">', item.count, '</span>',
          '</div>'
        ].join("");
      }
    });
  }

  function popstate() {
    // read the query string and set values accordingly
    var data = hourglass.extend(
      getFormData(),
      hourglass.qs.parse(location.search)
    );
    inputs.on("change", null);
    setFormData(data);
    inputs.on("change", function onchange() {
      submit(true);
    });

    var sort = parseSortOrder(data.sort);
    sortHeaders
      .classed("sorted", function(d) {
        return d.sorted = (d.key === sort.key);
      })
      .classed("descending", function(d) {
        return d.descending = (d.sorted && sort.order === "-");
      });
    updateSortOrder(sort.key);

    submit(false);
  }

  function submit(pushState) {
    var data = getFormData();
    inputs.classed("filter_active", function() {
      return !!this.value;
    });

    console.log("submitting:", data);

    form.classed("loaded", false);
    form.classed("loading", true);

    // cancel the outbound request if there is one
    if (request) request.abort();
    var defaults = {
      histogram: 10
    };
    request = api.get({
      uri: "rates", 
      data: hourglass.extend(defaults, data)
    }, update);


    d3.select("#export-data")
      .attr("href", function() {
        return [
          this.href.split("?").shift(),
          hourglass.qs.format(data)
        ].join("?");
      });

    if (pushState) {
      var href = "?" + hourglass.qs.format(data)
      history.pushState(null, null, href);
    }
  }

  function update(error, data) {
    form.classed("loading", false);
    request = null;

    if (error) {
      if (error.statusText === "abort") {
        // ignore aborts
        return;
      }

      form.classed("error", true);

      loadingIndicator.select(".error")
        .text(error.responseText);

      console.error(error.responseText);
    } else {
      form.classed("error", false);
    }

    console.log("update:", data);
    form.classed("loaded", true);

    d3.select("#results-total")
      .text(data ? formatCommas(data.count) : "(none)");

    if (data && data.results && data.results.length) {
      updatePriceRange(data);
      updatePriceHistogram(data);
      // updateHourlyWages(data.hourly_wage_stats, [data.minimum, data.maximum]);
      updateResults(data.results || []);
    } else {
      data = EMPTY_DATA;
      updatePriceRange(EMPTY_DATA);
      updatePriceHistogram(EMPTY_DATA);
      // updateHourlyWages([], [0, 0]);
      updateResults([]);
    }
  }

  function updatePriceRange(data) {
    var priceScale = d3.scale.linear()
      .domain([data.minimum, data.maximum])
      .range([0, 100]);

    var graph = d3.select("#price-range");

    graph.select(".min")
      .call(setPrice, data.minimum);
    graph.select(".max")
      .call(setPrice, data.maximum);
    graph.select(".average")
      .call(setPrice, data.average)
      .style("left", priceScale(data.average) + "%");

    function setPrice(selection, price) {
      selection.select(".value")
        .text(formatPrice(+price));
    }
  }

  var histogramUpdated = false,
      EMPTY_DATA = {
        minimum: 0,
        maximum: 100,
        average: 50,
        wage_histogram: [
          {count: 0, min: 0, max: 50},
          {count: 0, min: 50, max: 1}
        ]
      };
  function updatePriceHistogram(data) {
    var width = 500,
        height = 200,
        pad = [30, 15, 50, 45],
        top = pad[0],
        left = pad[3],
        right = width - pad[1],
        bottom = height - pad[2],
        svg = d3.select("#price-histogram")
          .attr("viewBox", [0, 0, width, height].join(" ")),
        formatDecimal = d3.format(".02f"),
        formatDollars = function(n) {
          return "$" + formatDecimal(n);
        };

    var extent = [data.minimum, data.maximum],
        bins = data.wage_histogram,
        x = d3.scale.linear()
          .domain(extent)
          .range([left, right]),
        height = d3.scale.linear()
          .domain(d3.extent(bins, function(d) { return d.count; }))
          .range([0, bottom - top]);

    var xAxis = svg.select(".axis.x");
    if (xAxis.empty()) {
      xAxis = svg.append("g")
        .attr("class", "axis x");
    }

    var yAxis = svg.select(".axis.y");
    if (yAxis.empty()) {
      yAxis = svg.append("g")
        .attr("class", "axis y");
    }

    var gBar = svg.select("g.bars");
    if (gBar.empty()) {
      gBar = svg.append("g")
        .attr("class", "bars");
    }

    var avg = svg.select("g.avg");
    if (avg.empty()) {
      avg = svg.append("g")
        .attr("class", "avg");
      avg.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", -10)
        .html('<tspan class="value"></tspan> average');
      avg.append("line");
      avg.append("circle")
        .attr("cy", -4)
        .attr("r", 3);
    }

    avg.select("line")
      .attr("y1", -4)
      .attr("y2", bottom - top + 8); // XXX tick size = 6
    avg.select(".value")
      .text(formatDollars(data.average));

    var bars = gBar.selectAll(".bar")
      .data(bins);

    bars.exit().remove();

    var enter = bars.enter().append("g")
      .attr("class", "bar");
    enter.append("title");

    var step = (right - left) / bins.length;
    enter.append("rect")
      .attr("x", function(d, i) {
        return left + i * step;
      })
      .attr("y", bottom)
      .attr("width", step)
      .attr("height", 0);

    bars.select("title")
      .text(function(d, i) {
        var inclusive = (i === bins.length - 1),
            sign = inclusive ? "<=" : "<";
        return [formatCommas(d.count), ":", formatDollars(d.min), "<= x " + sign, formatDollars(d.max)].join(" ");
      });

    var t = histogramUpdated
      ? svg.transition().duration(500)
      : svg;

    t.select(".avg")
      .attr("transform", "translate(" + [~~x(data.average), top] + ")");

    t.selectAll(".bar")
      .each(function(d) {
        d.x = x(d.min);
        d.width = x(d.max) - d.x;
        d.height = height(d.count);
        d.y = bottom - d.height;
      })
      .select("rect")
        .attr("x", function(d, i) { return d.x; })
        .attr("y", function(d, i) { return d.y; })
        .attr("height", function(d, i) { return d.height; })
        .attr("width", function(d, i) { return d.width; });

    var ticks = bins.map(function(d) { return d.min; })
      .concat([data.maximum]);

    var xa = d3.svg.axis()
      .orient("bottom")
      .scale(x)
      .tickValues(ticks)
      .tickFormat(function(d, i) {
        return (i === 0 || i === bins.length)
          ? formatDollars(d)
          : formatDecimal(d);
      });
    xAxis.call(xa)
      .attr("transform", "translate(" + [0, bottom + 2] + ")")
      .selectAll(".tick")
        .classed("primary", function(d, i) {
          return i === 0 || i === bins.length;
        })
        .select("text")
          .attr("text-anchor", "end")
          .attr("transform", "translate(-20,16) rotate(-45)");

    var ya = d3.svg.axis()
      .orient("left")
      .scale(d3.scale.linear()
        .domain(height.domain())
        .range([bottom, top]))
      .tickValues(height.domain());
    ya.tickFormat(formatCommas);
    yAxis.call(ya)
      .attr("transform", "translate(" + [left - 2, 0] + ")");

    histogramUpdated = true;
  }

  function updateHourlyWages(stats, domain) {
    var graph = d3.select("#hourly-wages"),
        row = graph.selectAll(".row")
          .data(stats, function(d) {
            return d.min_years_experience;
          });

    row.exit().remove();

    var enter = row.enter().append("div")
      .attr("class", "row");

    enter.append("span")
      .attr("class", "row-label years");

    var bar = enter.append("div")
      .attr("class", "bar")
      .style({
        "margin-left": "0%",
        "margin-right": "0%"
      });
    bar.append("span")
      .attr("class", "average")
      .style("left", "0%")
      .append("span")
        .attr("class", "label")
        .html('$<b class="value"></b><i class="count"></i>');

    var wageScale = d3.scale.linear()
      .domain(domain)
      .range([0, 100]);

    row.select(".years")
      .text(function(d) {
        return d.min_years_experience;
      });

    var bar = row.select(".bar")
      .style("margin-left", function(d) {
        return wageScale(d.min_wage) + "%";
      })
      .style("margin-right", function(d) {
        return wageScale(d.max_wage) + "%";
      });

    var avg = bar.select(".average")
      .style("left", function(d) {
        return wageScale(d.average_wage) + "%";
      });
    avg.select(".value")
      .text(function(d) {
        return d.average_wage;
      });
    avg.select(".count")
      .text(function(d) {
        return d.num_contracts;
      });
  }

  function updateResults(results) {
    d3.select("#results-count")
      .text(formatCommas(results.length));

    resultsTable.style("display", null);

    var thead = resultsTable.select("thead"),
        columns = thead.selectAll("th").data(),
        tbody = resultsTable.select("tbody");

    var tr = tbody.selectAll("tr")
      .data(results);

    tr.exit().remove();
    tr.enter().append("tr");

    var td = tr.selectAll("td")
      .data(function(d) {
        return columns.map(function(column) {
          var key = column.key,
              value = d[key];
          return {
            column: column,
            row: d,
            key: key,
            value: value,
            string: column.format(value)
          };
        });
      });

    td.exit().remove();

    var sortKey = parseSortOrder(getFormData().sort).key;
    td.enter().append("td")
      .attr("class", function(column) {
        return "column-" + column.key;
      })
      .classed("collapsed", function(d) {
        return d.column.collapsed;
      })
      .classed("sorted", function(c) {
        return c.column.key === sortKey;
      });
    td.html(function(d) {
      return d.column.collapsed ? "" : d.string;
    });
  }

  function getFormData() {
    var data = {};
    inputs.each(function() {
      switch (this.type) {
        case "checkbox":
          if (!this.checked) return;
          break;
      }
      if (this.disabled || this.value === "") return;
      data[this.name] = this.value;
    });
    return data;
  }

  function setFormData(data) {
    if (!data) return;
    inputs.each(function() {
      if (data.hasOwnProperty(this.name)) {
        switch (this.type) {
          case "checkbox":
            this.checked = data[this.name] == this.value;
            return;
        }
        this.value = data[this.name];
      }
    });
  }

  function setupColumnHeader(headers) {
    headers
      .datum(function() {
        return {
          key: this.getAttribute("data-key"),
          format: getFormat(this.getAttribute("data-format")),
          sortable: this.classList.contains("sortable"),
          collapsible: this.classList.contains("collapsible")
        };
      })
      .each(function(d) {
        this.classList.add("column-" + d.key);
      });

    headers.filter(function(d) { return d.sortable; })
      .call(setupSortHeader);

    headers.filter(function(d) { return d.collapsible; })
      .call(setupCollabsibleHeader);
  }

  function setupSortHeader(headers) {
    headers
      .each(function(d) {
        d.sorted = false;
        d.descending = false;
      })
      .on("click", setSortOrder);

    function setSortOrder(d, i) {
      headers.each(function(c, j) {
        if (j !== i) {
          c.sorted = false;
          c.descending = false;
        }
      });

      if (d.sorted) {
        d.descending = !d.descending;
      }
      d.sorted = true;

      var sort = (d.descending ? "-" : "") + d.key;
      setFormData({sort: sort});

      updateSortOrder(d.key);

      submit(true);
    }
  }

  function updateSortOrder(key) {
    sortHeaders
      .classed("sorted", function(c) { return c.sorted; })
      .classed("descending", function(c) { return c.sorted && c.descending; });

    resultsTable.selectAll("tbody td")
      .classed("sorted", function(c) {
        return c.column.key === key;
      });
  }

  function setupCollabsibleHeader(headers) {
    headers
      .each(function(d) {
        d.collapsed = this.classList.contains("collapsed");
        d.label = this.innerText;
      })
      .on("click", function(d) {
        d.collapsed = !d.collapsed;
        updateCollapsed.apply(this, arguments);
      })
      .each(updateCollapsed);

    function updateCollapsed(d) {
      var title = [
        (d.collapsed ? "Show" : "Hide"),
        d.label
      ].join(" ");

      d3.select(this)
        .classed("collapsed", d.collapsed)
        .attr("title", title)
        .text(d.collapsed ? "" : d.label);

      resultsTable.selectAll("td.column-" + d.key)
        .classed("collapsed", d.collapsed)
        .html(d.collapsed
          ? ""
          : function(d) { return d.string; });
    }
  }

  function parseSortOrder(order) {
    if (!order) return {key: null, order: null};
    var first = order.charAt(0),
        sort = {order: ""};
    switch (first) {
      case "-":
        sort.order = first;
        order = order.substr(1);
        break;
    }
    sort.key = order;
    return sort;
  }

  function showError(error) {
    alert(error);
  }

  function getFormat(spec) {
    if (!spec) return function(d) { return d; };

    if (spec.indexOf("{}") > -1) {
      return function(d) {
        return spec.replace(/{}/g, d)
          .replace(/\?{(.+)}/g, d == 1 ? "" : "$1");
      };
    }

    var index = spec.indexOf("%");
    if (index === -1) {
      return d3.format(spec);
    }
    var prefix = spec.substr(0, index),
        format = d3.format(spec.substr(index + 1));
    return function(str) {
      if (!str) return "";
      return prefix + format(+str);
    };
  }

})(this);
