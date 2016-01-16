{% extends "base.tpl" %}
{% block content %}	  
		<div class="span8">
		{%if user.logon%}
		{{user.nikname}} 
		{% if uprefs.registred %}
		Зарегестрирован:
		<b>API:</b> {{uprefs.apikey}}
		{%else%} 
		
		Зарегестрироватся.
		<br>
		Пользовательское соглашение.
		<br>
		<form class="form-inline" action="/registration/" method = "post" >
		<label class="checkbox">
			<input type="checkbox" name="reg" value="yes"> Принять соглашение
		</label>
		<button type="submit" class="btn">Sign in</button>
		</form>
		{%endif%}
		<a href="{{user.logout_url}}">Sign out</a>
		{%else%}<a href="{{user.login_url}}">Sign in</a>{%endif%}
		</div>
		<div class="span4">
		
		</div>
{% endblock %}