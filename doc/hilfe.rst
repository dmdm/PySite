Hilfe
#####

Die Adresse deiner Website lautet

	http://parenchym.com/pysite/sites/www.meine-adresse.de

Ist die Site fertig installiert, kann sie auch unter

	http://www.meine-adresse.de

erreicht werden.

Um die Seiten zu bearbeiten, führst du 3 Schritte durch:

1. Anmelden
2. Dateimanager aufrufen
3. Abmelden


Anmelden
========

Um dich anzumelden, führe den Befehl "@@login" aus, z.B.:
	
	http://parenchym.com/pysite/sites/www.meine-adresse.de/@@login


DateiManager
============

Den Dateimanager rufst du mit dem Befehl "@@filemgr" auf:
	
	http://parenchym.com/pysite/sites/www.meine-adresse.de/@@filemgr

Er lässt sich ähnlich bedienen wie der Dateimanager von Fenster. Du verwaltest damit
deine gesamte Website, d.h. alle Seiten, alle Styles, Scripte, Bilder etc.

Zwei Ordner sind vorgegeben (und müssen so bleiben):

"content": Hier legst du die einzelnen Seiten an

"assets": Hier speicherst du deine Bilder, Styles etc.

Du kannst nach Belieben Dateien und Unterordner anlegen. Hast du eine neue Datei
angelegt, ist sie zunächst leer. Hineinschreiben kannst du nach Rechtsklick auf die
Datei und "Datei bearbeiten". Es ist auch möglich, einzelne Dateien (z.B. Bilder)
von deinem Computer hochzuladen.

Erkunde die Icons des DateiManagers, indem du mit der Maus auf einem Icon verweilst:
ein kurzer Hilfetext erscheint.


Eine Seite anlegen
------------------

Seiten legst du im Ordner "content" an. Für jede sichtbare Seite musst du 2 Dateien erzeugen,
die eine für den Inhalt, die andere für Meta-Informationen wie z.B. Titel, Stichwörter etc. Der
Dateiname entspricht dann dem Namen der Seite in der URL.

Möchtest du z.B. eine Seite unter der Adresse

	http://parenchym.com/pysite/sites/www.meine-adresse.de/ueber-mich

anlegen, erzeugst du die Dateien ``ueber-mich.jinja2`` für den Inhalt
und ``ueber-mich.yaml`` für die Meta-Informationen.

In die jinja2-Datei schreibst du beliebiges HTML. Wie der Name schon andeutet,
wird die Datei durch das Template-System Jinja2_ verarbeitet. Wie das funktioniert
ist in der Jinja2 Dokumentation_ beschrieben. Schaue dir auch meine Beispieldateien
an.

In die yaml-Datei trägst du die Meta-Informationen ein, z.B. so:

	title: "Über mich"
	keywords: hase, igel, seepferd

In der Jinja-Datei kannst du auf ein solches Feld wieder zugreifen:

	<html>
	<head>
	<title>{{ page.title }}</title>
	<meta name="keywords" content="{{ page.keywords }}">
	</head>

Meine Beispieldateien zeigen, wie du mithilfe von Jinja mehrere Seiten mit dem selben
Master-Layout ausstatten kannst. Lies auch die Vererbungsdoku_ dazu.


Eine Seite verlinken
--------------------

Wenn du einen Link auf eine andere Seite deiner eigen Site setzen möchtest, geht das so:

	<a href="{{ url('andere-seite') }}">andere Seite</a>

Du schreibst nur den Namen ohne ".jinja2" bzw. ".yaml".

Einen externen Link setzt du HTML-üblich:
	
	<a href="http://www.wdrmaus.de/">Die Maus</a>


Ein Bild oder anderes Asset verlinken
-------------------------------------

Bild:

	<img src="{{ asset_url("img/grass-mud-horse2.jpg") }}">

Stylesheet:

	<link rel="stylesheet" href="{{ asset_url('css/main.css') }}">


Abmelden
========

Bist du mit der Arbeit fertig, meldest du dich mit dem Befehl "@@logout" wieder ab:

	http://parenchym.com/pysite/sites/www.meine-adresse.de/@@logout


.. _Jinja2: http://jinja.pocoo.org/docs/
.. _Dokumentation: http://jinja.pocoo.org/docs/templates/
.. _Vererbungsdoku: http://jinja.pocoo.org/docs/templates/#template-inheritance
