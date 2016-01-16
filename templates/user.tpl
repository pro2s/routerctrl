{% extends "base.tpl" %}
{% block content %}	  
		<div class="span8">
		{% if uprefs.registred %}Зарегестрирован{%else%} Принять соглашение, зарегестрироватся {%endif%}
		{{uprefs}}
		</div>
		<div class="span4">
		
		</div>
{% endblock %}