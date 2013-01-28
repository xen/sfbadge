# sfbadge

Small API to use sourceforge.com downloads statistics embeded as AJAX calls hosted on Heroku. Sourceforge.com don't allow cross origin calls so that is primary reason to make this project.

## Install

Read this [official tutorial](https://devcenter.heroku.com/articles/python#start-flask-app-inside-a-virtualenv)  

## Usage

Format is very simple:

    http://sfbadge.herokuapp.com/sf/:reponame/:set
    

Parameters:

- `reponame` is your repository on sf.net, for example "fontforge"
- `set` is size of result set. Now it accept only two values: `json` and `fulljson`. `json` returns only total downloads number.

Optional parameters:

- `start_date` sourceforge allow to limit statistic to particular date range. If not provided then limited to 7 days ago. Format `%Y-%m-%d`
- `end_date`, if not provided then today, format the same
- `jsonp` callback function name for JSONP requests

## Example

For example you can use this code on [FontForge homepage](http://fontforge.github.com/en-US/index.html):

    Downloads <strong id="cnt-downloads"></strong>
    
    <script type="text/javascript">
    function humanise(n){
      var d = ',';
      var s = '.';
      n = n.toString().split('.');
      n[0] = n[0].replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1' + d);
      return n.join(s);
    };

    $(document).ready(function(){
        $.getJSON("http://sfbadge.herokuapp.com/sf/fontforge/json", function(json) {
            $('#cnt-downloads').html(humanise(json.total));
        });
    });
    </script>


