(function(hourglass) {

  /**
   * The API class is used to access the Hourglass REST API. Usage:
   *
   * var api = hourglass.API();
   * api.get("uri", function(error, data) {
   *   if (error) return console.log("error:", error.statusText);
   * });
   *
   * // e.g. for paginated responses
   * api.get({
   *   uri: "rates",
   *   data: {page: 2, ...}
   * }, function(error, data) {
   * });
   */
  hourglass.API = function(path) {
    if (!(this instanceof hourglass.API)) {
      return new hourglass.API(path);
    }
    this.path = path || "/api/";
  };

  hourglass.API.prototype = {
    /**
     * get the fully qualified URL for a given request, specified either as a
     * URI string or a "request" object with either a .url or .uri property.
     */
    url: function(request) {
      var uri = (typeof request === "object")
        ? request.uri || request.url
        : request;
      // TODO: merge request.data if provided and uri includes "?"
      return (this.path + uri).replace(/\/\/+/g, "/");
    },

    /**
     * perform an API request, where `request` is a URI (string)
     * or an object with a `uri` property and an optional `data`
     * object containing query string parameters. The `callback`
     * function is called node-style ("error-first"):
     *
     * api.get("blarg", function(error, data) {
     *   if (error) return console.error("error:", error);
     * });
     *
     * api.get("rates/", function(error, data) {
     *   // do something with data
     * });
     */
    get: function(request, callback) {
      var url = this.url(request),
          data = hourglass.extend({
            format: "json"
          }, hourglass.qs.coerce(request.data));
      return $.getJSON(url, data)
        .done(function(data) {
          return callback(null, data);
        })
        .fail(function(error) {
          return callback(error);
        });
    }
  };

  /**
   * query string parse/format
   */

  hourglass.qs = {

    // parse a query string into a data object
    parse: function(str) {
      // return an empty object if there's no string or values
      if (!str || str === "?") return {};
      var data = {};
      // lop off the ? at the start
      if (str.charAt(0) === "?") str = str.substr(1);
      str.split("&").forEach(function(part) {
        var i = part.indexOf("=");
        if (i === -1) {
          data[part] = true;
        } else {
          var key = unescape(part.substr(0, i)),
              val = unescape(part.substr(i + 1));
          switch (val) {
            case "true": val = true; break;
            case "false": val = false; break;
          }
          data[key] = val;
        }
      });
      return data;
    },

    // format a query data object as a string
    format: $.param,

    // coerce a string into a query string data object
    coerce: function(data) {
      return (data && typeof data === "string")
        ? hourglass.qs.parse(data)
        : data || {};
    },

    // merge two or more query strings or data objects
    // into a single data object
    merge: function(data) {
      data = hourglass.qs.coerce(data);
      for (var i = 1; i < arguments.length; i++) {
        hourglass.extend(data, hourglass.qs.coerce(arguments[i]));
      }
      return data;
    }
  };

  // identity function
  hourglass.identity = function identity(d) {
    return d;
  };

  // noop function
  hourglass.noop = function noop() {
  };

  // export hourglass.extend()
  hourglass.extend = extend;

  /**
   * private utility functions
   */

  function extend(obj, ext) {
    for (var i = 1; i < arguments.length; i++) {
      var ex = arguments[i];
      if (!ex) continue;
      for (var k in ex) {
        obj[k] = ex[k];
      }
    }
    return obj;
  }

})(this.hourglass = {});
