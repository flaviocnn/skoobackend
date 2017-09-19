{% extends "mail_templated/base.tpl" %}

{% block subject %}
Buone notizie {{ user }}
{% endblock %}

{% block body %}
Ciao {{ user }}
l'utente {{ other_user }} e' disponibile per la trattativa del libro {{book}}
{% endblock %}

{% block html %}
{{ user }}, this is an <strong>html</strong> message.
{% endblock %}