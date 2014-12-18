(function(hourglass) {

  /**
   * var api = hourglass.API();
   * api.get("
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
          data = extend({
            format: "json"
          }, request.data);
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
          var key = part.substr(0, i),
              val = part.substr(i + 1);
          data[unescape(key)] = unescape(val);
        }
      });
      return data;
    },
    format: $.param
  };

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
