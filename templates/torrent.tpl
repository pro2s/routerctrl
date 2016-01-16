{% extends "base.tpl" %}
{% block content %}	  
		<div class="span8">
		{% for row in torrent %}
			{% if row.name == "state" %}
        	<b>Состояние</b> - {{ row.value }} (обновлено: {{row.updated.strftime('%d.%m.%Y %H:%M')}})</br>
			{% endif %}
		{% endfor %}
		</br>
		Список активных торентов:</br>
		{% for t in torrents %}
			{% if t.status == 'downloading' %}
				{{t.status}} - {{t.name}} - {{'%0.2f' % t.progress|float}}% ({{'{0:,}'.format(t.totalSize)|replace(","," ")}})</br>
			{% endif %}
		{% endfor %}
		</br>
		Список скаченых:</br>
		{% for t in torrents %}
			{% if t.status != 'downloading' %}
				{{t.status}} - {{t.name}} - {{'%0.2f' % t.progress|float}}% ()</br>
			{% endif %}
		{% endfor %}
		</br>
		Добавить торрент:<br>
		<form name = "input" action = "/add" method = "post" enctype="multipart/form-data">
		torrent: <input type = "file" name = "file"><input type="submit">
		</form>
		</div>
		<div class="span4">
		Команды:<br>
		{% for row in commands %}
        	 {{ c_name.get(row.name) }} ({{ c_type.get(row.value)}})</br>
		{% endfor %}
		</div>
{% endblock %}