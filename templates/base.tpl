<!DOCTYPE html>
{% autoescape true %}
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Router{% endblock %}</title>
    <link href="/css/bootstrap.css" rel="stylesheet">
    <link href="/css/bootstrap-responsive.css" rel="stylesheet">
    <link href="/css/tablecloth.css" rel="stylesheet">
    <link href="/css/prettify.css" rel="stylesheet"> 

    <script src="/js/jquery-1.7.2.min.js"></script>
    <script src="/js/bootstrap.js"></script>
    <script src="/js/jquery.metadata.js"></script>
    <script src="/js/jquery.tablesorter.min.js"></script>
    <script src="/js/jquery.tablecloth.js"></script>

	{% block head%}{% endblock %}
  </head> 
  <body>

    
      
	{% block menu %}
	<div class="navbar navbar-static-top">
	<div class="navbar-inner">
    <a class="brand" href="#">Router Control</a>
    <ul class="nav">
      {% for item in menu %}
		<li {% if active==item.id %}class="active"{%endif%}><a href="{{item.url}}">{{item.name}}</a></li>
	  {% endfor %}
    </ul>
	<ul class="nav pull-right">
	<li>{%if user.logon%}{{user.nikname}}<a href="{{user.logout_url}}">Sign out</a>{%else%}<a href="{{user.login_url}}">Sign in</a>{%endif%}</li>
	</ul>
	</div>
	</div>
	{% endblock %}
		
	<div class="container">
	<div class="row">
		{% block content %}{% endblock %}
		{{ raw_content|safe }}
     </div>
	</div>
    
   
  </body>
</html>
{% endautoescape %}