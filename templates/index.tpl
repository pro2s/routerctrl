{% extends "base.tpl" %}
{% block content %}	  
		<div class="span8">
		
		{% for row in router %}
			{% if row.name == "state" %}
        	<b>Состояние</b> - {{ row.value }} (обновлено: {{row.updated.strftime('%d.%m.%Y %H:%M')}})</br>
			{% endif %}
		{% endfor %}

		</div>
		<div class="span4">
		
		</div>
{% endblock %}